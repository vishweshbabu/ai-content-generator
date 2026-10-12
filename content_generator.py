import os
import re
import json
import random
import urllib.request
import urllib.error
from datetime import datetime


# =====================================================================
# 1. DOCUMENTED PROMPT TEMPLATES FOR EACH CONTENT TYPE
# =====================================================================
PROMPT_TEMPLATES = {
    "Blog Post": {
        "description": (
            "Generates a structured, SEO-friendly blog article with a "
            "catchy title, introduction, key takeaways, body sections, "
            "and a conclusion."
        ),
        "system_role": (
            "You are an expert content writer and SEO blog strategist."
        ),
        "template": (
            "Write a comprehensive, engaging blog post about the topic: "
            "'{topic}'.\n"
            "Target Tone: {tone}\n"
            "Additional Context / Keywords: {extra_context}\n"
            "Refinement Instructions: {refinement}\n\n"
            "Structure your blog post with:\n"
            "1. An attention-grabbing Headline (H1)\n"
            "2. An engaging Introduction that hooks the reader\n"
            "3. 3 to 4 well-structured Subheadings (H2) with actionable "
            "insights and examples\n"
            "4. A bulleted 'Key Takeaways' section\n"
            "5. A strong Conclusion with a Call-to-Action (CTA)"
        )
    },
    "Social Media Caption": {
        "description": (
            "Creates engaging social media captions tailored for "
            "Instagram, LinkedIn, and X/Twitter with hooks, emojis, "
            "call-to-action, and trending hashtags."
        ),
        "system_role": (
            "You are a viral social media manager and digital marketer."
        ),
        "template": (
            "Create a high-converting social media caption pack for the "
            "topic: '{topic}'.\n"
            "Target Tone: {tone}\n"
            "Additional Context / Keywords: {extra_context}\n"
            "Refinement Instructions: {refinement}\n\n"
            "Include:\n"
            "1. Scroll-Stopping Hook (first line)\n"
            "2. Engaging Body Copy with relevant emojis\n"
            "3. Clear Call-to-Action (CTA) encouraging comments/shares\n"
            "4. 8 to 12 relevant, high-reach Hashtags"
        )
    },
    "Text Summary": {
        "description": (
            "Condenses a complex topic or long passage into an executive "
            "summary, core bullet points, and a 1-sentence TL;DR."
        ),
        "system_role": (
            "You are an executive research analyst skilled at distilling "
            "complex topics into clear, concise summaries."
        ),
        "template": (
            "Provide a clear, structured summary of the following topic "
            "or text: '{topic}'.\n"
            "Target Tone: {tone}\n"
            "Additional Focus: {extra_context}\n"
            "Refinement Instructions: {refinement}\n\n"
            "Format the output as:\n"
            "1. Executive Overview (1 concise paragraph)\n"
            "2. Key Highlights (4 to 5 bullet points)\n"
            "3. Core Impact / Why It Matters\n"
            "4. TL;DR (1 punchy sentence)"
        )
    },
    "LinkedIn / Thought Leadership Post": {
        "description": (
            "Produces a professional thought-leadership post formatted "
            "with short punchy lines, industry insights, and a question "
            "to drive professional engagement."
        ),
        "system_role": (
            "You are an industry thought leader and executive ghostwriter."
        ),
        "template": (
            "Write a compelling LinkedIn thought-leadership post on: "
            "'{topic}'.\n"
            "Target Tone: {tone}\n"
            "Additional Context / Keywords: {extra_context}\n"
            "Refinement Instructions: {refinement}\n\n"
            "Include:\n"
            "1. Bold opening statement\n"
            "2. Short, readable paragraphs explaining the problem & shift\n"
            "3. 3 actionable lessons or industry predictions\n"
            "4. An engaging closing question for the comments + 5 hashtags"
        )
    }
}

TONE_MODIFIERS = {
    "Professional": {
        "intro_prefix": "In today's rapidly evolving landscape,",
        "style_adj": "strategic, authoritative, and results-driven",
        "cta": "Share your professional perspective in the comments below."
    },
    "Casual": {
        "intro_prefix": "Let's be real for a second—",
        "style_adj": "friendly, relatable, and easy-to-digest",
        "cta": "Drop your thoughts below! Always fun hearing what you think."
    },
    "Enthusiastic": {
        "intro_prefix": "Big things are happening right now!",
        "style_adj": "high-energy, inspiring, and forward-looking",
        "cta": "Try this out today and let us know how it transforms your workflow!"
    },
    "Informative": {
        "intro_prefix": "Understanding the fundamentals is key:",
        "style_adj": "clear, evidence-based, and educational",
        "cta": "Bookmark this guide for future reference and share it with your team."
    },
    "Persuasive": {
        "intro_prefix": "If you aren't paying attention to this shift, you're missing out:",
        "style_adj": "compelling, action-oriented, and high-impact",
        "cta": "Take action today—start implementing these steps right away."
    },
    "Witty": {
        "intro_prefix": "Grab your coffee, because things just got interesting:",
        "style_adj": "clever, sharp, and entertaining",
        "cta": "Agree, disagree, or have a better hot take? Sound off below!"
    }
}


# =====================================================================
# 2. AI CONTENT GENERATOR CLASS (Multi-Backend + Error Handling)
# =====================================================================
class AIContentGenerator:
    def __init__(self, backend="auto", api_key=None):
        self.backend = backend
        self.api_key = (
            api_key
            or os.environ.get("GEMINI_API_KEY")
            or os.environ.get("OPENAI_API_KEY")
            or os.environ.get("HF_API_KEY")
            or ""
        ).strip()

    def build_prompt(
        self,
        topic,
        content_type="Blog Post",
        tone="Professional",
        extra_context="",
        refinement=""
    ):
        """Constructs a structured prompt from the documented template."""
        if not topic or not topic.strip():
            raise ValueError("Topic cannot be empty. Please enter a valid topic.")

        template_info = PROMPT_TEMPLATES.get(
            content_type, PROMPT_TEMPLATES["Blog Post"]
        )
        prompt_text = template_info["template"].format(
            topic=topic.strip(),
            tone=tone,
            extra_context=extra_context.strip() if extra_context else "General audience",
            refinement=refinement.strip() if refinement else "None"
        )
        return template_info["system_role"], prompt_text

    @staticmethod
    def compute_metrics(text):
        """Computes word count, character count, and estimated reading time."""
        clean_text = text.strip()
        if not clean_text:
            return {
                "words": 0,
                "characters": 0,
                "characters_no_spaces": 0,
                "reading_time_sec": 0
            }
        words = re.findall(r"\S+", clean_text)
        word_count = len(words)
        char_count = len(clean_text)
        char_no_spaces = len(re.sub(r"\s+", "", clean_text))
        reading_sec = max(5, int(round((word_count / 200.0) * 60)))
        return {
            "words": word_count,
            "characters": char_count,
            "characters_no_spaces": char_no_spaces,
            "reading_time_sec": reading_sec
        }

    # -----------------------------------------------------------------
    # API Callers (Google Gemini, OpenAI, HuggingFace)
    # -----------------------------------------------------------------
    def _call_gemini_api(self, system_role, prompt_text, temperature=0.7):
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"gemini-1.5-flash:generateContent?key={self.api_key}"
        )
        payload = {
            "contents": [
                {"parts": [{"text": f"{system_role}\n\n{prompt_text}"}]}
            ],
            "generationConfig": {"temperature": temperature, "maxOutputTokens": 1024}
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["candidates"][0]["content"]["parts"][0]["text"]

    def _call_openai_api(self, system_role, prompt_text, temperature=0.7):
        url = "https://api.openai.com/v1/chat/completions"
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": system_role},
                {"role": "user", "content": prompt_text}
            ],
            "temperature": temperature
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            },
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"]

    def _call_huggingface_api(self, system_role, prompt_text, temperature=0.7):
        url = (
            "https://api-inference.huggingface.co/models/"
            "mistralai/Mistral-7B-Instruct-v0.3"
        )
        full_prompt = f"<s>[INST] {system_role}\n\n{prompt_text} [/INST]"
        payload = {
            "inputs": full_prompt,
            "parameters": {
                "max_new_tokens": 700,
                "temperature": temperature,
                "return_full_text": False
            }
        }
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if isinstance(data, list) and data:
                return data[0].get("generated_text", "").strip()
            return str(data)

    # -----------------------------------------------------------------
    # Built-in Smart Local Generator (Guaranteed Offline / Fallback Mode)
    # -----------------------------------------------------------------
    def _generate_local_smart_content(
        self, topic, content_type, tone, extra_context="", refinement="", variation=1
    ):
        clean_topic = topic.strip()
        tone_cfg = TONE_MODIFIERS.get(tone, TONE_MODIFIERS["Professional"])
        keywords = [
            w.capitalize()
            for w in re.findall(r"[A-Za-z0-9]+", clean_topic)
            if len(w) > 3
        ]
        hashtags = [f"#{w}" for w in keywords[:5]] + [
            "#AI", "#Innovation", "#FutureTrends", "#DigitalGrowth", "#TechInsights"
        ]
        unique_tags = " ".join(dict.fromkeys(hashtags))

        angles = [
            ("Practical Implementation", "turning core concepts into measurable daily workflows"),
            ("Strategic Advantage", "leveraging modern tools to stay ahead of industry shifts"),
            ("Future-Proofing & Scale", "building sustainable systems that adapt to long-term growth")
        ]
        if variation > 1:
            random.shuffle(angles)

        extra_note = (
            f"\n*Context Focus: Tailored for {extra_context.strip()}.*\n"
            if extra_context and extra_context.strip()
            else ""
        )
        refine_note = (
            f"\n> **Refinement Applied ({refinement.strip()}):** Content "
            f"optimized with a {tone_cfg['style_adj']} emphasis.\n"
            if refinement and refinement.strip()
            else ""
        )

        if content_type == "Blog Post":
            title_variants = [
                f"# The Complete Guide to {clean_topic}: Strategies, Impact & Future Outlook",
                f"# Mastering {clean_topic}: Why It Matters and How to Succeed",
                f"# How {clean_topic} Is Reshaping the Modern Landscape"
            ]
            headline = title_variants[(variation - 1) % len(title_variants)]
            return (
                f"{headline}\n"
                f"{extra_note}{refine_note}\n"
                f"## Introduction\n"
                f"{tone_cfg['intro_prefix']} **{clean_topic}** has emerged as one of the "
                f"most transformative focus areas in its domain. Adopting a "
                f"{tone_cfg['style_adj']} approach to {clean_topic} empowers individuals "
                f"and organizations to unlock higher efficiency, deeper insights, and "
                f"sustainable results.\n\n"
                f"## 1. Core Foundations of {clean_topic}\n"
                f"At its heart, {clean_topic} bridges the gap between traditional methods "
                f"and modern optimization. By focusing on {angles[0][1]}, teams can "
                f"eliminate bottlenecks and establish a strong operational baseline.\n\n"
                f"## 2. {angles[1][0]} and Real-World Applications\n"
                f"When applying {clean_topic} in real-world scenarios, the biggest gains "
                f"come from {angles[1][1]}. Key areas of impact include:\n"
                f"- **Enhanced Decision-Making:** Using structured data and clear metrics.\n"
                f"- **Scalable Workflows:** Automating repetitive tasks to focus on high-value creative work.\n"
                f"- **Measurable ROI:** Tracking quality, speed, and user satisfaction continuously.\n\n"
                f"## 3. Best Practices for {angles[2][0]}\n"
                f"To get the most out of {clean_topic}, focus on {angles[2][1]}. Start with "
                f"small, measurable milestones, gather feedback early, and iterate rapidly.\n\n"
                f"## Key Takeaways\n"
                f"* **Start with Clear Goals:** Define what success looks like for {clean_topic}.\n"
                f"* **Stay Adaptive:** Combine foundational principles with modern tools.\n"
                f"* **Measure & Iterate:** Continuously refine your process based on real outcomes.\n\n"
                f"## Conclusion\n"
                f"{clean_topic} is more than just a passing trend—it is a foundational pillar "
                f"for long-term success. {tone_cfg['cta']}"
            )

        elif content_type == "Social Media Caption":
            hooks = [
                f"🚀 Ready to level up your approach to **{clean_topic}**?",
                f"💡 Most people overcomplicate **{clean_topic}**—here is what actually works!",
                f"🔥 Stop scrolling if you care about **{clean_topic}**!"
            ]
            chosen_hook = hooks[(variation - 1) % len(hooks)]
            return (
                f"### 📸 Instagram / LinkedIn Caption\n"
                f"{chosen_hook}\n\n"
                f"{tone_cfg['intro_prefix']} mastering **{clean_topic}** doesn't have to be "
                f"overwhelming. When you focus on {angles[0][1]}, the results speak for "
                f"themselves! ✨\n"
                f"{extra_note}{refine_note}\n"
                f"Here are 3 quick wins to keep in mind today:\n"
                f"1️⃣ Focus on consistency and {angles[0][0].lower()}.\n"
                f"2️⃣ Leverage smart workflows for {angles[1][0].lower()}.\n"
                f"3️⃣ Keep learning and iterating for {angles[2][0].lower()}.\n\n"
                f"💬 **{tone_cfg['cta']}**\n"
                f"🔖 Save this post for later & share it with a friend!\n\n"
                f"{unique_tags}\n\n"
                f"---\n"
                f"### 🐦 Short X (Twitter) Version\n"
                f"{chosen_hook} Focus on {angles[0][1]} and watch your workflow transform. "
                f"{tone_cfg['cta']} { ' '.join(hashtags[:4]) }"
            )

        elif content_type == "Text Summary":
            return (
                f"# Executive Summary: {clean_topic}\n"
                f"{extra_note}{refine_note}\n"
                f"### 📌 Overview\n"
                f"{tone_cfg['intro_prefix']} **{clean_topic}** represents a critical area "
                f"of focus characterized by {angles[0][1]} and {angles[1][1]}. This "
                f"{tone_cfg['style_adj']} summary distills the primary concepts, core "
                f"benefits, and strategic takeaways.\n\n"
                f"### 🎯 Key Highlights\n"
                f"* **Primary Objective:** Streamlining processes and maximizing impact "
                f"through {clean_topic}.\n"
                f"* **Core Mechanism:** Combines {angles[0][0].lower()} with "
                f"{angles[1][0].lower()}.\n"
                f"* **Operational Benefit:** Reduces manual overhead while improving "
                f"accuracy, speed, and consistency.\n"
                f"* **Long-Term Value:** Supports {angles[2][1]} across diverse teams.\n\n"
                f"### 💡 Why It Matters\n"
                f"Organizations and professionals who effectively adopt {clean_topic} "
                f"gain a measurable edge in productivity, adaptability, and decision quality.\n\n"
                f"### ⚡ TL;DR\n"
                f"**{clean_topic}** drives measurable growth and efficiency by combining "
                f"{angles[0][1]} with {angles[2][1]}."
            )

        else:  # LinkedIn / Thought Leadership Post
            return (
                f"**{tone_cfg['intro_prefix']} {clean_topic} is changing faster than ever.**\n\n"
                f"Over the past year, I've noticed a major shift in how top performers "
                f"approach **{clean_topic}**.\n"
                f"{extra_note}{refine_note}\n"
                f"It's no longer just about working harder—it's about {angles[0][1]}.\n\n"
                f"Here are 3 lessons that stand out:\n\n"
                f"🔹 **1. {angles[0][0]}:** Build repeatable habits before scaling complexity.\n"
                f"🔹 **2. {angles[1][0]}:** Focus on {angles[1][1]} to create real value.\n"
                f"🔹 **3. {angles[2][0]}:** Invest in {angles[2][1]}.\n\n"
                f"The future belongs to those who combine curiosity with execution.\n\n"
                f"👇 {tone_cfg['cta']}\n\n"
                f"{unique_tags}"
            )

    # -----------------------------------------------------------------
    # Main Generation Entry Point with Full Error Handling
    # -----------------------------------------------------------------
    def generate(
        self,
        topic,
        content_type="Blog Post",
        tone="Professional",
        extra_context="",
        refinement="",
        temperature=0.7,
        variation=1
    ):
        system_role, prompt_text = self.build_prompt(
            topic, content_type, tone, extra_context, refinement
        )

        used_backend = "Smart Local NLP Engine (Offline/Template Mode)"
        api_warning = None
        content = ""

        # Try chosen live API if key is provided
        if self.api_key and self.backend != "local":
            try:
                if self.backend in ("gemini", "auto") and self.api_key.startswith("AIza"):
                    content = self._call_gemini_api(
                        system_role, prompt_text, temperature
                    )
                    used_backend = "Google Gemini API (gemini-1.5-flash)"
                elif self.backend in ("openai", "auto") and self.api_key.startswith("sk-"):
                    content = self._call_openai_api(
                        system_role, prompt_text, temperature
                    )
                    used_backend = "OpenAI API (gpt-4o-mini)"
                elif self.backend in ("huggingface", "auto"):
                    content = self._call_huggingface_api(
                        system_role, prompt_text, temperature
                    )
                    used_backend = "HuggingFace Inference API (Mistral-7B)"
            except urllib.error.HTTPError as e:
                api_warning = (
                    f"API HTTP Error ({e.code}): Switched automatically to "
                    f"Smart Local Generator so your workflow is uninterrupted."
                )
            except Exception as e:
                api_warning = (
                    f"API Connection Notice ({str(e)[:60]}): Switched to "
                    f"Smart Local Generator."
                )

        if not content.strip():
            content = self._generate_local_smart_content(
                topic=topic,
                content_type=content_type,
                tone=tone,
                extra_context=extra_context,
                refinement=refinement,
                variation=variation
            )

        metrics = self.compute_metrics(content)
        return {
            "content": content,
            "prompt_used": prompt_text,
            "backend_used": used_backend,
            "warning": api_warning,
            "metrics": metrics,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }


# =====================================================================
# 3. DELIVERABLE GENERATOR: SAMPLE OUTPUTS FOR 3 DIFFERENT TOPICS
# =====================================================================
def generate_three_sample_outputs(output_file="sample_outputs_3_topics.md"):
    """Generates sample outputs for 3 distinct topics across content types and tones."""
    gen = AIContentGenerator(backend="local")
    samples = [
        {
            "topic": "Generative AI and Retrieval-Augmented Generation (RAG) in Healthcare",
            "content_type": "Blog Post",
            "tone": "Professional",
            "extra_context": "Clinical decision support, medical accuracy, hospital workflows"
        },
        {
            "topic": "5 Morning Cycling Habits for Mental Clarity and Sustainable Fitness",
            "content_type": "Social Media Caption",
            "tone": "Enthusiastic",
            "extra_context": "Daily fitness enthusiasts, outdoor cycling, healthy lifestyle"
        },
        {
            "topic": "The Shift Toward Remote AI Engineering Teams and Global Collaboration",
            "content_type": "Text Summary",
            "tone": "Informative",
            "extra_context": "Async productivity, cloud development environments, global talent"
        }
    ]

    lines = [
        "# AI Content Generator — Sample Outputs for 3 Diverse Topics\n",
        f"*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n---\n"
    ]

    for idx, item in enumerate(samples, 1):
        res = gen.generate(
            topic=item["topic"],
            content_type=item["content_type"],
            tone=item["tone"],
            extra_context=item["extra_context"],
            variation=idx
        )
        m = res["metrics"]
        lines.append(f"## Sample #{idx}: {item['content_type']} ({item['tone']} Tone)\n")
        lines.append(f"- **Topic:** {item['topic']}\n")
        lines.append(f"- **Context / Keywords:** {item['extra_context']}\n")
        lines.append(
            f"- **Metrics:** {m['words']} Words | {m['characters']} Characters | "
            f"~{m['reading_time_sec']} sec read\n\n"
        )
        lines.append("### Generated Output:\n")
        lines.append(res["content"] + "\n\n---\n")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return output_file


if __name__ == "__main__":
    out_path = generate_three_sample_outputs()
    print(f"[SUCCESS] Generated 3 diverse topic samples in '{out_path}'!")