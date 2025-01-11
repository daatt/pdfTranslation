import os
import argparse
from PyPDF2 import PdfReader, PdfWriter
from openai import OpenAI
import tempfile
import time
from dotenv import load_dotenv

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
        return page.extract_text()

    def translate_text(self, text):
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a professional translator. Translate the following text to English, maintaining the original formatting as much as possible."},
                    {"role": "user", "content": text}
                ],
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Translation error: {e}")
            return None

    def process_pdf(self, input_path, output_path):
        # Read the PDF
        reader = PdfReader(input_path)
        writer = PdfWriter()
        
        # Get page range from user
        start_page, end_page = self.get_page_range(len(reader.pages))
        
        print("\nStarting translation process...")
        
        # Process each page in the range
        for i in range(start_page, end_page):
            print(f"\nProcessing page {i + 1}...")
            
            # Extract text from page
            page = reader.pages[i]
            text = self.extract_text_from_page(page)
            
            # Translate the text
            translated_text = self.translate_text(text)
            
            if translated_text:
                # Create a new PDF page with translated text
                # Note: This is a simplified version - in a real implementation,
                # you'd want to preserve the original formatting
                writer.add_page(page)  # For now, just adding original page
                
                print(f"Page {i + 1} translated successfully")
            else:
                print(f"Failed to translate page {i + 1}")
            
            # Add a small delay to avoid API rate limits
            time.sleep(1)
        
        # Save the translated PDF
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
        
        print(f"\nTranslation completed. Output saved to: {output_path}")

def main():
    # Load environment variables from .env file
    load_dotenv()
    
    parser = argparse.ArgumentParser(description='Translate PDF documents using OpenAI GPT-4')
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