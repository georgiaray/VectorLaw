# Data Folder Setup Guide

This guide explains how to populate the `data/` folder for a legal comparison project using LLMs. The workflow involves collecting legal documents, extracting text, translating when necessary, and organizing the data for analysis.

## Data Sources

### Climate Policy Radar

One way to obtain curated datasets of legal documents is from [Climate Policy Radar](https://www.climatepolicyradar.org/). Climate Policy Radar provides structured datasets with metadata about climate-related legal documents, including document types, geographies, instruments, and content URLs.

**Note**: The `sample_df.csv` file included in this folder is an example dataset from Climate Policy Radar. Following the steps below (scraping, extraction, translation) will **not** generate this type of curated metadata CSV. Instead, this file represents a pre-existing curated dataset that you might obtain from Climate Policy Radar or similar sources.

If you have a curated dataset similar to `sample_df.csv`, you can use `utils/exploration.py` to analyze it:

```bash
# Explore the dataset and discover patterns
python utils/exploration.py --input data/sample_df.csv

# Save filtered outputs by geography
python utils/exploration.py --input data/sample_df.csv --output data/filtered
```

The `exploration.py` script will automatically discover:
- All unique geographies in your dataset
- All document types and their distribution
- All instruments (parsing semicolon-separated values)
- Relationships between document types and instruments

### Using Document Content URLs

In the original pilot of this project, the `Document Content URL` column from Climate Policy Radar datasets was used as the starting point. These URLs often point to PDF documents that can be downloaded and processed using the workflow described below:

1. Extract URLs from the `Document Content URL` column of your curated dataset
2. Use `utils/scraping.py` to download and extract text from PDFs and HTML pages (see Step 2 below)
3. Use `utils/extract.py` to convert text files to CSV format (optional, see Step 3 below)
4. Use `utils/process.py` to translate/filter the text (see Step 4 below)

This approach allows you to combine curated metadata (from Climate Policy Radar) with the actual document text extraction and processing workflow.

## Overview

The data folder structure supports multi-jurisdictional legal document analysis. Documents are organized by jurisdiction, with each jurisdiction having its own subfolder containing PDF files. The workflow includes:

1. **Collection**: Gathering URLs or file paths for legal documents
2. **Download**: Fetching PDF documents from URLs
3. **Extraction**: Extracting text from PDFs
4. **Translation**: Translating non-English documents to English (if needed)
5. **Processing**: Filtering and cleaning text for analysis
6. **Storage**: Saving processed data in structured formats (CSV)

## Folder Structure

```
data/
├── README.md (this file)
├── jurisdiction1/          # e.g., "canada", "brasil", "china", "eu"
│   ├── 1.txt               # Extracted text from PDFs or HTML pages
│   ├── 2.txt
│   └── ...
├── jurisdiction2/
│   ├── 1.txt
│   └── ...
└── processed/               # Optional: for processed/translated outputs
    ├── jurisdiction1_filtered.csv
    └── ...
```

## Step-by-Step Workflow

### Step 1: Collect Document URLs

Create a `urls/` folder at the project root (outside `data/`) and create text files with one URL per line for each jurisdiction:

```
urls/
├── jurisdiction1_urls.txt
├── jurisdiction2_urls.txt
└── ...
```

Each `.txt` file should contain one URL per line (can be PDFs or HTML pages):
```
https://example.com/document1.pdf
https://example.com/document2.html
https://example.com/document3.pdf
```

### Step 2: Download and Extract Documents

Use the provided `scraping.py` script to download PDFs and HTML pages from your URL files and extract their text content:

```bash
python utils/scraping.py --urls-file urls/jurisdiction1_urls.txt --out data/jurisdiction1
python utils/scraping.py --urls-file urls/jurisdiction2_urls.txt --out data/jurisdiction2
```

The script will:
- Create the output directory if it doesn't exist
- Download both PDF files and HTML web pages
- Extract text content from both formats
- Save extracted text as `.txt` files, naming them `1.txt`, `2.txt`, etc.
- Skip files that already exist
- Use retry logic with exponential backoff for failed requests
- Handle SSL certificate errors and network issues gracefully

**Note**: If a link fails to download or extract, the scraper will print an error message and continue with the next URL. You may need to provide an alternate link or handle problematic URLs manually.

**Example**:
```bash
python utils/scraping.py --urls-file urls/canada_urls.txt --out data/canada
```

### Step 3: Extract Text from Files (Optional)

If you need to re-extract text from already-downloaded files, use the provided `extract.py` script. Note that `scraping.py` already extracts text during download, so this step is only needed if you want to re-process existing files.

#### 3.1 Command Line Usage

```bash
python utils/extract.py --folder data/jurisdiction1 --output data/processed/jurisdiction1_extracted.csv
```

This will:
- Extract text from all PDF and text files in the specified folder
- Save results to a CSV file with columns: `file`, `text`
- Show progress and summary statistics

#### 3.2 Using in Python Code

You can also import and use the extraction function directly in your own scripts:

```python
from utils.extract import load_files

# Extract text from PDFs and text files
df = load_files('data/jurisdiction1')
```

### Step 4: Process Text (Language Detection and Translation)

Use the `process.py` script to process your extracted text. This script handles language detection, translation, and filtering with automatic checkpointing (so you can resume if interrupted).

#### 4.1 Command Line Usage

```bash
# Process with auto mode (translate if not English)
python utils/process.py --input data/processed/jurisdiction1_extracted.csv --output data/processed/jurisdiction1_processed.csv --mode auto

# Process with translation (always translate)
python utils/process.py --input data/processed/jurisdiction1_extracted.csv --output data/processed/jurisdiction1_processed.csv --mode translate

# Filter for English only
python utils/process.py --input data/processed/jurisdiction1_extracted.csv --output data/processed/jurisdiction1_processed.csv --mode filter

# Detect language only
python utils/process.py --input data/processed/jurisdiction1_extracted.csv --output data/processed/jurisdiction1_processed.csv --mode detect_only
```

The script will:
- Load your CSV file
- Process each row (detecting language, translating/filtering as needed)
- Save a checkpoint after each row (so you can resume if interrupted)
- Add `processed` and `detected_language` columns to the output
- Show progress and summary statistics

**Note**: If you run the script again with the same output file, it will automatically resume from where it left off, skipping already-processed rows.

The script supports several processing modes:

- **`auto`** (default): Automatically detects language and translates if not English
- **`translate`**: Always translates text (useful if you want to translate English too)
- **`filter`**: Filters text to keep only English sentences (removes non-English)
- **`detect_only`**: Only detects language, doesn't translate or filter

#### 4.2 Using Translation Functions Directly

If you need more control, you can import and use the translation functions from `translate.py` directly:

```python
from utils.translate import detect_language, translate_text, filter_english_sentences, process_text

# Detect language
lang = detect_language(text)

# Translate text (auto-detects source language)
translated = translate_text(text)

# Filter for English only
english_only = filter_english_sentences(text)

# Process with automatic mode (translates if not English)
processed, detected_lang = process_text(text, mode='auto')
```

#### 4.3 Using in Python Code with Checkpointing

You can also import and use the processing function directly:

```python
import pandas as pd
from utils.process import process_dataframe_with_checkpoints

# Load your extracted data
df = pd.read_csv('data/processed/jurisdiction1_extracted.csv')

# Process with checkpointing
df_processed = process_dataframe_with_checkpoints(
    df,
    save_path='data/processed/jurisdiction1_processed.csv',
    mode='auto'
)
```

## Best Practices

1. **Use Checkpointing**: Always use `process.py` for processing CSV files, as it automatically saves checkpoints after each row. This allows you to resume if interrupted, which is especially important for long-running translation tasks.

2. **Error Handling**: The scripts handle errors gracefully:
   - `extract.py` will continue processing even if some PDFs fail to extract
   - `process.py` will skip failed rows and continue with the rest
   - Both scripts report errors in their summaries

3. **Language Detection**: The `process.py` script automatically detects language before processing. For large documents, it uses a sample (first 1000 characters) for faster detection.

4. **Resume Processing**: If `process.py` is interrupted, simply run it again with the same input and output files. It will automatically resume from where it left off, skipping already-processed rows.

5. **File Naming**: The `scraping.py` script automatically names extracted text files as `1.txt`, `2.txt`, etc. to maintain order and make tracking easier.

6. **Validation**: After processing, validate that:
   - All expected files were processed (check the summary output)
   - Text extraction was successful (non-empty text in the output)
   - Translations are complete (if applicable, check the `processed` column)

## Dependencies

Key Python packages you'll need:

```bash
# Web scraping and document processing
pip install requests beautifulsoup4 PyPDF2

# Text processing
pip install nltk langdetect

# Translation (optional, for translate.py and process.py)
pip install deep-translator

# Data handling
pip install pandas tqdm
```

**Note**: 
- `beautifulsoup4` is required for HTML extraction
- `pdfminer.six` is recommended for PDF extraction (more robust than PyPDF2). PyPDF2 can be used as a fallback
- `nltk` requires downloading data. Run `python -c "import nltk; nltk.download('punkt')"` after installation
- `deep-translator` is optional but required if you want to translate non-English text. Without it, you can still detect languages and filter for English-only text

## Complete Workflow Example

Here's a complete example for processing documents from a single jurisdiction:

**Step 1: Download and extract documents**
```bash
python utils/scraping.py --urls-file urls/jurisdiction1_urls.txt --out data/jurisdiction1
```
This downloads PDFs and HTML pages and extracts text, saving as `.txt` files.

**Step 2: Convert to CSV (optional)**
```bash
python utils/extract.py --folder data/jurisdiction1 --output data/processed/jurisdiction1_extracted.csv
```
This converts the extracted text files to a CSV format for easier processing.

**Step 3: Process with translation/filtering (with checkpointing)**
```bash
python utils/process.py --input data/processed/jurisdiction1_extracted.csv --output data/processed/jurisdiction1_processed.csv --mode auto
```

**Step 4: Review results**
The output CSV will have:
- Original columns from extraction (`file`, `text`)
- `processed` column with translated/filtered text
- `detected_language` column showing the detected language

## Troubleshooting

- **PDF extraction fails**: 
  - Some PDFs may be corrupted or have unusual encoding. The script will continue with other files and report errors in the summary.
  - Check the error messages in the output to identify problematic files.

- **Translation API errors**: 
  - `process.py` handles errors gracefully and continues processing other rows
  - If you hit API rate limits, wait a bit and run `process.py` again - it will resume from where it left off
  - Check that `deep-translator` is installed: `pip install deep-translator`

- **Memory issues**: 
  - `process.py` processes files one at a time, so memory usage should be minimal
  - If processing very large files, consider splitting them into smaller batches

- **Language detection errors**: 
  - The script uses the first 1000 characters for detection, which is usually sufficient
  - Very short texts may fail detection - these will be marked with 'unknown' language
  - If detection consistently fails, the text may be too short or contain mostly numbers/symbols

## Scripts Overview

The project includes three main scripts for data processing:

1. **`utils/scraping.py`**: Downloads PDF and HTML documents from URLs and extracts text
   - Input: Text file with URLs (one per line)
   - Output: Text files (`.txt`) with extracted content in a folder
   - Features: Handles both PDFs and HTML pages, retry logic with exponential backoff

2. **`utils/extract.py`**: Extracts text from PDF and text files (for re-processing)
   - Input: Folder containing PDF or text files
   - Output: CSV file with `file` and `text` columns
   - Note: Usually not needed since `scraping.py` already extracts text during download

3. **`utils/process.py`**: Processes text (language detection, translation, filtering)
   - Input: CSV file with a `text` column
   - Output: CSV file with `processed` and `detected_language` columns
   - Features: Automatic checkpointing, resume capability

4. **`utils/translate.py`**: Library module with translation functions
   - Not meant to be run directly
   - Provides functions for language detection, translation, and filtering
   - Used by `process.py` internally

5. **`utils/exploration.py`**: Analyze curated datasets with metadata
   - Input: CSV file with columns for geographies, document types, and instruments
   - Output: Formatted analysis report showing discovered patterns
   - Automatically discovers all geographies, document types, and instruments from your data
   - Useful for analyzing pre-existing curated datasets (e.g., from Climate Policy Radar)
   - Example: `python utils/exploration.py --input data/sample_df.csv`

## Notes

- The `.gitignore` file is configured to ignore `.pdf`, `.csv`, `.txt`, `.json`, `.docx`, `.xlsx`, and `.pkl` files in the `data/` folder
- Keep original PDFs for reference, but processed text can be stored in CSV format for easier analysis
- Consider creating separate folders for different processing stages:
  - `data/jurisdiction1/` - Raw PDFs
  - `data/processed/` - Extracted and processed CSV files
