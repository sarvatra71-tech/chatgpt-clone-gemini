import os
import uuid
import aiofiles
import mimetypes
from typing import Dict, Optional
from fastapi import UploadFile, HTTPException
import PyPDF2
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()

class FileService:
    def __init__(self):
        self.upload_dir = "uploads"
        self.max_file_size = int(os.getenv("MAX_FILE_SIZE", 10485760))  # 10MB default
        self.allowed_types = os.getenv("ALLOWED_FILE_TYPES", "txt,pdf,png,jpg,jpeg,gif,md,py,js,html,css,json").split(",")
        self.file_storage = {}  # In-memory storage for demo
        
        # Create upload directory
        os.makedirs(self.upload_dir, exist_ok=True)
    
    def _get_file_type(self, filename: str) -> str:
        """Get file type from filename extension."""
        mime_type, _ = mimetypes.guess_type(filename)
        if mime_type:
            return mime_type.split('/')[0]  # Return main type (text, image, application, etc.)
        return "unknown"
    
    async def validate_file(self, file: UploadFile) -> Dict:
        """Validate uploaded file"""
        # Check file size
        file_content = await file.read()
        await file.seek(0)  # Reset file pointer
        
        if len(file_content) > self.max_file_size:
            raise HTTPException(
                status_code=413, 
                detail=f"File too large. Maximum size is {self.max_file_size / 1024 / 1024:.1f}MB"
            )
        
        # Check file type
        file_extension = file.filename.split('.')[-1].lower() if '.' in file.filename else ''
        if file_extension not in self.allowed_types:
            raise HTTPException(status_code=400, detail=f"File type '{file_extension}' not allowed")
        
        return {
            "valid": True,
            "size": len(file_content),
            "type": file_extension,
            "filename": file.filename
        }
    
    async def save_file(self, file: UploadFile) -> str:
        """Save uploaded file to disk"""
        file_id = str(uuid.uuid4())
        file_extension = file.filename.split(".")[-1] if file.filename else "txt"
        file_path = os.path.join(self.upload_dir, f"{file_id}.{file_extension}")
        
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        # Store file metadata
        self.file_storage[file_id] = {
            "path": file_path,
            "filename": file.filename,
            "content_type": file.content_type,
            "size": len(content)
        }
        
        return file_id
    
    async def extract_content(self, file_path: str, content_type: str) -> str:
        """Extract text content from file"""
        try:
            if content_type == "application/pdf" or file_path.endswith('.pdf'):
                return await self._extract_pdf_content(file_path)
            elif content_type and content_type.startswith("text/"):
                return await self._extract_text_content(file_path)
            elif file_path.endswith(('.py', '.js', '.html', '.css', '.json', '.md', '.txt')):
                return await self._extract_text_content(file_path)
            elif content_type and content_type.startswith("image/"):
                return f"[Image file: {os.path.basename(file_path)}] - Image analysis not implemented in this demo"
            else:
                return f"[File: {os.path.basename(file_path)}] - Content extraction not supported for this file type"
        except Exception as e:
            return f"Error extracting content: {str(e)}"
    
    async def _extract_text_content(self, file_path: str) -> str:
        """Extract content from text files"""
        async with aiofiles.open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = await f.read()
            return content
    
    async def _extract_pdf_content(self, file_path: str) -> str:
        """Extract content from PDF files"""
        try:
            with open(file_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text.strip()
        except Exception as e:
            return f"Error reading PDF: {str(e)}"
    
    async def get_file_content(self, file_id: str) -> str:
        """Get file content by file ID"""
        if file_id not in self.file_storage:
            raise HTTPException(status_code=404, detail="File not found")
        
        file_info = self.file_storage[file_id]
        return await self.extract_content(file_info["path"], file_info["content_type"])
    
    async def delete_file(self, file_id: str):
        """Delete file from storage"""
        if file_id in self.file_storage:
            file_path = self.file_storage[file_id]["path"]
            if os.path.exists(file_path):
                os.remove(file_path)
            del self.file_storage[file_id]