import re

def replace_characters(text: str) -> str:
    """Replace specific characters according to transliteration rules"""
    replacements = {
        "sz": "š",
        "s,": "ṣ",
        "t,": "ṭ",
        "h": "ḫ"
    }
    pattern = re.compile('|'.join(re.escape(k) for k in replacements))
    text = pattern.sub(lambda m: replacements[m.group(0)], text)
    
    return re.sub(r'_(.*?)_', lambda m: m.group(1).upper(), text)

def extract_cleaned_transliteration(raw_atf: str) -> str:
    """Extract and clean transliteration from raw ATF data"""
    if not raw_atf:
        return None

    cleaned_lines = []
    for line in raw_atf.splitlines():
        stripped_line = line.strip()
        
        if any(stripped_line.startswith(prefix) for prefix in ["#tr.", "\u0026P", "#"]):
            continue

        cleaned_line = replace_characters(stripped_line)
        cleaned_lines.append(cleaned_line)

    return "\n".join(cleaned_lines) if cleaned_lines else None

def extract_existing_translation(raw_atf: str) -> str:
    """Extract existing translations from raw ATF data"""
    if not raw_atf:
        return None

    translation_lines = []
    raw_atf_lines = raw_atf.splitlines()
    nearest_prefix = None

    for i, line in enumerate(raw_atf_lines):
        stripped_line = line.strip()

        if stripped_line.startswith("#tr.") and not stripped_line.startswith("#tr.ts:"):
            nearest_prefix = find_nearest_prefix(raw_atf_lines, i)
            if nearest_prefix:
                cleaned_translation = stripped_line.split(":", 1)[1].strip()
                translation_lines.append(f"{nearest_prefix} {cleaned_translation}")

    return "\n".join(translation_lines) if translation_lines else None

def find_nearest_prefix(lines: list, current_index: int) -> str:
    """Find the nearest non-comment prefix in previous lines"""
    for i in range(current_index - 1, -1, -1):
        if not lines[i].strip().startswith("#"):
            return re.split(r'\s+', lines[i].strip())[0]
    return None
