import os
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

import store
from rank import rank

load_dotenv()

VALID_KINDS = {"internship", "hackathon", "scholarship"}

app = FastAPI(title="CampusCopilot API", version="1.0.0")

# The frontend connects from localhost:3000 / 127.0.0.1:3000
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"status": "CampusCopilot Backend is running!"}


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/search")
def search(
    profile: dict,
    live: bool = Query(False),
    kind: Optional[str] = Query(None),
):
    if kind in (None, "", "all"):
        kind = None
    elif kind not in VALID_KINDS:
        raise HTTPException(status_code=400, detail=f"kind must be one of {sorted(VALID_KINDS)} or 'all'")

    source, warning = "cache", None

    if live:
        api_key = os.getenv("TINYFISH_API_KEY", "").strip()
        if not api_key or api_key == "your-key-here":
            warning = "TINYFISH_API_KEY not configured in .env. Showing verified cached opportunities."
            opportunities = store.load()
        else:
            try:
                from fetch import fetch_all
                opportunities = fetch_all()
                if opportunities:
                    source = "live"
                else:
                    warning = "Live scan returned no results (check TINYFISH_API_KEY / server logs); showing cached results."
                    opportunities = store.load()
            except ImportError as e:
                raise HTTPException(status_code=503, detail=f"Live scan unavailable (import failed): {e}")
            except Exception as e:
                raise HTTPException(status_code=502, detail=f"Live scan failed: {type(e).__name__}: {e}")
    else:
        opportunities = store.load()

    results = rank(profile, opportunities, kind)
    return {"count": len(results), "results": results, "source": source, "warning": warning}
