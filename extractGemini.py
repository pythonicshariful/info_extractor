import google.generativeai as genai
import base64
import json
from PIL import Image
import pandas as pd
import os
from io import BytesIO
from config import GEMINI_API_KEY  # <-- store your Gemini API key in config.py

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

def extract_customer_info(image_path):
    try:
        # Load and encode the image
        with Image.open(image_path) as img:
            if img.mode != "RGB":
                img = img.convert("RGB")
            
            buffered = BytesIO()
            img.save(buffered, format="JPEG")
            img_bytes = buffered.getvalue()
        
        # Define model
        model = genai.GenerativeModel("gemini-2.5-flash")  # or "gemini-1.5-pro"
        
        # Define prompt
        prompt = (
            "Extract customer information from this image and return ONLY a valid JSON object "
            "with this exact structure:\n"
            "{\n"
            "  \"Name\": \"\",\n"
            "  \"Phone Number\": \"\",\n"
            "  \"Mobile Number\": \"\",\n"
            "  \"Email\": \"\",\n"
            "  \"Street\": \"\",\n"
            "  \"Street Number\": \"\",\n"
            "  \"City\": \"\",\n"
            "  \"ZIP Code\": \"\",\n"
            "  \"State\": \"\",\n"
            "  \"Country\": \"\",\n"
            "  \"Latitude\": \"\",\n"
            "  \"Longitude\": \"\"\n"
            "}"
        )
        
        # Send image + prompt to Gemini
        response = model.generate_content(
            [
                prompt,
                {"mime_type": "image/jpeg", "data": img_bytes},
            ]
        )

        # Extract text
        customer_info_text = response.text.strip()
        print(f"Extracted Customer Information from {image_path}:\n", customer_info_text)

        # Try to extract valid JSON from the response
        if customer_info_text.startswith("{") and customer_info_text.endswith("}"):
            json_str = customer_info_text
        else:
            start = customer_info_text.find("{")
            end = customer_info_text.rfind("}") + 1
            if start != -1 and end != 0:
                json_str = customer_info_text[start:end]
            else:
                raise json.JSONDecodeError("No valid JSON found", customer_info_text, 0)

        customer_info = json.loads(json_str)
        return customer_info

    except json.JSONDecodeError as e:
        print(f"Could not convert to JSON. Error: {str(e)}")
        print("Raw response:", customer_info_text)
        return None
    except Exception as e:
        print(f"An error occurred while processing {image_path}: {str(e)}")
        return None


def process_image_folder(folder_path):
    image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    all_customer_info = []

    for image_file in image_files:
        image_path = os.path.join(folder_path, image_file)
        customer_info = extract_customer_info(image_path)
        if customer_info:
            all_customer_info.append(customer_info)

    try:
        df = pd.DataFrame(all_customer_info)
        df.to_excel("customer_info.xlsx", index=False)
        print("\n✅ Excel file 'customer_info.xlsx' has been created successfully!")
    except Exception as e:
        print(f"An error occurred while creating the Excel file: {str(e)}")


# === Run ===
folder_path = "images"  # Change to your folder path
process_image_folder(folder_path)
