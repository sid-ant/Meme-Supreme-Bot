import json
import logging
import os
from botocore.exceptions import ClientError
import boto3
from datetime import date
from boto3.dynamodb.conditions import Key, Attr

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')

def get_users():
    users_table = dynamodb.Table('Chats')
    subscribers = []
    chats = users_table.scan(ProjectionExpression='chatid,user_status',FilterExpression=Attr('user_status').eq(True)) 
    logger.info(f"chats type is {type(chats)} and value is {chats}")
    for items in chats['Items']:
        chat_id = items['chatid']
        subscribers.append(chat_id)
    logger.info(f"all chats are {subscribers}")
    if len(subscribers)==0:
        logger.error("found no chat ids")
        raise Exception('No chat ids')
    return subscribers


def get_memes():
    today = date.today()
    current_day = today.strftime("%d/%m/%Y")
    memes_table = dynamodb.Table('Memes')
    logger.info("Looking for memes in the table")
    results = memes_table.query(Select="SPECIFIC_ATTRIBUTES",ScanIndexForward=False,KeyConditionExpression=Key("Meme_ID").eq(current_day),FilterExpression=Attr('Category').eq('default'),ProjectionExpression="Author,ContentUrl,PostUrl,Caption,Category",Limit=5)
    logger.info(f"Result is f{results}")
    memes = results['Items']
    if len(memes)==0:
        logger.error(f"Found no memes... ")
        raise Exception('DB returned no results')
    return memes


def lambda_handler(event, context):
    logging.info("get users_memes started")
    users = get_users()
    memes = get_memes()
    lambda_client = boto3.client('lambda')
    for user in users:
        logging.info(f'Sending memes to chat_id {user}')
        data = {}
        data['chat_id']=user
        data['memes']=memes
        data = json.dumps(data)
        response = lambda_client.invoke(
            FunctionName="sendMemes",
            InvocationType='Event',
            Payload=data
        )
        logger.info(f"Invoked sendMemes Lambda with response f{response}")
