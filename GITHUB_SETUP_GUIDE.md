# GitHub Setup Guide for MechautoX

## Step 1: Create Repository on GitHub

### Using GitHub Web Interface:
1. Go to https://github.com/new
2. **Repository name**: `MechautoX` (or your preferred name)
3. **Description**: "AI Assistant with RAG, Agents, Voice I/O, and Automation"
4. **Visibility**: Public (unless you want private)
5. **Initialize repository**: ❌ NO (we already have local repo)
6. Click **Create repository**

### After creation, GitHub will show commands like:
```
git remote add origin https://github.com/YourUsername/MechautoX.git
git branch -M main
git push -u origin main
```

---

## Step 2: Connect Local Repo to GitHub

### Copy the remote URL from GitHub (HTTPS or SSH):

**Using HTTPS** (easier, no SSH key needed):
```bash
git remote add origin https://github.com/YourUsername/MechautoX.git
```

**Using SSH** (if you have SSH key configured):
```bash
git remote add origin git@github.com:YourUsername/MechautoX.git
```

### Verify connection:
```bash
git remote -v
# Should output:
# origin  https://github.com/YourUsername/MechautoX.git (fetch)
# origin  https://github.com/YourUsername/MechautoX.git (push)
```

---

## Step 3: Push Code to GitHub

### Rename branch to `main` (GitHub standard):
```bash
git branch -M main
```

### Push to GitHub:
```bash
git push -u origin main
```

**First time?** You'll be prompted for authentication:
- **HTTPS**: Enter GitHub username and Personal Access Token (PAT)
  - Generate PAT: https://github.com/settings/tokens
  - Scopes needed: `repo`, `read:user`, `user:email`
- **SSH**: Uses your SSH key (if configured)

### Subsequent pushes:
```bash
git push
```

---

## Step 4: Verify on GitHub

1. Visit: `https://github.com/YourUsername/MechautoX`
2. ✅ Verify all files are there
3. ✅ Verify `.env` and `.venv` are NOT there (check .gitignore worked)
4. ✅ See commit history with your message

---

## Step 5: Add README (Recommended)

Create `README.md` in repo root:

```markdown
# MechautoX - AI Desktop Assistant

An intelligent AI assistant that combines Retrieval-Augmented Generation (RAG), real-time web search, speech I/O, image generation, and system automation in a single desktop application.

## Features

- 🤖 **AI Chatbot**: Powered by Groq/Cohere LLMs
- 📄 **RAG System**: Upload PDFs/documents for intelligent Q&A
- 🌐 **Web Search**: Real-time information retrieval
- 🎤 **Voice I/O**: Speech-to-text and text-to-speech
- 🖼️ **Image Generation**: Text-to-image synthesis
- 🔧 **Automation**: System control via natural language
- 🧠 **Agentic Routing**: Intelligent tool selection

## Quick Start

### Prerequisites
- Python 3.10+
- Windows/Mac/Linux

### Installation

1. **Clone repository**:
```bash
git clone https://github.com/YourUsername/MechautoX.git
cd MechautoX
```

2. **Create virtual environment**:
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Mac/Linux
source .venv/bin/activate
```

3. **Install dependencies**:
```bash
pip install -r Requirements.txt
```

4. **Configure environment**:
```bash
# Copy .env.example to .env
cp .env.example .env
# Edit .env and add your API keys:
# - GROQ_API_KEY
# - COHERE_API_KEY
```

5. **Run application**:
```bash
python Main.py
```

## Project Architecture

See [PROJECT_ARCHITECTURE.md](PROJECT_ARCHITECTURE.md) for:
- System design and components
- Technology stack justification
- Data flow diagrams
- Deployment considerations

## Interview Q&A

See [INTERVIEW_GUIDE.md](INTERVIEW_GUIDE.md) for:
- Architecture questions with detailed answers
- Implementation details
- Scaling strategies
- Behavioral questions

## File Structure

```
MechautoX/
├── Frontend/
│   ├── GUI.py              # PyQt5 main interface
│   └── Data/
├── Backend/
│   ├── Chatbot.py          # Chat engine
│   ├── OrchestratorAgent.py # Agentic routing
│   ├── RAGSystem.py         # Vector search
│   ├── RealtimeSearchEngine.py # Web search
│   ├── ImageGeneration.py   # Image synthesis
│   ├── SpeechToText.py      # Voice input
│   ├── TextToSpeech.py      # Voice output
│   ├── Automation.py        # System control
│   └── Data/                # FAISS indices
├── Main.py                 # Entry point
├── Requirements.txt        # Dependencies
└── PROJECT_ARCHITECTURE.md # Full documentation
```

## Technologies

| Layer | Technology |
|-------|-----------|
| **Frontend** | PyQt5, HTML/CSS |
| **Backend** | Python, LangChain |
| **LLM** | Groq, Cohere |
| **Vector DB** | FAISS, Sentence-Transformers |
| **Voice** | Edge-TTS, PyAudio |
| **Search** | BeautifulSoup, Requests |

## Configuration

Edit `.env` with your API keys:

```env
# LLM Configuration
GROQ_API_KEY=your_key_here
COHERE_API_KEY=your_key_here

# Username & Assistant Name
Username=Siddhesh
Assistantname=MechautoX
```

## Performance

- ⚡ Vector search: <100ms
- 🚀 Chat response: 1-3 seconds
- 📊 Voice processing: 2-5 seconds
- 🖼️ Image generation: 10-30 seconds

## Future Roadmap

- [ ] Web version (FastAPI + React)
- [ ] Mobile app (React Native)
- [ ] Multi-language support
- [ ] Custom model fine-tuning
- [ ] Collaborative features
- [ ] Enterprise deployment

## Contributing

Contributions welcome! Please:
1. Fork repository
2. Create feature branch (`git checkout -b feature/your-feature`)
3. Commit changes (`git commit -m 'Add feature'`)
4. Push to branch (`git push origin feature/your-feature`)
5. Open Pull Request

## License

MIT License - see [LICENSE](LICENSE) file for details

## Author

Created by Siddhesh Asati

## Support

For issues or questions:
- Open an issue on GitHub
- Check documentation in [PROJECT_ARCHITECTURE.md](PROJECT_ARCHITECTURE.md)
- See [INTERVIEW_GUIDE.md](INTERVIEW_GUIDE.md) for technical deep-dives

---

**⭐ If you find this project helpful, please give it a star!**
```

Then commit and push:
```bash
git add README.md
git commit -m "Add comprehensive README"
git push
```

---

## Step 6: Add License (Optional but Recommended)

Create `LICENSE` file with MIT license text:

```
MIT License

Copyright (c) 2024 Siddhesh Asati

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
```

Then:
```bash
git add LICENSE
git commit -m "Add MIT license"
git push
```

---

## Step 7: Verify .gitignore is Working

Check what will be pushed:
```bash
git status
```

**Should NOT see**:
- ❌ `.venv/` folder
- ❌ `.env` file
- ❌ `__pycache__/` folders
- ❌ `.pyc` files

---

## GitHub Best Practices

### 1. **Add .env.example** (so users know what variables to set):

Create `.env.example`:
```env
# Copy this to .env and fill in your values

# LLM APIs
GROQ_API_KEY=your_groq_key_here
COHERE_API_KEY=your_cohere_key_here

# Configuration
Username=YourName
Assistantname=MechautoX
```

Then:
```bash
git add .env.example
git commit -m "Add environment variables example"
git push
```

### 2. **Create useful branch structure**:
```bash
# Main branches
git branch develop          # Development branch
git branch production       # Production-ready code

# Feature branches (for collaborative work)
git checkout -b feature/rag-improvements
git checkout -b feature/ui-enhancement
```

### 3. **Use meaningful commit messages**:
```
❌ Bad:    git commit -m "fix bug"
✅ Good:   git commit -m "Fix RAG retrieval returning empty results

- Updated FAISS index refresh logic
- Added error handling for corrupted indices
- Fixes issue #42"
```

### 4. **Create Issues for tracking**:
- On GitHub: Issues tab → New Issue
- Label with: bug, feature, documentation, etc.
- Link PRs to issues: "Closes #42"

### 5. **Keep repo organized**:
```
/docs         # Documentation
/examples     # Usage examples
/tests        # Unit tests
/scripts      # Utility scripts
/.github      # GitHub config (CI/CD, templates)
```

---

## Protecting Main Branch (Optional)

### On GitHub:
1. Settings → Branches
2. Add rule for `main`
3. ✅ Require pull request reviews
4. ✅ Require status checks
5. ✅ Dismiss stale reviews

---

## Continuous Integration (Optional but Recommended)

### Create `.github/workflows/python-lint.yml`:

```yaml
name: Python Lint & Test

on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - run: pip install flake8 pytest
      - run: flake8 Backend/ Frontend/ --count --select=E9,F63,F7,F82
      - run: pytest test_system.py
```

---

## Troubleshooting

### Push rejected - "fatal: 'origin' does not appear to be a git repository"
```bash
git remote add origin https://github.com/YourUsername/MechautoX.git
git push -u origin main
```

### Authentication error
```bash
# Regenerate PAT: https://github.com/settings/tokens
# For Windows, update credentials in: Control Panel → Credential Manager
```

### Want to change remote URL
```bash
git remote remove origin
git remote add origin https://github.com/NewUsername/MechautoX.git
```

---

## Summary

✅ **Completed**:
- Git initialized locally
- All files committed (excluding .venv, .env)
- Ready to push to GitHub

✅ **Next Steps**:
1. Create repo on GitHub (https://github.com/new)
2. Copy remote URL
3. Run: `git remote add origin <URL>`
4. Run: `git push -u origin main`
5. Add README.md and LICENSE
6. Set up branch protection (optional)

🎉 **Your project is now on GitHub!**

