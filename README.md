# Law Comparisons

A project for analyzing and comparing documents using LLMs, RAG (Retrieval-Augmented Generation), and data science tools. This repository provides a complete pipeline for scraping documents, processing text, creating embeddings, and performing analysis.

## Overview

This project enables you to:

1. **Collect and process legal and policy documents** - Scrape PDFs and HTML pages, extract text, detect languages, and translate content
2. **Create vector embeddings** - Build searchable vector stores for RAG applications
3. **Analyze documents** - Generate summaries, classify content, and explore datasets
4. **Work with curated datasets** - Analyze pre-existing datasets with metadata (e.g., from Climate Policy Radar)

## Repository Structure

```
law_comparisons/
├── utils/              # Utility scripts for data processing and analysis
│   ├── scraping.py     # Download and extract text from PDFs/HTML
│   ├── extract.py      # Extract text from files (for re-processing)
│   ├── translate.py    # Language detection and translation functions
│   ├── process.py      # Process text with checkpointing support
│   ├── exploration.py  # Analyze curated datasets with metadata
│   ├── embed.py        # Create vector embeddings for RAG
│   ├── summarize.py    # Generate question-focused summaries
│   └── rag.py          # RAG utilities for vector store queries
├── data/               # Data folder (see data/README.md for setup)
│   └── README.md       # Guide for populating the data folder
├── urls/               # URL lists for documents to scrape
│   └── README.md       # Format for URL list files
├── analysis/           # Analysis workflows and examples
│   ├── prompts_example.py    # Example prompts module (customize for your use case)
│   ├── groundtruth_example.xlsx  # Example ground truth data structure
│   └── README.md       # Analysis workflow documentation
├── test_pipeline.py    # Test script to verify everything works
└── README.md           # This file
```

## Quick Start

### 1. Install Dependencies

This project uses Poetry for dependency management:

```bash
# Install Poetry if you haven't already
curl -sSL https://install.python-poetry.org | python3 -

# Install project dependencies
poetry install --no-root

# Activate the virtual environment
poetry shell
```

### 2. Install NLTK Data

Required for text processing:

```bash
python -c "import nltk; nltk.download('punkt')"
```

### 3. Set Up API Keys

Create a `.env` file in the project root with your OpenRouter API key:

```bash
echo "OPENROUTER_API_KEY=your_api_key_here" > .env
```

**Important:** Replace `your_api_key_here` with your actual OpenRouter API key. You can get one at https://openrouter.ai/

### 4. Test the Pipeline

Run the test script to verify everything is working:

```bash
python test_pipeline.py
```

This will:
- Scrape 5 URLs from `urls/urls_example.txt`
- Extract text from the scraped files
- Detect languages in the text
- Create vector embeddings
- Test RAG utilities (query the vector store)
- Generate summaries for one document
- Test exploration.py with sample data (if available)

All test data goes into `test_data/` directory, which you can delete after testing.

**The test pipeline serves two purposes:**
1. **Verification** - Confirms all utilities are working correctly
2. **Learning** - Demonstrates how to use each script in the workflow

## Workflow Overview

### Data Collection and Processing

1. **Collect URLs** - Create text files in `urls/` with one URL per line
2. **Scrape documents** - Use `utils/scraping.py` to download and extract text
3. **Process text** - Use `utils/process.py` for language detection and translation
4. **Explore datasets** - Use `utils/exploration.py` to analyze curated datasets

See `data/README.md` for detailed instructions.

### Analysis Workflow

1. **Create embeddings** - Use `utils/embed.py` to create vector stores
2. **Generate summaries** - Use `utils/summarize.py` with custom prompts
3. **Query documents** - Use `utils/rag.py` for RAG-based retrieval

See `analysis/README.md` for detailed instructions.

## Key Features

### Data Processing

- **Multi-format support**: Handles both PDFs and HTML pages
- **Robust scraping**: Retry logic with exponential backoff
- **Language detection**: Automatic detection with translation support
- **Checkpointing**: Resume interrupted processing tasks
- **Data exploration**: Analyze curated datasets with metadata

### Analysis Tools

- **Vector embeddings**: Create searchable document stores
- **RAG utilities**: Query documents using semantic search
- **Summarization**: Generate question-focused summaries
- **Customizable prompts**: Example prompts module you can adapt

## Dependencies

Key dependencies (managed via Poetry):

- `pandas`, `numpy` - Data manipulation
- `requests`, `beautifulsoup4`, `PyPDF2` - Web scraping and PDF extraction
- `openai`, `tiktoken` - LLM API calls and token counting
- `nltk`, `langdetect`, `deep-translator` - Text processing and translation
- `tqdm` - Progress bars

See `pyproject.toml` for the complete list.

## Documentation

- **`data/README.md`** - Complete guide for setting up and populating the data folder
- **`urls/README.md`** - Format for URL list files
- **`analysis/README.md`** - Analysis workflow documentation
- **`analysis/prompts_example.py`** - Example prompts module (customize for your use case)

## Troubleshooting

**If you get "command not found: poetry":**
- Install Poetry first (see Quick Start section)

**If you get import errors:**
- Make sure you're in the Poetry shell (`poetry shell`)
- Try `poetry install --no-root` again

**If you get "OPENROUTER_API_KEY not found":**
- Make sure you created the `.env` file in the project root
- Check that the file contains: `OPENROUTER_API_KEY=your_key_here`

**If scraping fails:**
- Check your internet connection
- Some URLs may be broken - that's okay, the script will continue

**If you get NLTK errors:**
- Run: `python -c "import nltk; nltk.download('punkt')"`

## Example Use Cases

### Working with Your Own URLs

1. Create `urls/my_documents.txt` with your URLs
2. Run: `python utils/scraping.py --urls-file urls/my_documents.txt --out data/my_documents`
3. Process: `python utils/process.py --input data/my_documents --output data/processed/my_documents.csv --mode auto`
4. Analyze: `python utils/exploration.py --input data/processed/my_documents.csv`

### Working with Curated Datasets

1. Get a dataset from Climate Policy Radar (or similar source)
2. Save as CSV with columns: `Geographies`, `Document Type`, `Instrument`
3. Analyze: `python utils/exploration.py --input data/my_dataset.csv`
4. Extract URLs from `Document Content URL` column if you want to scrape the actual documents

### Creating Vector Embeddings

1. Scrape documents: `python utils/scraping.py --urls-file urls/documents.txt --out data/documents`
2. Create embeddings: `python utils/embed.py --input data/documents --output data/vector_store/vectors.pkl`
3. Use in RAG: Import `utils.rag` and query documents

### Generating Summaries

1. Create your prompts module (see `analysis/prompts_example.py` as a template)
2. Run: `python utils/summarize.py --input data/documents --output data/summaries --prompts-module analysis.prompts_example`

## Contributing

This is a general-purpose framework. To adapt it for your use case:

1. Customize `analysis/prompts_example.py` for your classification questions
2. Modify the workflow scripts as needed
3. Add your own analysis notebooks or scripts

## License

See LICENSE file for details.