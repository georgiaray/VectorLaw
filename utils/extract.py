#!/usr/bin/env python3
"""
PDF Text Extraction Script

This script extracts text from PDF files in a given folder and returns a pandas DataFrame.
"""

import os
import pandas as pd
import PyPDF2
from tqdm import tqdm
import argparse
from pathlib import Path


def load_files(folder):
    """
    Load files from a folder and extract text.
    
    Args:
        folder: Path to folder containing PDF files
    
    Returns:
        DataFrame with columns: 'file', 'text'
    """
    df = []
    folder_path = Path(folder)
    
    if not folder_path.exists():
        raise FileNotFoundError(f"Folder not found: {folder}")
    
    files = sorted([f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))])
    
    for file in tqdm(files, desc=f"Loading files from {folder}"):
        file_path = folder_path / file
        ext = os.path.splitext(file)[-1].lower()
        
        try:
            if ext == '.pdf':
                text = ""
                with open(file_path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    for page in reader.pages:
                        try:
                            text += page.extract_text() or ""
                        except Exception:
                            continue
            else:
                # Handle non-PDF text files
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    text = f.read()
            
            df.append({'file': file, 'text': text})
        except Exception as e:
            df.append({'file': file, 'text': '', 'error': str(e)})
    
    return pd.DataFrame(df)


def main():
    """Command-line interface for the extraction script."""
    parser = argparse.ArgumentParser(
        description="Extract text from PDF files in a folder",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example:
  python extract.py --folder data/jurisdiction1 --output extracted_text.csv
        """
    )
    parser.add_argument(
        '--folder',
        required=True,
        help='Path to folder containing PDF files'
    )
    parser.add_argument(
        '--output',
        required=True,
        help='Output CSV file path'
    )
    
    args = parser.parse_args()
    
    # Extract text
    print(f"Extracting text from: {args.folder}")
    df = load_files(args.folder)
    
    # Save to CSV
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False, escapechar='\\')
    
    print(f"\n✅ Extracted text from {len(df)} files")
    print(f"✅ Saved to: {output_path}")
    
    # Show summary
    successful = df[df['text'].str.len() > 0].shape[0]
    failed = df[df['text'].str.len() == 0].shape[0]
    print(f"   - Successful: {successful}")
    if failed > 0:
        print(f"   - Failed: {failed}")
        if 'error' in df.columns:
            errors = df[df['text'].str.len() == 0]
            print("\n   Errors:")
            for idx, row in errors.iterrows():
                print(f"     - {row['file']}: {row.get('error', 'Unknown error')}")


if __name__ == "__main__":
    main()
