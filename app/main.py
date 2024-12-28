from uvicorn import main
from fastapi import FastAPI
import uuid 
from ..database import Database
from ..langchain import Agent,Config


app = FastAPI()

@app.post("/ChatBot")

async def ChatBot(session_id: str = None,  message: str = ""):
    if session_id is None:
        session_id = str(uuid.uuid4())
        print("New session_id:", session_id)
    else:
        print("Old session_id:", session_id)
    message = f"'session_id':'{session_id}','message':'{message}'"
    agent=Agent.create_agent(session_id)

    response=agent.invoke({"input": message})
    # if Config.bearer_token!=None:
    #     print("inside agents",Config.session_id,Config.bearer_token)
    #     Database.update_bearer_token(Config.session_id, Config.bearer_token)
    result=response.get('output') 
    
    if result:
        return result
    else:
        return {"error": "Unable to get data"}


































# import json
# from agents import *

# import random
# import logging   #The logging module is imported and configured to log at the INFO level.
# logging.basicConfig(level=logging.INFO)


# def chat(event, context):
#     data = json.loads(event['body'])
   
#     session_id= data.get('session_id')
   
#     # If session_id is not present, generate a random one
#     if not session_id :
#         session_id = str(random.randint(100000, 999999))    
#         logging.info(f'Generated new session_id: {session_id}')
#         print(f'Generated new session_id: {session_id}')

#     message = data.get('message')
#     message = f"'session_id':'{session_id}','message':'{message}'"
#     agent=create_agent(session_id)

    
#     response=agent.invoke({"input": message,})
#     if config.bearer_token!=None:
#         print("inside agents",config.session_id,config.bearer_token)
#         update_bearer_token(config.session_id, config.bearer_token)
#     result=response.get('output')

#     response = {
#         "statusCode": 200,
#         "headers": {
#             'Access-Control-Allow-Origin': '*',
#             'Content-Type': 'application/json',
#         },
#         "body": json.dumps(result)
#     }

#     return response
