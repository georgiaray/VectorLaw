#!/usr/bin/env python3
"""
Data Exploration Script

This script explores a curated dataset of legal documents, automatically discovering
patterns in the data including geographies, document types, and instruments.

REQUIRED COLUMNS:
- 'Geographies' (or similar): Column containing geography/jurisdiction names
- 'Document Type' (or similar): Column containing document type classifications
- 'Instrument' (or similar): Column containing instrument classifications (may contain multiple values separated by semicolons)

The script will automatically discover:
- All unique geographies in the dataset
- All unique document types
- All unique instruments (parsing semicolon-separated values)
- Distribution statistics for each category
"""

import pandas as pd
import numpy as np
import argparse
from pathlib import Path
from typing import List, Optional, Dict
from collections import Counter


def print_section(title: str, char: str = "="):
    """Print a formatted section header."""
    print(f"\n{char * 60}")
    print(f"{title:^60}")
    print(f"{char * 60}\n")


def print_subsection(title: str):
    """Print a formatted subsection header."""
    print(f"\n{title}")
    print("-" * len(title))


def discover_geographies(df: pd.DataFrame, geography_column: str = 'Geographies') -> List[str]:
    """
    Discover all unique geographies in the dataset.
    
    Args:
        df: DataFrame
        geography_column: Name of the geography column
    
    Returns:
        List of unique geography names, sorted
    """
    if geography_column not in df.columns:
        return []
    
    geographies = df[geography_column].dropna().unique()
    return sorted([g for g in geographies if str(g).strip()])


def discover_document_types(df: pd.DataFrame, doc_type_column: str = 'Document Type') -> pd.Series:
    """
    Discover all document types and their counts.
    
    Args:
        df: DataFrame
        doc_type_column: Name of the document type column
    
    Returns:
        Series with document type counts, sorted by count descending
    """
    if doc_type_column not in df.columns:
        return pd.Series(dtype=int)
    
    return df[doc_type_column].value_counts()


def discover_instruments(df: pd.DataFrame, instrument_column: str = 'Instrument') -> Dict[str, int]:
    """
    Discover all unique instruments in the dataset.
    Instruments may be semicolon-separated in a single cell.
    
    Args:
        df: DataFrame
        instrument_column: Name of the instrument column
    
    Returns:
        Dictionary mapping instrument to count of documents containing it
    """
    if instrument_column not in df.columns:
        return {}
    
    all_instruments = []
    
    for value in df[instrument_column].dropna():
        if pd.notna(value):
            # Split by semicolon and clean
            instruments = [item.strip() for item in str(value).split(';') if item.strip()]
            all_instruments.extend(instruments)
    
    # Count occurrences
    instrument_counts = Counter(all_instruments)
    return dict(sorted(instrument_counts.items(), key=lambda x: x[1], reverse=True))


def filter_by_instruments(
    df: pd.DataFrame,
    instruments: List[str],
    instrument_column: str = 'Instrument'
) -> pd.DataFrame:
    """
    Filter dataframe to rows where Instrument contains any of the specified instruments.
    
    Args:
        df: DataFrame with an instrument column
        instruments: List of instrument strings to search for
        instrument_column: Name of the instrument column
    
    Returns:
        Filtered DataFrame
    """
    if instrument_column not in df.columns:
        return df.copy()
    
    mask = df[instrument_column].apply(
        lambda x: any(instr in str(x) for instr in instruments) if pd.notna(x) else False
    )
    return df[mask].copy()


def filter_by_document_types(
    df: pd.DataFrame,
    excluded_types: List[str],
    doc_type_column: str = 'Document Type'
) -> pd.DataFrame:
    """
    Filter dataframe to exclude specified document types.
    
    Args:
        df: DataFrame with a document type column
        excluded_types: List of document types to exclude
        doc_type_column: Name of the document type column
    
    Returns:
        Filtered DataFrame
    """
    if doc_type_column not in df.columns:
        return df.copy()
    
    mask = ~df[doc_type_column].str.strip().str.casefold().isin(
        [x.casefold() for x in excluded_types]
    )
    return df[mask].copy()


def filter_by_geography(
    df: pd.DataFrame,
    geography: str,
    geography_column: str = 'Geographies'
) -> pd.DataFrame:
    """
    Filter dataframe by geography.
    
    Args:
        df: DataFrame with a geography column
        geography: Geography name to filter by
        geography_column: Name of the geography column
    
    Returns:
        Filtered DataFrame
    """
    if geography_column not in df.columns:
        return df.copy()
    
    return df[df[geography_column] == geography].copy()


def explore_dataset(
    input_path: str,
    output_dir: Optional[str] = None,
    geography_column: str = 'Geographies',
    doc_type_column: str = 'Document Type',
    instrument_column: str = 'Instrument',
    filter_instruments: Optional[List[str]] = None,
    exclude_doc_types: Optional[List[str]] = None,
    filter_geographies: Optional[List[str]] = None
) -> dict:
    """
    Explore and analyze a dataset of legal documents.
    
    Args:
        input_path: Path to input CSV file
        output_dir: Directory to save filtered outputs (optional)
        geography_column: Name of the geography column
        doc_type_column: Name of the document type column
        instrument_column: Name of the instrument column
        filter_instruments: List of instruments to filter by (optional, if None shows all)
        exclude_doc_types: Document types to exclude (optional)
        filter_geographies: List of geographies to filter by (optional, if None shows all)
    
    Returns:
        Dictionary with filtered dataframes and statistics
    """
    # Load data
    print_section("Loading Dataset")
    df = pd.read_csv(input_path)
    print(f"✅ Loaded {len(df):,} documents from {input_path}")
    print(f"   Total columns: {len(df.columns)}")
    
    # Check for required columns
    required_cols = [geography_column, doc_type_column, instrument_column]
    available_cols = [col for col in required_cols if col in df.columns]
    missing_cols = [col for col in required_cols if col not in df.columns]
    
    if missing_cols:
        print(f"⚠️  Warning: Missing columns: {missing_cols}")
        print(f"   Available columns: {list(df.columns)[:10]}...")
    
    # Discover geographies
    print_section("Discovering Geographies")
    geographies = discover_geographies(df, geography_column)
    if geographies:
        print(f"✅ Found {len(geographies)} unique geographies:")
        for geo in geographies:
            count = (df[geography_column] == geo).sum()
            print(f"   {geo:30} {count:>6} documents")
    else:
        print("⚠️  No geographies found (column may be missing or empty)")
    
    # Discover document types
    print_section("Discovering Document Types")
    doc_type_counts = discover_document_types(df, doc_type_column)
    if len(doc_type_counts) > 0:
        print(f"✅ Found {len(doc_type_counts)} unique document types:")
        for doc_type, count in doc_type_counts.head(20).items():
            print(f"   {doc_type:40} {count:>6}")
        if len(doc_type_counts) > 20:
            print(f"   ... and {len(doc_type_counts) - 20} more types")
    else:
        print("⚠️  No document types found (column may be missing or empty)")
    
    # Discover instruments
    print_section("Discovering Instruments")
    instrument_counts = discover_instruments(df, instrument_column)
    if instrument_counts:
        print(f"✅ Found {len(instrument_counts)} unique instruments:")
        for instr, count in list(instrument_counts.items())[:30]:
            print(f"   {instr:50} {count:>6}")
        if len(instrument_counts) > 30:
            print(f"   ... and {len(instrument_counts) - 30} more instruments")
    else:
        print("⚠️  No instruments found (column may be missing or empty)")
    
    # Apply filters if specified
    working_df = df.copy()
    original_count = len(working_df)
    
    # Filter by instruments if specified
    if filter_instruments:
        print_section("Filtering by Instruments")
        print(f"Filtering for documents containing any of {len(filter_instruments)} instruments...")
        working_df = filter_by_instruments(working_df, filter_instruments, instrument_column)
        print(f"✅ {len(working_df):,} documents after instrument filtering")
        print(f"   Removed {original_count - len(working_df)} documents")
        original_count = len(working_df)
    
    # Filter by document types if specified
    if exclude_doc_types:
        print_section("Filtering by Document Type")
        print(f"Excluding {len(exclude_doc_types)} document types:")
        for doc_type in exclude_doc_types:
            count = (working_df[doc_type_column] == doc_type).sum()
            if count > 0:
                print(f"   - {doc_type} ({count} documents)")
        
        working_df = filter_by_document_types(working_df, exclude_doc_types, doc_type_column)
        print(f"\n✅ {len(working_df):,} documents after filtering")
        print(f"   Removed {original_count - len(working_df)} documents")
        original_count = len(working_df)
    
    # Filter by geography if specified, otherwise show all
    if filter_geographies is None:
        filter_geographies = geographies
    
    geography_dataframes = {}
    geography_counts = {}
    
    for geo in filter_geographies:
        geo_df = filter_by_geography(working_df, geo, geography_column)
        count = len(geo_df)
        geography_dataframes[geo] = geo_df
        geography_counts[geo] = count
    
    # Additional analysis: Document Type and Instrument relationships
    if doc_type_column in working_df.columns and instrument_column in working_df.columns:
        print_section("Document Type and Instrument Relationships")
        print("Top instruments by document type:")
        
        # Get top document types
        top_doc_types = working_df[doc_type_column].value_counts().head(10)
        
        for doc_type in top_doc_types.index:
            doc_type_df = working_df[working_df[doc_type_column] == doc_type]
            if len(doc_type_df) > 0:
                doc_type_instruments = discover_instruments(doc_type_df, instrument_column)
                print(f"\n   {doc_type} ({len(doc_type_df)} documents):")
                for instr, count in list(doc_type_instruments.items())[:3]:
                    pct = (count / len(doc_type_df) * 100) if len(doc_type_df) > 0 else 0
                    print(f"      {instr:50} {count:>4} ({pct:>5.1f}%)")
    
    # Additional analysis: Instrument distribution by geography (if multiple geographies)
    if len(geographies) > 1 and instrument_column in working_df.columns:
        print_section("Instrument Distribution by Geography")
        print("Top instruments for each geography:")
        
        for geo in geographies:
            geo_df = geography_dataframes[geo]
            if len(geo_df) > 0:
                geo_instruments = discover_instruments(geo_df, instrument_column)
                print(f"\n   {geo}:")
                for instr, count in list(geo_instruments.items())[:5]:
                    pct = (count / len(geo_df) * 100) if len(geo_df) > 0 else 0
                    print(f"      {instr:50} {count:>4} ({pct:>5.1f}%)")
    
    # Save outputs if requested
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        print_section("Saving Filtered Datasets")
        for geo, geo_df in geography_dataframes.items():
            if len(geo_df) > 0:
                # Create safe filename
                safe_name = str(geo).lower().replace(' ', '_').replace('/', '_')
                output_file = output_path / f"{safe_name}_df.csv"
                geo_df.to_csv(output_file, index=False)
                print(f"  ✅ Saved {geo}: {output_file} ({len(geo_df)} documents)")
    
    return {
        'original': df,
        'filtered': working_df,
        'by_geography': geography_dataframes,
        'statistics': {
            'total': len(df),
            'after_filtering': len(working_df),
            'by_geography': geography_counts,
            'geographies': geographies,
            'document_types': doc_type_counts.to_dict(),
            'instruments': instrument_counts
        }
    }


def main():
    """Command-line interface for the exploration script."""
    parser = argparse.ArgumentParser(
        description="Explore and analyze a curated dataset of legal documents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic exploration (discovers everything from data)
  python utils/exploration.py --input data/data.csv
  
  # Save filtered outputs
  python utils/exploration.py --input data/data.csv --output data/filtered
  
  # Filter specific geographies
  python utils/exploration.py --input data/data.csv --geographies "Brazil" "China"
  
  # Filter by specific instruments
  python utils/exploration.py --input data/data.csv --instruments "Climate finance tools|Economic" "Subsidies|Economic"
  
  # Exclude specific document types
  python utils/exploration.py --input data/data.csv --exclude-doc-types "Press Release" "Summary"
        """
    )
    parser.add_argument(
        '--input',
        required=True,
        help='Input CSV file path with document metadata'
    )
    parser.add_argument(
        '--output',
        help='Output directory to save filtered CSV files (optional)'
    )
    parser.add_argument(
        '--geography-column',
        default='Geographies',
        help='Name of the geography column (default: "Geographies")'
    )
    parser.add_argument(
        '--doc-type-column',
        default='Document Type',
        help='Name of the document type column (default: "Document Type")'
    )
    parser.add_argument(
        '--instrument-column',
        default='Instrument',
        help='Name of the instrument column (default: "Instrument")'
    )
    parser.add_argument(
        '--geographies',
        nargs='+',
        help='List of geographies to filter by (default: shows all discovered geographies)'
    )
    parser.add_argument(
        '--instruments',
        nargs='+',
        help='List of instruments to filter by (optional, if not provided shows all documents)'
    )
    parser.add_argument(
        '--exclude-doc-types',
        nargs='+',
        help='Document types to exclude (optional)'
    )
    parser.add_argument(
        '--instruments-file',
        help='Path to text file with one instrument per line (alternative to --instruments)'
    )
    
    args = parser.parse_args()
    
    # Load custom instruments if provided
    instruments = args.instruments
    if args.instruments_file:
        with open(args.instruments_file, 'r') as f:
            instruments = [line.strip() for line in f if line.strip()]
        print(f"Loaded {len(instruments)} instruments from {args.instruments_file}")
    
    # Run exploration
    results = explore_dataset(
        input_path=args.input,
        output_dir=args.output,
        geography_column=args.geography_column,
        doc_type_column=args.doc_type_column,
        instrument_column=args.instrument_column,
        filter_instruments=instruments,
        exclude_doc_types=args.exclude_doc_types,
        filter_geographies=args.geographies
    )
    
    print_section("Exploration Complete", "=")
    print("✅ All analysis complete!")


if __name__ == "__main__":
    main()
