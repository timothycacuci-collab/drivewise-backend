from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict
from database import get_db, TestResult, User
from routers.auth import get_current_user
from routers.static_data import COUNTRIES_MAP, LANGUAGES_MAP
import anthropic
import uuid
import json
import os

router = APIRouter()
ai = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# In-memory session store (use Redis in production)
SESSIONS: Dict[str, dict] = {}

class GenerateRequest(BaseModel):
    country_code: str
    language_code: str
    num_questions: int = 10

class SubmitRequest(BaseModel):
    session_id: str
    answers: Dict[str, str]
    duration_seconds: int = 0

class TranslateRequest(BaseModel):
    session_id: str
    target_language: str

def generate_questions_with_ai(country: dict, language: dict, num_questions: int) -> list:
    lang_instruction = (
        f"Translate ALL questions and answer options into {language['name']} ({language['native']})."
        if language["code"] != "en"
        else "Write everything in English."
    )
    prompt = f"""You are a driving theory test question generator for {country['name']}.
{country['description']}

Generate exactly {num_questions} multiple-choice questions for the {country['name']} driving theory test.
{lang_instruction}

Return ONLY a valid JSON array. Each object must have:
- "id": unique string (q1, q2, etc.)
- "question": the question text
- "options": object with keys "A", "B", "C", "D" and translated option text
- "correct": the correct key ("A", "B", "C", or "D")
- "explanation": brief explanation in the same language
- "topic": short topic label (e.g. "Speed Limits", "Road Signs")

No markdown, no code fences, just the raw JSON array."""

    message = ai.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}]
    )
    text = message.content[0].text.strip()
    # Strip any accidental markdown fences
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    return json.loads(text)

@router.post("/generate")
def generate_test(body: GenerateRequest, user: User = Depends(get_current_user)):
    country = COUNTRIES_MAP.get(body.country_code)
    language = LANGUAGES_MAP.get(body.language_code)
    if not country:
        raise HTTPException(status_code=400, detail="Invalid country code")
    if not language:
        raise HTTPException(status_code=400, detail="Invalid language code")
    if body.num_questions not in [10, 15, 20]:
        raise HTTPException(status_code=400, detail="num_questions must be 10, 15, or 20")

    try:
        questions = generate_questions_with_ai(country, language, body.num_questions)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate questions: {str(e)}")

    session_id = str(uuid.uuid4())
    SESSIONS[session_id] = {
        "user_id": user.id,
        "country": country,
        "language": language,
        "questions": questions,
        "passing_score": country["passing_score"],
    }

    return {
        "session_id": session_id,
        "country": country,
        "language": language,
        "questions": questions,
        "passing_score": country["passing_score"],
    }

@router.post("/translate")
def translate_test(body: TranslateRequest, user: User = Depends(get_current_user)):
    session = SESSIONS.get(body.session_id)
    if not session or session["user_id"] != user.id:
        raise HTTPException(status_code=404, detail="Session not found")

    target_lang = LANGUAGES_MAP.get(body.target_language)
    if not target_lang:
        raise HTTPException(status_code=400, detail="Invalid language")

    questions = session["questions"]
    lang_name = target_lang["name"]

    prompt = f"""Translate these driving test questions into {lang_name}.
Keep the same JSON structure, same IDs, same correct answers.
Return ONLY the raw JSON array.

{json.dumps(questions)}"""

    message = ai.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}]
    )
    text = message.content[0].text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    translated = json.loads(text)
    return {"questions": translated}

@router.post("/submit")
def submit_test(body: SubmitRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    session = SESSIONS.get(body.session_id)
    if not session or session["user_id"] != user.id:
        raise HTTPException(status_code=404, detail="Session not found")

    questions = session["questions"]
    correct_count = 0
    review = []

    for q in questions:
        given = body.answers.get(q["id"])
        is_correct = given == q["correct"]
        if is_correct:
            correct_count += 1
        review.append({
            "id": q["id"],
            "question": q["question"],
            "options": q["options"],
            "correct": q["correct"],
            "given": given,
            "is_correct": is_correct,
            "explanation": q.get("explanation", ""),
            "topic": q.get("topic", ""),
        })

    total = len(questions)
    score_pct = round((correct_count / total) * 100) if total > 0 else 0
    passed = score_pct >= session["passing_score"]

    result_id = str(uuid.uuid4())
    result = TestResult(
        id=result_id,
        user_id=user.id,
        country_code=session["country"]["code"],
        language_code=session["language"]["code"],
        total=total,
        correct=correct_count,
        score_pct=score_pct,
        passed=passed,
        duration_seconds=body.duration_seconds,
        review=review,
    )
    db.add(result)
    db.commit()

    # Clean up session
    SESSIONS.pop(body.session_id, None)

    return {
        "result_id": result_id,
        "score_pct": score_pct,
        "correct": correct_count,
        "total": total,
        "passed": passed,
        "passing_score": session["passing_score"],
        "country": session["country"],
        "language": session["language"],
        "review": review,
    }

@router.get("/stats")
def get_stats(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    results = db.query(TestResult).filter(TestResult.user_id == user.id).all()
    if not results:
        return {"total_tests": 0, "best_score": 0, "avg_score": 0, "passed_count": 0}
    scores = [r.score_pct for r in results]
    return {
        "total_tests": len(results),
        "best_score": max(scores),
        "avg_score": round(sum(scores) / len(scores)),
        "passed_count": sum(1 for r in results if r.passed),
    }

@router.get("/history")
def get_history(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    results = db.query(TestResult).filter(TestResult.user_id == user.id).order_by(TestResult.created_at.desc()).limit(20).all()
    return [
        {
            "id": r.id,
            "country": COUNTRIES_MAP.get(r.country_code),
            "language": LANGUAGES_MAP.get(r.language_code),
            "total": r.total,
            "correct": r.correct,
            "score_pct": r.score_pct,
            "passed": r.passed,
            "created_at": r.created_at.isoformat(),
        }
        for r in results
    ]
