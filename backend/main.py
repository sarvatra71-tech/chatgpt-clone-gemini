from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import json
import uuid
from datetime import datetime
from typing import List, Optional
import aiofiles
from pydantic import BaseModel

from .chat_service import ChatService
from .file_service import FileService
from .research_agent import ResearchAgent

app = FastAPI(title="ChatGPT Clone", version="1.0.0")

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

# Create uploads directory
os.makedirs("uploads", exist_ok=True)

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
    return FileResponse("frontend/index.html")

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
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Validate file
        file_info = await file_service.validate_file(file)
        
        # Save file
        file_path = await file_service.save_file(file)
        
        # Process file content
        content = await file_service.extract_content(file_path, file.content_type)
        
        return {
            "filename": file.filename,
            "file_id": file_info["file_id"],
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