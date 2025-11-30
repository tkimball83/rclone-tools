#!/usr/bin/env python

import requests
from bs4 import BeautifulSoup
import re
from typing import List, Optional
import sys

EXCLUSION_PATTERN = re.compile(
    r'\((?:Proto|Alpha|Beta|Sample|Demo|Kiosk|Unreleased)\)',
    re.IGNORECASE
)

TITLE_EXTRACTION_PATTERN = re.compile(
    r'(.+?)\s*(?:\[|\(|{)',
    re.IGNORECASE
)

REVISION_EXTRACTION_PATTERN = re.compile(
    r'\((?:Rev|V)\s*([\d\.]+)\)',
    re.IGNORECASE
)

def get_revision_value(filename):
    match = REVISION_EXTRACTION_PATTERN.search(filename)
    if match:
        rev_str = match.group(1)
        try:
            return float(rev_str)
        except ValueError:
            return 0.0
    return 0.0

def compare_files(current_best, new_candidate):
    is_best_usa = '(USA)' in current_best
    is_new_usa = '(USA)' in new_candidate
    is_best_world = '(World)' in current_best
    is_new_world = '(World)' in new_candidate

    if is_best_usa and not is_new_usa:
        return current_best
    if is_new_usa and not is_best_usa:
        return new_candidate

    if is_best_usa == is_new_usa and is_best_world == is_new_world:
        best_rev = get_revision_value(current_best)
        new_rev = get_revision_value(new_candidate)

        if new_rev > best_rev:
            return new_candidate
        elif new_rev < best_rev:
            return current_best
        else:
            return current_best if len(current_best) < len(new_candidate) else new_candidate

    return current_best

def fetch_and_filter_file_list(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        return []

    soup = BeautifulSoup(response.content, 'html.parser')

    best_games = {}

    for link in soup.find_all('a'):
        filename = link.get('href')
        if not filename:
            continue

        if filename.endswith('/') or filename in ('../', 'index.html'):
            continue

        filename = requests.utils.unquote(filename)

        if EXCLUSION_PATTERN.search(filename):
            continue

        if '(USA)' not in filename and '(World)' not in filename:
            continue

        title_match = TITLE_EXTRACTION_PATTERN.search(filename)

        # Rewritten from a single-line conditional assignment to a standard if/else block
        if title_match:
            normalized_title = title_match.group(1).strip().lower()
        else:
            normalized_title = filename.split('(')[0].strip().lower()

        if not normalized_title:
            continue

        if normalized_title in best_games:
            current_best_filename = best_games[normalized_title]

            updated_best = compare_files(current_best_filename, filename)
            best_games[normalized_title] = updated_best
        else:
            best_games[normalized_title] = filename

    final_list = list(best_games.values())
    final_list.sort()
    return final_list

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: Please provide the target URL as a command-line argument.")
        print(f"Usage: python {sys.argv[0]} <URL>")
        sys.exit(1)

    target_url = sys.argv[1]

    cleaned_list = fetch_and_filter_file_list(target_url)

    if cleaned_list:
        for item in cleaned_list:
            print(f"+ {item}")
        print('- *')
