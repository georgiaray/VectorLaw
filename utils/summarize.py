#!/usr/bin/env python3
"""
Document Summarization Script

This script generates question-focused summaries of documents using LLMs.
It processes text files and creates summaries focused on specific aspects
of the documents (e.g., sectoral focus, market failures, etc.).
"""

import os
import argparse
from pathlib import Path
from typing import List, Optional
import tiktoken

from dotenv import load_dotenv
from openai import OpenAI


def prompt_token_count(prompt: str, encoding: str = "gpt-4") -> int:
    """
    Utility to count tokens in a single prompt.
    
    Args:
        prompt: Text to count tokens for
        encoding: Encoding model to use
    
    Returns:
        Number of tokens
    """
    try:
        enc = tiktoken.encoding_for_model(encoding)
    except KeyError:
        enc = tiktoken.get_encoding("cl100k_base")
    return len(enc.encode(prompt))


def available_tokens_for_doc(
    doc_prompts: List[str], 
    max_tokens: int = 128000, 
    safety_margin: int = 1024, 
    encoding: str = "gpt-4"
) -> int:
    """
    Determines the maximum tokens that can be used for doc_text
    to ensure that the prompt plus system messages fit in context.
    
    Args:
        doc_prompts: List of prompt templates (without doc_text filled in)
        max_tokens: Maximum context window size
        safety_margin: Tokens to reserve for system messages, etc.
        encoding: Encoding model to use
    
    Returns:
        Maximum tokens available for document text
    """
    # Estimate length of the largest prompt (prompt is built from doc_text)
    prompt_overhead = max([prompt_token_count(p, encoding) for p in doc_prompts]) if doc_prompts else 0
    # Just to be sure, allow a safety margin on top of the max_tokens
    return max_tokens - prompt_overhead - safety_margin


def truncate_text_to_token_limit(text: str, max_tokens: int, encoding: str = "gpt-4") -> str:
    """
    Truncate text so its tokenized length is <= max_tokens.
    
    Args:
        text: Text to truncate
        max_tokens: Maximum number of tokens
        encoding: Encoding model to use
    
    Returns:
        Truncated text
    """
    try:
        enc = tiktoken.encoding_for_model(encoding)
    except KeyError:
        enc = tiktoken.get_encoding("cl100k_base")
    tokens = enc.encode(text)
    if len(tokens) > max_tokens:
        print(f"  ⚠️  Truncating document from {len(tokens)} tokens to {max_tokens} tokens.")
        tokens = tokens[:max_tokens]
        text = enc.decode(tokens)
    return text


def perform_summarization(
    client: OpenAI,
    doc_prompts: List[str],
    system_prompt: str,
    model: str = "gpt-4o-mini"
) -> List[str]:
    """
    Generate summaries for a list of prompts.
    
    Args:
        client: OpenAI client instance
        doc_prompts: List of prompts to summarize
        system_prompt: System prompt for the LLM
        model: Model to use for summarization
    
    Returns:
        List of summary texts
    """
    summaries = []
    for idx, prompt in enumerate(doc_prompts):
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
        )
        text_response = response.choices[0].message.content
        summaries.append(text_response)
        print(f"  ✓ Generated summary {idx + 1}/{len(doc_prompts)}")
    return summaries


def summarize_document(
    client: OpenAI,
    doc_text: str,
    doc_name: str,
    output_dir: Path,
    get_prompts_func,
    system_prompt: str,
    max_tokens: int = 128000,
    safety_margin: int = 1024,
    model: str = "gpt-4o-mini",
    encoding: str = "gpt-4"
) -> None:
    """
    Summarize a single document with multiple question-focused prompts.
    
    Args:
        client: OpenAI client instance
        doc_text: Document text to summarize
        doc_name: Name of the document (without extension)
        output_dir: Directory to save summaries
        get_prompts_func: Function that takes doc_text and returns list of prompts
        system_prompt: System prompt for the LLM
        max_tokens: Maximum context window size
        safety_margin: Tokens to reserve for system messages
        model: Model to use for summarization
        encoding: Encoding model to use
    """
    # Step 1: Estimate what doc_prompts would look like for a chunk of doc_text
    # Temporarily build prompts with the full doc_text
    temp_doc_prompts = get_prompts_func(doc_text)
    # Calculate maximum allowed tokens in doc_text (subtracting prompt overhead and margin)
    max_allowed_tokens = available_tokens_for_doc(
        temp_doc_prompts, 
        max_tokens=max_tokens, 
        safety_margin=safety_margin,
        encoding=encoding
    )
    
    # Step 2: Actually truncate doc_text to fit
    doc_text = truncate_text_to_token_limit(doc_text, max_allowed_tokens, encoding)
    
    # Step 3: Build prompts again (using truncated doc_text)
    doc_prompts = get_prompts_func(doc_text)
    doc_summaries = perform_summarization(client, doc_prompts, system_prompt, model)
    
    # Create subfolder for document summary
    doc_summary_folder = output_dir / doc_name
    doc_summary_folder.mkdir(parents=True, exist_ok=True)
    
    # Save each summary as a separate file inside the subfolder
    # Note: summary indices start from 2 (question_2, question_3, etc.)
    for idx, summary in enumerate(doc_summaries, start=2):
        summary_filename = f"question_{idx}_summary.txt"
        summary_path = doc_summary_folder / summary_filename
        summary_path.write_text(summary, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(
        description="Generate question-focused summaries of documents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Summarize documents (requires a prompts module with get_all_prompts function)
  python utils/summarize.py --input data/scraped_documents --output data/summaries
  
Note: This script requires a prompts module that provides:
  - SYSTEM_PROMPT: System prompt for the LLM
  - get_all_prompts(doc_text): Function that returns a list of prompts
  
See prompts_example.py in the analysis folder for an example implementation.
        """
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Directory containing text files to summarize"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Directory to save summaries (will create subdirectories per document)"
    )
    parser.add_argument(
        "--prompts-module",
        required=True,
        help="Python module path containing SYSTEM_PROMPT and get_all_prompts function (e.g., analysis.prompts_example)"
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=128000,
        help="Maximum context window size (default: 128000)"
    )
    parser.add_argument(
        "--safety-margin",
        type=int,
        default=1024,
        help="Tokens to reserve for system messages (default: 1024)"
    )
    parser.add_argument(
        "--model",
        default="gpt-4o-mini",
        help="Model to use for summarization (default: gpt-4o-mini)"
    )
    parser.add_argument(
        "--no-skip-existing",
        action="store_true",
        help="Process documents even if summaries already exist (skipping is enabled by default)"
    )
    
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv()
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    if not OPENROUTER_API_KEY:
        raise ValueError("Please set OPENROUTER_API_KEY in your .env file or environment variables")
    
    # Import prompts module
    import importlib
    import sys
    # Add project root to path to allow importing analysis module
    project_root = Path(__file__).parent.parent.resolve()
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    prompts_module = importlib.import_module(args.prompts_module)
    if not hasattr(prompts_module, "SYSTEM_PROMPT"):
        raise ValueError(f"Module {args.prompts_module} must have SYSTEM_PROMPT")
    if not hasattr(prompts_module, "get_all_prompts"):
        raise ValueError(f"Module {args.prompts_module} must have get_all_prompts function")
    
    system_prompt = prompts_module.SYSTEM_PROMPT
    get_all_prompts = prompts_module.get_all_prompts
    
    # Setup paths
    input_dir = Path(args.input).expanduser().resolve()
    output_dir = Path(args.output).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if not input_dir.exists():
        raise FileNotFoundError(f"Input directory not found: {input_dir}")
    
    # Initialize OpenAI client
    client = OpenAI(
        api_key=OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1"
    )
    
    # Get all text files
    all_docs = sorted([f for f in input_dir.glob("*.txt")])
    print(f"Found {len(all_docs)} documents to process")
    
    successful = 0
    skipped = 0
    
    for doc_path in all_docs:
        doc_name = doc_path.stem
        doc_summary_folder = output_dir / doc_name
        
        if not args.no_skip_existing and doc_summary_folder.exists():
            print(f"Skipping {doc_name}: summary already exists")
            skipped += 1
            continue
        
        print(f"Processing {doc_name}...")
        try:
            doc_text = doc_path.read_text(encoding="utf-8")
            summarize_document(
                client=client,
                doc_text=doc_text,
                doc_name=doc_name,
                output_dir=output_dir,
                get_prompts_func=get_all_prompts,
                system_prompt=system_prompt,
                max_tokens=args.max_tokens,
                safety_margin=args.safety_margin,
                model=args.model
            )
            successful += 1
            print(f"  ✅ Completed {doc_name}\n")
        except Exception as e:
            print(f"  ❌ Error processing {doc_name}: {e}\n")
    
    print(f"\n✅ Summarization complete!")
    print(f"   - Successful: {successful}")
    print(f"   - Skipped: {skipped}")
    print(f"   - Total: {len(all_docs)}")


if __name__ == "__main__":
    main()
