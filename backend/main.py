import json
import re
import traceback

import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from config import settings

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)

ALLOWED_ORIGINS = [
    "https://rs-startuplaunch.vercel.app",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

ANALYSIS_PROMPT = """\
You are an expert startup analyst. Analyze the following startup idea and return a JSON object with exactly these fields:

- "score": an integer 0-100 representing overall viability
- "verdict": one of "Promising", "Needs refinement", or "Underdeveloped"
- "market_size_estimate": a string like "$12B TAM" with a realistic market size estimate
- "competition_level": one of "Low", "Medium", or "High"
- "strengths": an array of exactly 3 concise strengths
- "risks": an array of exactly 3 concise risks
- "suggestions": an array of exactly 3 actionable suggestions

Return ONLY valid JSON, no markdown fences, no extra text.

Startup Idea: {idea}
Industry: {industry}
Target Audience: {audience}
Country: {country}
"""


class AnalyzeRequest(BaseModel):
    idea: str
    industry: str = ""
    target_audience: str = ""
    country: str = ""


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}


@app.post("/analyze")
async def analyze_idea(payload: AnalyzeRequest):
    prompt = ANALYSIS_PROMPT.format(
        idea=payload.idea,
        industry=payload.industry or "Not specified",
        audience=payload.target_audience or "Not specified",
        country=payload.country or "Not specified",
    )

    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": settings.OPENROUTER_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 1000,
                "temperature": 0.7,
            },
        )
        data = resp.json()
        if resp.status_code != 200:
            print(f"OpenRouter error {resp.status_code}: {data}")
            raise Exception(f"OpenRouter API error: {data.get('error', {}).get('message', data)}")

    raw = data["choices"][0]["message"]["content"].strip()

    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    try:
        analysis = json.loads(raw)
    except json.JSONDecodeError:
        print(f"Failed to parse LLM response: {raw}")
        return {
            "idea": payload.idea,
            "industry": payload.industry or "Not specified",
            "target_audience": payload.target_audience or "Not specified",
            "country": payload.country or "Not specified",
            "score": 0,
            "verdict": "Underdeveloped",
            "market_size_estimate": "N/A",
            "competition_level": "N/A",
            "strengths": [],
            "risks": ["Unable to parse AI response"],
            "suggestions": ["Please try again later"],
        }

    return {
        "idea": payload.idea,
        "industry": payload.industry or "Not specified",
        "target_audience": payload.target_audience or "Not specified",
        "country": payload.country or "Not specified",
        "score": int(analysis.get("score", 0)),
        "verdict": analysis.get("verdict", "Underdeveloped"),
        "market_size_estimate": analysis.get("market_size_estimate", "N/A"),
        "competition_level": analysis.get("competition_level", "N/A"),
        "strengths": analysis.get("strengths", []),
        "risks": analysis.get("risks", []),
        "suggestions": analysis.get("suggestions", []),
    }
