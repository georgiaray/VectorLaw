"""
RAG (Retrieval-Augmented Generation) Utilities

This module provides utilities for working with vector stores and performing
semantic search on document embeddings for RAG applications.
"""

import pickle
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Optional

from openai import OpenAI


def load_vector_store(path: Path) -> Dict[str, Dict[str, Any]]:
    """
    Load a vector store from a pickle file.
    
    Args:
        path: Path to the vector store pickle file
    
    Returns:
        Dictionary mapping document names to their embeddings and chunks
    """
    if not path.exists():
        raise FileNotFoundError(f"Vector store not found at {path}. Create embeddings first.")
    
    with open(path, "rb") as f:
        store = pickle.load(f)
    
    # Ensure embeddings are numpy arrays after unpickling
    for entry in store.values():
        entry["embeddings"] = np.array(entry["embeddings"], dtype=np.float32)
    
    return store


def query_document(
    store: Dict[str, Dict[str, Any]], 
    client: OpenAI, 
    doc_name: str, 
    query: str, 
    top_k: int = 3, 
    embedding_model: str = "text-embedding-3-large"
) -> List[Dict[str, Any]]:
    """
    Query a document in the vector store and return top_k most similar chunks.
    
    Args:
        store: The vector store dictionary
        client: OpenAI client instance
        doc_name: Name of the document to query
        query: Query string
        top_k: Number of top results to return
        embedding_model: Model to use for embedding the query.
                        Must match the model used to create the stored embeddings.
    
    Returns:
        List of dictionaries with 'chunk_index', 'similarity', and 'text' keys
    """
    doc_entry = store.get(doc_name)
    if doc_entry is None:
        available = ", ".join(sorted(store.keys()))
        raise KeyError(f"Document '{doc_name}' not in vector store. Available names: {available}")

    query_embedding = client.embeddings.create(
        model=embedding_model,
        input=[query]
    ).data[0].embedding

    doc_embeddings = doc_entry["embeddings"]
    if not len(doc_embeddings):
        return []

    query_vector = np.array(query_embedding, dtype=np.float32)
    query_norm = np.linalg.norm(query_vector)
    doc_norms = np.linalg.norm(doc_embeddings, axis=1)
    similarities = (doc_embeddings @ query_vector) / (doc_norms * query_norm + 1e-8)

    top_indices = similarities.argsort()[-top_k:][::-1]

    results: List[Dict[str, Any]] = []
    chunks = doc_entry["chunks"]
    
    # Handle both list and dict structures for chunks
    for idx in top_indices:
        idx_int = int(idx)  # Ensure we have a Python int, not numpy int64
        if isinstance(chunks, list):
            # If chunks is a list, access by index
            if idx_int < len(chunks):
                chunk_meta = chunks[idx_int]
            else:
                continue
        elif isinstance(chunks, dict):
            # If chunks is a dict, we need to find the chunk with matching index
            if idx_int in chunks:
                chunk_meta = chunks[idx_int]
            elif str(idx_int) in chunks:
                chunk_meta = chunks[str(idx_int)]
            else:
                # If dict is keyed by other values, try to get by position
                chunk_keys = sorted(chunks.keys(), key=lambda x: int(x) if str(x).isdigit() else float('inf'))
                if idx_int < len(chunk_keys):
                    chunk_meta = chunks[chunk_keys[idx_int]]
                else:
                    continue
        else:
            continue
            
        # Extract chunk data - handle both dict and direct access
        if isinstance(chunk_meta, dict):
            chunk_index_val = chunk_meta.get("chunk_index", idx)
            chunk_text = chunk_meta.get("text", "")
        else:
            # If chunk_meta is not a dict, try to extract from it
            chunk_index_val = idx
            chunk_text = str(chunk_meta)
            
        results.append(
            {
                "chunk_index": chunk_index_val,
                "similarity": float(similarities[idx]),
                "text": chunk_text,
            }
        )
    return results
