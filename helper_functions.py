
from typing import Optional, List, Union, Dict
import fitz
from PIL import Image
import io

def pdf_to_images(pdf_bytes: bytes) -> List[Image.Image]:
    """
    Helper function: Convert PDF bytes to list of PIL Images
    """
    images = []
    try:
        pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        for page_number in range(len(pdf_document)):
            page = pdf_document[page_number]
            
            mat = fitz.Matrix(2, 2)
            pix = page.get_pixmap(matrix=mat)
            
            img_bytes = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_bytes))
            images.append(img)
        
        pdf_document.close()
        return images
        
    except Exception as e:
        print(f"Error converting PDF to images: {e}")
