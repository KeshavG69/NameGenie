# NameGenie: Smart Content-Based File Renamer

Imagine you have a folder full of various document types, and you're looking for a quick and secure way to rename them. NameGenie is designed to help you do just that! It's like having a personal assistant who reads through your files and suggests new, concise names for each one, ensuring your data stays safe by running everything locally.

## Supported Formats

NameGenie supports a wide range of file formats:

- Documents: `.docx`, `.doc`, `.odt`, `.rtf`, `.md`
- Spreadsheets: `.xlsx`, `.csv`, `.tsv`
- Presentations: `.pptx`, `.ppt`
- Emails: `.eml`, `.msg`
- eBooks: `.epub`
- Web Pages: `.html`, `.xml`
- PDFs: `.pdf`
- Text Files: `.txt`
- Images: `.jpg`, `.jpeg`, `.png`, `.heic`

## How It Works

### 1. Scan Files
NameGenie scans a specified folder on your computer, looking for the supported file types. It then reads the content of each file, pulling out the information that will inspire the new file names.

### 2. Generate Names
With the content in hand, NameGenie leverages an intelligent open-source model to generate short, catchy names for each file.

### 3. Rename Files
Once the new names are generated, NameGenie renames each file accordingly. Now, instead of generic names like "document1.pdf" or "report.txt," you have meaningful, concise titles that reflect the content of each file.
## Installation Instructions

### Windows
To install the necessary dependencies, run the following commands:

```bash
apt-get update
apt-get install libreoffice -y

