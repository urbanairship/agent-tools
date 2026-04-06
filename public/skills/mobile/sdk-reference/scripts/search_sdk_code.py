#!/usr/bin/env python3
"""Search Airship SDK sample app code for implementation examples.

This script fetches and searches official Airship SDK sample apps from GitHub.
Results are cached for 24 hours to respect GitHub rate limits.

Usage:
    python search_sdk_code.py --platform ios --query "push notification handler"
    python search_sdk_code.py -p android -q "message center"
    python search_sdk_code.py -p flutter -q "preference center" --max-results 10
"""

import argparse
import httpx
import json
import re
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

GITHUB_API = "https://api.github.com"

# Official Airship SDK repositories
SDK_REPOS = {
    "ios": "urbanairship/ios-library",
    "android": "urbanairship/android-library",
    "flutter": "urbanairship/airship-flutter",
    "react-native": "urbanairship/react-native-airship",
    "capacitor": "urbanairship/capacitor-airship",
    "cordova": "urbanairship/urbanairship-cordova",
    "dotnet": "urbanairship/airship-dotnet",
}

# Sample app paths within each repo
SAMPLE_APP_PATHS = {
    "ios": ["Documentation/Sample/", "Sample/"],
    "android": ["sample/", "urbanairship-sample/"],
    "flutter": ["example/"],
    "react-native": ["example/"],
    "capacitor": ["example/"],
    "cordova": ["Example/"],
    "dotnet": ["Sample/"],
}

# Code file extensions to fetch
CODE_EXTENSIONS = {".swift", ".kt", ".java", ".dart", ".ts", ".tsx", ".js", ".jsx", ".m", ".h", ".cs"}

# Cache directory (relative to this script)
CACHE_DIR = Path(__file__).parent.parent / "cache"
CACHE_TTL_HOURS = 24


def get_cache_path(platform: str) -> Path:
    """Get the cache file path for a platform."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return CACHE_DIR / f"{platform}_sample.json"


def get_cached_files(platform: str) -> Optional[Dict[str, str]]:
    """Get cached sample app files if not expired."""
    cache_file = get_cache_path(platform)
    if not cache_file.exists():
        return None

    try:
        data = json.loads(cache_file.read_text())
        cached_at = datetime.fromisoformat(data["cached_at"])
        if datetime.utcnow() - cached_at > timedelta(hours=CACHE_TTL_HOURS):
            return None
        return data["files"]
    except Exception:
        return None


def save_to_cache(platform: str, files: Dict[str, str]) -> None:
    """Save files to cache with timestamp."""
    cache_file = get_cache_path(platform)
    data = {
        "cached_at": datetime.utcnow().isoformat(),
        "files": files
    }
    cache_file.write_text(json.dumps(data))


def is_code_file(name: str) -> bool:
    """Check if file is a code file worth indexing."""
    return any(name.endswith(ext) for ext in CODE_EXTENSIONS)


def fetch_directory(client: httpx.Client, repo: str, path: str, max_files: int = 50) -> Dict[str, str]:
    """Fetch all code files in a directory recursively."""
    files = {}

    url = f"{GITHUB_API}/repos/{repo}/contents/{path}"
    headers = {"Accept": "application/vnd.github.v3+json"}

    try:
        resp = client.get(url, headers=headers)
        resp.raise_for_status()
        contents = resp.json()
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return files
        raise

    if not isinstance(contents, list):
        return files

    for item in contents:
        if len(files) >= max_files:
            break

        if item["type"] == "file" and is_code_file(item["name"]):
            try:
                file_resp = client.get(item["download_url"])
                if file_resp.status_code == 200:
                    files[item["path"]] = file_resp.text
            except Exception as e:
                print(f"Warning: Failed to fetch {item['path']}: {e}", file=sys.stderr)

        elif item["type"] == "dir" and len(files) < max_files:
            try:
                subfiles = fetch_directory(client, repo, item["path"], max_files - len(files))
                files.update(subfiles)
            except Exception as e:
                print(f"Warning: Failed to fetch directory {item['path']}: {e}", file=sys.stderr)

    return files


def fetch_sample_app(platform: str) -> Dict[str, str]:
    """Fetch sample app files for a platform (with caching)."""
    repo = SDK_REPOS.get(platform)
    if not repo:
        raise ValueError(f"Unknown platform: {platform}. Supported: {list(SDK_REPOS.keys())}")

    # Check cache first
    cached = get_cached_files(platform)
    if cached:
        print(f"Using cached sample app for {platform} ({len(cached)} files)", file=sys.stderr)
        return cached

    print(f"Fetching sample app from GitHub for {platform}...", file=sys.stderr)

    sample_paths = SAMPLE_APP_PATHS.get(platform, ["sample/"])
    files = {}

    with httpx.Client(timeout=30.0, follow_redirects=True) as client:
        for sample_dir in sample_paths:
            try:
                fetched = fetch_directory(client, repo, sample_dir)
                files.update(fetched)
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    continue
                raise

    if files:
        save_to_cache(platform, files)
        print(f"Cached {len(files)} files for {platform}", file=sys.stderr)

    return files


def search_files(files: Dict[str, str], query: str, max_results: int = 5, context_lines: int = 3) -> List[Dict]:
    """Search files for query terms and extract snippets."""
    terms = query.lower().split()
    results = []

    for file_path, content in files.items():
        content_lower = content.lower()

        # Count matches
        match_count = sum(content_lower.count(term) for term in terms)
        if match_count == 0:
            continue

        # Extract snippet around first match
        snippet = extract_snippet(content, terms, context_lines)

        # Build GitHub URL
        platform = None
        for p, repo in SDK_REPOS.items():
            if repo.split("/")[1] in file_path or p in file_path.lower():
                platform = p
                break

        repo = SDK_REPOS.get(platform, "urbanairship/ios-library")
        github_url = f"https://github.com/{repo}/blob/main/{file_path}"

        results.append({
            "file_path": file_path,
            "github_url": github_url,
            "match_count": match_count,
            "snippet": snippet[:2000]  # Limit snippet size
        })

    # Sort by match count descending
    results.sort(key=lambda x: x["match_count"], reverse=True)

    return results[:max_results]


def extract_snippet(content: str, terms: List[str], context_lines: int = 3) -> str:
    """Extract a code snippet around the first match."""
    lines = content.split("\n")
    content_lower = content.lower()

    # Find first matching line
    first_match_line = None
    for i, line in enumerate(lines):
        line_lower = line.lower()
        if any(term in line_lower for term in terms):
            first_match_line = i
            break

    if first_match_line is None:
        return ""

    # Extract context
    start = max(0, first_match_line - context_lines)
    end = min(len(lines), first_match_line + context_lines + 1)

    snippet_lines = lines[start:end]
    return "\n".join(snippet_lines)


def main():
    parser = argparse.ArgumentParser(
        description="Search Airship SDK sample app code for implementation examples."
    )
    parser.add_argument(
        "-p", "--platform",
        required=True,
        choices=list(SDK_REPOS.keys()),
        help="Platform to search (ios, android, flutter, react-native, capacitor, cordova, dotnet)"
    )
    parser.add_argument(
        "-q", "--query",
        required=True,
        help="Search query (e.g., 'push notification handler')"
    )
    parser.add_argument(
        "--max-results",
        type=int,
        default=5,
        help="Maximum number of results to return (default: 5)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )

    args = parser.parse_args()

    try:
        files = fetch_sample_app(args.platform)

        if not files:
            print(f"No sample app files found for {args.platform}", file=sys.stderr)
            sys.exit(1)

        results = search_files(files, args.query, args.max_results)

        if args.json:
            output = {
                "platform": args.platform,
                "query": args.query,
                "repo": f"https://github.com/{SDK_REPOS[args.platform]}",
                "result_count": len(results),
                "results": results
            }
            print(json.dumps(output, indent=2))
        else:
            if not results:
                print(f"No results found for '{args.query}' in {args.platform} sample app")
                sys.exit(0)

            print(f"\n{'='*60}")
            print(f"Search Results: '{args.query}' in {args.platform}")
            print(f"Repository: https://github.com/{SDK_REPOS[args.platform]}")
            print(f"{'='*60}\n")

            for i, result in enumerate(results, 1):
                print(f"[{i}] {result['file_path']} ({result['match_count']} matches)")
                print(f"    {result['github_url']}")
                print()
                if result['snippet']:
                    for line in result['snippet'].split('\n'):
                        print(f"    {line}")
                print()
                print("-" * 60)
                print()

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
