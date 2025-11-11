from pydantic import BaseModel, Field
from openai import OpenAI
from typing import Optional
import json
from dotenv import load_dotenv

load_dotenv()

class QatarID(BaseModel):
    """Qatar ID information extraction model"""
    id_no: str = Field(default="", description="Qatar ID number")
    name: str = Field(default="", description="Full name of the person")
    expiry_date: str = Field(default="", description="Qatar ID expiry date")
    dob: str = Field(default="", description="Date of birth")
    occupation: str = Field(default="", description="Occupation")
    nationality: str = Field(default="", description="Nationality")
    passport_number: str = Field(default="", description="Passport number")
    passport_expiry: str = Field(default="", description="Passport expiry date")
    serial_no: str = Field(default="", description="Serial number")
    employer: str = Field(default="", description="Employer name")


class Istimara(BaseModel):
    """Istimara (Vehicle Registration) information extraction model"""
    vehicle_number: str = Field(default="", description="Vehicle plate number")
    vehicle_type: str = Field(default="", description="Type of vehicle")
    owner_ar: str = Field(default="", description="Owner name in Arabic")
    owner_en: str = Field(default="", description="Owner name in English")
    owner_qid: str = Field(default="", description="Owner's Qatar ID")
    nationality: str = Field(default="", description="Owner's nationality")
    vehicle_expiry_date: str = Field(default="", description="Vehicle registration expiry date")
    vehicle_renewal_date: str = Field(default="", description="Vehicle renewal date")
    vehicle_registration_date: str = Field(default="", description="Vehicle registration date")
    vehicle_make: str = Field(default="", description="Vehicle manufacturer/make")
    vehicle_model: str = Field(default="", description="Vehicle model")
    vehicle_body_type: str = Field(default="", description="Vehicle body type")
    vehicle_year: str = Field(default="", description="Vehicle manufacturing year")
    vehicle_shape: str = Field(default="", description="Vehicle shape")
    vehicle_cylinder: str = Field(default="", description="Number of cylinders")
    vehicle_seat: str = Field(default="", description="Number of seats")
    vehicle_weight: str = Field(default="", description="Vehicle weight")
    vehicle_net_weight: str = Field(default="", description="Vehicle net weight")
    vehicle_color: str = Field(default="", description="Vehicle color")
    vehicle_chassis_no: str = Field(default="", description="Chassis number")
    vehicle_engine_no: str = Field(default="", description="Engine number")
    vehicle_insurance_company: str = Field(default="", description="Insurance company name")
    vehicle_policy_number: str = Field(default="", description="Insurance policy number")
    vehicle_expiry: str = Field(default="", description="Insurance expiry date")
    vehicle_policy_type: str = Field(default="", description="Insurance policy type")


class DocumentExtractionResponse(BaseModel):
    """Combined response model for both Qatar ID and Istimara"""
    qatar_id: QatarID
    istimara: Istimara


def extract_document_info(context: str, api_key: str = None) -> dict:
    """
    Extract Qatar ID and Istimara information from the given context.
    
    Args:
        context: Text content containing Qatar ID and/or Istimara information
        api_key: OpenAI API key (optional, will use environment variable if not provided)
    
    Returns:
        Dictionary with extracted information in the specified structure
    """
    # Initialize OpenAI client
    client = OpenAI(api_key=api_key) if api_key else OpenAI()
    
    # Create the completion with structured output
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {
                "role": "system",
                "content": """You are an expert document information extractor for Qatar documents.
                Extract all available information from Qatar ID cards and Istimara (vehicle registration) documents.
                
                Important instructions:
                - Extract ALL information that is present in the context
                - If a field is not mentioned or cannot be found, leave it as an empty string ""
                - Be precise and accurate with dates, numbers, and names
                - For names, extract both Arabic and English versions if available
                - Ensure all extracted data matches the original context exactly
                """
            },
            {
                "role": "user",
                "content": f"Extract Qatar ID and Istimara information from the following context:\n\n{context}"
            }
        ],
        response_format=DocumentExtractionResponse,
    )
    
    # Get the parsed response
    extracted_data = completion.choices[0].message.parsed
    
    # Convert to dictionary
    result = {
        "qatar_id": extracted_data.qatar_id.model_dump(),
        "istimara": extracted_data.istimara.model_dump()
    }
    
    return result


def extract_document_info_with_refusal_handling(context: str, api_key: str = None) -> dict:
    """
    Extract document information with proper refusal handling.
    
    Args:
        context: Text content containing Qatar ID and/or Istimara information
        api_key: OpenAI API key (optional, will use environment variable if not provided)
    
    Returns:
        Dictionary with extracted information or error message
    """
    client = OpenAI(api_key=api_key) if api_key else OpenAI()
    
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {
                "role": "system",
                "content": """You are an expert document information extractor for Qatar documents.
                Extract all available information from Qatar ID cards and Istimara (vehicle registration) documents.
                
                Important instructions:
                - Extract ALL information that is present in the context
                - If a field is not mentioned or cannot be found, leave it as an empty string ""
                - Be precise and accurate with dates, numbers, and names
                - For names, extract both Arabic and English versions if available
                - Ensure all extracted data matches the original context exactly
                """
            },
            {
                "role": "user",
                "content": f"Extract Qatar ID and Istimara information from the following context:\n\n{context}"
            }
        ],
        response_format=DocumentExtractionResponse,
    )
    
    message = completion.choices[0].message
    
    # Check for refusal
    if message.refusal:
        return {
            "error": "Request was refused",
            "refusal_message": message.refusal
        }
    
    # Get the parsed response
    extracted_data = message.parsed
    
    result = {
        "qatar_id": extracted_data.qatar_id.model_dump(),
        "istimara": extracted_data.istimara.model_dump()
    }
    
    return result


# # Example usage
# if __name__ == "__main__":
#     # Example context with Qatar ID and Istimara information
#     sample_context = """
#     Qatar ID Information:
#     ID Number: 12345678901
#     Name: Ahmed Mohammed Al-Kuwari
#     Date of Birth: 15/03/1985
#     Nationality: Qatari
#     Occupation: Engineer
#     Passport Number: A1234567
#     Passport Expiry: 20/12/2028
#     Serial Number: QA-2024-001
#     Expiry Date: 10/05/2025
#     Employer: Qatar Petroleum
    
#     Istimara (Vehicle Registration) Information:
#     Vehicle Number: 12345
#     Owner (English): Ahmed Mohammed Al-Kuwari
#     Owner (Arabic): أحمد محمد الكواري
#     Owner QID: 12345678901
#     Nationality: Qatari
#     Vehicle Type: Private
#     Vehicle Make: Toyota
#     Vehicle Model: Land Cruiser
#     Vehicle Year: 2022
#     Vehicle Color: White
#     Body Type: SUV
#     Chassis Number: JTMCY7AJ5K4123456
#     Engine Number: 1GRFE123456
#     Number of Cylinders: 8
#     Number of Seats: 7
#     Vehicle Weight: 2500 kg
#     Net Weight: 1800 kg
#     Registration Date: 15/01/2022
#     Expiry Date: 15/01/2025
#     Renewal Date: 15/01/2024
#     Insurance Company: Qatar Insurance Company
#     Policy Number: QIC-2024-12345
#     Insurance Expiry: 15/01/2025
#     Policy Type: Comprehensive
#     """
    
#     # Extract information
#     try:
#         result = extract_document_info_with_refusal_handling(sample_context)
        
#         # Pretty print the result
#         print(json.dumps(result, indent=2, ensure_ascii=False))
        
#     except Exception as e:
#         print(f"Error: {str(e)}")
#         print("Make sure you have set your OPENAI_API_KEY environment variable")