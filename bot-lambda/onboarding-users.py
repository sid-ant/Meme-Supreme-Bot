import json
import logging
import boto3 
import requests
import os
from datetime import date
from botocore.exceptions import ClientError
from requests import RequestException
from boto3.dynamodb.conditions import Key, Attr

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')

texts = ['/start','/stop']

class ResponseMessages():
    registered = "Succefully, registered. Your path to being a meme-lord has begun! Welcome"
    already_re = "You are already registered"
    error_re = "Sorry, we couldn't register you. Please try again later."
    deregistered = "You have been successfully de-registered. Goodbye :("
    error_occured  = "I don't feel so good! an error occured"
    default = "Hi! MemeSupreme is primarly a meme delievery bot and doesn't yet support conversations. Thanks!" 

reply = ResponseMessages()

def lambda_handler(event, context):
    logger.info(f"Event {event}")
    logger.info(f"#Event Body {event['body']} ")
    body = event['body']
    body = json.loads(body)
    
    try:
        process(body["message"])
    except:
        logger.error("Exception when invoking process")
        raise 
    
    return {
        'statusCode': 200
    }

def process(request): 
    try:
        logger.info(f"request: {request}")

        user_id = request['from']['id']
        chat_id = request['chat']['id']
        username = request['from']['first_name']
        message = request['text']
        
        logger.info(f"user_id {user_id}, chat_id {chat_id}, message {message}")

        result_msg = reply.default 
        if message.lower() in texts:
            method_name = "perform_"+message[1:].lower()
            result_msg = globals()[method_name](chat_id,user_id,username)
        
        send_reply(chat_id,result_msg)
        if result_msg == reply.registered:
            send_memes(chat_id)
        
    except:
        logger.error("exeception occured while trying to match message with function")
        raise

# if already exists skip and send different message else insert 
def perform_start(chat_id,user_id,username):

    chats = dynamodb.Table("Chats")
    try:
        chats.put_item(Item={
            'chatid':str(chat_id),
            'userid':str(user_id),
            'username':str(username)
        },
        ConditionExpression='attribute_not_exists(chatid)'
        )
        logger.info("Successfully inserted the chatid in the db")
        return reply.registered
    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            logger.info(f'already registered {e}')
            return reply.already_re
        else:
            logger.error(f"Error while inserting into table Chats {e.response['Error']['Message']}")
    return reply.error_re


def perform_stop(chat_id,user_id,username):
    chats = dynamodb.Table("Chats")    
    try:
        deleted = chats.delete_item(Key={
            'chatid':str(chat_id)
        },
        ReturnValues='ALL_OLD')
        logger.info(f"{deleted} deleted successfully")
        return reply.deregistered
    except ClientError as e:
        logger.error(e.response['Error']['Message'])

    return reply.error_occured

# decouple this and put it in seperate lambda? 
def send_reply(chat_id,message):
    accesscode = os.environ['accesscode']

    try:
        url = f"https://api.telegram.org/bot{accesscode}/sendMessage"
        logger.info(f"url formed is {url}")
        response = requests.post(url, data={'chat_id':chat_id,'text':message})
        logger.info(f"Successfully sent message! {message}")
    except RequestException as e:
        logger.error(f"Couldn't send reply {e}")


def send_memes(chat_id):
    memes = get_memes()
    logger.info("Succesfully Retrived memes")
    data = {}
    data['chat_id']=chat_id
    data['memes']=memes
    data = json.dumps(data)
    aws_lambda = boto3.client('lambda')
    logger.info("Calling Send-Memes Lambda")
    response = aws_lambda.invoke(
        FunctionName="Send-Memes",
        InvocationType='Event',
        Payload=data
    )
    logger.info(f"Send-Meme Lambda Added to Queue? Response: {response}")
    return

def get_memes():
    today = date.today()
    current_day = today.strftime("%d/%m/%Y")
    memes_table = dynamodb.Table('Memes')
    results = memes_table.query(Select="ALL_ATTRIBUTES",ScanIndexForward=True,KeyConditionExpression=Key("Meme_ID").eq(current_day),FilterExpression=Attr('Category').eq('default'),Limit=5)
    memes = results['Items']
    if len(memes)==0:
        raise Exception('DB returned no results')
    return memes