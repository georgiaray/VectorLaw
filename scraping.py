#!/usr/bin/env python3
import os
import re
import argparse
from pathlib import Path
from urllib.parse import urlparse, unquote
import requests

def sanitize_filename(name: str) -> str:
    return re.sub(r'[\\/:*?"<>|]+', "_", name).strip()

def infer_filename(url: str, headers: dict) -> str:
    # Try from headers first
    cd = headers.get("Content-Disposition", "")
    match = re.search(r'filename="?([^";]+)"?', cd)
    if match:
        return sanitize_filename(unquote(match.group(1)))
    # Fallback to URL path
    path = urlparse(url).path
    name = os.path.basename(path) or "document.pdf"
    if not name.lower().endswith(".pdf"):
        name += ".pdf"
    return sanitize_filename(name)


def download_pdf(url: str, dest_path: Path, index: int) -> bool:
    try:
        resp = requests.get(
            url,
            stream=True,
            timeout=30,
            allow_redirects=True,
            headers={"User-Agent": "pdf-fetcher/1.0"},
        )
        if not resp.ok:
            return False
        content_type = resp.headers.get("Content-Type", "").lower()
        if "application/pdf" not in content_type and "application/x-pdf" not in content_type:
            return False

        filename = f"{index}.pdf"
        full_path = dest_path / filename

        with open(full_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        return True
    except requests.RequestException:
        return False

def main():
    parser = argparse.ArgumentParser(description="Download only PDF URLs to a folder, preserving queue order and skipping existing files.")
    parser.add_argument("--out", required=True, help="Destination folder to save PDFs.")
    parser.add_argument("--urls-file", required=True, help="Path to a text file with one URL per line.")
    args = parser.parse_args()

    out_dir = Path(args.out).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    with open(args.urls_file, "r", encoding="utf-8") as f:
        urls = [
            line.strip()
            for line in f
            if line.strip() and not re.match(r"^(n/?a|none|null)$", line.strip(), flags=re.IGNORECASE)
        ]

    for idx, url in enumerate(urls, start=1):
        filename = f"{idx}.pdf"
        full_path = out_dir / filename

        if full_path.exists():
            print(f"{idx} already exists — skipped.")
            continue

        success = download_pdf(url, out_dir, idx)
        if success:
            print(f"{idx} was saved successfully.")
        else:
            print(f"{idx} was skipped (not a PDF or request failed).")

if __name__ == "__main__":
    main()
