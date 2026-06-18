from typing import Optional

import streamlit as st

from backend.container import get_orchestrator
from backend.orchestrator import SessionEvent, SessionState


def load_session() -> SessionState:
    if "app_session" not in st.session_state:
        st.session_state["app_session"] = SessionState().model_dump(mode="json")
    return SessionState(**st.session_state["app_session"])


def save_session(state: SessionState) -> None:
    st.session_state["app_session"] = state.model_dump(mode="json")


def dispatch(event: SessionEvent, payload: Optional[dict] = None) -> SessionState:
    state = load_session()
    updated = get_orchestrator().handle(state, event, payload or {})
    save_session(updated)
    return updated
