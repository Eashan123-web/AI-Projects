
import json
import re
from pathlib import Path

# Locate configuration files
BASE_DIR = Path(__file__).resolve().parents[1]

SKILLS_FILE = BASE_DIR / "data" / "skills.json"
SKILL_ALIASES_FILE = BASE_DIR / "data" / "skill_aliases.json"

def load_json_file(file_path: Path):
    """Load JSON configuration safely."""

    if not file_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {file_path.name}")

    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def load_skills():
    """Load skill categories and their configured skills."""

    skills = load_json_file(SKILLS_FILE)

    if not isinstance(skills, dict):
        raise ValueError("Invalid skills configuration.")

    return skills

def load_skill_aliases():
    """Load skill aliases and synonyms."""

    if not SKILL_ALIASES_FILE.exists():
        return {}

    aliases = load_json_file(SKILL_ALIASES_FILE)

    if not isinstance(aliases, dict):
        raise ValueError("Invalid skill aliases configuration.")

    return aliases

def normalize_text(text: str):
    """Normalize text for consistent skill comparison."""

    return re.sub(r"\s+", " ", text.casefold()).strip()

def build_skill_pattern(skill: str):
    """Build a case-insensitive pattern that matches complete skill terms."""

    escaped_skill = re.escape(skill.strip())

    return re.compile(r"(?<!\w)" + escaped_skill + r"(?!\w)", re.IGNORECASE)

def extract_skills(text: str):
    """Extract technical skills using:
    1. Exact keyword matching.
    2. Alias recognition.
    3. Skill normalization.
    4. Duplicate prevention.
    Returns the existing category-wise dictionary format."""

    if not isinstance(text, str) or not text.strip():
        return {}

    skill_categories = load_skills()
    skill_aliases = load_skill_aliases()

    normalized_text = normalize_text(text)

    extracted_skills = {}

    for category, skills in skill_categories.items():

        if not isinstance(skills, list):
            continue

        category_aliases = skill_aliases.get(category, {})

        if not isinstance(category_aliases, dict):
            category_aliases = {}

        matched_skills = []
        seen_skills = set()

        # Identify aliases that represent existing canonical skills.
        alias_names = {
            normalize_text(alias)
            for aliases in category_aliases.values()
            if isinstance(aliases, list)
            for alias in aliases
        }

        for skill in skills:

            if not isinstance(skill, str):
                continue

            canonical_skill = skill.strip()

            if not canonical_skill:
                continue

            normalized_skill = normalize_text(
                canonical_skill
            )

            # Avoid duplicate entries such as NLP
            
            if normalized_skill in alias_names:
                continue

            if normalized_skill in seen_skills:
                continue

            # Exact skill matching.
            patterns = [build_skill_pattern(canonical_skill)]

            # Add configured synonyms.
            aliases = category_aliases.get(canonical_skill, [])

            if isinstance(aliases, list):

                for alias in aliases:

                    if isinstance(alias, str) and alias.strip():
                        patterns.append(build_skill_pattern(alias))

            # Check canonical skill and its aliases.
            if any(
                pattern.search(normalized_text)
                for pattern in patterns):

                matched_skills.append(canonical_skill)
                seen_skills.add(normalized_skill)

        if matched_skills:
            extracted_skills[category] = matched_skills

    return extracted_skills