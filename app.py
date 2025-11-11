from fastapi import FastAPI, File, UploadFile, HTTPException, Header, Depends, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import uvicorn

from pydantic import BaseModel, Field
from typing import Optional, List, Union, Dict

from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)

class OCR_Model(BaseModel):
    request_id: str
    client_name: str
    phone_number: str

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}


@app.post("/ocr-processing")
async def ocr_processing(request: OCR_Model):
    try:
        request_id = request.request_id
        client_name = request.client_name
        phone_number = request.phone_number

    except Exception as e:
        print(f"Exception OCR Processing: {e}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9001)