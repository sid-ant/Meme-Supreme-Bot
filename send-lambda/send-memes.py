import json
import logging
import requests
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)

url = os.environ['url']   #sendMediaGroup Telegram Method 
error_url = os.environ['eurl']

def send_photo(chat_id,memes):  
    InputMediaPhoto = []
    for meme in memes:
        media = {
            "type":"photo",
            "media":meme['ContentUrl'],
            "caption":meme['Caption']
        }
        InputMediaPhoto.append(media)

    InputMediaJson = json.dumps(InputMediaPhoto)
    body = {
        "chat_id":chat_id, 
        "media":InputMediaJson
    }

    logging.info("Constructed Request is f'{body}")
    response = requests.post(url, data=body)
    logging.info(f"Response f{response}")
    json_response = response.json()
    logging.info(f"Json Response f{json_response}")
    ok_status = json_response['ok']
    if not ok_status:
        send_error(chat_id)
    # check for ok field and create appropriate response 


def send_error(chat_id):
    error = "Error occured while getting memes, our engineers has been notified of their incompetency."

    body = {
        "chat_id":chat_id, 
        "text":error
    }
    
    logging.info(f"Constructed SendError Request '{body}")
    response = requests.post(error_url,data=body)
    logging.info(f"Response {response}")
    json_response = response.json()
    logging.info(f"SendError Respose {json_response}")
    ok_status = json_response['ok']
    if not ok_status:
        logging.error(f"SendError failed")
    

def lambda_handler(event, context):
    chat_id = event["chat_id"]
    memes = event["memes"]
    send_photo(chat_id,memes)