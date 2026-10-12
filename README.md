# AI Content Generator Studio

## 1. Project Overview
**AI Content Generator Studio** is a web-based AI writing assistant built with **Python** and **Streamlit**. It produces coherent, high-quality written content across **4 content types** (**Blog Posts, Social Media Captions, Text Summaries, and LinkedIn Thought-Leadership Posts**) and **6 customizable tones** (**Professional, Casual, Enthusiastic, Informative, Persuasive, and Witty**).

---

## 2. Key Features
- **Multiple Content Types**: Supports Blog Posts, Social Media Captions (Instagram/LinkedIn + X/Twitter), Executive Text Summaries, and LinkedIn Posts.
- **Structured Prompt Engineering**: Uses role-based system instructions and dynamic prompt templates stored in `PROMPT_TEMPLATES`.
- **Regenerate & Refine Support**: Users can add refinement instructions and click **Regenerate / Refine** to produce fresh variations.
- **Word & Character Analytics**: Calculates and displays **Word Count**, **Total Character Count**, **Characters (excluding spaces)**, and **Estimated Reading Time**.
- **One-Click Copy & Export**: Includes a built-in copy-to-clipboard code block and `.md` file download button.
- **Error Handling & Multi-Backend Resilience**: Validates empty inputs and handles API timeouts/errors gracefully by falling back to a built-in Smart Local Generator.

---

## 3. API Key Setup Instructions

This application supports **Google Gemini API**, **OpenAI API**, **HuggingFace Inference API**, and an **Offline Smart Local Mode**.

### Option A: Enter API Key Directly in the UI
1. Launch the Streamlit app (`streamlit run app.py`).
2. In the left sidebar under **AI Backend Settings**, choose your provider (**Google Gemini**, **OpenAI**, or **HuggingFace**).
3. Paste your API key into the **API Key** password field.

### Option B: Set API Key via Environment Variables
* **Google Gemini API Key** (Get a free key from Google AI Studio):
  ```bash
  # Windows (PowerShell)
  $env:GEMINI_API_KEY="AIzaSyYourGeminiKeyHere"

  # Linux / macOS
  export GEMINI_API_KEY="AIzaSyYourGeminiKeyHere"