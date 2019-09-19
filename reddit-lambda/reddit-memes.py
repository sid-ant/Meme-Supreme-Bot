import praw
import os
import logging
import boto3 
from requests_futures.sessions import FuturesSession

logger = logging.getLogger()
logger.setLevel(logging.INFO)

db = boto3.resource('dynamodb')
table = db.Table('Chats')

def lambda_handler(event,context):
    try:
        dank = get_dem_memes()
        subsribers = get_chats()
        boys_go_deliver(dank,subsribers)
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
        if submission.url.find("i.redd.it")!=-1:
            memes.append(submission.url)
    memes = memes[:6]
    logger.info(f"Got memes from reddit {memes}")
    return memes    


def store_memes():
    #TODO
    pass

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