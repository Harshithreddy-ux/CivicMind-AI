import streamlit as st
from components.ai_panel import show_ai_panel

def render_assistant(selected_city, weather, aqi):
    st.markdown("## AI Assistant")
    st.caption("Grounded decision support with a visible reasoning workflow and cached telemetry.")

    question = st.text_input("Ask CivicMind AI", value=f"Why is {selected_city} at elevated risk today?")
    if st.button("Analyze"):
        st.session_state["assistant_context"] = {
            "question": question
        }

    context = st.session_state.get("assistant_context")
    if context:
        st.success("Reasoning initialized. Streaming telemetry and agent data...")
        question_to_pass = context["question"]
    else:
        question_to_pass = None

    show_ai_panel(weather, aqi, selected_city, question=question_to_pass)
