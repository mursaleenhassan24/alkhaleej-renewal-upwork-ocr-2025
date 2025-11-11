# gcp_helper.py me ye simple solution use karen:

import io
from google.cloud import vision
from google.api_core import retry
from google.api_core.exceptions import ServiceUnavailable, InternalServerError, DeadlineExceeded
from PIL import Image
import os
import time
import logging

class GCPHelper:
    def __init__(self):
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'alkhaleej-454901-15ecd8efcec5.json'
    
    def extract_text_from_image(self, image):
        """Simple retry with fresh client creation"""
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Fresh client har attempt pe
                client = vision.ImageAnnotatorClient()
                
                # Convert PIL Image to bytes
                img_byte_arr = io.BytesIO()
                image.save(img_byte_arr, format='PNG')
                img_byte_arr.seek(0)
                
                # Create Vision API image object
                vision_image = vision.Image(content=img_byte_arr.getvalue())
                
                # Perform text detection with timeout
                response = client.text_detection(
                    image=vision_image,
                    retry=retry.Retry(
                        predicate=retry.if_exception_type(
                            ServiceUnavailable,
                            InternalServerError,
                            DeadlineExceeded
                        ),
                        initial=2.0,
                        maximum=60.0,
                        multiplier=2.0,
                        deadline=180.0  # Total 3 minutes
                    ),
                    timeout=90.0  # Individual request timeout
                )
                
                # Close client connection explicitly
                if hasattr(client, 'transport') and hasattr(client.transport, 'grpc_channel'):
                    client.transport.grpc_channel.close()
                
                if response.error.message:
                    raise Exception(f"Vision API Error: {response.error.message}")
                
                # Process response
                texts = response.text_annotations
                if not texts:
                    return "", 0.0
                    
                full_text = texts[0].description
                
                # Calculate confidence
                total_confidence = 0.0
                word_count = 0
                
                for text in texts[1:]:
                    if hasattr(text, 'confidence'):
                        total_confidence += text.confidence
                        word_count += 1
                
                overall_confidence = total_confidence / word_count if word_count > 0 else 0.0
                
                return full_text, overall_confidence
                
            except (ServiceUnavailable, InternalServerError, DeadlineExceeded) as e:
                logging.warning(f"GCP OCR attempt {attempt + 1} failed: {str(e)}")
                
                if attempt == max_retries - 1:
                    raise Exception(f"GCP Vision API failed after {max_retries} attempts: {str(e)}")
                
                # Wait before retry
                wait_time = (2 ** attempt) + 1
                logging.info(f"Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
                
            except Exception as e:
                logging.error(f"Unexpected OCR error: {str(e)}")
                raise
        
        return "", 0.0