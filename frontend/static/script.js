// Global variables
let currentConversationId = null;
let uploadedFile = null;
let isTyping = false;

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    const messageInput = document.getElementById('messageInput');
    const sendButton = document.getElementById('sendButton');
    
    // Enable send button when there's text
    messageInput.addEventListener('input', function() {
        sendButton.disabled = this.value.trim() === '';
        autoResize(this);
    });
    
    // Focus on input
    messageInput.focus();
});

// Handle keyboard shortcuts
function handleKeyDown(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

// Auto-resize textarea
function autoResize(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
}

// Send message function
async function sendMessage() {
    const messageInput = document.getElementById('messageInput');
    const message = messageInput.value.trim();
    
    if (!message || isTyping) return;
    
    // Clear input and disable send button
    messageInput.value = '';
    messageInput.style.height = 'auto';
    document.getElementById('sendButton').disabled = true;
    
    // Add user message to chat
    addMessage(message, 'user');
    
    // Show typing indicator
    showTypingIndicator();
    
    try {
        let response;
        const useResearch = document.getElementById('researchToggle').checked;
        
        if (uploadedFile) {
            // Send message with file
            response = await sendMessageWithFile(message, uploadedFile.file_id, useResearch);
            removeFile(); // Clear file after sending
        } else {
            // Send regular message
            response = await sendRegularMessage(message, useResearch);
        }
        
        // Hide typing indicator and add response
        hideTypingIndicator();
        addMessage(response.response, 'assistant');
        
        // Update conversation ID
        currentConversationId = response.conversation_id;
        
    } catch (error) {
        hideTypingIndicator();
        addMessage('Sorry, I encountered an error. Please try again.', 'assistant');
        console.error('Error sending message:', error);
    }
}

// Send regular message
async function sendRegularMessage(message, useResearch) {
    const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            message: message,
            conversation_id: currentConversationId,
            use_research: useResearch
        })
    });
    
    if (!response.ok) {
        throw new Error('Failed to send message');
    }
    
    return await response.json();
}

// Send message with file
async function sendMessageWithFile(message, fileId, useResearch) {
    const formData = new FormData();
    formData.append('message', message);
    formData.append('file_id', fileId);
    formData.append('use_research', useResearch);
    if (currentConversationId) {
        formData.append('conversation_id', currentConversationId);
    }
    
    const response = await fetch('/api/chat-with-file', {
        method: 'POST',
        body: formData
    });
    
    if (!response.ok) {
        throw new Error('Failed to send message with file');
    }
    
    return await response.json();
}

// Add message to chat
function addMessage(content, sender) {
    const chatContainer = document.getElementById('chatContainer');
    
    // Remove welcome message if it exists
    const welcomeMessage = chatContainer.querySelector('.welcome-message');
    if (welcomeMessage) {
        welcomeMessage.remove();
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.innerHTML = sender === 'user' ? '<i class="fas fa-user"></i>' : '<i class="fas fa-robot"></i>';
    
    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    
    // Format message content (handle markdown-like formatting)
    messageContent.innerHTML = formatMessage(content);
    
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(messageContent);
    
    chatContainer.appendChild(messageDiv);
    
    // Scroll to bottom
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Format message content
function formatMessage(content) {
    // Basic markdown-like formatting
    let formatted = content
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/`(.*?)`/g, '<code>$1</code>')
        .replace(/\n/g, '<br>');
    
    // Handle code blocks
    formatted = formatted.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');
    
    return formatted;
}

// Show typing indicator
function showTypingIndicator() {
    if (isTyping) return;
    
    isTyping = true;
    const chatContainer = document.getElementById('chatContainer');
    
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message assistant typing-message';
    typingDiv.id = 'typingIndicator';
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.innerHTML = '<i class="fas fa-robot"></i>';
    
    const typingContent = document.createElement('div');
    typingContent.className = 'typing-indicator';
    typingContent.innerHTML = `
        <span>Thinking</span>
        <div class="typing-dots">
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        </div>
    `;
    
    typingDiv.appendChild(avatar);
    typingDiv.appendChild(typingContent);
    
    chatContainer.appendChild(typingDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Hide typing indicator
function hideTypingIndicator() {
    isTyping = false;
    const typingIndicator = document.getElementById('typingIndicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

// Handle file upload
async function handleFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    try {
        // Show loading
        showLoading('Uploading file...');
        
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error('Failed to upload file');
        }
        
        const result = await response.json();
        
        // Store uploaded file info
        uploadedFile = result;
        
        // Show file preview
        showFilePreview(result);
        
        hideLoading();
        
    } catch (error) {
        hideLoading();
        alert('Error uploading file: ' + error.message);
        console.error('Upload error:', error);
    }
    
    // Clear file input
    event.target.value = '';
}

// Show file preview
function showFilePreview(fileInfo) {
    const filePreview = document.getElementById('filePreview');
    const fileName = document.getElementById('fileName');
    
    fileName.textContent = `${fileInfo.filename} (${formatFileSize(fileInfo.size)})`;
    filePreview.style.display = 'block';
}

// Remove file
function removeFile() {
    uploadedFile = null;
    document.getElementById('filePreview').style.display = 'none';
}

// Format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Show loading overlay
function showLoading(message = 'Loading...') {
    const overlay = document.getElementById('loadingOverlay');
    const loadingText = overlay.querySelector('p');
    loadingText.textContent = message;
    overlay.style.display = 'flex';
}

// Hide loading overlay
function hideLoading() {
    document.getElementById('loadingOverlay').style.display = 'none';
}

// Start new chat
function startNewChat() {
    currentConversationId = null;
    uploadedFile = null;
    
    // Clear chat container
    const chatContainer = document.getElementById('chatContainer');
    chatContainer.innerHTML = `
        <div class="welcome-message">
            <div class="welcome-icon">
                <i class="fas fa-robot"></i>
            </div>
            <h2>Welcome to Enkay LLM ChatClone</h2>
            <p>I'm here to help you with questions, file analysis, and research. You can:</p>
            <ul>
                <li><i class="fas fa-comment"></i> Ask me anything</li>
                <li><i class="fas fa-file-upload"></i> Upload files for analysis</li>
                <li><i class="fas fa-search"></i> Enable research mode for web-based answers</li>
            </ul>
        </div>
    `;
    
    // Hide file preview
    document.getElementById('filePreview').style.display = 'none';
    
    // Focus on input
    document.getElementById('messageInput').focus();
}

// Toggle sidebar (for mobile)
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    sidebar.classList.toggle('open');
}

// Select chat (placeholder for future implementation)
function selectChat(chatId) {
    // This would load a specific chat conversation
    console.log('Selected chat:', chatId);
}

// Close sidebar when clicking outside (mobile)
document.addEventListener('click', function(event) {
    const sidebar = document.getElementById('sidebar');
    const sidebarToggle = document.querySelector('.sidebar-toggle');
    
    if (window.innerWidth <= 768 && 
        !sidebar.contains(event.target) && 
        !sidebarToggle.contains(event.target) &&
        sidebar.classList.contains('open')) {
        sidebar.classList.remove('open');
    }
});

// Handle window resize
window.addEventListener('resize', function() {
    const sidebar = document.getElementById('sidebar');
    if (window.innerWidth > 768) {
        sidebar.classList.remove('open');
    }
});