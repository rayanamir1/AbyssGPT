# ui/chat.py
import streamlit as st
from datetime import datetime
from logic.core import handle_query


def render_chat(height=520):
    """
    AbyssGPT chat UI only (native Streamlit bubbles + scrollable window if supported).
    - Uses st.chat_message for clean look
    - Tries to render inside fixed-height scroll container
    - Falls back safely if Streamlit version doesn't support height containers
    - No backend yet
    """

    # ---------------------------
    # Session state init
    # ---------------------------
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "Hi, I’m **AbyssGPT**. Ask me about hazards, biodiversity, "
                    "mining zones, or deep-sea routes."
                ),
                "time": _now()
            }
        ]

    st.subheader("🌊 AbyssGPT")

    # ---------------------------
    # Scrollable native chat window (best-effort)
    # ---------------------------
    try:
        # Newer Streamlit: fixed-height scroll box
        chat_window = st.container(height=height, border=True)
    except TypeError:
        # Older Streamlit: no height arg, fallback to normal container
        chat_window = st.container()

    with chat_window:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                st.caption(msg.get("time", ""))

    # ---------------------------
    # Demo prompts
    # ---------------------------
    demo_prompts = [
        "Where are the best mining zones with low coral impact?",
        "Which area has the highest danger for submarines?",
        "Explain why this region is important for biodiversity."
    ]

    cols = st.columns(3)
    for i, p in enumerate(demo_prompts):
        with cols[i]:
            if st.button(p, use_container_width=True):
                _add_user_message(p)
                _add_assistant_placeholder(p)

    # ---------------------------
    # Input (native)
    # ---------------------------
    user_text = st.chat_input("Ask AbyssGPT…")

    if user_text and user_text.strip():
        _add_user_message(user_text.strip())
        _add_assistant_placeholder(user_text.strip())


# ---------------------------
# Helpers (UI only)
# ---------------------------
def _add_user_message(text: str):
    st.session_state.messages.append(
        {"role": "user", "content": text, "time": _now()}
    )

def _call_backend(user_text: str):
    """
    Send the user's text to the backend (logic.core.handle_query),
    store the payload for the map, and add the assistant's reply to the chat.
    """
    result = handle_query(user_text)

    # Save the full payload so the map panel can read it
    st.session_state.last_payload = result

    # Get the answer text for the chat
    answer = result.get("answer", "I couldn't generate an answer.")
    st.session_state.messages.append(
        {"role": "assistant", "content": answer, "time": _now()}
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