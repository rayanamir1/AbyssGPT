# ui/chat.py
import streamlit as st
from datetime import datetime
from logic.core import handle_query


def render_chat(height=520):
    demo_prompts = [
        "Where are the best mining zones with low coral impact?",
        "Which area has the highest danger for submarines?",
        "Explain why this region is important for biodiversity."
    ]

    # ---------------------------
    # Init state
    # ---------------------------
    if "messages" not in st.session_state:
        st.session_state.messages = [{
            "role": "assistant",
            "content": "Hi, I'm **AbyssGPT**. Ask me anything about the deep sea.",
            "time": _now()
        }]

    st.subheader("🌊 AbyssGPT")

    # ---------------------------
    # Chat history UI
    # ---------------------------
    try:
        chat_window = st.container(height=height, border=True)
    except TypeError:
        chat_window = st.container()

    with chat_window:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                st.caption(msg.get("time", ""))

    # ---------------------------
    # Demo buttons
    # ---------------------------
    cols = st.columns(3)
    for i, p in enumerate(demo_prompts):
        with cols[i]:
            if st.button(p, use_container_width=True, key=f"demo_{i}"):
                _add_user_message(p)
                _call_backend(p)
                st.rerun()

    # ---------------------------
    # Chat input
    # ---------------------------
    user_text = st.chat_input("Ask AbyssGPT…")

    if user_text:
        _add_user_message(user_text)
        _call_backend(user_text)
        st.rerun()


# ---------------------------
# Helpers
# ---------------------------
def _add_user_message(text):
    st.session_state.messages.append(
        {"role": "user", "content": text, "time": _now()}
    )

def _call_backend(text):
    result = handle_query(text)
    st.session_state.last_payload = result

    # Compose structured reply: main answer + source + key bullets
    answer = result.get("answer", "I couldn't generate an answer.")
    source = result.get("source", "Abyssal data layers")
    important = result.get("important_info", [])

    lines = [answer, f"- Where the data was found: {source}"]
    if important:
        lines.append("- Important info:")
        lines.extend([f"  - {item}" for item in important])

    formatted = "\n".join(lines)
    st.session_state.messages.append(
        {"role": "assistant", "content": formatted, "time": _now()}
    )


def _add_assistant_placeholder(user_text: str):
    canned = [
        "Good question — once the backend is wired, I'll analyze the Abyssal data layers.",
        "Noted. When connected, I’ll return a heatmap and key stats.",
        "Got it — this will map to an intent and generate a response soon."
    ]
    idx = abs(hash(user_text)) % len(canned)

    st.session_state.messages.append(
        {"role": "assistant", "content": canned[idx], "time": _now()}
    )

def _now() -> str:
    return datetime.now().strftime("%H:%M")
