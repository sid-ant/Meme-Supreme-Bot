# Meme-Supreme-Bot

Get top teir memes from reddit sent directly to your telegram in fixed intervals.


1. bot-lambda : Handles user inputs, registers and deregisters users. Communicates with DynamoDB. 
2. send-lambda : Send memes to a user. Takes chat_id as input. 
3. reddit-lambda: Calls reddit APIs to get top teir meme and store their urls in DynamoDB. 
4. getusers-lambda: Gets a list of users from DynamoDB and calls send-lambda for each user. 
