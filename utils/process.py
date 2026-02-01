#!/usr/bin/env python3
"""
Data Processing Script with Checkpointing

This script processes text data with automatic checkpoint saving, allowing you to
resume from partial progress if interrupted. Supports language detection, translation,
and filtering operations.
"""

import pandas as pd
import argparse
from pathlib import Path
from tqdm import tqdm

from translate import process_text


def process_dataframe_with_checkpoints(
    df: pd.DataFrame,
    save_path: str,
    mode: str = 'auto',
    text_column: str = 'text',
    id_column: str = 'file'
) -> pd.DataFrame:
    """
    Process dataframe with automatic checkpoint saving.
    Supports resuming from partial progress.
    
    Args:
        df: DataFrame with text data
        save_path: Path to save checkpoint CSV
        mode: Processing mode - 'auto', 'translate', 'filter', or 'detect_only'
        text_column: Name of the column containing text to process
        id_column: Name of the column to use for identifying rows (for checkpointing)
    
    Returns:
        Processed DataFrame
    """
    working_df = df.copy()
    
    # Ensure required columns exist
    if text_column not in working_df.columns:
        raise ValueError(f"Column '{text_column}' not found in DataFrame. Available columns: {list(working_df.columns)}")
    
    if id_column not in working_df.columns:
        # Use index as identifier if id_column doesn't exist
        working_df[id_column] = working_df.index
        print(f"Warning: '{id_column}' column not found. Using index as identifier.")
    
    # Load existing checkpoint if available
    checkpoint_path = Path(save_path)
    if checkpoint_path.exists():
        try:
            checkpoint_df = pd.read_csv(checkpoint_path, escapechar='\\')
            print(f"📂 Loaded checkpoint from {save_path}")
            
            # Merge processed results from checkpoint
            if 'processed' in checkpoint_df.columns:
                # Create mapping from id_column to processed text
                id_to_processed = dict(zip(checkpoint_df[id_column], checkpoint_df['processed']))
                working_df['processed'] = working_df[id_column].map(id_to_processed)
            else:
                working_df['processed'] = None
            
            if 'detected_language' in checkpoint_df.columns:
                id_to_lang = dict(zip(checkpoint_df[id_column], checkpoint_df['detected_language']))
                working_df['detected_language'] = working_df[id_column].map(id_to_lang)
            else:
                working_df['detected_language'] = None
        except (pd.errors.EmptyDataError, Exception) as e:
            print(f"⚠️  Could not load checkpoint: {e}")
            print("🆕 Starting fresh")
            working_df['processed'] = None
            working_df['detected_language'] = None
    else:
        print("🆕 Starting fresh (no checkpoint found)")
        working_df['processed'] = None
        working_df['detected_language'] = None
    
    # Process each row
    total_rows = len(working_df)
    processed_count = 0
    skipped_count = 0
    error_count = 0
    
    for idx, row in tqdm(working_df.iterrows(), total=total_rows, desc="Processing"):
        text = row[text_column]
        existing_processed = row.get('processed') if pd.notna(row.get('processed')) else None
        
        # Skip if already processed
        if existing_processed and len(str(existing_processed)) > 0:
            skipped_count += 1
            continue
        
        # Process the text
        try:
            processed, detected_lang = process_text(text, mode=mode)
            working_df.at[idx, 'processed'] = processed
            working_df.at[idx, 'detected_language'] = detected_lang
            processed_count += 1
        except Exception as e:
            error_count += 1
            row_id = row.get(id_column, idx)
            print(f"\n⚠️  Error processing {row_id}: {e}")
            working_df.at[idx, 'processed'] = None
            working_df.at[idx, 'detected_language'] = None
        
        # Save checkpoint after each row
        working_df.to_csv(save_path, index=False, escapechar='\\')
    
    # Print summary
    print(f"\n✅ Processing complete!")
    print(f"   - Processed: {processed_count}")
    print(f"   - Skipped (already done): {skipped_count}")
    print(f"   - Errors: {error_count}")
    print(f"   - Total: {total_rows}")
    
    return working_df


def main():
    """Command-line interface for the processing script."""
    parser = argparse.ArgumentParser(
        description="Process text data with checkpointing support",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process with auto mode (translate if not English)
  python process.py --input extracted.csv --output processed.csv --mode auto
  
  # Process with translation
  python process.py --input extracted.csv --output processed.csv --mode translate
  
  # Filter for English only
  python process.py --input extracted.csv --output processed.csv --mode filter
        """
    )
    parser.add_argument(
        '--input',
        required=True,
        help='Input CSV file path (must have a text column)'
    )
    parser.add_argument(
        '--output',
        required=True,
        help='Output CSV file path (also used as checkpoint)'
    )
    parser.add_argument(
        '--mode',
        choices=['auto', 'translate', 'filter', 'detect_only'],
        default='auto',
        help='Processing mode: auto (translate if not English), translate (always translate), filter (English only), detect_only (just detect)'
    )
    parser.add_argument(
        '--text-column',
        default='text',
        help='Name of the text column in the CSV (default: "text")'
    )
    parser.add_argument(
        '--id-column',
        default='file',
        help='Name of the ID column for checkpointing (default: "file")'
    )
    
    args = parser.parse_args()
    
    # Load CSV
    input_path = Path(args.input)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {args.input}")
    
    print(f"Loading: {args.input}")
    df = pd.read_csv(args.input)
    print(f"Loaded {len(df)} rows")
    
    # Process with checkpointing
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    df_processed = process_dataframe_with_checkpoints(
        df,
        save_path=str(output_path),
        mode=args.mode,
        text_column=args.text_column,
        id_column=args.id_column
    )
    
    # Final save (already saved during processing, but ensure it's there)
    df_processed.to_csv(output_path, index=False, escapechar='\\')
    
    print(f"\n✅ Results saved to: {output_path}")
    
    # Show language distribution if available
    if 'detected_language' in df_processed.columns:
        lang_counts = df_processed['detected_language'].value_counts()
        print(f"\nLanguage distribution:")
        for lang, count in lang_counts.items():
            print(f"  {lang}: {count}")
    
    # Show processing statistics
    if 'processed' in df_processed.columns:
        successful = df_processed['processed'].notna().sum()
        failed = df_processed['processed'].isna().sum()
        print(f"\nProcessing statistics:")
        print(f"  - Successful: {successful}")
        print(f"  - Failed: {failed}")
        
        if successful > 0:
            avg_length = df_processed['processed'].str.len().mean()
            print(f"  - Average text length: {avg_length:.0f} characters")


if __name__ == "__main__":
    main()
