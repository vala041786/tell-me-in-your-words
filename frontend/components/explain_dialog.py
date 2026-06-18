import streamlit as st

from backend.orchestrator.session import ExplainView, SessionEvent
from frontend.session_store import dispatch


@st.dialog("Explain & expert context", width="large")
def render_explain_dialog(view: ExplainView):
    context = view.expert_context

    st.markdown(f"## {view.term}")
    st.caption(f"{context.icon} {context.domain.title()} · routed to {context.expert_type.lower()}")
    st.markdown(view.explanation)

    st.markdown(f"### {context.icon} Expert context")
    st.info(context.routing_message)
    st.markdown(f"**Who can help:** {context.expert_type}")
    st.markdown("**Suggested next steps**")
    for step in context.next_steps:
        st.write(f"- {step}")

    st.markdown(f"### {context.resource_label}")
    st.link_button(
        f"Open {view.source_name}",
        view.source_url,
        use_container_width=True,
    )

    st.markdown("### Helpful follow-up questions")
    st.caption("Tap a question to continue in this expert context.")
    for question in view.followups:
        is_selected = question == view.selected_followup
        if st.button(
            question,
            key=f"followup_{view.term}_{question}",
            type="primary" if is_selected else "secondary",
        ):
            dispatch(SessionEvent.ASK_FOLLOWUP, {"question": question})
            st.rerun()

    if view.followup_guidance:
        st.markdown("#### Follow-up guidance")
        st.markdown(view.followup_guidance)

    st.markdown(f"### {context.consult_label}")
    st.write(context.consult_prompt)

    if view.consult_submitted:
        st.success(context.consult_success)
        if view.care_links:
            st.markdown("#### Find care near you")
            st.caption("These links open a map search in your browser. This app does not book appointments.")
            for link in view.care_links:
                st.link_button(link.label, link.url, use_container_width=True)
    else:
        with st.form(f"consult_{view.term}", clear_on_submit=False):
            concern = st.text_area(
                "Your concern",
                value=view.consult_concern or "",
                height=100,
                placeholder="Example: I have a painful rash on one side and I'm not sure if it's urgent.",
            )
            submitted = st.form_submit_button(context.consult_cta, type="primary", use_container_width=True)
            if submitted:
                dispatch(SessionEvent.REQUEST_CONSULT, {"concern": concern})
                st.rerun()

    st.caption(view.safety_note)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Choose a different match", key="back_to_suggestions", use_container_width=True):
            dispatch(SessionEvent.BACK_TO_SUGGESTIONS)
            st.rerun()
    with col2:
        if st.button("Close", key="close_explain", use_container_width=True, type="primary"):
            dispatch(SessionEvent.CLOSE_EXPLAIN)
            st.rerun()
