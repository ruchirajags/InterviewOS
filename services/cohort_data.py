import json
from functools import lru_cache
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"

@lru_cache(maxsize=1)
def load_curriculum():
    with open(DATA_DIR / "curriculum.json", "r", encoding="utf-8") as f:
        return json.load(f)

@lru_cache(maxsize=1)
def load_candidates():
    with open(DATA_DIR / "candidates.json", "r", encoding="utf-8") as f:
        payload = json.load(f)
    return payload.get("candidates", payload)

def curriculum_days():
    return load_curriculum().get("days", [])

def curriculum_day_map():
    return {item.get("day"): item for item in curriculum_days()}

def module_for_day(day):
    for module in load_curriculum().get("modules", []):
        start, end = module.get("days", [None, None])
        if start is not None and end is not None and start <= day <= end:
            return module.get("title", "AI Engineering")
    return "AI Engineering"

def find_candidate(candidate_id):
    for candidate in load_candidates():
        if candidate.get("member", {}).get("id") == candidate_id:
            return candidate
    return None
