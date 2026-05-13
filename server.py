from fastapi import FastAPI, UploadFile, File
from create_database import create_database
from chat_db import load_chat, save_message
from query_data import llm_response
from pydantic import BaseModel

app = FastAPI()

class ChatRequest(BaseModel):
    user_input: str
    collection_name: str

@app.get("/")
def home():
    return {"response": "Server is live..."}


@app.post("/upload_file")
async def upload_file(uploaded_file: UploadFile = File(...)):
    print(uploaded_file)
    name = await create_database(uploaded_file)

    return {"collection_name": name}


@app.get("/load_chat")
def load_chats(collection_name: str):
    chats = load_chat(collection_name)

    return {"chat_list": chats}


@app.post("/send_chat")
def send_chat(data: ChatRequest):
    save_message(
        collection_name=data.collection_name,
        content=data.user_input.strip(),
        role="user",
    )
    response = llm_response(query_text=data.user_input, collection_name=data.collection_name)
    save_message(
        collection_name=data.collection_name,
        content=response,
        role="assistant",
    )
    return {"response": response}
