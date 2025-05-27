import os
import io
import base64
from PIL import Image, ImageDraw

# --- Helper Function to Encode Image ---
# def encode_image_to_base64(image_path):
#     """
#     Encodes an image file to a base64 string.
#     """
#     try:
#         # Open the image to ensure it's a valid image file
#         with Image.open(image_path) as img:
#             # Create a bytes buffer
#             img_byte_arr = io.BytesIO()
#             # Save the image to the buffer, preserving format if possible, otherwise default to PNG
#             # Use 'PNG' as a safe default if original format is unknown or problematic for base64
#             img.save(img_byte_arr, format='PNG')
#             encoded_image = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
#             return encoded_image
#     except FileNotFoundError:
#         print(f"Error: Image file not found at {image_path}")
#         return None
#     except Exception as e:
#         print(f"Error encoding image: {e}")
#         return None

def encode_image_to_base64_resized(image_path, max_dim=1024):
    """
    Encodes an image file to a base64 string, resizing it if its largest dimension exceeds max_dim.
    """
    try:
        with Image.open(image_path) as img:
            original_width, original_height = img.size

            if max(original_width, original_height) > max_dim:
                # Calculate new dimensions, maintaining aspect ratio
                if original_width > original_height:
                    new_width = max_dim
                    new_height = int(original_height * (max_dim / original_width))
                else:
                    new_height = max_dim
                    new_width = int(original_width * (max_dim / original_height))
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS) # Use LANCZOS for quality

            if img.mode != 'RGB':
                img = img.convert('RGB')

            buffered = io.BytesIO()
            img.save(buffered, format="JPEG")
            return base64.b64encode(buffered.getvalue()).decode('utf-8')
    except FileNotFoundError:
        print(f"Error: Image file not found at {image_path}")
        return None
    except Exception as e:
        print(f"An error occurred while encoding image: {e}")
        return None