import json
import logging
import requests
import os

url = os.environ['url']   #sendMediaGroup Telegram Method 
error_url = os.environ['eurl']

def send_photo(chat_id,memes):
    
    InputMediaPhoto = []
    for meme in memes:
        media = {
            "type":"photo",
            "media":meme['url'],
            "caption":meme['caption']
        }
        InputMediaPhoto.append(media)

    body = {
        "chat_id":chat_id, 
        "media":InputMediaPhoto
    }

    logging.info("Constructed Request is f'{body}")
    response = requests.post(url, data=body)
    logging.info("Response f{response}")
    json_response = response.json()
    # check for ok field and create appropriate response 


def send_error(chat_id):
    error = "Error occured while getting memes, our engineers has been notified of their incompetency."

    body = {
        "chat_id":chat_id, 
        "message":error
    }
    
    logging.info("Constructed Error Response f'{body}")
    response = requests.post(url,data=body)
    logging.info("Response f{response}")
    json_response = response.json()
    # check here as well, if error occurs here generate a urgent sms to notify me. # have a flag to keep track if all requests are failing send msg only once 


def lambda_handler(event, context):
    #TODO
    pass