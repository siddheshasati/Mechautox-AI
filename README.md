#  MechautoX AI

> **A multi-modal AI assistant for the automotive domain — combining RAG  knowledge bases, real-time web search, desktop automation, AI image generation, and code synthesis — all orchestrated through LangChain and delivered via a native PyQt5 desktop application.**

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python" />
  <img src="https://img.shields.io/badge/LangChain-Orchestration-green?style=for-the-badge" />
  <img src="https://img.shields.io/badge/LLM-Groq%20llama--3.3--70b-orange?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Vector_DB-FAISS-blueviolet?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Embeddings-Cohere-coral?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Frontend-PyQt5-41CD52?style=for-the-badge&logo=qt" />
  <img src="https://img.shields.io/badge/Image_Gen-Pollinations_API-ff69b4?style=for-the-badge" />
</p>



## 🔍 Project Overview

MechautoX AI is a desktop-native, domain-specific AI assistant. It goes far beyond a simple chatbot — it can retrieve grounded answers from knowledge bases, search the live web for real-time information, execute system automations, generate diagnostic images, write and explain code, and deliver contextual or abbreviated answers based on the user's intent.

Everything runs through a single **PyQt5 desktop application**, keeping the experience native and offline-capable, with cloud APIs (Groq, Cohere, Pollinations) called only when needed.

---

## ⚙️ Core Capabilities

| Capability | Description |
|---|---|
| 🔍 RAG — Document Q&A | Retrieves answers from ingested automotive PDFs, manuals, and DTC databases grounded in source documents |
| 🌐 Real-Time Search | Integrated web search engine for live queries — current recalls, part prices, news |
| 🤖 Desktop Automation | Opens applications, executes system commands, and runs workflow sequences on the user's machine |
| 🎨 Image Generation | Generates automotive diagrams, concept visuals, and illustrations via Pollinations API |
| 💻 Code Writing | Writes, explains, and debugs code — from OBD-II scripts to automation utilities |
| 📝 Context-Aware Answers | Adapts response format: detailed contextual explanations or sharp abbreviated answers based on intent |
| 🔄 System Workflows | Chains multi-step tasks (search → summarize → open app → generate image) into automated pipelines |
| 💬 Conversational Memory | Multi-turn dialogue with full context retention across the session |

---

## 🏗 System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          MechautoX AI — System Architecture                      │
└─────────────────────────────────────────────────────────────────────────────────┘

  ┌──────────────────────────────────────────────────────────────┐
  │                    PyQt5 Desktop Application                   │
  │         Chat Window · Input Bar · Image Panel · History        │
  └───────────────────────────┬──────────────────────────────────┘
                               │  Python function calls (no HTTP)
                               ▼
  ┌──────────────────────────────────────────────────────────────┐
  │                  LangChain Orchestration Layer                 │
  │                                                                │
  │   ConversationalRetrievalChain   AgentExecutor (Tools)        │
  │   PromptTemplates                ConversationBufferMemory      │
  └──────┬───────────────┬──────────────────┬────────────────────┘
         │               │                  │
         ▼               ▼                  ▼
  ┌────────────┐  ┌──────────────┐  ┌──────────────────────────┐
  │  RAG Chain │  │  Tool Router │  │    LLM — Groq API         │
  │            │  │              │  │  llama-3.3-70b-versatile  │
  │  FAISS     │  │ ┌──────────┐ │  │  via Ollama locally       │
  │  Vector    │  │ │Web Search│ │  └──────────────────────────┘
  │  Store     │  │ ├──────────┤ │
  │            │  │ │Automation│ │
  │  Cohere    │  │ ├──────────┤ │
  │  Embeddings│  │ │Image Gen │ │
  └────────────┘  │ ├──────────┤ │
         ▲        │ │Code Tool │ │
         │        │ ├──────────┤ │
  ┌──────┴──────┐ │ │Workflow  │ │
  │  Ingestion  │ └──────────────┘
  │  Pipeline   │
  │  PDF→Chunk  │
  │  →Embed→   │
  │  FAISS Index│
  └─────────────┘
```

### Component Breakdown

**PyQt5 Desktop Application**
The entire UI runs as a native desktop window — no browser, no web server. PyQt5 renders the chat window, input controls, image panels, and history sidebar. Calls into LangChain happen as direct Python function calls in the same process, giving near-zero latency between UI and AI.

**LangChain Orchestration Layer**
The decision-making hub. It inspects every user message and routes it to the right chain or tool: RAG retrieval for document questions, the web search tool for live queries, the automation tool for system commands, the image tool for generation requests, and the code tool for programming tasks. `ConversationBufferMemory` preserves the full dialogue history so every response is context-aware.

**FAISS Vector Store**
Stores dense Cohere embeddings of all ingested automotive documents. At query time performs a cosine similarity search and returns the top-K most relevant chunks as grounding context for the LLM. Runs entirely in-process — no separate database server.

**Cohere Embeddings**
Converts both document chunks (at ingestion) and user queries (at retrieval) into dense vectors. Cohere's embedding API is used currently; HuggingFace local models are planned for future offline embedding support.

**Groq API — `llama-3.3-70b-versatile`**
The inference engine. Groq's LPU hardware delivers near-instant responses even for a 70B parameter model. The same model handles all tasks: RAG answers, web search summarization, code generation, and workflow planning — a single powerful model rather than multiple specialized ones.

**Ollama (Local fallback)**
For fully offline operation, the system can route LLM calls to a locally running Ollama model, swapped in via config without code changes.

**Pollinations API (Image Generation)**
Generates automotive visuals, concept diagrams, and illustration on demand. A diffusion model-based self-hosted solution is planned as the future replacement for production-quality, privacy-safe image generation.

**Real-Time Web Search**
Integrated search engine tool that fetches live web results, enabling the assistant to answer questions about current recalls, breaking news, live part availability, and anything beyond the knowledge cutoff of the LLM.

**Desktop Automation Engine**
A tool that maps natural language commands to OS-level actions — opening applications (e.g., "open the diagnostic tool"), running scripts, and executing multi-step system workflows. Built on Python's `subprocess` and `os` modules with LangChain tool binding.

---

## 🔁 RAG Pipeline Deep Dive

RAG (Retrieval-Augmented Generation) grounds the AI's answers in actual automotive documents rather than relying on what the LLM memorised during training. This is the core mechanism preventing hallucination on domain-specific questions like torque specs, fluid grades, and OBD-II fault codes.

```
USER QUERY: "What causes P0301 on a Maruti Swift?"
    │
    ▼
┌──────────────────────────────────────────────────┐
│  Step 1 — Query Embedding                         │
│  Cohere embed-english-v3.0                        │
│  "P0301 Maruti Swift" → Dense Vector [1024 dims]  │
└────────────────────────┬─────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────┐
│  Step 2 — Similarity Search                       │
│  FAISS IndexFlatIP (inner product / cosine)       │
│  Top-K = 4 most relevant chunks returned          │
│  e.g. chunk from dtc_guide.pdf, page 312          │
└────────────────────────┬─────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────┐
│  Step 3 — Context Construction                    │
│  Retrieved chunks + ConversationBufferMemory      │
│  Assembled into PromptTemplate                    │
└────────────────────────┬─────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────┐
│  Step 4 — LLM Generation                          │
│  Groq — llama-3.3-70b-versatile                  │
│  Generates answer strictly from context           │
│  Cannot fabricate beyond provided chunks          │
└────────────────────────┬─────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────┐
│  Step 5 — Response Delivery                       │
│  Answer + source document reference               │
│  Rendered in PyQt5 chat window                    │
└──────────────────────────────────────────────────┘
```

### Retrieval Quality Techniques

**Chunk Overlap** — Documents are split with overlapping windows so a key fact (like a torque spec) is never cut off at a chunk boundary. Overlap ensures continuity between adjacent segments.

**Similarity Threshold** — A minimum similarity score filters out irrelevant chunks. If no chunk clears the threshold, the system falls back to telling the user it doesn't have enough grounded information — rather than hallucinating.

**Metadata Preservation** — Each stored chunk carries its source filename and page number so answers can be traced back to the exact document and page.

### Prompt Template

```
You are MechautoX AI, an intelligent automotive assistant.
Answer ONLY using the context provided below. If the context is
insufficient, clearly say so. Never guess. Never hallucinate specs.

Context:
{context}

Chat History:
{chat_history}

User: {question}
MechautoX:
```

The explicit "never hallucinate specs" instruction is critical in an automotive context where a wrong torque value or fluid spec could cause engine damage.

---

## 📥 Data & Ingestion Pipeline

```
RAW AUTOMOTIVE DOCUMENTS
(PDFs, service manuals, DTC guides, spec sheets)
    │
    ▼
┌──────────────────────────────────────────┐
│  Document Loaders (LangChain)             │
│  PyPDFLoader · TextLoader · CSVLoader    │
└─────────────────┬────────────────────────┘
                  │
                  ▼
┌──────────────────────────────────────────┐
│  Text Splitter                            │
│  RecursiveCharacterTextSplitter           │
│  chunk_size = 1000 · chunk_overlap = 200  │
└─────────────────┬────────────────────────┘
                  │
                  ▼
┌──────────────────────────────────────────┐
│  Embedding Model — Cohere API             │
│  embed-english-v3.0                       │
│  Each chunk → 1024-dim dense vector       │
│  (HuggingFace local embeddings: planned)  │
└─────────────────┬────────────────────────┘
                  │
                  ▼
┌──────────────────────────────────────────┐
│  FAISS Vector Index                       │
│  IndexFlatIP — cosine similarity          │
│  Persisted to disk as faiss_index/        │
│  Loaded into memory at app startup        │
└──────────────────────────────────────────┘
```

---

## 🔄 How It Works — End to End

### Scenario A — RAG Query

User types: **"What is the valve clearance spec for a 2022 Toyota Fortuner?"**

1. PyQt5 captures the input and passes it to the LangChain `ConversationalRetrievalChain`.
2. Cohere embeds the query into a 1024-dim vector.
3. FAISS performs cosine similarity search, returning the top 4 chunks from ingested Toyota service documents.
4. LangChain constructs the prompt with retrieved chunks + chat history.
5. Groq (`llama-3.3-70b-versatile`) generates a grounded answer from the context.
6. PyQt5 renders the answer with the source document reference.

---

### Scenario B — Real-Time Search

User types: **"Are there any active recalls on the 2023 Hyundai Creta?"**

1. LangChain's agent recognises this as a live-data query (beyond the document knowledge base).
2. The **Web Search Tool** is invoked — fetches current results from the search engine.
3. Results are summarised by the LLM and presented with source links.
4. The answer reflects the current state of recalls, not the LLM's training-time knowledge.

---

### Scenario C — Desktop Automation

User types: **"Open the OBD diagnostic software."**

1. LangChain routes to the **Automation Tool**.
2. The tool maps the intent to the configured application path.
3. `subprocess` launches the application on the user's desktop.
4. Confirmation is shown in the chat window.

---

### Scenario D — Image Generation

User types: **"Generate a diagram of a turbocharged engine layout."**

1. LangChain routes to the **Image Generation Tool**.
2. The prompt is forwarded to the **Pollinations API**.
3. A generated image is returned and rendered in the PyQt5 image panel.

---

### Scenario E — Code Writing

User types: **"Write a Python script to read live OBD-II data using python-obd."**

1. LangChain routes to the **Code Tool**.
2. The LLM (`llama-3.3-70b-versatile`) generates the complete, annotated script.
3. The code is rendered in a syntax-highlighted panel in the desktop UI.

---

### Scenario F — System Workflow (Chained)

User types: **"Search for the latest diesel particulate filter cleaning methods, summarise them, and open the service notes app."**

1. LangChain's AgentExecutor decomposes this into a multi-step plan.
2. **Step 1** → Web Search Tool fires for DPF cleaning methods.
3. **Step 2** → LLM summarises the results.
4. **Step 3** → Automation Tool opens the service notes application.
5. All three outputs are delivered sequentially in the chat.

---

## 🛠 Tech Stack & Why Not Alternatives

### Python 3.10+
The entire stack — LangChain, FAISS, Cohere client, PyQt5, Ollama — is Python-native. The ML/AI ecosystem on Python is unmatched in maturity and community support.

---

### LangChain
Provides the orchestration glue: document loaders, text splitters, retrieval chains, agent tool routing, and conversation memory — all composable without writing the plumbing from scratch.

**Why not LlamaIndex?** LlamaIndex excels at document indexing workflows but LangChain's AgentExecutor and tool-binding system is far better suited for routing between multiple capabilities (RAG, search, automation, image gen, code) in a single conversational agent. LangChain also has richer memory primitives for multi-turn dialogue.

---

### FAISS (Facebook AI Similarity Search)
In-process vector similarity search. Zero infrastructure overhead — no database server to run, no Docker, no network calls. The FAISS index is loaded into RAM at startup and persisted to disk between sessions.

**Why not Qdrant / Pinecone?** Both are excellent but add operational overhead — Qdrant needs a running server process, Pinecone requires cloud credentials and network latency. For a local desktop application where all inference should be instant and offline-capable, FAISS's in-process design is the right tradeoff.

**Why not ChromaDB?** Chroma is a great embedded option but FAISS is more performant at scale and has tighter LangChain integration with simpler serialization to disk.

---

### Cohere Embeddings (`embed-english-v3.0`)
High-quality 1024-dimensional embeddings via Cohere's API. Outperforms older OpenAI `ada-002` on automotive domain retrieval benchmarks and provides a generous free tier for development.

**Why not HuggingFace `all-MiniLM-L6-v2`?** HuggingFace local models produce 384-dim vectors which are less expressive for technical automotive language. Cohere's embeddings capture domain-specific terminology (OBD codes, torque specs, part numbers) with noticeably better recall. **Note:** HuggingFace local embeddings are on the roadmap to enable fully offline operation.

**Why not OpenAI `text-embedding-ada-002`?** Similar quality but costs more per token. Cohere offers a larger free tier which is significant during development and testing with large automotive document corpora.

---

### Groq API — `llama-3.3-70b-versatile`
Sub-second inference on a 70B model via Groq's LPU hardware. This model handles every task in the system — RAG answers, code generation, search summarization, and workflow planning — without needing task-specific models.

**Why not OpenAI GPT-4o?** GPT-4o is marginally stronger at reasoning but every query sends data to OpenAI's servers. For an automotive workshop assistant that may handle proprietary vehicle service records and fleet data, cloud data egress is a concern. Groq + Llama keeps the model open-weight and the provider more transparent.

**Why not a smaller model (llama3.2 3B)?** Automotive diagnostics requires precise, technical accuracy. Smaller models frequently confuse OBD-II codes, misquote torque specs, and produce plausible-sounding but wrong answers. The 70B model's reasoning quality is the minimum acceptable bar for domain-critical automotive answers.

---

### Ollama (Local Fallback)
When Groq API is unavailable or the user prefers full offline operation, LLM calls are routed to a locally running Ollama instance. Same LangChain chain, different provider — swapped in config.

---

### Pollinations API (Image Generation)
Zero-cost, no-auth image generation API built on open diffusion models. Accepts a text prompt and returns a generated image — sufficient for diagrams, concept visuals, and part illustrations in the current version.

**Why not Stable Diffusion locally?** Running a full diffusion model locally demands significant VRAM (8GB+) and setup complexity. Pollinations abstracts all of that as a simple API call. A self-hosted diffusion model pipeline is on the roadmap for production-quality, fully offline image generation.

**Why not DALL·E / Midjourney?** Both require paid API access. Pollinations is free and open — appropriate for a development-stage assistant.

---

### PyQt5 (Desktop Frontend)
Native desktop GUI built with Qt. Renders the chat window, image panels, history sidebar, and input controls as a native application — no browser, no Electron overhead, no web server.

**Why not a web frontend (React / Next.js)?** A web frontend would require running a backend API server, managing CORS, and dealing with browser security restrictions around local file access and system automation. PyQt5 runs in the same Python process as LangChain, giving direct function calls instead of HTTP round-trips — critical for the desktop automation and local FAISS access features.

**Why not Tkinter?** Tkinter's UI is dated and severely limited in layout flexibility. PyQt5 supports modern widgets, custom stylesheets, threaded workers (essential for non-blocking LLM calls), and rich media rendering for generated images.

---

## 🗺 Future Roadmap

- [ ] **HuggingFace Local Embeddings** — Replace Cohere API with `all-MiniLM-L6-v2` or `nomic-embed-text` for fully offline embedding and zero API cost
- [ ] **Self-Hosted Diffusion Model** — Replace Pollinations with a local Stable Diffusion pipeline for production-quality, privacy-safe image generation
- [ ] **Fine-tuned Automotive LLM** — QLoRA fine-tuning on automotive corpora for improved domain accuracy on Indian vehicle data
- [ ] **Multi-language Support** — Hindi and Marathi query support
- [ ] **Muti User Support** — With Advanced Encryption  

---

## 👨‍💻 Author

**Siddhesh Asati**
Gen AI Engineer Intern @ Hexaware Technologies
B.E. Computer Science — Sinhgad Institute of Technology & Science, Pune

[![LinkedIn](https://img.shields.io/badge/LinkedIn-siddhesh--asati-blue?logo=linkedin)](https://linkedin.com/in/siddhesh-asati)
[![Portfolio](https://img.shields.io/badge/Portfolio-siddhesh--asati.netlify.app-green)](https://siddhesh-asati.netlify.app)
[![GitHub](https://img.shields.io/badge/GitHub-siddheshasati-black?logo=github)](https://github.com/siddheshasati)

---

## 📄 License

MIT License 
