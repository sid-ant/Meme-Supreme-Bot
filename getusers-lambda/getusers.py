import json
import logging
import os
from botocore.exceptions import ClientError
import boto3
from datetime import date
from boto3.dynamodb.conditions import Key, Attr


dynamodb = boto3.resource('dynamodb')

def get_users():
    pass

def get_memes():
    today = date.today()
    current_day = today.strftime("%d/%m/%Y")
    memes_table = dynamodb.Table('Memes')
    results = memes_table.query(Select="SPECIFIC_ATTRIBUTES",ScanIndexForward=True,KeyConditionExpression=Key("Meme_ID").eq(current_day),FilterExpression=Attr('Category').eq('default'),ProjectionExpression="Author,ContentUrl,PostUrl,Caption,Category",Limit=5)
    memes = results['Items']
    if len(memes)==0:
        raise Exception('DB returned no results')
    return memes


def lambda_handler(event, context):
    #TODO
    pass