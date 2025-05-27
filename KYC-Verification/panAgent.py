import os
import requests
from PIL import Image, ImageDraw
import io
import json
from config import configOpenAI
from encodeImagesBase64 import encode_image_to_base64_resized

# Obtain OPENAI_API_KEY from configuration
CONFIG_OPEN_API = configOpenAI()
OPENAI_API_KEY = CONFIG_OPEN_API.get('openai_api_key', None)


if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable not set.")

# Path to the PAN card image file
# IMAGE_PATH = os.path.join("Documents", "PAN-Tuhin.jpg")#"/Documents/PAN-Tuhin.jpg"

# --- PAN Card Parsing Function ---
def parse_pan_card(image_path):
    """
    Parses a PAN card image using OpenAI GPT-4o and extracts specified data.
    """
    base64_image = encode_image_to_base64_resized(image_path)
    if not base64_image:
        print("Failed to encode image. Exiting.")
        return None

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }

    # Prompt for GPT-4o to identify and extract PAN card details
    prompt_text = """
    You are an expert at extracting information from Indian PAN cards.
    Image can be in any format (JPEG, JPG, PNG, PDF, TIFF etc.)
    Analyze the provided image of a PAN card and extract the following details.
    Return the information in a JSON object.

    If a field is not found or unclear, use `null` as its value.

    Expected fields:
    1.  `card_type`: (Should be "Permanent Account Number Card" or similar)
    2.  `government_of_india`: (Should be "GOVERNMENT OF INDIA" or similar)
    3.  `income_tax_department`: (Should be "INCOME TAX DEPARTMENT" or similar)
    4.  `name`: Full Name of the cardholder
    5.  `father_name`: Father's Name
    6.  `date_of_birth`: Date of Birth (format YYYY-MM-DD or DD-MM-YYYY, prefer DD-MM-YYYY if clear)
    7.  `pan_number`: The 10-character PAN number
    8.  `signature_present`: boolean (true if signature is clearly visible, false otherwise)
    9.  `photo_present`: boolean (true if photo is clearly visible, false otherwise)

    Only return the JSON object. Do not include any other text or explanation.
    """

    payload = {
        "model": "gpt-4o", # Using gpt-4o for its vision capabilities
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt_text
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpg;base64,{base64_image}",
                            "detail": "low" # Use "high" detail for better accuracy but for POC "low" is sufficient
                        }
                    }
                ]
            }
        ],
        "max_tokens": 500 # Limit tokens to avoid excessive generation
    }

    print(f"Sending request to OpenAI API for image: {image_path}")
    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        response.raise_for_status() # Raise an exception for bad status codes

        response_json = response.json()
        # print("Raw API Response:", json.dumps(response_json, indent=2)) # For debugging

        # Extract the content from the response
        if response_json and response_json.get('choices'):
            message_content = response_json['choices'][0]['message']['content']

            # Attempt to parse the JSON string from the response
            try:
                # The model might sometimes include markdown ```json around the output.
                if message_content.startswith("```json") and message_content.endswith("```"):
                    json_str = message_content[7:-3].strip()
                else:
                    json_str = message_content.strip()

                parsed_data = json.loads(json_str)
                return parsed_data
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON from API response: {e}")
                print(f"Raw content received: {message_content}")
                return None
        else:
            print("No valid response or choices found in the API response.")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        if e.response is not None:
            print(f"Response status code: {e.response.status_code}")
            print(f"Response body: {e.response.text}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

def pan_agent(image_path):
    """
    Display and store the extracted PAN details.
    """
    extracted_data = parse_pan_card(image_path)

    if extracted_data:
        print("\n--- Extracted PAN Card Data ---")
        print(json.dumps(extracted_data, indent=4))

        print(f"\nCard Type: {extracted_data.get('card_type', 'N/A')}"
              f"\nGovernment of India: {extracted_data.get('government_of_india', 'N/A')}")
        print(f"\nName: {extracted_data.get('name', 'N/A')}")
        print(f"PAN Number: {extracted_data.get('pan_number', 'N/A')}")
        print(f"Date of Birth: {extracted_data.get('date_of_birth', 'N/A')}")
        print(f"Signature Present: {'Yes' if extracted_data.get('signature_present', False) else 'No'}")
        print(f"Photo Present: {'Yes' if extracted_data.get('photo_present', False) else 'No'}")
    else:
        print("\nFailed to extract PAN card data.")

# --- Main Execution ---
# if __name__ == "__main__":

#     print(f"\nAttempting to parse PAN card image: {IMAGE_PATH}")
#     extracted_data = parse_pan_card(IMAGE_PATH)

#     if extracted_data:
#         print("\n--- Extracted PAN Card Data ---")
#         # print(json.dumps(extracted_data, indent=4))

#         print(f"\nCard Type: {extracted_data.get('card_type', 'N/A')}"
#               f"\nGovernment of India: {extracted_data.get('government_of_india', 'N/A')}")
#         print(f"\nName: {extracted_data.get('name', 'N/A')}")
#         print(f"PAN Number: {extracted_data.get('pan_number', 'N/A')}")
#         print(f"Date of Birth: {extracted_data.get('date_of_birth', 'N/A')}")
#         print(f"Signature Present: {'Yes' if extracted_data.get('signature_present', False) else 'No'}")
#         print(f"Photo Present: {'Yes' if extracted_data.get('photo_present', False) else 'No'}")
#     else:
#         print("\nFailed to extract PAN card data.")