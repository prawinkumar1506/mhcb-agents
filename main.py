from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
import uvicorn
# from database.mongodb import init_db
from routers import chat, agents, booking, assessment
from models.schemas import ChatRequest, ChatResponse

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database connection
    # await init_db()
    yield

app = FastAPI(
    title="Mental Health Chatbot API",
    description="Multi-agent mental health support system with Gemini AI and CrewAI",
    version="1.0.0",
    # lifespan=lifespan
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(agents.router, prefix="/api/agents", tags=["agents"])
app.include_router(booking.router, prefix="/api/booking", tags=["booking"])
app.include_router(assessment.router, prefix="/api/assessment", tags=["assessment"])

@app.get("/", response_class=HTMLResponse)
async def chat_interface():
    with open("static/index.html", "r") as f:
        return HTMLResponse(content=f.read())

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "mental-health-chatbot"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
