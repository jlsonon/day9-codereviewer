import gradio as gr
import os
import requests
from dotenv import load_dotenv

# -------------------------------------
# Load environment variables
# -------------------------------------
load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY")
API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.3-70b-versatile"


# -------------------------------------
# Helpers
# -------------------------------------
def read_uploaded_file(file_obj):
    try:
        with open(file_obj.name, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"⚠️ Error reading file: {str(e)}"


def detect_language(code, file_name=None):
    if file_name:
        ext = os.path.splitext(file_name)[1].lower()
        mapping = {
            ".py": "Python", ".js": "JavaScript", ".cpp": "C++", ".cc": "C++", ".c": "C++",
            ".java": "Java", ".html": "HTML", ".htm": "HTML", ".css": "CSS", ".php": "PHP",
            ".cs": "C#", ".rb": "Ruby", ".rs": "Rust", ".go": "Go", ".ts": "TypeScript",
            ".jsx": "JavaScript", ".tsx": "TypeScript", ".txt": "PlainText"
        }
        if ext in mapping:
            return mapping[ext]
    if "def " in code or "import " in code:
        return "Python"
    if "function " in code or "console.log" in code or "=> " in code:
        return "JavaScript"
    if "#include" in code or "int main(" in code:
        return "C++"
    if "public static void main" in code:
        return "Java"
    return "Unknown"


LANG_TO_SHORT = {
    "Python": "python", "JavaScript": "javascript", "C++": "cpp", "Java": "java",
    "HTML": "html", "CSS": "css", "PHP": "php", "C#": "csharp", "Ruby": "ruby",
    "Rust": "rust", "Go": "go", "TypeScript": "typescript", "PlainText": "python",
    "Unknown": "python"
}


# -------------------------------------
# File upload handler
# -------------------------------------
def handle_file_upload(file_obj):
    if file_obj is None:
        return "", LANG_TO_SHORT["Unknown"], "Unknown"
    code = read_uploaded_file(file_obj)
    lang_name = detect_language(code, file_obj.name)
    lang_short = LANG_TO_SHORT.get(lang_name, "python")
    return code, lang_short, lang_name


# -------------------------------------
# Main AI Review Logic
# -------------------------------------
def review_code(code, file, mode, lang_name_state):
    if (not code or not code.strip()) and file is not None:
        code = read_uploaded_file(file)

    if not code or code.startswith("⚠️"):
        return (code if code else "⚠️ Please paste or upload code first."), None
    if not API_KEY:
        return "⚠️ Missing API Key. Please check your .env file.", None

    language = lang_name_state if lang_name_state and lang_name_state != "Unknown" else detect_language(code, file.name if file else None)

    if mode == "Summarize/Explain":
        prompt = f"Provide both a short summary and a beginner-friendly explanation for this {language} code:\n\n{code}"
    elif mode == "Improve":
        prompt = f"Suggest improvements for this {language} code and show the improved version in the SAME {language}:\n\n{code}"
    elif mode == "Optimize":
        prompt = f"Rewrite this {language} code to be more efficient, clean, and professional. Output only {language} code:\n\n{code}"
    else:
        prompt = f"Summarize this {language} code:\n\n{code}"

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": f"You are an expert {language} programmer and AI code reviewer."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2,
        "max_tokens": 1500
    }

    try:
        response = requests.post(
            API_URL,
            headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
            json=payload,
            timeout=60
        )
        data = response.json()
        if "choices" in data and len(data["choices"]) > 0:
            result = data["choices"][0]["message"]["content"].strip()
            safe_ext = {"Python": "py", "JavaScript": "js", "C++": "cpp", "Java": "java"}.get(language, "txt")

            output_filename = f"ai_output.{safe_ext}"
            with open(output_filename, "w", encoding="utf-8") as f:
                f.write(result)
            return result, output_filename
        elif "error" in data:
            return f"❌ API Error: {data['error'].get('message', 'Unknown error')}", None
        else:
            return f"❌ Unexpected API response: {data}", None
    except Exception as e:
        return f"⚠️ Exception: {str(e)}", None


# -------------------------------------
# Clear All Function
# -------------------------------------
def clear_all():
    return "", None, "python", "Unknown", "Summarize/Explain", "", None


# -------------------------------------
# Gradio UI
# -------------------------------------
with gr.Blocks(
    theme=gr.themes.Soft(),
    css="""
    #code_input textarea, #output_text textarea {
        white-space: pre-wrap !important;
        resize: vertical !important; /* Allow vertical resizing like IDE panels */
        overflow-y: auto !important;
        min-height: 300px !important;
        max-height: 800px !important;
        height: 400px !important;
    }
    """
) as app:
    gr.Markdown("# 🤖 AI Code Reviewer & Optimizer")
    gr.Markdown("Analyze, explain, and improve code in multiple programming languages.")

    with gr.Row(equal_height=True):
        # Left column - Input
        with gr.Column(scale=1, min_width=500):
            code_input = gr.Code(
                label="💻 Paste Code Here (or Upload Below)",
                language="python",
                lines=25,
                elem_id="code_input"
            )
            file_input = gr.File(label="📁 Upload Code File",
                                 file_types=[".py", ".js", ".cpp", ".java", ".html", ".css", ".php", ".txt"])
            syntax_state = gr.State("python")
            lang_name_state = gr.State("Unknown")

            file_input.change(handle_file_upload,
                              inputs=[file_input],
                              outputs=[code_input, syntax_state, lang_name_state]) \
                      .then(lambda short: gr.update(language=short),
                            inputs=syntax_state,
                            outputs=code_input)

            mode = gr.Radio(["Summarize/Explain", "Improve", "Optimize"],
                            value="Summarize/Explain", label="Select Mode")

            with gr.Row():
                run_btn = gr.Button("🚀 Run Analysis", variant="primary")
                clear_btn = gr.Button("🧹 Clear All", variant="secondary")

        # Right column - Output
        with gr.Column(scale=1, min_width=500):
            output_text = gr.Textbox(
                label="🧠 AI Output (Resizable Text Window)",
                elem_id="output_text",
                lines=25,
                show_copy_button=True,
                interactive=False
            )
            download_btn = gr.File(label="⬇️ Download AI Output")

    # Button logic
    run_btn.click(review_code,
                  inputs=[code_input, file_input, mode, lang_name_state],
                  outputs=[output_text, download_btn])

    clear_btn.click(clear_all,
                    outputs=[code_input, file_input, syntax_state,
                             lang_name_state, mode, output_text, download_btn])

    gr.Markdown("---")
    gr.Markdown("Built by **jlsonon** · Day 9 of 30 Days of Generative AI Journey")

if __name__ == "__main__":
    app.launch()
