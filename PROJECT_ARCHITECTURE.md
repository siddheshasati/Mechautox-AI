# MechautoX - AI Assistant Project Architecture

## 🎯 Project Overview
MechautoX is a comprehensive AI-powered desktop assistant that combines **Retrieval-Augmented Generation (RAG)**, **Real-time Web Search**, **Image Generation**, **Speech Processing**, and **Intelligent Automation** in a single PyQt5-based GUI application.

---

## 📁 File Structure & Responsibilities

### **Root Files**
| File | Role | Technology |
|------|------|-----------|
| `Main.py` | **Entry point** - Orchestrates all backend services and GUI communication | Python, PyQt5, Threading |
| `Requirements.txt` | **Dependency manager** - Lists all Python packages needed | pip |
| `.env` | **Configuration** - Stores API keys and settings (EXCLUDED from git) | Environment variables |

### **Frontend/** (GUI Layer)
| File | Role | Technology |
|------|------|-----------|
| `GUI.py` | **Main UI rendering** - Chat interface, buttons, responsiveness | PyQt5, HTML/CSS, JavaScript |
| `Data/Voice.html` | **Voice interface** - Web Audio API for speech I/O | HTML5, Web Audio API |

### **Backend/** (Business Logic)
| File | Role | Technology |
|------|------|-----------|
| `Chatbot.py` | **Main chatbot engine** - Processes queries, manages conversation history | LangChain, Python |
| `OrchestratorAgent.py` | **Agentic orchestrator** - Routes queries to specialized agents (RAG, Search, Automation) | LangChain Agents, LLM |
| `RAGSystem.py` | **Retrieval-Augmented Generation** - Vector search over uploaded files and local docs | FAISS, Sentence-Transformers, Embeddings |
| `RealtimeSearchEngine.py` | **Web search integration** - Fetches real-time info from internet | BeautifulSoup, Requests, Scraping |
| `Model.py` | **LLM integration** - Connects to Groq/Cohere LLM APIs | Groq, Cohere |
| `SpeechToText.py` | **Voice input** - Converts speech to text | Edge-TTS, PyAudio, Speech Recognition |
| `TextToSpeech.py` | **Voice output** - Converts text to speech | Edge-TTS, Pygame |
| `ImageGeneration.py` | **Image generation** - Creates images from text prompts | Hugging Face API, Diffusion Models |
| `Automation.py` | **System automation** - Opens apps, controls media, system commands | PyWhatKit, AppOpener, Keyboard |
| `AgentTools.py` | **Tool definitions** - Functions available to the AI agent | LangChain Tools |
| `StreamingHandler.py` | **Real-time response streaming** - Handles token-by-token output | Streaming APIs |
| `UploadProcessor.py` | **File processing** - Extracts text from PDFs, images, docs | PyPDF2, Pillow, Document parsers |

### **Backend/Data/** (Vector Databases & Cache)
| File | Role | Technology |
|------|------|-----------|
| `faiss_index/index.faiss` | **Vector store** - Stores embeddings of documents for fast retrieval | FAISS |
| `metadata.json` | **Metadata tracking** - Info about uploaded documents | JSON |
| `ChatLog.json` | **Conversation history** - All user-assistant exchanges | JSON |

### **Data/** (User Data & Uploads)
| File | Role | Purpose |
|------|------|---------|
| `ChatLog.json` | **Main chat log** - Current session messages | Session management |
| `ChatSessions.json` | **Session history** - Previous conversations | Chat history |
| `UploadedContext.json` | **File context** - Metadata of uploaded files | Document management |
| `faiss_index/` | **Embeddings cache** | Performance optimization |

### **Scripts/**
| File | Role | Purpose |
|------|------|---------|
| `generate_pdf.py` | **Utility** - Generates PDF reports from conversations | Report generation |

---

## 🔄 Application Workflow

```
User Input (Text/Voice/Upload)
         ↓
    Main.py (orchestrator)
         ↓
    ┌────┴────┬─────────┬──────────┐
    ↓         ↓         ↓          ↓
 GUI.py  Chatbot.py  Speech    ImageGen
         ↓
  Orchestrator Agent
    ↓        ↓        ↓
  RAG   WebSearch  Automation
    ↓        ↓        ↓
 Result ← LLM Routes → Tools
    ↓
 Response → GUI/TTS
    ↓
 User sees answer
```

### **Detailed Flow**
1. **User Query Input**: Text/Voice/Upload through GUI
2. **Query Processing**: `Main.py` receives input, normalizes it
3. **Agentic Routing**: `OrchestratorAgent` decides:
   - Should I use RAG (document search)?
   - Should I use web search?
   - Should I trigger automation?
   - Should I generate an image?
4. **Processing**: Specialized modules handle each task
5. **Response Generation**: LLM (Groq/Cohere) generates response
6. **Output**: Text displayed in GUI + optional voice output

---

## 🛠️ Technology Stack

### **Frontend**
- **PyQt5**: Cross-platform desktop GUI framework
  - Why? Rich widgets, native look-and-feel, good Python integration
  
### **Backend - AI/ML**
- **LangChain**: LLM orchestration & agent framework
  - Why? Simplifies LLM interactions, built-in agent patterns
- **Groq/Cohere**: LLM APIs for text generation
  - Why? Fast inference, good quality, cost-effective
- **FAISS**: Vector similarity search
  - Why? Lightning-fast nearest-neighbor search for millions of vectors
- **Sentence-Transformers**: Text embeddings
  - Why? Pre-trained, efficient, accurate semantic representations
- **Transformers**: Language models for embeddings
  - Why? Industry standard, extensive pre-trained models

### **Backend - Data Processing**
- **PyPDF2**: PDF extraction
  - Why? Lightweight, pure Python, no external dependencies
- **Pillow**: Image processing
  - Why? Fast, comprehensive image operations
- **BeautifulSoup**: Web scraping
  - Why? Simple HTML/XML parsing, beginner-friendly

### **Backend - Speech & Media**
- **Edge-TTS**: Text-to-speech
  - Why? Free, natural voice, no API keys required
- **Pygame**: Audio playback
  - Why? Cross-platform, lightweight, reliable
- **SpeechRecognition**: Speech-to-text
  - Why? Works with multiple backends, offline support

### **Backend - Automation**
- **PyWhatKit**: App automation
  - Why? Simplifies browser/app control
- **AppOpener**: System app launcher
  - Why? Cross-platform app launching
- **Keyboard/Mouse**: System control
  - Why? Direct OS interaction for automation

### **Database**
- **JSON**: Data storage
  - Why? Human-readable, simple structure, no external DB needed
- **FAISS**: Vector database
  - Why? Optimized for ML use cases

### **Other Tools**
- **Dotenv**: Environment management
  - Why? Secure API key handling

---

## ❓ Why These Technologies? (Justification)

| Component | Choice | Alternative | Why NOT Alternative |
|-----------|--------|-------------|---------------------|
| GUI | PyQt5 | Tkinter, PySimpleGUI, Kivy | PyQt5 has better styling, more widgets, professional appearance |
| LLM | Groq/Cohere | OpenAI, Anthropic | Groq is faster, cheaper; good for this use case |
| Vector DB | FAISS | Pinecone, Weaviate, Chroma | FAISS is local, free, fast; no cloud dependency |
| Embeddings | Sentence-Transformers | OpenAI Embeddings | Open-source, runs locally, free, privacy-focused |
| Speech | Edge-TTS | Google TTS, AWS Polly | Edge-TTS is free, no API keys, natural voices |
| PDF Processing | PyPDF2 | PDFPlumber, pdfminer | PyPDF2 is lightweight, fast, sufficient for extraction |
| Web Scraping | BeautifulSoup | Selenium, Playwright | BeautifulSoup is lighter; Selenium for JS-heavy sites |

---

## 🔑 Key Features

### 1. **RAG System (Retrieval-Augmented Generation)**
- Upload PDF/DOCX → Extract text → Create embeddings → Store in FAISS
- User query → Search FAISS → Retrieve relevant chunks → LLM generates answer
- **Benefit**: Answer questions about uploaded documents

### 2. **Real-time Web Search**
- Integrates live internet search
- Falls back to web when local knowledge insufficient
- **Benefit**: Always up-to-date information

### 3. **Agentic Orchestration**
- LLM decides which tool to use (RAG, Search, Automation, etc.)
- Autonomous decision-making based on query intent
- **Benefit**: Intelligent tool selection

### 4. **Voice I/O**
- Speech-to-text input
- Text-to-speech output
- Hands-free operation
- **Benefit**: Accessibility, convenience

### 5. **Image Generation**
- Text-to-image synthesis
- Integration with generative models
- **Benefit**: Creative content generation

### 6. **System Automation**
- Open applications
- Control media playback
- System commands
- **Benefit**: Full system control via natural language

---

## 📊 Data Flow Architecture

```
┌─────────────────────────────────────────────────────┐
│                   USER INTERFACE                     │
│              (PyQt5 GUI + Voice I/O)                │
└─────────────┬───────────────────────────────────────┘
              │
              ↓
┌─────────────────────────────────────────────────────┐
│                    MAIN.PY                          │
│            (Central Orchestrator)                    │
│  - Handles GUI events                               │
│  - Routes requests to backend                       │
│  - Manages threading                                │
└─────────────┬───────────────────────────────────────┘
              │
        ┌─────┴──────┬───────────┬──────────┐
        ↓            ↓           ↓          ↓
┌──────────────┐ ┌───────────┐ ┌────────┐ ┌──────────┐
│   CHATBOT    │ │ORCHESTR.  │ │ SPEECH │ │  IMAGE   │
│   ENGINE     │ │  AGENT    │ │ PROCESS│ │   GEN    │
└──────┬───────┘ └─────┬─────┘ └────────┘ └──────────┘
       │               │
       ├─ RAG SEARCH ──┤
       │ (FAISS DB)    │
       │               │
       ├─ WEB SEARCH ──┤
       │ (BeautifulSoup)
       │               │
       └─ AUTOMATION ──┘
         (System Control)
              │
              ↓
        ┌─────────────┐
        │  GROQ/COHERE│
        │    LLM      │
        └─────────────┘
```

---

## 🚀 Deployment Considerations

### Current: Local Desktop Application
- **Advantages**:
  - No internet required (mostly)
  - Privacy-first (data stays local)
  - Fast response times
  - Full system access

### Future: Cloud Deployment
- Move to FastAPI backend
- Containerize with Docker
- Deploy on Azure/AWS
- Add authentication
- Implement rate limiting

---

## 📈 Performance Optimization

| Component | Optimization | Impact |
|-----------|-------------|--------|
| FAISS | Indexing documents once | 100x faster search |
| Speech | Streaming responses | Real-time output |
| Caching | Store frequent queries | Reduce API calls |
| Threading | Non-blocking UI | Responsive interface |
| Embeddings | Pre-computed | Instant semantic search |

---

## 🔒 Security Considerations

- ✅ API keys in `.env` (excluded from git)
- ✅ Local vector database (no cloud exposure)
- ✅ Input sanitization for system commands
- ⚠️ Future: Add user authentication for cloud version
- ⚠️ Future: Implement rate limiting for APIs

---

## 🧪 Testing & Debugging

- `test_system.py`: System integration tests
- Logging for all components
- Error handling with fallbacks
- Chat log history for debugging

---

## 📚 Learning Resources

- **RAG**: https://python.langchain.com/docs/modules/data_connection/
- **Agents**: https://python.langchain.com/docs/modules/agents/
- **PyQt5**: https://doc.qt.io/qt-5/classes.html
- **FAISS**: https://github.com/facebookresearch/faiss/wiki
- **LangChain**: https://python.langchain.com/

