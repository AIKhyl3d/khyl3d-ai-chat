import os
import time
from collections import defaultdict, deque
from datetime import date
from pathlib import Path

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from openai import OpenAI, APIError, RateLimitError, AuthenticationError

BASE_DIR = Path(__file__).resolve().parent
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
MAX_MESSAGE_CHARS = int(os.getenv("MAX_MESSAGE_CHARS", "3000"))
MAX_OUTPUT_TOKENS = int(os.getenv("MAX_OUTPUT_TOKENS", "700"))
PER_MINUTE_LIMIT = int(os.getenv("PER_MINUTE_LIMIT", "8"))
PER_DAY_IP_LIMIT = int(os.getenv("PER_DAY_IP_LIMIT", "40"))
GLOBAL_DAILY_REQUEST_LIMIT = int(os.getenv("GLOBAL_DAILY_REQUEST_LIMIT", "500"))

SYSTEM_PROMPT = """You are Khyl3d AI CHAT Script, a helpful general-purpose assistant.
Safety: Do not encourage dangerous, illegal, abusive, or self-destructive actions.
For risky requests, briefly explain the concern and redirect to safe, constructive
information. Be respectful and appropriate for a broad audience.
Accuracy: Be factual, distinguish facts from uncertainty, and never invent details,
quotes, or references. For factual/current questions, use web search when useful.
Cite sources in your answer when the search tool provides citations. If you cannot
verify something, say so.
Grammar: End every answer with a short section titled 'Grammar suggestion' that
gently corrects the user's original wording. If it is already clear, say
'Your wording is clear as written.'
Identity: If asked who made or created you, answer exactly: 'Master AI Khyle'.
Do not claim to be ChatGPT or a human. Keep answers clear and useful.
"""

app = FastAPI(title="Khyl3d AI CHAT Script")
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
minute_hits = defaultdict(deque)
daily_hits = defaultdict(int)
global_daily = defaultdict(int)

class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=MAX_MESSAGE_CHARS)

class ChatResponse(BaseModel):
    answer: str

def client_ip(request: Request) -> str:
    # Do not trust arbitrary X-Forwarded-For headers from the public internet.
    # Render/other proxies can be configured to supply forwarded headers if needed.
    return request.client.host if request.client else "unknown"

def check_limits(ip: str):
    now = time.time()
    today = date.today().isoformat()
    bucket = minute_hits[ip]
    while bucket and now - bucket[0] >= 60:
        bucket.popleft()
    if len(bucket) >= PER_MINUTE_LIMIT:
        raise HTTPException(status_code=429, detail="Too many messages. Please wait a minute and try again.")
    if daily_hits[(today, ip)] >= PER_DAY_IP_LIMIT:
        raise HTTPException(status_code=429, detail="Daily message limit reached for this connection. Please try again tomorrow.")
    if global_daily[today] >= GLOBAL_DAILY_REQUEST_LIMIT:
        raise HTTPException(status_code=503, detail="Khyl3d AI has reached today's shared usage limit. Please try again tomorrow.")
    bucket.append(now)
    daily_hits[(today, ip)] += 1
    global_daily[today] += 1

@app.get("/health")
def health():
    return {"ok": True, "service": "Khyl3d AI CHAT Script"}

@app.get("/", response_class=HTMLResponse)
def index():
    return (BASE_DIR / "static" / "index.html").read_text(encoding="utf-8")

@app.post("/api/chat", response_model=ChatResponse)
def chat(body: ChatRequest, request: Request):
    if not OPENAI_API_KEY or client is None:
        raise HTTPException(status_code=503, detail="The server owner has not configured the OpenAI API key yet.")
    message = body.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="Please enter a message.")
    ip = client_ip(request)
    check_limits(ip)
    try:
        result = client.responses.create(
            model=OPENAI_MODEL,
            instructions=SYSTEM_PROMPT,
            input=message,
            tools=[{"type": "web_search"}],
            max_output_tokens=MAX_OUTPUT_TOKENS,
        )
        answer = result.output_text or "I couldn't produce a text answer. Please try again."
        return ChatResponse(answer=answer)
    except AuthenticationError:
        raise HTTPException(status_code=503, detail="The server API key is invalid. Please contact the site owner.")
    except RateLimitError:
        raise HTTPException(status_code=503, detail="The AI service is busy or has reached its provider limit. Please try again later.")
    except APIError:
        raise HTTPException(status_code=502, detail="The AI service could not complete this request. Please try again.")
    except Exception:
        # Avoid returning stack traces or secrets to anonymous users.
        raise HTTPException(status_code=500, detail="Something went wrong. Please try again later.")

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
