# AI Code Reviewer  
**Day 9 of 30 Days of Generative AI**

An AI-powered code reviewer that can summarize, explain, and improve any code in multiple programming languages using Groq Llama 3.3 — all inside a modern, resizable Gradio interface.

---

## Features
- Multi-language support – Works with Python, Java, C++, JavaScript, and more.  
- Summarize and explain – Generates clear, beginner-friendly explanations in seconds.  
- Upload or paste code – Review your code directly or upload a file.  
- Download output – Save AI-reviewed code as a readable text file.  
- Clear all button – Instantly resets the interface.  
- Resizable output panel – Adjustable like an IDE console window.  

---

## Tech Stack
- Frontend: Gradio (custom layout and responsive resizing)  
- Backend: Groq API (Llama 3.3)  
- Environment: Python 3.10+, dotenv for secure key management  

---

## Setup
```bash
git clone https://github.com/jlsonon/ai-code-reviewer.git
cd ai-code-reviewer
pip install -r requirements.txt
```

## Create a .env file:
```bash
GROQ_API_KEY=your_api_key_here
```

## Run the app:
```bash
python app.py
```

---
## Project Structure
```bash
ai-code-reviewer/
│
├── app.py              # Main Gradio application  
├── requirements.txt    # Dependencies  
├── .env                # API Key (not included)  
└── README.md           # Documentation
```

---

## Deployment
- Easily deploy on Hugging Face Spaces.
- Deployment Demo: https://huggingface.co/spaces/jlsonon/day9-codereview

---
## Author

### Jericho Sonon
#### Medium: medium.com/@jlsonon12
#### GitHub: github.com/jlsonon
#### LinkedIn: linkedin.com/in/jlsonon

