# Enkay LLM ChatClone (Google Gemini Integration)

A modern, feature-rich Enkay LLM ChatClone built with FastAPI and Google Gemini AI, featuring file upload capabilities and a deep research agent.

## Features

- **AI Chat Interface**: Powered by Google Gemini Pro for intelligent conversations
- **File Upload & Analysis**: Support for text files, PDFs, and images with AI-powered analysis
- **Deep Research Agent**: Web search integration with comprehensive research capabilities
- **Modern UI/UX**: Clean, responsive interface similar to ChatGPT
- **Conversation History**: Persistent chat sessions with easy navigation
- **Error Handling**: Robust error handling with retry mechanisms and fallback responses
- **Real-time Updates**: Live typing indicators and seamless message flow

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/enkay_llm_chatclone.git
   cd enkay_llm_chatclone
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv ai_env
   source ai_env/bin/activate  # On Windows: ai_env\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your API keys:
   ```
   GEMINI_API_KEY=your_google_gemini_api_key_here
   MAX_FILE_SIZE=10485760  # 10MB
   ALLOWED_FILE_TYPES=txt,pdf,jpg,jpeg,png,gif,bmp
   ```

5. **Run the application**
   ```bash
   uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
   ```

6. **Access the application**
   Open your browser and navigate to `http://localhost:8000`

## Usage

### Basic Chat
- Type your message in the input field and press Enter or click Send
- The AI will respond using Google Gemini Pro
- Conversations are automatically saved and can be accessed from the sidebar

### File Upload
- Click the attachment icon to upload files
- Supported formats: TXT, PDF, JPG, JPEG, PNG, GIF, BMP
- Ask questions about the uploaded file content
- The AI will analyze and provide insights about your files

### Research Mode
- Use the research feature for in-depth analysis of topics
- The system will search the web and provide comprehensive responses
- Combines multiple sources for accurate, up-to-date information

## API Endpoints

- `GET /` - Main chat interface
- `POST /api/chat` - Send chat messages
- `POST /api/upload` - Upload and analyze files
- `POST /api/research` - Perform deep research queries
- `GET /api/conversations` - Get conversation history
- `DELETE /api/conversations/{id}` - Delete specific conversation

## Project Structure

```
chatgpt-clone/
├── backend/
│   ├── main.py              # FastAPI application entry point
│   ├── chat_service.py      # Google Gemini chat service with error handling
│   ├── file_service.py      # File upload and processing service
│   └── research_agent.py    # Web research and analysis agent
├── frontend/
│   ├── static/
│   │   ├── script.js        # Frontend JavaScript logic
│   │   └── styles.css       # Modern CSS styling
│   └── templates/
│       └── index.html       # Main chat interface
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
└── README.md               # This file
```

## Configuration

### Environment Variables
- `GEMINI_API_KEY`: Your Google Gemini API key (required)
- `MAX_FILE_SIZE`: Maximum file upload size in bytes (default: 10MB)
- `ALLOWED_FILE_TYPES`: Comma-separated list of allowed file extensions

### Google Gemini API Setup
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add the key to your `.env` file as `GEMINI_API_KEY`

### Web Search Setup (Optional)
If you plan to integrate a web search provider, configure its API key according to your chosen service. The current implementation uses simulated results and does not require an additional key.

## Supported File Types

- **Text Files**: .txt
- **PDF Documents**: .pdf
- **Images**: .jpg, .jpeg, .png, .gif, .bmp

## Error Handling & Reliability

The application includes comprehensive error handling:

- **Retry Mechanisms**: Automatic retries for transient API failures
- **Rate Limit Handling**: Exponential backoff for rate-limited requests
- **Fallback Responses**: Graceful degradation when services are unavailable
- **Input Validation**: Robust validation for file uploads and user inputs
- **Network Resilience**: Handles network connectivity issues

## Troubleshooting

### Common Issues

1. **Server won't start**
   - Check that all dependencies are installed: `pip install -r requirements.txt`
   - Verify your virtual environment is activated
   - Ensure port 8000 is not in use by another application

2. **API Key errors**
   - Verify your `GEMINI_API_KEY` is correctly set in the `.env` file
   - Check that your Google Gemini API key is valid and has sufficient quota
   - Ensure the `.env` file is in the project root directory

3. **File upload issues**
   - Check file size limits (default 10MB)
   - Verify file type is supported
   - Ensure sufficient disk space for temporary files

4. **Research features not working**
   - Research currently uses simulated search results (no extra API key required)
   - Check internet connectivity if you integrate a real web search API
   - If you add a provider, ensure its key is configured properly

## Development

### Git Workflow

1. **Create a new branch for features**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes and commit**:
   ```bash
   git add .
   git commit -m "Add your descriptive commit message"
   ```

3. **Push to your branch**:
   ```bash
   git push origin feature/your-feature-name
   ```

4. **Create a Pull Request** on GitHub

### Local Development

1. **Start the development server**:
   ```bash
   uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Adding New Features
1. Backend changes go in the `backend/` directory
2. Frontend changes go in `frontend/static/`
3. Follow the existing code structure and error handling patterns
4. Test thoroughly with various file types and edge cases

### API Integration
The application uses Google Gemini Pro API with the following features:
- Conversation context management
- File content analysis
- Research query processing
- Error handling and retry logic

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and test thoroughly
4. Commit your changes: `git commit -am 'Add new feature'`
5. Push to the branch: `git push origin feature-name`
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/) for the backend API
- Powered by [Google Gemini](https://ai.google.dev/) for AI capabilities
-- Placeholder web search simulation; you can integrate a search API of choice
- Frontend styling inspired by ChatGPT's modern interface# Deployment trigger - Wed Oct  1 17:01:07 PDT 2025