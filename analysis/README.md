# Analysis Folder

This folder contains tools and examples for analyzing legal documents using LLMs and RAG (Retrieval-Augmented Generation). The workflow enables you to extract structured information from documents through summarization and classification.

## Overview

The analysis workflow consists of three main steps:

1. **Embedding & Chunking**: Create vector embeddings for RAG
2. **Summarization**: Generate question-focused summaries for each document
3. **Classification**: Classify documents using RAG (optional, project-specific)

## Workflow

### Step 1: Embedding & Chunking

Use `utils/embed.py` to create vector embeddings from your document text files:

```bash
# For a specific jurisdiction
python utils/embed.py --input data/jurisdiction1 --output data/vector_store/vector_store.pkl

```

**What it does:**
- Loads all `.txt` files from the input directory
- Chunks documents into overlapping segments (default: 200 words, 75 word overlap)
- Creates embeddings using OpenAI's embedding models (default: `text-embedding-3-large`)
- Stores embeddings and metadata in a pickle file for later retrieval

**Options:**
- `--chunk-size`: Number of words per chunk (default: 200)
- `--chunk-overlap`: Number of words to overlap between chunks (default: 75)
- `--embedding-model`: OpenAI embedding model to use
- `--batch-size`: Batch size for embedding generation (default: 64)
- `--trim-content`: Trim boilerplate/navigation content from documents

**Output:** A pickle file containing the vector store with document embeddings and chunks.

### Step 2: Summarization

Use `utils/summarize.py` to generate question-focused summaries:

```bash
# For a specific jurisdiction
python utils/summarize.py \
  --input data/jurisdiction1 \
  --output data/summaries \
  --prompts-module analysis.prompts_example
```

**What it does:**
- Loads text files from the input directory
- For each document, generates multiple summaries focused on different questions/aspects
- Handles token limits by truncating documents if needed
- Saves summaries in subdirectories: `data/summaries/{document_name}/question_{N}_summary.txt`

**Requirements:**
- A prompts module that provides:
  - `SYSTEM_PROMPT`: System prompt for the LLM
  - `get_all_prompts(doc_text)`: Function that returns a list of prompts

**Options:**
- `--prompts-module`: Python module path (e.g., `analysis.prompts_example`)
- `--max-tokens`: Maximum context window size (default: 128000)
- `--safety-margin`: Tokens to reserve for system messages (default: 1024)
- `--model`: Model to use for summarization (default: `gpt-4o-mini`)
- `--skip-existing`: Skip documents that already have summaries

**See `prompts_example.py`** in this folder for an example of how to structure your prompts module.

### Step 3: Classification (Optional)

Classification is project-specific and depends on your use case. The general approach is:

1. Use RAG to retrieve relevant document chunks for each classification question
2. Use LLMs to classify documents based on summaries and retrieved chunks
3. Optionally implement a correction loop (e.g., two-LLM approach) for improved accuracy

**Utilities available:**
- `utils/rag.py`: Functions for loading vector stores and querying documents
  - `load_vector_store(path)`: Load a vector store from a pickle file
  - `query_document(store, client, doc_name, query, top_k)`: Retrieve top-k most similar chunks

## Example Files

### `prompts_example.py`

This file provides an example of how to structure prompts for summarization and classification. It includes:

- System prompts for summarization and classification
- JSON schemas for different question types
- Functions to generate prompts for each question
- A `get_all_prompts(doc_text)` function that returns a list of prompts

**Note:** This is an example specific to climate finance policy classification. You should create your own prompts module tailored to your use case, using this as a reference.

### `groundtruth_example.xlsx`

An example Excel file showing the structure of ground truth data for evaluation. This is project-specific and provided as a reference only.

## Dependencies

- `openai` - LLM API calls (via OpenRouter)
- `numpy` - Vector operations
- `pickle` - Vector store serialization
- `tiktoken` - Token counting for context window management
- `pandas` - Data handling (for classification workflows)

## Notes

- The workflow uses OpenRouter API for LLM access (set `OPENROUTER_API_KEY` in your `.env` file)
- Vector store uses OpenAI embeddings (default: `text-embedding-3-large`)
- Summarization uses GPT-4o-mini by default for cost efficiency
- The prompts module pattern allows you to customize the summarization/classification questions for your specific use case

## Integration with Data Pipeline

This analysis workflow works with documents prepared using the data pipeline:

1. Documents are scraped and extracted using `utils/scraping.py` (saves as `.txt` files in jurisdiction-specific folders like `data/jurisdiction1/`)
2. Documents are embedded using `utils/embed.py` (creates vector store)
3. Documents are summarized using `utils/summarize.py` (creates question-focused summaries)
4. Documents can be classified using custom scripts that use `utils/rag.py` for retrieval

**Note:** The data pipeline creates jurisdiction-specific folders (e.g., `data/canada/`, `data/jurisdiction1/`) rather than a single `data/scraped_documents/` folder. You can process each jurisdiction separately or combine them as needed.

See the `data/README.md` for details on the data preparation pipeline.
