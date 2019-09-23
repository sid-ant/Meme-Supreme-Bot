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
    logger.info("Creating reddit client")
    reddit = praw.Reddit(client_id=clientid,
                     client_secret=secret,
                     user_agent=user_agent)

    logger.info(f"Client created  in {reddit.read_only}")
   
    subreddits = ['wholesomememes','memes','pics','aww','CozyPlaces']
    memes=[]
    for i in subreddits:
        memes = get_subreddit_posts(i,memes,reddit)
    
    return memes 

def get_subreddit_posts(subr,memes,reddit):
    max_score = 0 
    best_submission = None
    for submission in reddit.subreddit(subr).hot(limit=5):
        if submission.url.find("i.redd.it")==-1 or submission.over_18 is True:
            continue
        if submission.score>max_score:
            max_score = submission.score
            best_submission = submission

    if not best_submission:
        return  

    post = {}
    post['content_url']=best_submission.url
    post['caption']=best_submission.title
    post['url']=best_submission.permalink
    post['author']=best_submission.author
    memes.append(post)
    logger.info(f"Got memes from reddit {post}")
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

