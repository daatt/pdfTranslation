from pdf2image import convert_from_path
from openai import OpenAI
import base64
from io import BytesIO

def extract_and_translate_pdf(pdf_path, target_language='en'):
    client = OpenAI()
    page_contents = {}
    
    # Convert PDF pages to images
    images = convert_from_path(pdf_path)
    
    for page_num, image in enumerate(images, 1):
        # Convert PIL Image to bytes
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        image_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
        
        # Send to OpenAI Vision API
        response = client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"Please read all text from this image, including any tables or figures, and translate it to {target_language}."},
                        {"type": "image_url", "image_url": f"data:image/png;base64,{image_base64}"}
                    ],
                }
            ],
            max_tokens=1000
        )
        
        page_contents[page_num] = response.choices[0].message.content

    return page_contents