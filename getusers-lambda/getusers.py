import json
import logging
import os
from botocore.exceptions import ClientError
import boto3
from datetime import date
from boto3.dynamodb.conditions import Key, Attr

logger = logging.getLogger()
logger.setLevel(logging.info)

dynamodb = boto3.resource('dynamodb')

def get_users():
    users_table = dynamodb.Table('Chats')
    subscribers = []
    try:
        chats = users_table.scan(AttributesToGet=['chatid']) #TODO check for status is active 
        logger.info(f"chats type is {type(chats)} and value is {chats}")
        for items in chats['Items']:
            chat_id = items['chatid']
            subscribers.append(chat_id)
        logger.info(f"all subs are {subscribers}")
    except:
        logger.error("couldn't query db to get chats")
        raise Exception('Error occured while scanning for chatids')
    
    if len(subscribers)==0:
        logger.error("found no chat ids")
        raise Exception('No chat ids')
    return subscribers


def get_memes():
    today = date.today()
    current_day = today.strftime("%d/%m/%Y")
    memes_table = dynamodb.Table('Memes')
    logger.info("Looking for memes in the table")
    results = memes_table.query(Select="SPECIFIC_ATTRIBUTES",ScanIndexForward=True,KeyConditionExpression=Key("Meme_ID").eq(current_day),FilterExpression=Attr('Category').eq('default'),ProjectionExpression="Author,ContentUrl,PostUrl,Caption,Category",Limit=5)
    logger.info(f"Result is f{results}")
    memes = results['Items']
    if len(memes)==0:
        logger.error(f"Found no memes... ")
        raise Exception('DB returned no results')
    return memes


def lambda_handler(event, context):
    #TODO
    pass