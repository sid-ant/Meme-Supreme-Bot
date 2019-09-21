import praw
import os
import logging
import boto3 
import time
from datetime import date
from botocore.exceptions import ClientError


logger = logging.getLogger()
logger.setLevel(logging.INFO)

db = boto3.resource('dynamodb')
table_memes = db.Table('Memes')

def lambda_handler(event,context):
    try:
        memes = get_reddit_memes()
        store_memes(memes,'default')
    except:
        logger.info("opps, something bad happened")
        raise
    
def get_reddit_memes():
    clientid = os.environ['client_id']
    secret = os.environ['client_secret']
    user_agent = os.environ['useragent']
    reddit = praw.Reddit(client_id=clientid,
                     client_secret=secret,
                     user_agent=user_agent)

    logger.info(f"The reddit is in {reddit.read_only}")
    memes=[]
    for submission in reddit.subreddit("memes").top('day',limit=10):
        post = {}
        if submission.url.find("i.redd.it")!=-1:
            post['content_url']=submission.url
            post['caption']=submission.title
            post['url']=submission.permalink
            post['author']=submission.author
            memes.append(post)
    logger.info(f"Got memes from reddit {memes}")
    return memes    


def store_memes(memes,category):
    today = date.today()
    current_day = today.strftime("%d/%m/%Y")
    for m in memes:
        logger.info(f"storing meme : {m}")
        epoch = int(round(time.time() * 1000))
        try:
            table_memes.put_item(
                Item={
                    "Meme_ID":current_day, 
                    "Creation_Time":epoch,
                    "ContentUrl":m["content_url"],
                    "Caption":m["caption"],
                    "Url":m["url"],
                    "Author":m["author"].name,
                    "Category":category
                },
                ConditionExpression='attribute_not_exists(Creation_Time)'
            )
        logger.info(f"successfully stored meme : {m}")
        except ClientError as e:
            logger.error(f"Error while inserting into table Memes {e.response['Error']['Message']}")
    return

# query database
# def get_chats():
#     try:
#         subsribers = []
#         chats = table.scan(AttributesToGet=['chatid'])
#         logger.info(f"chats type xx is {type(chats)} and value is {chats}")
#         for items in chats['Items']:
#             chat_id = items['chatid']
#             subsribers.append(chat_id)
#         logger.info(f"all subs are {subsribers}")
#         return subsribers
#     except:
#         logger.info("couldn't query db to get chats")
#     return None


# make async calls to telegram api 
# def boys_go_deliver(good_stuff,audience):
#     accesscode = os.environ['accesscode']
#     try:
#         session = FuturesSession()
#         url = f"https://api.telegram.org/bot{accesscode}/sendPhoto"
#         logger.info(f"url formed is {url}")
#         for chat_id in audience:
#             for stuff in good_stuff:
#                 response = session.post(url, data={'chat_id':chat_id,'photo':stuff})
#         logger.info(f"Successfully sent message! {good_stuff}")
#     except:
#         logger.error(f"Couldn't send reply")