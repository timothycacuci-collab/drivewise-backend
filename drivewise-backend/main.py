from fastapi import FastAPI, HTTPException, Depends, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import uvicorn
import os
from dotenv import load_dotenv

load_dotenv()

from database import get_db, engine, Base
from routers import auth, tests, static_data

Base.metadata.create_all(bind=engine)

app = FastAPI(title="DriveWise API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:3000"), "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(tests.router, prefix="/api/tests", tags=["tests"])
app.include_router(static_data.router, prefix="/api", tags=["static"])

@app.get("/api/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
