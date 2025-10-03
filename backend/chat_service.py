try:
    import google.generativeai as genai
except Exception:
    genai = None
import os
import json
import uuid
import time
from datetime import datetime
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()

class ChatService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        self.model = None
        if genai and api_key:
            try:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel('gemini-2.5-flash')
            except Exception:
                # If model initialization fails, keep graceful fallback
                self.model = None
        
        self.conversations = {}  # In-memory storage for demo
        self.max_retries = 3
        self.retry_delay = 1  # seconds
        
    async def get_response(self, message: str, conversation_id: Optional[str] = None) -> str:
        """Get response from Gemini API with error handling and retries"""
        if not self.model:
            return "AI service is not configured. Please set GEMINI_API_KEY."
        for attempt in range(self.max_retries):
            try:
                # Get or create conversation
                if conversation_id and conversation_id in self.conversations:
                    conversation_history = self.conversations[conversation_id]
                else:
                    conversation_id = conversation_id or str(uuid.uuid4())
                    conversation_history = []
                    self.conversations[conversation_id] = conversation_history
                
                # Build conversation context for Gemini
                context = "You are a helpful AI assistant similar to ChatGPT. You are knowledgeable, friendly, and provide detailed responses.\n\n"
                
                # Add conversation history
                for msg in conversation_history:
                    if msg["role"] == "user":
                        context += f"User: {msg['content']}\n"
                    elif msg["role"] == "assistant":
                        context += f"Assistant: {msg['content']}\n"
                
                # Add current user message
                context += f"User: {message}\nAssistant:"
                
                # Get response from Gemini
                response = self.model.generate_content(context)
                
                # Check if response is valid
                if not response or not response.text:
                    raise ValueError("Empty response from Gemini API")
                
                assistant_message = response.text
                
                # Add messages to conversation history
                conversation_history.append({"role": "user", "content": message})
                conversation_history.append({"role": "assistant", "content": assistant_message})
                
                # Update conversation
                self.conversations[conversation_id] = conversation_history
                
                return assistant_message
                
            except Exception as e:
                error_msg = str(e).lower()
                
                # Check for specific error types
                if "quota" in error_msg or "rate limit" in error_msg:
                    if attempt < self.max_retries - 1:
                        wait_time = self.retry_delay * (2 ** attempt)  # Exponential backoff
                        time.sleep(wait_time)
                        continue
                    else:
                        return "I'm currently experiencing high demand. Please try again in a few moments."
                
                elif "api key" in error_msg or "authentication" in error_msg:
                    return "There's an issue with the API configuration. Please contact support."
                
                elif "network" in error_msg or "connection" in error_msg:
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay)
                        continue
                    else:
                        return "I'm having trouble connecting to the service. Please check your internet connection and try again."
                
                elif attempt < self.max_retries - 1:
                    # Generic retry for other errors
                    time.sleep(self.retry_delay)
                    continue
                else:
                    # Final fallback
                    return f"I apologize, but I encountered an error: {str(e)}. Please try rephrasing your question or try again later."
        
        return "I'm currently unable to process your request. Please try again later."
    
    async def get_conversation_history(self, conversation_id: str) -> List[Dict]:
        """Get conversation history"""
        if conversation_id in self.conversations:
            return self.conversations[conversation_id]
        return []
    
    async def get_all_conversations(self) -> Dict:
        """Get all conversations with metadata"""
        result = {}
        for conv_id, messages in self.conversations.items():
            if messages:
                first_message = next((msg for msg in messages if msg["role"] == "user"), None)
                title = first_message["content"][:50] + "..." if first_message and len(first_message["content"]) > 50 else first_message["content"] if first_message else "New Conversation"
                result[conv_id] = {
                    "title": title,
                    "message_count": len(messages),
                    "last_updated": datetime.now().isoformat()
                }
        return result
    
    async def clear_conversation(self, conversation_id: str):
        """Clear conversation history"""
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
    
    async def analyze_file_content(self, content: str, filename: str, user_question: str = None) -> str:
        """Analyze file content using Gemini with error handling and retries"""
        if not self.model:
            return "AI service is not configured for file analysis. Please set GEMINI_API_KEY."
        for attempt in range(self.max_retries):
            try:
                # Prepare the prompt for file analysis
                if user_question:
                    prompt = f"""Please analyze the following file content and answer the user's question.

File: {filename}
User Question: {user_question}

File Content:
{content}

Please provide a detailed analysis and answer the user's question based on the file content."""
                else:
                    prompt = f"""Please analyze the following file content and provide a comprehensive summary.

File: {filename}

File Content:
{content}

Please provide:
1. A summary of the content
2. Key points or important information
3. Any insights or observations about the file"""
                
                # Get response from Gemini
                response = self.model.generate_content(prompt)
                
                # Check if response is valid
                if not response or not response.text:
                    raise ValueError("Empty response from Gemini API")
                
                return response.text
                
            except Exception as e:
                error_msg = str(e).lower()
                
                # Check for specific error types
                if "quota" in error_msg or "rate limit" in error_msg:
                    if attempt < self.max_retries - 1:
                        wait_time = self.retry_delay * (2 ** attempt)  # Exponential backoff
                        time.sleep(wait_time)
                        continue
                    else:
                        return "I'm currently experiencing high demand analyzing files. Please try again in a few moments."
                
                elif "api key" in error_msg or "authentication" in error_msg:
                    return "There's an issue with the API configuration for file analysis. Please contact support."
                
                elif "network" in error_msg or "connection" in error_msg:
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay)
                        continue
                    else:
                        return "I'm having trouble connecting to the service for file analysis. Please check your internet connection and try again."
                
                elif "content too large" in error_msg or "token limit" in error_msg:
                    return f"The file '{filename}' is too large to analyze. Please try with a smaller file or extract specific sections."
                
                elif attempt < self.max_retries - 1:
                    # Generic retry for other errors
                    time.sleep(self.retry_delay)
                    continue
                else:
                    # Final fallback
                    return f"I apologize, but I encountered an error analyzing the file '{filename}': {str(e)}. Please try again later or with a different file."
        
        return f"I'm currently unable to analyze the file '{filename}'. Please try again later."