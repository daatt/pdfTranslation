# PDF Translator

A Python-based tool that translates PDF documents to English using OpenAI's GPT-4o. The tool preserves formatting, including tables and numerical data, and outputs the translation in Markdown format.

## Features

- Translates PDF documents to English
- Preserves original formatting using Markdown
- Handles tables and numerical data
- Allows selection of specific page ranges for translation
- Supports all languages that GPT-4V can process

## Prerequisites

- Python 3.6 or higher
- OpenAI API key with GPT-4V access
- Poppler (required for pdf2image)

## Installation

1. Clone the repository:
2. Install the required Python package
3. Set up your OpenAI API key:
   - Create a `.env` file in the project directory
   - Add your API key: `OPENAI_API_KEY=your_api_key_here`

## Usage

Run the script from the command line:

python translate_pdf.py input.pdf output.pdf

The program will:
1. Ask you to specify the page range you want to translate
2. Process each page and translate it to English
3. Save the output as a Markdown file (with the same name as your output file but with .md extension)


## Dependencies

- `PyPDF2`: PDF file handling
- `openai`: OpenAI API interface
- `python-dotenv`: Environment variable management
- `pdf2image`: PDF to image conversion
- `Pillow`: Image processing

## Limitations

- Requires GPT-4V API access
- Processing time depends on the number of pages and API response time
- API rate limits may apply
- Image quality may affect translation accuracy

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[Add your chosen license here]

## Acknowledgments

- OpenAI for providing the GPT-4V API
- The open-source community for the various Python libraries used in this project
