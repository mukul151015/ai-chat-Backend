from ast import get_docstring
from datetime import datetime
from fastapi import FastAPI, HTTPException, WebSocket, Depends,status
from fastapi.middleware.cors import CORSMiddleware
import jwt
from sqlalchemy.orm import Session
from auth_bearer import ALGORITHM, JWTBearer
import models
import schemas
from models import TokenTable, User
from database import Base, engine, SessionLocal
import json
import websockets
import uvicorn
import asyncio
from dotenv import load_dotenv
import os

from utils import JWT_SECRET_KEY, create_access_token, create_refresh_token, get_hashed_password, verify_password

load_dotenv() 
 
app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

Base.metadata.create_all(engine)
def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
app=FastAPI()

@app.post("/register")
def register_user(user: schemas.UserCreate, session: Session = Depends(get_session)):
    existing_user = session.query(models.User).filter_by(email=user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    encrypted_password =get_hashed_password(user.password)

    new_user = models.User(username=user.username, email=user.email, password=encrypted_password )

    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    return {"message":"user created successfully"}    

@app.post('/login', response_model=schemas.TokenSchema)
def login(request: schemas.requestdetails, db: Session = Depends(get_session)):
    user = db.query(User).filter(User.email == request.email).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email"
        )

    access = create_access_token(user.id)
    refresh = create_refresh_token(user.id)

    # Check if a token entry for the user already exists
    token_db = db.query(models.TokenTable).filter_by(user_id=user.id).first()

    if token_db:
        # Update the existing token entry
        token_db.access_token = access
        token_db.refresh_token = refresh
        token_db.status = True
    else:
        # Create a new token entry
        token_db = models.TokenTable(
            user_id=user.id,
            access_token=access,
            refresh_token=refresh,
            status=True
        )

    db.add(token_db)
    db.commit()
    db.refresh(token_db)

    return {
        "access_token": access,
        "refresh_token": refresh,
    }




# Add CORS middleware to allow cross-origin requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to match your frontend's domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connection configuration
HOST = os.getenv('HOST')
URI = f'wss://{HOST}/api/v1/stream'

@app.post("/generate-text")  # Modify the API endpoint route as needed
async def generate_text(input_data: dict):
    # print("coming here")
      # Receive data from the frontend
    try:
        text = input_data.get("text")  # Extract the "text" field from the input data
        # return input_data
        if text is None:
            return {"error": "Missing 'text' field in input data"}
        async with websockets.connect(URI, ping_interval=None) as websocket:
            request = { 
                'prompt': text,
                'max_new_tokens': 250,
                'auto_max_new_tokens': False,
                'history': None,
                'mode': 'instruct',  # Valid options: 'chat', 'chat-instruct', 'instruct'
                'character': 'Example',
                'instruction_template': 'Vicuna-v1.1',  # Will get autodetected if unset
                'your_name': 'You',
                # 'name1': 'name of user', # Optional
                # 'name2': 'name of character', # Optional
                # 'context': 'character context', # Optional
                # 'greeting': 'greeting', # Optional
                # 'name1_instruct': 'You', # Optional
                # 'name2_instruct': 'Assistant', # Optional
                # 'context_instruct': 'context_instruct', # Optional
                # 'turn_template': 'turn_template', # Optional
                'regenerate': False,
                '_continue': False,
                # 'chat_instruct_command': 'Continue the chat dialogue below. Write a single reply for the character "<|character|>".\n\n<|prompt|>',

                # Generation params. If 'preset' is set to different than 'None', the values
                # in presets/preset-name.yaml are used instead of the individual numbers.
                'preset': 'None',
                'do_sample': True,
                'temperature': 0.7,
                'top_p': 0.1,
                'typical_p': 1,
                'epsilon_cutoff': 0,  # In units of 1e-4
                'eta_cutoff': 0,  # In units of 1e-4
                'tfs': 1,
                'top_a': 0,
                'repetition_penalty': 1.18,
                'repetition_penalty_range': 0,
                'top_k': 40,
                'min_length': 0,
                'no_repeat_ngram_size': 0,
                'num_beams': 1,
                'penalty_alpha': 0,
                'length_penalty': 1,
                'early_stopping': False,
                'mirostat_mode': 0,
                'mirostat_tau': 5,
                'mirostat_eta': 0.1,
                'guidance_scale': 1,
                'negative_prompt': '',

                'seed': -1,
                'add_bos_token': True,
                'truncation_length': 2048,
                'ban_eos_token': False,
                'skip_special_tokens': True,
                'stopping_strings': []
            }

            await websocket.send(json.dumps(request))
            
            response_text = ""
            while True:
                incoming_data = await websocket.recv()
                incoming_data = json.loads(incoming_data)

                if incoming_data['event'] == 'text_stream':
                    response_text += incoming_data['text']
                elif incoming_data['event'] == 'stream_end':
                    break
                
            return {"generated_text": response_text}
    except websockets.exceptions.ConnectionClosedError as e:
        print("WebSocket Connection Closed:", e)
        return {"error": "WebSocket Connection Closed"}
    except Exception as e:
        print("WebSocket Error:", e)
        return {"error": "WebSocket Error"}

if __name__ == '__main__':
    PORT = os.getenv('PORT') //8000
    uvicorn.run(app, host="0.0.0.0", port=PORT)
