import os
import argparse
from PyPDF2 import PdfReader, PdfWriter
from openai import OpenAI
import tempfile
import time
from dotenv import load_dotenv
from pdf2image import convert_from_path
import io
from PIL import Image
import base64

class PDFTranslator:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)

    def get_page_range(self, total_pages):
        while True:
            try:
                print(f"\nTotal pages in document: {total_pages}")
                start = int(input("Enter start page (1-based): "))
                end = int(input("Enter end page: "))
                
                if 1 <= start <= end <= total_pages:
                    return start - 1, end  # Convert to 0-based indexing
                else:
                    print("Invalid page range. Please try again.")
            except ValueError:
                print("Please enter valid numbers.")

    def extract_text_from_page(self, page):
        # Convert page to image and get text via vision API
        try:
            response = self.client.chat.completions.create(
                model="chatgpt-4o-latest",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional translator. Translate the following file to English, maintaining the original formatting as much as possible. This file may contain lots of tables and numbers. If it does please also translate any labels or annotations to English also, preserving the table structure as much as you can. Output in markdown and use advanced markdown formatting when you need to to achieve your goal."
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{self._convert_page_to_base64(page)}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=4096
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error processing page image: {e}")
            return None

    def _convert_page_to_base64(self, page):
        # Convert PDF page to image
        temp_path = tempfile.mktemp(suffix='.pdf')
        writer = PdfWriter()
        writer.add_page(page)
        with open(temp_path, 'wb') as temp_file:
            writer.write(temp_file)
        
        # Convert to image
        images = convert_from_path(temp_path)
        image = images[0]  # Get first (and only) page
        
        # Convert to base64
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        # Clean up
        os.remove(temp_path)
        
        return img_str

    def process_pdf(self, input_path, output_path):
        # Read the PDF
        reader = PdfReader(input_path)
        
        # Get page range from user
        start_page, end_page = self.get_page_range(len(reader.pages))
        
        print("\nStarting translation process...")
        
        # Create markdown content
        markdown_content = f"# Translated Document\nOriginal file: {input_path}\n\n"
        
        # Process each page in the range
        for i in range(start_page, end_page):
            print(f"\nProcessing page {i + 1}...")
            
            # Extract text from page
            page = reader.pages[i]
            text = self.extract_text_from_page(page)
            
            if text:
                # Add page number and translated text to markdown
                markdown_content += f"## Page {i + 1}\n\n{text}\n\n"
                print(f"Page {i + 1} translated successfully")
            else:
                print(f"Failed to translate page {i + 1}")
            
            # Add a small delay to avoid API rate limits
            time.sleep(1)
        
        # Save the translated text as markdown
        output_path = output_path.rsplit('.', 1)[0] + '.md'  # Change extension to .md
        with open(output_path, 'w', encoding='utf-8') as output_file:
            output_file.write(markdown_content)
        
        print(f"\nTranslation completed. Output saved to: {output_path}")

def main():
    # Load environment variables from .env file
    load_dotenv()
    
    parser = argparse.ArgumentParser(description='Translate PDF documents using OpenAI GPT-4o')
    parser.add_argument('input_file', help='Path to the input PDF file')
    parser.add_argument('output_file', help='Path for the translated PDF file')
    parser.add_argument('--api-key', help='OpenAI API key', default=os.getenv('OPENAI_API_KEY'))
    
    args = parser.parse_args()
    
    if not args.api_key:
        print("Error: OpenAI API key not provided. Either use --api-key or set OPENAI_API_KEY environment variable.")
        return
    
    if not os.path.exists(args.input_file):
        print(f"Error: Input file '{args.input_file}' does not exist.")
        return
    
    translator = PDFTranslator(args.api_key)
    translator.process_pdf(args.input_file, args.output_file)

if __name__ == "__main__":
    main() 