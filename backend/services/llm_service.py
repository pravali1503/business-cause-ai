
import os
import streamlit as st
from groq import Groq


MODEL_NAME = "openai/gpt-oss-120b"


def get_groq_api_key():
    try:
        api_key = st.secrets.get("GROQ_API_KEY", "")
    except Exception:
        api_key = ""

    if not api_key:
        api_key = os.getenv("GROQ_API_KEY", "")

    if not api_key or api_key == "your_groq_api_key_here":
        raise ValueError(
            "Groq API key is missing. Add your key to "
            ".streamlit/secrets.toml."
        )

    return api_key


def generate_business_insight(question, analysis_context, chat_history=None):

    if not question or not question.strip():
        raise ValueError("Please enter a question.")

    if not isinstance(analysis_context, dict) or not analysis_context:
        raise ValueError(
            "No investigation results are available. "
            "Perform a business analysis first."
        )

    api_key = get_groq_api_key()

    client = Groq(api_key=api_key)

    system_prompt = """
You are RootCause AI, a business data analysis assistant.

Your job is to explain business investigation results in simple English.

IMPORTANT RULES:

1. Use only the investigation information provided by the application.
2. Never invent sales values, percentages, dates, or segment names.
3. Python calculates all business metrics. You only explain the results.
4. Clearly distinguish observations from possible explanations.
5. Never claim that a contribution proves causation.
6. If information is missing, clearly mention that.
7. Give practical suggestions based on the available evidence.
8. Use simple English and clear headings.
9. If the user asks something unrelated to the supplied business data,
   explain that you can help with the current investigation.
10. Never execute Python code, SQL queries, or external commands.
"""

    messages = [
        {
            "role": "system",
            "content": system_prompt
        }
    ]

    if chat_history:
        for message in chat_history[-6:]:
            if message.get("role") in ["user", "assistant"]:
                messages.append({
                    "role": message["role"],
                    "content": str(message.get("content", ""))[:3000]
                })

    user_message = f"""
INVESTIGATION RESULTS:

{str(analysis_context)[:12000]}

USER QUESTION:

{question}

Explain the answer using only the investigation results above.
Mention when the available data is insufficient.
"""

    messages.append({
        "role": "user",
        "content": user_message
    })

    try:

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.2,
            max_completion_tokens=1000
        )

        answer = response.choices[0].message.content

        if not answer:
            raise ValueError("The AI returned an empty response.")

        return answer.strip()

    except Exception as error:

        raise RuntimeError(
            f"Unable to generate business insights: {error}"
        ) from error
