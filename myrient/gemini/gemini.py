import requests
from bs4 import BeautifulSoup
import re
import sys

# REGEX to match (USA) or (USA, *) more precisely
USA_REGION_PATTERN = re.compile(r'\(USA[,)]', re.IGNORECASE)

# FINAL CORRECTED EXCLUSION PATTERN:
EXCLUSION_PATTERN = re.compile(
    r'\((?:Proto|Alpha|Beta|Sample|Demo|Kiosk|Unreleased|Alt|Anthology)\s*\d*\)|\bBIOS\b',
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
            return sum(float(x) / (100**i) for i, x in enumerate(rev_str.split('.')))
    return 0.0

def is_usa_preferred(filename):
    # NOW uses the dedicated regex pattern for greater precision
    return bool(USA_REGION_PATTERN.search(filename))

def is_world_preferred(filename):
    return '(World)' in filename and not is_usa_preferred(filename)

def compare_files(current_best, new_candidate):
    is_best_usa = is_usa_preferred(current_best)
    is_new_usa = is_usa_preferred(new_candidate)
    
    # Priority 1: USA-preferred version
    if is_new_usa and not is_best_usa:
        return new_candidate
    if is_best_usa and not is_new_usa:
        return current_best

    # Priority 2: World-preferred version (only checked if neither is USA-preferred)
    is_best_world = is_world_preferred(current_best)
    is_new_world = is_world_preferred(new_candidate)

    if not is_best_usa and not is_new_usa:
        if is_new_world and not is_best_world:
            return new_candidate
        if is_best_world and not is_new_world:
            return current_best

    # Priority 3: Revision
    if (is_best_usa == is_new_usa) and (is_best_world == is_new_world):
        best_rev = get_revision_value(current_best)
        new_rev = get_revision_value(new_candidate)

        if new_rev > best_rev:
            return new_candidate
        elif new_rev < best_rev:
            return current_best
        else:
            # Priority 4: NTSC vs PAL tie-breaker
            is_best_ntsc = 'NTSC' in current_best.upper()
            is_new_ntsc = 'NTSC' in new_candidate.upper()
            is_best_pal = 'PAL' in current_best.upper()
            is_new_pal = 'PAL' in new_candidate.upper()
            
            if is_new_ntsc and is_best_pal and not is_best_ntsc:
                return new_candidate
            if is_best_ntsc and is_new_pal and not is_new_ntsc:
                return current_best
            
            # FINAL Tie-breaker: If all previous criteria are equal, keep the existing best file.
            return current_best
    
    return current_best

def get_normalized_title(filename):
    """Robustly extracts the game title for grouping and comparison."""
    title_match = TITLE_EXTRACTION_PATTERN.search(filename)
    if title_match:
        return title_match.group(1).strip().lower()
    
    try:
        title_part = filename.split('(')[0]
        if title_part.endswith('.zip'):
            title_part = title_part[:-4]
        return title_part.strip().lower()
    except:
        return filename.split('.zip')[0].strip().lower()


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

        # 1. EXCLUSION CHECK
        if EXCLUSION_PATTERN.search(filename):
            continue
            
        # 2. INCLUSION CHECK: Must contain (USA) or (World).
        if not (is_usa_preferred(filename) or is_world_preferred(filename)):
            continue

        normalized_title = get_normalized_title(filename)

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
        print("Error: Please provide at least one target URL as a command-line argument.")
        print(f"Usage: python {sys.argv[0]} <URL_1> [URL_2] [URL_N...]")
        sys.exit(1)

    target_urls = sys.argv[1:]
    all_best_games = {}


    for url in target_urls:
        current_list = fetch_and_filter_file_list(url)

        for filename in current_list:
            
            if EXCLUSION_PATTERN.search(filename):
                continue
            
            normalized_title = get_normalized_title(filename)

            if not normalized_title:
                continue

            if normalized_title in all_best_games:
                current_best_filename = all_best_games[normalized_title]

                updated_best = compare_files(current_best_filename, filename)
                all_best_games[normalized_title] = updated_best
            else:
                all_best_games[normalized_title] = filename

    final_list = list(all_best_games.values())
    final_list.sort()

    for item in final_list:
        print(f"+ {item}")
    print('- *')

