# PDF Translator

A Python tool that translates PDF documents from any language to English using OpenAI's GPT-4o vision capabilities. The translator preserves formatting, tables, and numerical data while outputting clean Markdown.

## Features

- Translates PDFs from any language to English
- Preserves original document formatting with Markdown
- Handles complex elements like tables and numerical data
- Allows translation of specific page ranges
- Offers both sequential and parallel translation options

## Requirements

- Python 3.6+
- OpenAI API key with GPT-4o access
- Poppler (for pdf2image library)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/pdf-translator.git
   cd pdf-translator
   ```

2. Install required packages:
   ```
   pip install -r requirements.txt
   ```

3. Set up your OpenAI API key:
   - Create a `.env` file in the project directory
   - Add your API key: `OPENAI_API_KEY=your_api_key_here`

## Usage

### Basic Translation

```
python translate_pdf.py input.pdf output.pdf
```

### Parallel Translation (Faster)

```
python parallelTranslate.py input.pdf output.pdf --max-workers 5
```

The program will:
1. Ask you to specify the page range to translate
2. Process and translate each page to English
3. Save the output as a Markdown file

## How It Works

1. Converts PDF pages to high-quality images
2. Sends each image to OpenAI's GPT-4o for translation
3. Uses the vision capabilities of GPT-4o to understand content and formatting
4. Preserves structure by converting to Markdown format
5. Combines all translated pages into a single document

## Performance

The `parallelTranslate.py` script provides significantly faster processing by translating multiple pages simultaneously. You can adjust the number of worker threads with the `--max-workers` parameter based on your needs and API rate limits.

## Limitations

- Requires GPT-4o API access
- Processing speed depends on document complexity and API response time
- API rate limits and costs may apply
- Image quality affects translation accuracy

## License

[Add your chosen license here]

## Acknowledgments

- OpenAI for providing the GPT-4o API
- The open-source Python community