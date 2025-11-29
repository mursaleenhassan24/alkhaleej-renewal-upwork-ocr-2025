from fastapi import FastAPI, File, UploadFile, HTTPException, Header, Depends, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from typing import Optional, List, Union, Dict

from dotenv import load_dotenv
import os
import io
import fitz  # PyMuPDF
from PIL import Image
import json

from ocr import GCPHelper
from llm_response import extract_document_info_with_refusal_handling
from database import MongoDB, CRUDOperations
from helper_functions import *
from whatsapp_func import *

load_dotenv()

# Initialize database connection
mongo_connection = os.getenv("MONGO_DB_URI")
mongo_db_name = os.getenv("MONGO_DB_NAME")

mongodb = MongoDB(mongo_connection, mongo_db_name)

# Initialize CRUD operations for different collections
documents_crud = CRUDOperations(mongodb, "documents")
qatar_ids_crud = CRUDOperations(mongodb, "qatar_ids")
istimaras_crud = CRUDOperations(mongodb, "istimaras")
requests_crud = CRUDOperations(mongodb, "requests")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}


@app.post("/ocr-processing")
async def ocr_processing(
    request_id: str = Form(...),
    client_name: str = Form(...),
    phone_number: str = Form(...),
    files: List[UploadFile] = File(...)
):
    """
    OCR Processing Endpoint:
    - Accepts multiple files (PDF or images)
    - Converts PDFs to images
    - Processes all images through GCP OCR
    - Extracts structured data using ChatGPT
    - Stores data in MongoDB
    - Returns extracted data and database IDs
    """
    try:
        if not files:
            raise HTTPException(status_code=400, detail="No files uploaded")
        
        # Initialize GCP OCR helper
        gcp_helper = GCPHelper()
        
        all_extracted_text = ""
        processed_files_info = []
        
        # Process each uploaded file
        for file in files:
            file_content = await file.read()
            file_name = file.filename
            file_size = len(file_content)
            mime_type = file.content_type
            
            images_to_process = []
            
            # Check if PDF or image
            if mime_type == "application/pdf":
                print(f"Converting PDF to images: {file_name}")
                images_to_process = pdf_to_images(file_content)
            else:
                # Assume it's an image
                try:
                    img = Image.open(io.BytesIO(file_content))
                    images_to_process = [img]
                except Exception as e:
                    print(f"Error opening image {file_name}: {e}")
                    continue
            
            # Process each image with GCP OCR
            file_text = ""
            for idx, img in enumerate(images_to_process):
                print(f"Processing image {idx + 1}/{len(images_to_process)} from {file_name}")
                extracted_text, confidence = gcp_helper.extract_text_from_image(img)
                file_text += extracted_text + "\n"
            
            all_extracted_text += file_text + "\n\n"
            
            # Store file info
            processed_files_info.append({
                "file_name": file_name,
                "file_size": file_size,
                "mime_type": mime_type,
                "pages_processed": len(images_to_process),
                "extracted_text_length": len(file_text)
            })
        
        print(f"Total extracted text length: {len(all_extracted_text)}")
        
        # Pass extracted text to ChatGPT for structured extraction
        print("Extracting structured data using ChatGPT...")
        structured_data = extract_document_info_with_refusal_handling(all_extracted_text)
        
        # Check for errors in extraction
        if "error" in structured_data:
            raise HTTPException(
                status_code=500, 
                detail=f"ChatGPT extraction failed: {structured_data.get('refusal_message', 'Unknown error')}"
            )
        
        # Store Qatar ID data in database
        qatar_id_data = dict(structured_data.get("qatar_id", {}))
        qatar_id_data["request_id"] = request_id
        qatar_id_id = await qatar_ids_crud.create(qatar_id_data)
        print(f"Qatar ID stored with ID: {qatar_id_id}")
        
        # Store Istimara data in database
        istimara_data = dict(structured_data.get("istimara", {}))
        istimara_data["request_id"] = request_id
        istimara_id = await istimaras_crud.create(istimara_data)
        print(f"Istimara stored with ID: {istimara_id}")
        
        # Prepare response data
        response_data = {
            "success": True,
            "request_id": request_id,
            "client_name": client_name,
            "phone_number": phone_number,
            "files_processed": len(files),
            "files_info": processed_files_info,
            "extracted_data": {
                "qatar_id": dict(structured_data.get("qatar_id", {})),
                "istimara": dict(structured_data.get("istimara", {}))
            }
        }
        
        # Send WhatsApp message with extracted information
        try:
            from whatsapp_func import format_extraction_message
            
            whatsapp_message = format_extraction_message(
                request_id=request_id,
                client_name=client_name,
                qatar_id_data=dict(structured_data.get("qatar_id", {})),
                istimara_data=dict(structured_data.get("istimara", {}))
            )
            
            whatsapp_result = send_text_message(phone_number, whatsapp_message)
            
            if whatsapp_result.get("success"):
                print(f"WhatsApp message sent successfully to {phone_number}")
                response_data["whatsapp_sent"] = True
            else:
                print(f"Failed to send WhatsApp message: {whatsapp_result.get('error')}")
                response_data["whatsapp_sent"] = False
                response_data["whatsapp_error"] = whatsapp_result.get("error")
                
        except Exception as e:
            print(f"Error sending WhatsApp message: {e}")
            response_data["whatsapp_sent"] = False
            response_data["whatsapp_error"] = str(e)
        
        return JSONResponse(content=response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Exception OCR Processing: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"OCR processing failed: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9001)