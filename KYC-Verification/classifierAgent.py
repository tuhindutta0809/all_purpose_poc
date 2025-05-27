import os
import sys
import requests
from PIL import Image, ImageDraw
import io
import json
from panAgent import parse_pan_card, pan_agent


# --- Main Execution ---
if __name__ == "__main__":

    # Path to the PAN card image file
    current_dir = os.path.dirname(os.path.abspath(__file__))
 
    IMAGE_PATH = os.path.join(current_dir, "Documents/PAN-Tuhin.PNG") #"/Documents/PAN-Tuhin.jpg"
    if not os.path.exists(IMAGE_PATH):
        print(f"Image file does not exist: {IMAGE_PATH}")
        sys.exit(1)
    # if the document is classified as PAN card, then it will be processed by the pan_agent
    pan_agent(IMAGE_PATH)