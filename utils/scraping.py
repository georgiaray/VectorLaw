#!/usr/bin/env python3
"""
Scraping Script

Downloads PDF and HTML documents from URLs and extracts text content.
Supports both PDF files and HTML web pages.
"""

import os
import re
import argparse
from pathlib import Path
from urllib.parse import urlparse, unquote
from io import BytesIO
from typing import Optional, Tuple

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False

try:
    import PyPDF2
    HAS_PYPDF2 = True
except ImportError:
    HAS_PYPDF2 = False


def sanitize_filename(name: str) -> str:
    """Sanitize filename by removing invalid characters."""
    return re.sub(r'[\\/:*?"<>|]+', "_", name).strip()


def build_scraping_session(
    total_retries: int = 3,
    backoff_factor: float = 0.5,
    status_forcelist: tuple = (429, 500, 502, 503, 504),
) -> requests.Session:
    """
    Create a requests session with retry logic and exponential backoff.
    
    Args:
        total_retries: Maximum number of retries
        backoff_factor: Backoff multiplier for retries
        status_forcelist: HTTP status codes that trigger retries
    
    Returns:
        Configured requests Session
    """
    session = requests.Session()
    retry = Retry(
        total=total_retries,
        read=total_retries,
        connect=total_retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        allowed_methods=("GET", "HEAD"),
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    session.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/119.0.0.0 Safari/537.36"
        )
    })
    return session


def is_pdf_response(response: requests.Response, url: str) -> bool:
    """Check if response is a PDF based on content-type or URL."""
    content_type = response.headers.get("Content-Type", "").lower()
    is_pdf_content = "pdf" in content_type or "application/x-pdf" in content_type
    is_pdf_url = url.lower().split("?")[0].endswith(".pdf")
    return is_pdf_content or is_pdf_url


def extract_text_from_pdf(content: bytes) -> str:
    """
    Extract text from PDF bytes using PyPDF2.
    
    Args:
        content: PDF file content as bytes
    
    Returns:
        Extracted text
    """
    if not HAS_PYPDF2:
        raise ImportError(
            "PyPDF2 is required for PDF extraction. Install with: pip install PyPDF2"
        )
    
    try:
        text = ""
        reader = PyPDF2.PdfReader(BytesIO(content))
        for page in reader.pages:
            try:
                text += page.extract_text() or ""
            except Exception:
                continue
        return text
    except Exception as e:
        raise ValueError(f"PDF extraction failed: {e}")


def extract_text_from_html(response: requests.Response) -> str:
    """
    Extract text from HTML response using BeautifulSoup.
    
    Args:
        response: requests Response object with HTML content
    
    Returns:
        Extracted text
    """
    if not HAS_BS4:
        raise ImportError(
            "BeautifulSoup4 is required for HTML extraction. "
            "Install with: pip install beautifulsoup4"
        )
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Remove script and style elements
    for script in soup(["script", "style", "nav", "header", "footer"]):
        script.decompose()
    
    # Get text and clean it up
    text = soup.get_text()
    
    # Clean up whitespace
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = " ".join(chunk for chunk in chunks if chunk)
    
    return text


def download_and_extract(url: str, dest_path: Path, index: int, session: Optional[requests.Session] = None) -> Tuple[bool, str, str]:
    """
    Download a URL and extract text content.
    Handles both PDFs and HTML pages.
    
    Args:
        url: URL to download
        dest_path: Destination folder
        index: File index number
        session: Optional requests Session (for retry logic)
    
    Returns:
        Tuple of (success: bool, filename: str, error_message: str)
    """
    if session is None:
        session = build_scraping_session()
        close_session = True
    else:
        close_session = False
    
    try:
        response = session.get(url, stream=True, timeout=30, allow_redirects=True)
        
        if not response.ok:
            return False, "", f"HTTP {response.status_code}: {response.reason}"
        
        # Determine content type
        if is_pdf_response(response, url):
            # PDF file
            try:
                content = response.content
                text = extract_text_from_pdf(content)
                filename = f"{index}.txt"
                full_path = dest_path / filename
                
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(text)
                
                return True, filename, ""
            except Exception as e:
                return False, "", f"PDF extraction failed: {str(e)}"
        else:
            # HTML page
            try:
                text = extract_text_from_html(response)
                filename = f"{index}.txt"
                full_path = dest_path / filename
                
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(text)
                
                return True, filename, ""
            except Exception as e:
                return False, "", f"HTML extraction failed: {str(e)}"
    
    except requests.RequestException as e:
        return False, "", f"Request failed: {str(e)}"
    except Exception as e:
        return False, "", f"Unexpected error: {str(e)}"
    finally:
        if close_session:
            session.close()

def main():
    parser = argparse.ArgumentParser(
        description="Download PDF and HTML documents from URLs and extract text content.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download and extract from URLs
  python utils/scraping.py --urls-file urls/canada_urls.txt --out data/canada
  
  # The script will:
  # - Download both PDFs and HTML pages
  # - Extract text from both formats
  # - Save as .txt files (1.txt, 2.txt, etc.)
  # - Skip files that already exist
  # - Use retry logic with exponential backoff for failed requests
        """
    )
    parser.add_argument(
        "--out",
        required=True,
        help="Destination folder to save extracted text files"
    )
    parser.add_argument(
        "--urls-file",
        required=True,
        help="Path to a text file with one URL per line"
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=3,
        help="Maximum number of retries for failed requests (default: 3)"
    )
    
    args = parser.parse_args()

    out_dir = Path(args.out).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    # Check dependencies
    if not HAS_BS4:
        print("⚠️  Warning: beautifulsoup4 not installed. HTML extraction will fail.")
        print("   Install with: pip install beautifulsoup4")
    
    if not HAS_PYPDF2:
        print("⚠️  Warning: PyPDF2 not installed. PDF extraction will fail.")
        print("   Install with: pip install PyPDF2")

    # Read URLs
    with open(args.urls_file, "r", encoding="utf-8") as f:
        urls = [
            line.strip()
            for line in f
            if line.strip() and not re.match(r"^(n/?a|none|null)$", line.strip(), flags=re.IGNORECASE)
        ]

    print(f"Processing {len(urls)} URLs...")
    print(f"Output directory: {out_dir}\n")

    # Create session with retry logic
    session = build_scraping_session(total_retries=args.max_retries)
    
    successful = 0
    failed = 0
    skipped = 0

    for idx, url in enumerate(urls, start=1):
        filename = f"{idx}.txt"
        full_path = out_dir / filename

        if full_path.exists():
            print(f"[{idx}] ✓ Already exists — skipped.")
            skipped += 1
            continue

        print(f"[{idx}] Fetching {url[:80]}...", end=" ")
        success, saved_filename, error = download_and_extract(url, out_dir, idx, session)
        
        if success:
            if full_path.exists():
                char_count = full_path.stat().st_size
                print(f"✓ Success ({char_count:,} bytes)")
            else:
                print(f"✓ Success")
            successful += 1
        else:
            print(f"✗ Failed: {error}")
            failed += 1

    session.close()

    # Summary
    print(f"\n✅ Download complete!")
    print(f"   - Successful: {successful}")
    print(f"   - Skipped (already exists): {skipped}")
    print(f"   - Failed: {failed}")
    print(f"   - Total: {len(urls)}")

if __name__ == "__main__":
    main()
