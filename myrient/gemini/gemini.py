import re
import sys
from urllib.parse import unquote
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional, Tuple, Union

class FileSelector:
    USA_REGION_PATTERN = re.compile(r'[\[\(][^\]\)]*USA[^\]\)]*[\]\)]', re.IGNORECASE)
    REVISION_EXTRACTION_PATTERN = re.compile(r'\((?:Rev|V|)\s*([\d\.]+[a-z]?)\)', re.IGNORECASE)
    DATE_EXTRACTION_PATTERN = re.compile(r'\(\s*(\d{4}-\d{2}-\d{2})\s*\)', re.IGNORECASE)
    TITLE_EXTRACTION_PATTERN = re.compile(r'(.+?)\s*(?:\[|\(|{)', re.IGNORECASE)
    LANGUAGE_PATTERN = re.compile(r'[\[\(][^\]\)]*En[^\]\)]*[\]\)]', re.IGNORECASE)
    DISC_EXTRACTION_PATTERN = re.compile(r'(\(\s*Disc\s+\d+\s*\))|(\(\s*Part\s+\d+\s*\))|(\(\s*\d+\s+of\s+\d+\s*\))', re.IGNORECASE)

    EXCLUSION_KEYWORDS = [
        'Alpha', 'Alt', 'Anthology', 'Arcade', 'Beta', 'Capcom Town', 'Channel', 'Classics',
        'Collection', 'Console', 'Debug', 'Demo', 'Digital', 'e-Reader', 'Evercade',
        'GameCube', 'Kiosk', 'Limited', 'LodgeNet', 'Mini', 'Program', 'Proto', 'R.C.', 'Retro-Bit', 'Sample', 'Switch', 'Virtual'
    ]
    STANDALONE_EXCLUSION_KEYWORDS = [
        r'\bBIOS\b'
    ]

    _keywords_or_group = '|'.join(EXCLUSION_KEYWORDS)
    _parenthetical_pattern = r'\(' + r'.*' + r'(?:' + _keywords_or_group + r')' + r'.*' + r'\)'
    _final_regex_string_inner = '|'.join([_parenthetical_pattern] + STANDALONE_EXCLUSION_KEYWORDS)
    EXCLUSION_PATTERN = re.compile(_final_regex_string_inner, re.IGNORECASE)

    def _get_disc_tag(self, filename: str) -> str:
        """Extracts the Disc/Part tag, or returns 'SINGLE' if none is found."""
        match = self.DISC_EXTRACTION_PATTERN.search(filename)
        if match:
            return match.group(0)
        return 'SINGLE'

    def _get_revision_value(self, filename: str) -> Tuple[float, float]:
        date_value = 0.0
        date_match = self.DATE_EXTRACTION_PATTERN.search(filename)
        if date_match:
            date_str = date_match.group(1).replace('-', '')
            try:
                date_value = float(date_str)
            except ValueError:
                pass

        rev_value = 0.0
        match = self.REVISION_EXTRACTION_PATTERN.search(filename)
        if match:
            rev_str = match.group(1)

            try:
                parts = rev_str.split('.')

                base_number_str = parts[0]
                decimal_part_str = ""

                if len(parts) > 1:
                    decimal_part_str = "".join(parts[1:])

                trailing_letter_value = 0
                if decimal_part_str and decimal_part_str[-1].isalpha():
                    trailing_letter = decimal_part_str[-1]
                    trailing_letter_value = (ord(trailing_letter.lower()) - ord('a') + 1) * 0.00001
                    decimal_part_str = decimal_part_str[:-1]


                if decimal_part_str:
                    rev_value = float(f"{base_number_str}.{decimal_part_str}") + trailing_letter_value
                else:
                    rev_value = float(base_number_str) + trailing_letter_value

            except ValueError:
                pass

        return (date_value, rev_value)

    def _get_comparison_tuple(self, filename: str) -> Tuple[int, int, float, float, int, int]:
        filename_upper = filename.upper()

        is_usa = bool(self.USA_REGION_PATTERN.search(filename))
        is_world = '(WORLD)' in filename_upper and not is_usa

        region_preference = 0
        if is_usa:
            region_preference = 2
        elif is_world:
            region_preference = 1

        is_english = bool(self.LANGUAGE_PATTERN.search(filename))
        language_preference = 1 if is_english else 0

        date_value, rev_value = self._get_revision_value(filename)

        is_ntsc = 'NTSC' in filename_upper
        ntsc_preference = 1 if is_ntsc else 0

        is_pal = 'PAL' in filename_upper
        pal_preference = 1 if is_pal else 0

        return (region_preference, language_preference, date_value, rev_value, ntsc_preference, -pal_preference)


    def compare_files(self, current_best: str, new_candidate: str) -> str:
        best_tuple = self._get_comparison_tuple(current_best)
        new_tuple = self._get_comparison_tuple(new_candidate)

        if new_tuple > best_tuple:
            return new_candidate
        return current_best

    def get_normalized_title(self, filename: str) -> Optional[str]:
        temp_filename = self.DISC_EXTRACTION_PATTERN.sub('', filename).strip()

        title_match = self.TITLE_EXTRACTION_PATTERN.search(temp_filename)
        if title_match:
            return title_match.group(1).strip().lower()

        try:
            title_part = temp_filename.split('(')[0].split('[')[0].split('{')[0]
            if title_part.lower().endswith('.zip'):
                title_part = title_part[:-4]
            return title_part.strip().lower()
        except Exception:
            return temp_filename.split('.zip')[0].strip().lower()


    def fetch_and_filter_file_list(self, url: str) -> Dict[str, Dict[str, str]]:
        best_games: Dict[str, Dict[str, str]] = {}

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
        except requests.RequestException:
            return {}

        soup = BeautifulSoup(response.content, 'html.parser')

        for link in soup.find_all('a'):
            filename = link.get('href')
            if not filename or filename.endswith('/'):
                continue

            filename = unquote(filename)

            if self.EXCLUSION_PATTERN.search(filename):
                continue

            if not (self.USA_REGION_PATTERN.search(filename) or '(World)' in filename):
                continue

            normalized_title = self.get_normalized_title(filename)

            if not normalized_title:
                continue

            disc_tag = self._get_disc_tag(filename)

            if normalized_title not in best_games:
                best_games[normalized_title] = {disc_tag: filename}
            else:
                current_disc_set = best_games[normalized_title]
                if disc_tag in current_disc_set:
                    current_best_filename = current_disc_set[disc_tag]
                    updated_best = self.compare_files(current_best_filename, filename)
                    current_disc_set[disc_tag] = updated_best
                else:
                    current_disc_set[disc_tag] = filename

        return best_games

    def run(self, target_urls: List[str]) -> List[str]:
        all_best_games: Dict[str, Dict[str, str]] = {}

        for url in target_urls:
            current_best_dict = self.fetch_and_filter_file_list(url)

            for normalized_title, disc_set in current_best_dict.items():
                if normalized_title not in all_best_games:
                    all_best_games[normalized_title] = disc_set
                else:
                    overall_disc_set = all_best_games[normalized_title]
                    for disc_tag, filename in disc_set.items():
                        if disc_tag in overall_disc_set:
                            current_overall_best = overall_disc_set[disc_tag]
                            updated_best = self.compare_files(current_overall_best, filename)
                            overall_disc_set[disc_tag] = updated_best
                        else:
                            overall_disc_set[disc_tag] = filename

        final_list = []
        for disc_set in all_best_games.values():
            final_list.extend(disc_set.values())

        final_list.sort()
        return final_list


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(1)

    try:
        selector = FileSelector()
        best_files = selector.run(sys.argv[1:])

        for item in best_files:
            print(f"+ {item}")

        print('- *')

    except Exception:
        sys.exit(1)
