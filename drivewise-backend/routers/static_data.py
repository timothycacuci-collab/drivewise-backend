from fastapi import APIRouter

router = APIRouter()

COUNTRIES = [
    {"code": "US", "name": "United States", "flag": "🇺🇸", "description": "DMV-style permit & licence test questions covering federal road rules.", "passing_score": 80},
    {"code": "UK", "name": "United Kingdom", "flag": "🇬🇧", "description": "DVSA Theory Test format – UK Highway Code, road signs, hazard awareness.", "passing_score": 86},
    {"code": "CA", "name": "Canada", "flag": "🇨🇦", "description": "Provincial driver's licence (G1/Class 7) – Canadian road signs & rules.", "passing_score": 80},
    {"code": "DE", "name": "Germany", "flag": "🇩🇪", "description": "Führerschein Theorieprüfung – German road rules, signs, autobahn etiquette.", "passing_score": 90},
    {"code": "RO", "name": "Romania", "flag": "🇷🇴", "description": "Permis auto categoria B – Romanian highway code and traffic regulations.", "passing_score": 85},
]

LANGUAGES = [
    {"code": "en", "name": "English", "native": "English", "rtl": False},
    {"code": "ro", "name": "Romanian", "native": "Română", "rtl": False},
    {"code": "es", "name": "Spanish", "native": "Español", "rtl": False},
    {"code": "fr", "name": "French", "native": "Français", "rtl": False},
    {"code": "de", "name": "German", "native": "Deutsch", "rtl": False},
    {"code": "zh", "name": "Chinese", "native": "中文", "rtl": False},
    {"code": "ar", "name": "Arabic", "native": "العربية", "rtl": True},
    {"code": "hi", "name": "Hindi", "native": "हिन्दी", "rtl": False},
    {"code": "pt", "name": "Portuguese", "native": "Português", "rtl": False},
    {"code": "ru", "name": "Russian", "native": "Русский", "rtl": False},
    {"code": "ja", "name": "Japanese", "native": "日本語", "rtl": False},
    {"code": "ko", "name": "Korean", "native": "한국어", "rtl": False},
]

COUNTRIES_MAP = {c["code"]: c for c in COUNTRIES}
LANGUAGES_MAP = {l["code"]: l for l in LANGUAGES}

@router.get("/countries")
def get_countries():
    return COUNTRIES

@router.get("/languages")
def get_languages():
    return LANGUAGES
