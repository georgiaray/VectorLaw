#!/usr/bin/env python3
"""
Document Embedding and Chunking Script

This script chunks documents and creates vector embeddings for RAG (Retrieval-Augmented Generation).
It processes text files, splits them into overlapping chunks, generates embeddings, and saves
them to a vector store for later retrieval.
"""

import os
import re
import argparse
from pathlib import Path
from typing import Dict, List, Any
import pickle

import numpy as np
from dotenv import load_dotenv
from openai import OpenAI


def chunk_text(text: str, chunk_size: int = 200, chunk_overlap: int = 75) -> List[str]:
    """
    Split a document into overlapping word chunks of fixed size.
    
    Args:
        text: Text to chunk
        chunk_size: Number of words per chunk
        chunk_overlap: Number of words to overlap between chunks
    
    Returns:
        List of text chunks
    """
    words = text.split()
    if not words:
        return []

    chunks: List[str] = []
    start = 0
    total_words = len(words)

    while start < total_words:
        end = min(total_words, start + chunk_size)
        chunk = " ".join(words[start:end]).strip()
        if chunk:
            chunks.append(chunk)
        if end >= total_words:
            break
        # Decide new start: handle overlap
        start += max(1, chunk_size - chunk_overlap)

    return chunks


def trim_non_content(text: str) -> str:
    """
    Attempts to trim repeated navigation/boilerplate 'chrome' text
    like headers, navbars, footers, menus, and non-content at the head and tail of the doc.
    Not guaranteed to catch everything, but tries to remove common patterns.
    
    Args:
        text: Text to clean
    
    Returns:
        Cleaned text
    """
    # Common boilerplate phrases likely indicating start/end of content
    head_patterns = [
        r"^(?:.*Canada\.ca.*\n){1,5}",  # Canada.ca spam header
        r"^Skip to main content[\n\r]+", 
        r"^Skip to [^\n]+\n", 
        r"^Language selection\n", 
        r"^(?:Français|fr|Gouvernement du Canada)[\n/ ]+",
        r"^Search[^\n]*\n", 
        r"^Menu\n", 
        r"^Main\n", 
        r"^[\w \-/]+\nJobs and the workplace\n",  # menu bar spam
        r"^(?:[\w ,/&-]+\n){3,10}You are here:[^\n]*\n",  # Common 'menu' preamble
        r"^From:[^\n]+\n News release[\n]*",  # News release preamble
    ]

    # Extended tail patterns to catch press/media contact and keyword megamenus
    tail_patterns = [
        r"\nReport a problem or mistake on this page.*$", 
        r"\nDate modified:[^\n]*$", 
        r"\n(?:Footer|End of Document|Contact us)[^\n]*$", 
        r"\nThis page was last updated.*$",
        r"\nFor media:[\s\S]+?(?=\n\S)",  # Stop at next headline, non-indented line
        r"\nMedia Relations[\s\S]+?(?=\n\S|\Z)",
        r"(?:\n[\w \-.,/:\(\)@]+){6,}[\s\n]*$",  # If 6+ consecutive lines of mostly names, contacts, orgs
        r"\nSearch for related information by keyword:[\s\S]+?(?=\n\S|\Z)",
        r"\nPage details[\s\S]+?(?=\n\S|\Z)",
        r"\nAbout this site[\s\S]+?(?=\n\S|\Z)",
        r"\nGovernment of Canada[\s\S]+?(?=\n\S|\Z)",
        r"\nAll contacts[\s\S]+?(?=\n\S|\Z)",
    ]

    cleaned = text.strip()

    # Heuristically trim head
    for pat in head_patterns:
        cleaned_new = re.sub(pat, '', cleaned, flags=re.IGNORECASE|re.MULTILINE)
        if len(cleaned_new) < len(cleaned) - 8:  # Actually shortened content?
            cleaned = cleaned_new
            break

    # Heuristically trim tail
    trimmed = False
    for pat in tail_patterns:
        cleaned_new = re.sub(pat, '', cleaned, flags=re.IGNORECASE|re.MULTILINE)
        if len(cleaned_new) < len(cleaned) - 8:
            cleaned = cleaned_new
            trimmed = True
    # Try tail removal twice (to catch two-stage footers)
    if trimmed:
        for pat in tail_patterns:
            cleaned_new = re.sub(pat, '', cleaned, flags=re.IGNORECASE|re.MULTILINE)
            if len(cleaned_new) < len(cleaned) - 8:
                cleaned = cleaned_new

    # Secondary: For repeated menu/footer junk, try to cut on keyword
    NON_CONTENT_KEYWORDS = [
        "You are here:",
        "Main Menu",
        "Search Canada.ca",
        "Back to top",
        "Date modified:", 
        "Report a problem or mistake on this page",
        "Contact us",
        "Page details",
        "About this site",
        "Government of Canada",
        "All contacts",
    ]
    # Remove lines at top or bottom containing only these keywords
    lines = cleaned.splitlines()
    # Remove leading non-content lines
    while lines and any(k.lower() in lines[0].lower() for k in NON_CONTENT_KEYWORDS):
        lines = lines[1:]
    # Remove trailing non-content lines
    while lines and any(k.lower() in lines[-1].lower() for k in NON_CONTENT_KEYWORDS):
        lines = lines[:-1]

    return "\n".join(lines).strip()


def load_documents(data_dir: Path) -> Dict[str, str]:
    """
    Read every .txt file in the input directory.
    
    Args:
        data_dir: Directory containing text files
    
    Returns:
        Dictionary mapping document names (without extension) to their text content
    """
    documents: Dict[str, str] = {}
    for path in sorted(data_dir.glob("*.txt")):
        documents[path.stem] = path.read_text(encoding="utf-8")
    return documents


def embed_chunk_batch(client: OpenAI, batch: List[Dict[str, Any]], embedding_model: str = "text-embedding-3-large") -> List[List[float]]:
    """
    Generate embeddings for a batch of text chunks.
    
    Args:
        client: OpenAI client instance
        batch: List of chunk dictionaries with 'text' key
        embedding_model: Model to use for embeddings
    
    Returns:
        List of embedding vectors
    """
    inputs = [item["text"] for item in batch]
    response = client.embeddings.create(
        model=embedding_model,
        input=inputs
    )
    # OpenAI returns embeddings in the same order as inputs
    return [item.embedding for item in response.data]


def main():
    parser = argparse.ArgumentParser(
        description="Create vector embeddings for documents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create embeddings from documents in a folder
  python utils/embed.py --input data/scraped_documents --output data/vector_store/vector_store.pkl
  
  # Custom chunk size and overlap
  python utils/embed.py --input data/documents --output data/vectors.pkl --chunk-size 300 --chunk-overlap 100
        """
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Directory containing text files to embed"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output path for vector store pickle file"
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=200,
        help="Number of words per chunk (default: 200)"
    )
    parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=75,
        help="Number of words to overlap between chunks (default: 75)"
    )
    parser.add_argument(
        "--embedding-model",
        default="text-embedding-3-large",
        help="OpenAI embedding model to use (default: text-embedding-3-large)"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=64,
        help="Batch size for embedding generation (default: 64)"
    )
    parser.add_argument(
        "--no-trim-content",
        action="store_true",
        help="Skip trimming boilerplate/navigation content from documents (trimming is enabled by default)"
    )
    
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv()
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    if not OPENROUTER_API_KEY:
        raise ValueError("Please set OPENROUTER_API_KEY in your .env file or environment variables")
    
    # Setup paths
    input_dir = Path(args.input).expanduser().resolve()
    output_path = Path(args.output).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    if not input_dir.exists():
        raise FileNotFoundError(f"Input directory not found: {input_dir}")
    
    # Initialize OpenAI client
    client = OpenAI(
        api_key=OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1"
    )
    
    # Load documents
    print(f"Loading documents from: {input_dir}")
    documents = load_documents(input_dir)
    print(f"Loaded {len(documents)} documents")
    
    # Trim content (default behavior, matching original notebook)
    if not args.no_trim_content:
        print("Trimming boilerplate content...")
        for doc_name in documents:
            documents[doc_name] = trim_non_content(documents[doc_name])
    
    # Chunk documents
    print(f"Chunking documents (size={args.chunk_size}, overlap={args.chunk_overlap})...")
    chunk_records: List[Dict[str, Any]] = []
    for doc_name, text in documents.items():
        chunks = chunk_text(text, chunk_size=args.chunk_size, chunk_overlap=args.chunk_overlap)
        if not chunks:
            continue
        for idx, chunk in enumerate(chunks):
            chunk_records.append(
                {
                    "doc_name": doc_name,
                    "chunk_index": idx,
                    "text": chunk,
                }
            )
    
    print(f"Prepared {len(chunk_records)} chunks across all documents")
    
    if not chunk_records:
        print("No chunks were prepared; vector store was not created.")
        return
    
    # Generate embeddings
    print(f"Generating embeddings (batch size: {args.batch_size})...")
    enriched_records: List[Dict[str, Any]] = []
    for start in range(0, len(chunk_records), args.batch_size):
        batch = chunk_records[start:start + args.batch_size]
        embeddings = embed_chunk_batch(client, batch, args.embedding_model)
        for record, embedding in zip(batch, embeddings):
            enriched = {**record, "embedding": embedding}
            enriched_records.append(enriched)
        print(f"Embedded {len(enriched_records)} / {len(chunk_records)} chunks", end="\r")
    
    print()  # New line after progress
    
    # Organize per-document and persist
    print("Organizing vector store...")
    vector_store: Dict[str, Dict[str, Any]] = {}
    for record in enriched_records:
        doc_entry = vector_store.setdefault(
            record["doc_name"],
            {"embeddings": [], "chunks": []}
        )
        doc_entry["embeddings"].append(record["embedding"])
        doc_entry["chunks"].append(
            {
                "chunk_index": record["chunk_index"],
                "text": record["text"],
            }
        )
    
    # Convert embeddings to numpy arrays
    for doc_name, doc_entry in vector_store.items():
        doc_entry["embeddings"] = np.array(doc_entry["embeddings"], dtype=np.float32)
    
    # Save vector store
    with open(output_path, "wb") as f:
        pickle.dump(vector_store, f)
    
    print(f"✅ Persisted vector store to {output_path}")
    print(f"   - Documents: {len(vector_store)}")
    print(f"   - Total chunks: {len(enriched_records)}")


if __name__ == "__main__":
    main()
