import streamlit as st
from content_generator import (
    AIContentGenerator,
    PROMPT_TEMPLATES,
    TONE_MODIFIERS,
    generate_three_sample_outputs
)

st.set_page_config(
    page_title="AI Content Generator Studio",
    page_icon="✍️",
    layout="wide"
)

# Custom CSS for a clean, professional interface (Step 9)
st.markdown(
    """
    <style>
    .main-header {
        background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 1.4rem 1.8rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 1.2rem;
    }
    .main-header h1 {
        color: white !important;
        margin: 0;
        font-size: 2rem;
    }
    .main-header p {
        color: #e0e7ff;
        margin: 0.3rem 0 0 0;
        font-size: 1rem;
    }
    .content-card {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-left: 5px solid #2563eb;
        border-radius: 10px;
        padding: 1.5rem;
        color: #0f172a;
        margin-top: 0.8rem;
        margin-bottom: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="main-header">
        <h1>✍️ AI Content Generator Studio</h1>
        <p>Generate high-quality Blog Posts, Social Media Captions, Text Summaries & Thought Leadership Content</p>
    </div>
    """,
    unsafe_allow_html=True
)

# Initialize session state for history, variations, and output persistence
if "generated_result" not in st.session_state:
    st.session_state.generated_result = None
if "variation_counter" not in st.session_state:
    st.session_state.variation_counter = 1
if "history" not in st.session_state:
    st.session_state.history = []
if "topic_input" not in st.session_state:
    st.session_state.topic_input = (
        "How Generative AI and RAG Are Transforming Customer Support"
    )

# Sidebar: Backend & API Configuration + Preset Topics
with st.sidebar:
    st.header("⚙️ AI Backend Settings")
    backend_choice = st.selectbox(
        "Select AI Provider:",
        [
            "Auto (API if Key Provided, else Smart Local)",
            "Google Gemini API",
            "OpenAI GPT API",
            "HuggingFace Inference API",
            "Smart Local Engine (No API Key Needed)"
        ]
    )
    api_key_input = st.text_input(
        "API Key (Optional for Local Mode):",
        type="password",
        placeholder="Paste AIza... or sk-... or hf_..."
    )
    temperature = st.slider(
        "Creativity (Temperature):",
        min_value=0.1,
        max_value=1.0,
        value=0.7,
        step=0.1
    )

    st.divider()
    st.subheader("🎯 Quick Sample Topics")
    st.caption("Click any preset topic to test diverse domains:")
    if st.button("1. GenAI & RAG in Healthcare", use_container_width=True):
        st.session_state.topic_input = (
            "Generative AI and Retrieval-Augmented Generation (RAG) in Healthcare"
        )
    if st.button("2. Sustainable Electric Vehicles", use_container_width=True):
        st.session_state.topic_input = (
            "The Rise of Electric Vehicles and Smart Battery Management Systems"
        )
    if st.button("3. Morning Cycling & Fitness", use_container_width=True):
        st.session_state.topic_input = (
            "5 Morning Cycling Habits for Mental Clarity and Sustainable Weight Loss"
        )

    st.divider()
    if st.button("📄 Export 3 Sample Topics (.md)", use_container_width=True):
        path = generate_three_sample_outputs()
        st.success(f"Saved `{path}`!")

backend_map = {
    "Auto (API if Key Provided, else Smart Local)": "auto",
    "Google Gemini API": "gemini",
    "OpenAI GPT API": "openai",
    "HuggingFace Inference API": "huggingface",
    "Smart Local Engine (No API Key Needed)": "local"
}

# Main Input Form
col_form, col_output = st.columns([1, 1.25], gap="large")

with col_form:
    st.subheader("1. Configure Your Content Prompt")

    content_type = st.selectbox(
        "Content Type:",
        list(PROMPT_TEMPLATES.keys())
    )
    st.caption(f"ℹ️ *{PROMPT_TEMPLATES[content_type]['description']}*")

    tone = st.selectbox(
        "Select Tone of Voice:",
        list(TONE_MODIFIERS.keys())
    )

    topic = st.text_area(
        "Topic or Source Text:",
        value=st.session_state.topic_input,
        height=120,
        placeholder="Enter a topic (e.g., 'Benefits of Cloud Computing') or paste text to summarize..."
    )

    extra_context = st.text_input(
        "Target Audience / Keywords (Optional):",
        placeholder="e.g., AI Engineers, Tech Enthusiasts, SEO keywords..."
    )

    refinement = st.text_input(
        "Refine / Custom Instructions (Optional):",
        placeholder="e.g., Add more real-world examples, make it more concise..."
    )

    b1, b2 = st.columns(2)
    with b1:
        generate_clicked = st.button(
            "✨ Generate Content",
            type="primary",
            use_container_width=True
        )
    with b2:
        regenerate_clicked = st.button(
            "🔄 Regenerate / Refine",
            use_container_width=True
        )

    # Error handling for empty input (Step 8)
    if generate_clicked or regenerate_clicked:
        if not topic or not topic.strip():
            st.error("⚠️ Please enter a valid Topic or Source Text before generating content.")
        else:
            if regenerate_clicked:
                st.session_state.variation_counter += 1
            else:
                st.session_state.variation_counter = 1

            generator = AIContentGenerator(
                backend=backend_map[backend_choice],
                api_key=api_key_input
            )
            try:
                result = generator.generate(
                    topic=topic,
                    content_type=content_type,
                    tone=tone,
                    extra_context=extra_context,
                    refinement=refinement,
                    temperature=temperature,
                    variation=st.session_state.variation_counter
                )
                st.session_state.generated_result = result
                st.session_state.history.insert(
                    0,
                    {
                        "topic": topic.strip()[:50],
                        "type": content_type,
                        "tone": tone,
                        "words": result["metrics"]["words"],
                        "time": result["timestamp"]
                    }
                )
            except Exception as err:
                st.error(f"Error generating content: {err}")

    with st.expander("🔍 View Engineered Prompt Template"):
        if topic.strip():
            temp_gen = AIContentGenerator()
            sys_role, built_prompt = temp_gen.build_prompt(
                topic, content_type, tone, extra_context, refinement
            )
            st.code(f"System Role: {sys_role}\n\n{built_prompt}", language="text")

with col_output:
    st.subheader("2. Generated Content & Analytics")

    res = st.session_state.generated_result
    if res is None:
        st.info(
            "👈 Enter a topic on the left and click **Generate Content** "
            "to view your AI-generated output, word/character metrics, and copy options."
        )
    else:
        if res.get("warning"):
            st.warning(res["warning"])

        # Step 7: Word and Character Count Display
        metrics = res["metrics"]
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Word Count", f"{metrics['words']}")
        m2.metric("Character Count", f"{metrics['characters']}")
        m3.metric("Chars (No Spaces)", f"{metrics['characters_no_spaces']}")
        m4.metric("Est. Read Time", f"{metrics['reading_time_sec']} sec")

        st.caption(
            f"✅ Generated via **{res['backend_used']}** | "
            f"Variation #{st.session_state.variation_counter} | {res['timestamp']}"
        )

        # Formatted Readable Preview
        st.markdown("### 📖 Formatted Preview")
        st.markdown(res["content"])

        st.divider()

        # Step 6: Copy-to-Clipboard & Download Section
        st.markdown(
            "### 📋 Copy to Clipboard "
            "*(Click the copy icon in the top-right corner of the box below)*"
        )
        st.code(res["content"], language="markdown")

        st.download_button(
            label="📥 Download Generated Content (.md)",
            data=res["content"].encode("utf-8"),
            file_name=f"{content_type.lower().replace(' ', '_')}_output.md",
            mime="text/markdown",
            use_container_width=True
        )