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
import concurrent.futures

class PDFTranslator:
    def __init__(self, api_key, max_workers=3):
        """
        :param api_key: OpenAI API key.
        :param max_workers: Number of threads to use for parallel translation.
        """
        self.client = OpenAI(api_key=api_key)
        self.max_workers = max_workers

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

    def extract_text_from_page_with_retries(self, page, max_retries=1):
        """
        Extract text from a PDF page by converting it to base64 image and sending it
        to GPT-4o for translation. Will retry 'max_retries' times on error.
        Returns the translated text or None if unsuccessful after retries.
        """
        for attempt in range(max_retries + 1):
            try:
                # Attempt to translate
                return self._extract_text_from_page(page)
            except Exception as e:
                print(f"Error processing page image (attempt {attempt+1}): {e}")

                if attempt < max_retries:
                    print(f"Retrying page translation (retry {attempt+1})...")
                    # Optional delay before retry
                    time.sleep(2)
                else:
                    print("Max retries reached, skipping page.")
                    return None

    def _extract_text_from_page(self, page):
        """
        Performs the actual call to GPT-4o. Raises exception if it fails.
        """
        response = self.client.chat.completions.create(
            model="chatgpt-4o-latest",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a professional translator. Translate the following file to English, "
                        "maintaining the original formatting as much as possible. This file may contain lots "
                        "of tables and numbers. If it does, please also translate any labels or annotations to "
                        "English also, preserving the table structure as much as you can. Output in markdown "
                        "and use advanced markdown formatting when you need to to achieve your goal."
                    )
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

    def _convert_page_to_base64(self, page):
        """
        Convert a single PDF page to an image, then encode it in base64.
        """
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

        # Pre-allocate a list for the results (so we can store in correct order)
        num_pages = end_page - start_page
        results = [None] * num_pages

        # Use ThreadPoolExecutor to parallelize the process of fetching translation
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_index = {}
            for idx in range(start_page, end_page):
                page_index = idx  # keep actual PDF page index
                future = executor.submit(self.extract_text_from_page_with_retries, reader.pages[page_index], max_retries=1)
                future_to_index[future] = page_index

            for future in concurrent.futures.as_completed(future_to_index):
                page_index = future_to_index[future]
                result_index = page_index - start_page
                try:
                    text = future.result()
                    results[result_index] = text
                except Exception as e:
                    # This shouldn't occur since we handle exceptions internally, but just in case
                    print(f"Unexpected error translating page {page_index + 1}: {e}")

        # Create markdown content
        markdown_content = f"# Translated Document\nOriginal file: {input_path}\n\n"

        # Append results in correct order
        for i in range(num_pages):
            page_number = start_page + i + 1
            page_text = results[i]
            if page_text:
                markdown_content += f"## Page {page_number}\n\n{page_text}\n\n"
                print(f"Page {page_number} translated successfully")
            else:
                print(f"Failed to translate page {page_number}")

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
    parser.add_argument('--max-workers', type=int, default=3, help='Number of parallel threads for translation')

    args = parser.parse_args()

    if not args.api_key:
        print("Error: OpenAI API key not provided. Either use --api-key or set OPENAI_API_KEY environment variable.")
        return

    if not os.path.exists(args.input_file):
        print(f"Error: Input file '{args.input_file}' does not exist.")
        return

    translator = PDFTranslator(api_key=args.api_key, max_workers=args.max_workers)
    translator.process_pdf(args.input_file, args.output_file)


if __name__ == "__main__":
    main()
