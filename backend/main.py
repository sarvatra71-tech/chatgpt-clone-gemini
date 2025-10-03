from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
import os
import json
import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

from backend.chat_service import ChatService
from backend.file_service import FileService
from backend.research_agent import ResearchAgent

app = FastAPI(title="Enkay LLM ChatClone", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
chat_service = ChatService()
file_service = FileService()
research_agent = ResearchAgent()


class ChatMessage(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    use_research: bool = False

class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    timestamp: str

@app.get("/")
async def read_root():
    try:
        return FileResponse("frontend/index.html")
    except Exception:
        # Fallback HTML in case file is not accessible in serverless runtime
        return HTMLResponse(
            """
            <!doctype html>
            <html>
            <head><title>Enkay LLM ChatClone</title></head>
            <body>
              <h1>Enkay LLM ChatClone</h1>
              <p>Frontend static route is configured. If you see this, the static file may not be accessible in the serverless runtime. Navigate to <a href="/">home</a> or use the API endpoints.</p>
            </body>
            </html>
            """,
            status_code=200
        )

@app.post("/api/chat", response_model=ChatResponse)
async def chat(message: ChatMessage):
    try:
        if message.use_research:
            response = await research_agent.research_and_respond(message.message)
        else:
            response = await chat_service.get_response(
                message.message, 
                message.conversation_id
            )
        
        conversation_id = message.conversation_id or str(uuid.uuid4())
        
        return ChatResponse(
            response=response,
            conversation_id=conversation_id,
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        # Return friendly fallback instead of 500 to avoid FUNCTION_INVOCATION_FAILED
        conversation_id = message.conversation_id or str(uuid.uuid4())
        return ChatResponse(
            response=f"I'm sorry, I ran into an issue: {str(e)}. Please try again.",
            conversation_id=conversation_id,
            timestamp=datetime.now().isoformat()
        )

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Validate file
        file_info = await file_service.validate_file(file)
        
        # Save file (in-memory) and get its ID
        file_id = await file_service.save_file(file)
        
        # Process file content from in-memory storage
        content = await file_service.extract_content(file_id)
        
        return {
            "filename": file.filename,
            "file_id": file_id,
            "content_preview": content[:500] + "..." if len(content) > 500 else content,
            "file_type": file.content_type,
            "size": file_info["size"]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/chat-with-file")
async def chat_with_file(
    message: str = Form(...),
    file_id: str = Form(...),
    conversation_id: Optional[str] = Form(None),
    use_research: bool = Form(False)
):
    try:
        # Get file content
        file_content = await file_service.get_file_content(file_id)
        
        # Combine message with file content
        full_message = f"User message: {message}\n\nFile content:\n{file_content}"
        
        if use_research:
            response = await research_agent.research_and_respond(full_message)
        else:
            response = await chat_service.get_response(full_message, conversation_id)
        
        conversation_id = conversation_id or str(uuid.uuid4())
        
        return ChatResponse(
            response=response,
            conversation_id=conversation_id,
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    try:
        messages = await chat_service.get_conversation_history(conversation_id)
        return {"messages": messages}
    except Exception as e:
        raise HTTPException(status_code=404, detail="Conversation not found")

@app.get("/api/ping")
async def ping():
    return {"ok": True}

# Serve static files
# Static files mounting for local development
if os.getenv("VERCEL") != "1":
    app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
    app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

# Vercel handler
handler = app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)