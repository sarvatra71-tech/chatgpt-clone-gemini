try:
    import google.generativeai as genai
except Exception:
    genai = None
try:
    import requests
except Exception:
    requests = None
import os
import time
from typing import List, Dict, Optional
try:
    from bs4 import BeautifulSoup
except Exception:
    BeautifulSoup = None
import json
from dotenv import load_dotenv

load_dotenv()

class ResearchAgent:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        self.model = None
        if genai and api_key:
            try:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel('gemini-2.5-flash')
            except Exception:
                self.model = None
        self.max_retries = 3
        self.retry_delay = 1  # seconds
        
    async def research_and_respond(self, query: str) -> str:
        """Perform deep research and provide comprehensive response"""
        if not self.model:
            return "Research service is not configured. Please set GEMINI_API_KEY."
        try:
            # Step 1: Analyze the query and generate search terms
            search_terms = await self._generate_search_terms(query)
            
            # Step 2: Perform web searches
            search_results = []
            for term in search_terms[:3]:  # Limit to 3 searches
                results = await self._web_search(term)
                search_results.extend(results)
            
            # Step 3: Extract and analyze content from top results
            analyzed_content = await self._analyze_search_results(search_results[:5])
            
            # Step 4: Generate comprehensive response
            response = await self._generate_research_response(query, analyzed_content)
            
            return response
            
        except Exception as e:
            return f"I apologize, but I encountered an error during research: {str(e)}. I'll provide a response based on my training data instead.\n\n" + await self._fallback_response(query)
    
    async def _generate_search_terms(self, query: str) -> List[str]:
        """Generate relevant search terms for the query with error handling"""
        for attempt in range(self.max_retries):
            try:
                prompt = f"""You are a research assistant. Generate 2-3 specific search terms that would help find the most relevant and current information for the user's query. Return only the search terms, one per line.

Query: {query}"""
                
                response = self.model.generate_content(prompt)
                
                # Check if response is valid
                if not response or not response.text:
                    raise ValueError("Empty response from Gemini API")
                
                # Parse search terms from response
                terms = [term.strip() for term in response.text.strip().split('\n') if term.strip()]
                return terms[:3] if terms else [query]  # Fallback to original query
                
            except Exception as e:
                error_msg = str(e).lower()
                
                if "quota" in error_msg or "rate limit" in error_msg:
                    if attempt < self.max_retries - 1:
                        wait_time = self.retry_delay * (2 ** attempt)
                        time.sleep(wait_time)
                        continue
                    else:
                        # Fallback to using the original query
                        return [query]
                
                elif attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue
                else:
                    # Fallback to using the original query
                    return [query]
        
        return [query]
    
    async def _web_search(self, query: str) -> List[Dict]:
        """Perform web search using simulated results"""
        # This is a simplified simulation placeholder for web search
        try:
            # Simulated search results for demo purposes
            return [
                {
                    "title": f"Search result for: {query}",
                    "link": "https://example.com",
                    "snippet": f"This is a simulated search result for the query: {query}. In a real implementation, this would contain actual web search results from a search API."
                }
            ]
        except Exception as e:
            return []
    
    async def _analyze_search_results(self, results: List[Dict]) -> str:
        """Analyze search results and extract key information with error handling"""
        if not results:
            return "No search results available for analysis."
        
        for attempt in range(self.max_retries):
            try:
                # Prepare content for analysis
                content = "Search Results Analysis:\n\n"
                for i, result in enumerate(results, 1):
                    content += f"{i}. Title: {result.get('title', 'N/A')}\n"
                    content += f"   Link: {result.get('link', 'N/A')}\n"
                    content += f"   Summary: {result.get('snippet', 'N/A')}\n\n"
                
                prompt = f"""Please analyze the following search results and extract the most important and relevant information. Summarize the key points, facts, and insights that would be useful for answering user queries.

{content}

Please provide a concise analysis focusing on:
1. Key facts and information
2. Important insights or trends
3. Relevant details that answer common questions about this topic"""
                
                response = self.model.generate_content(prompt)
                
                # Check if response is valid
                if not response or not response.text:
                    raise ValueError("Empty response from Gemini API")
                
                return response.text
                
            except Exception as e:
                error_msg = str(e).lower()
                
                if "quota" in error_msg or "rate limit" in error_msg:
                    if attempt < self.max_retries - 1:
                        wait_time = self.retry_delay * (2 ** attempt)
                        time.sleep(wait_time)
                        continue
                    else:
                        # Fallback to basic summary
                        return self._create_basic_summary(results)
                
                elif attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue
                else:
                    return self._create_basic_summary(results)
        
        return self._create_basic_summary(results)
    
    def _create_basic_summary(self, results: List[Dict]) -> str:
        """Create a basic summary when AI analysis fails"""
        summary = "Based on search results:\n\n"
        for i, result in enumerate(results[:3], 1):
            summary += f"{i}. {result.get('title', 'N/A')}\n"
            summary += f"   {result.get('snippet', 'No description available')}\n\n"
        return summary
    
    async def _generate_research_response(self, original_query: str, research_content: str) -> str:
        """Generate comprehensive response based on research with error handling"""
        for attempt in range(self.max_retries):
            try:
                prompt = f"""Based on the research content provided below, please generate a comprehensive and well-structured response to the user's original query. The response should be informative, accurate, and directly address the user's question.

Original Query: {original_query}

Research Content:
{research_content}

Please provide a detailed response that:
1. Directly answers the user's question
2. Includes relevant facts and information from the research
3. Is well-organized and easy to understand
4. Provides actionable insights where applicable
5. Mentions if the information is based on recent research findings

Response:"""
                
                response = self.model.generate_content(prompt)
                
                # Check if response is valid
                if not response or not response.text:
                    raise ValueError("Empty response from Gemini API")
                
                return response.text
                
            except Exception as e:
                error_msg = str(e).lower()
                
                if "quota" in error_msg or "rate limit" in error_msg:
                    if attempt < self.max_retries - 1:
                        wait_time = self.retry_delay * (2 ** attempt)
                        time.sleep(wait_time)
                        continue
                    else:
                        # Fallback to basic response
                        return f"Based on the research findings:\n\n{research_content}\n\nThis information addresses your query about: {original_query}"
                
                elif attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue
                else:
                    return f"Based on the research findings:\n\n{research_content}\n\nThis information addresses your query about: {original_query}"
        
        return f"Based on the research findings:\n\n{research_content}\n\nThis information addresses your query about: {original_query}"
    
    async def _fallback_response(self, query: str) -> str:
        """Provide fallback response when research fails with error handling"""
        for attempt in range(self.max_retries):
            try:
                prompt = f"""Please provide a helpful and informative response to the following query based on your training data. Be clear that this response is based on your general knowledge and not current web research.

Query: {query}

Please provide a comprehensive answer while noting that this information is based on your training data and may not reflect the most recent developments."""
                
                response = self.model.generate_content(prompt)
                
                # Check if response is valid
                if not response or not response.text:
                    raise ValueError("Empty response from Gemini API")
                
                return response.text
                
            except Exception as e:
                error_msg = str(e).lower()
                
                if "quota" in error_msg or "rate limit" in error_msg:
                    if attempt < self.max_retries - 1:
                        wait_time = self.retry_delay * (2 ** attempt)
                        time.sleep(wait_time)
                        continue
                    else:
                        return f"I understand you're asking about: {query}\n\nI'm currently unable to provide a detailed response due to high demand. Please try again in a few moments, or rephrase your question for better results."
                
                elif attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue
                else:
                    return f"I understand you're asking about: {query}\n\nI'm currently experiencing technical difficulties. Please try again later or contact support if the issue persists."
        
        return f"I understand you're asking about: {query}\n\nI'm currently experiencing technical difficulties. Please try again later or contact support if the issue persists."