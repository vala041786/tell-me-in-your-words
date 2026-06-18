import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

from backend.orchestrator import SessionEvent, SessionStep
from frontend.components.explain_dialog import render_explain_dialog
from frontend.session_store import dispatch, load_session

EXAMPLES = [
    "I think I have fingles",
    "That paper that keeps secrets",
    "I want company baskets",
    "Ho una strana eruzione cutanea dolorosa",
    "Mujhe daane wali bimari hai",
]

SAMPLE_HINTS = [
    "I think I have fingles",
    "That paper that keeps secrets",
    "I want company baskets",
    "My head hurts when the light is bright",
    "I need to protect my business name",
    "Painful rash on one side of my body",
    "Itchy dry skin that will not go away",
    "I want to invest in a basket of companies",
    "Ho una strana eruzione cutanea dolorosa",
    "Mujhe daane wali bimari hai",
    "That legal paper before sharing my idea",
    "Money I put away for retirement tax-free",
]

INPUT_HEIGHT = 280


def _build_placeholder(examples: list[str]) -> str:
    half = (len(examples) + 1) // 2
    left = examples[:half]
    right = examples[half:]
    lines = ["Examples you can describe in your own words:\n"]
    for i in range(max(len(left), len(right))):
        left_line = f"• {left[i]}" if i < len(left) else ""
        right_line = f"• {right[i]}" if i < len(right) else ""
        if left_line and right_line:
            lines.append(f"{left_line}    {right_line}")
        else:
            lines.append(left_line or right_line)
    return "\n".join(lines)


PLACEHOLDER_TEXT = _build_placeholder(SAMPLE_HINTS)

st.set_page_config(page_title="Tell Me In Your Words", page_icon="💬", layout="centered")

st.markdown(
    """
    <style>
    div[data-testid="stTextArea"] textarea::placeholder {
        color: #9ca3af;
        opacity: 1;
    }
    div[data-testid="stTextArea"] [data-testid="InputInstructions"] {
        display: none !important;
    }
    .field-label {
        font-size: 0.875rem;
        font-weight: 400;
        color: rgb(49, 51, 63);
        margin: 0 0 0.35rem 0;
        min-height: 1.25rem;
        line-height: 1.25rem;
    }
    .field-label-hint {
        font-size: 0.6rem;
        font-style: italic;
        font-weight: 400;
        color: rgb(115, 117, 125);
    }
    div[data-testid="stVerticalBlockBorderWrapper"] {
        width: 100%;
    }
    div[data-testid="stExpander"] {
        width: 100%;
        margin-top: 0;
    }
    div[data-testid="stExpander"] summary {
        min-height: 2.5rem;
        display: flex;
        align-items: center;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

session = load_session()

if session.show_explain_modal and session.explain_view:
    render_explain_dialog(session.explain_view)

st.title("Tell Me In Your Words")
st.subheader("You don't need the right words.")
st.write("Describe it your way. We'll help find the term, explain it, and route you to the right expert context.")

input_col, examples_col = st.columns(2, gap="large", vertical_alignment="top")

with input_col:
    st.markdown(
        '<p class="field-label">Your words '
        '<span class="field-label-hint">(Click the box and start typing)</span></p>',
        unsafe_allow_html=True,
    )
    query = st.text_area(
        "Your words",
        value=session.user_query,
        height=INPUT_HEIGHT,
        placeholder=PLACEHOLDER_TEXT,
        label_visibility="collapsed",
    )

with examples_col:
    st.markdown(
        '<p class="field-label">Try examples '
        '<span class="field-label-hint">(Select the options from dropdown)</span></p>',
        unsafe_allow_html=True,
    )
    with st.container(border=True, height=INPUT_HEIGHT):
        with st.expander("Choose a sample", expanded=False):
            for example in EXAMPLES:
                if st.button(example, key=f"example_{example}", use_container_width=True):
                    dispatch(SessionEvent.SET_EXAMPLE, {"query": example})
                    st.rerun()

_, center_col, _ = st.columns([1, 3, 1])
with center_col:
    if st.button("Find what I mean", type="primary", use_container_width=True) and query.strip():
        dispatch(SessionEvent.SUBMIT_QUERY, {"query": query})
        st.rerun()

session = load_session()

if session.step == SessionStep.SUGGESTIONS and session.has_suggestions:
    st.markdown("### You might mean")
    st.caption("Choose the option that sounds closest. No pressure — close enough is a good start.")
    for item in session.suggestions:
        confidence = int(item.confidence * 100)
        with st.container(border=True):
            st.markdown(f"**{item.term}** · {item.domain.title()} · {confidence}% match")
            st.write(item.definition)
            st.caption(f"Matched phrase: {item.matched_alias}")
            if st.button(f"Yes, explain {item.term}", key=f"explain_{item.term}"):
                dispatch(SessionEvent.CONFIRM_TERM, {"term": item.term})
                st.rerun()

elif session.step == SessionStep.SUGGESTIONS and session.user_query:
    st.info(session.message)

st.markdown("---")
st.caption("MVP v0.2 · Orchestrator + local agents · English, Hindi, Marathi, Italian starter aliases")
