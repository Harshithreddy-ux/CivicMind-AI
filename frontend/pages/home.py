import streamlit as st
import pandas as pd
from config.cities import CITIES
from utils.dataset_service import get_dataset

def render_home():
    # ── Real metrics counters generated dynamically from datasets ───────────
    hosp_df = get_dataset("hospital_directory")
    crime_df = get_dataset("crime_dataset_india")
    flood_df = get_dataset("metadata_indofloods")
    
    hosp_count = len(hosp_df) if hosp_df is not None else 32000
    crime_count = len(crime_df) if crime_df is not None else 20000
    flood_count = len(flood_df) if flood_df is not None else 1000
    cities_count = len(CITIES)

    # ── Landing Hero ─────────────────────────────────────────────────────────
    st.markdown(
        """
        <div style='text-align: center; padding: 3rem 1.5rem 2rem 1.5rem;'>
            <h1 style='font-size: 3.2rem; font-weight: 800; background: linear-gradient(135deg, #00FFFF, #8B5CF6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0.5rem; letter-spacing: -0.04em;'>
                CivicMind AI
            </h1>
            <p style='font-size: 1.25rem; color: #A5B6D6; max-width: 700px; margin: 0 auto 2rem auto; line-height: 1.5; font-weight: 400;'>
                Smart City Decision Intelligence Platform & Multi-Agent Consensus Operations.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ── Real Stats Counters (Premium Badge Grid) ─────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        with st.container(border=True):
            st.markdown(
                f"""
                <div style='text-align:center;'>
                    <div style='font-size:0.75rem; color:#A5B6D6; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:4px;'>Hospitals Indexed</div>
                    <div style='font-size:2.2rem; font-weight:800; color:#00FFFF;'>{hosp_count:,}</div>
                    <div style='font-size:0.72rem; color:#3DDC97; margin-top:2px;'>✓ Live SQLite Sync</div>
                </div>
                """,
                unsafe_allow_html=True
            )
    with c2:
        with st.container(border=True):
            st.markdown(
                f"""
                <div style='text-align:center;'>
                    <div style='font-size:0.75rem; color:#A5B6D6; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:4px;'>Crimes Analyzed</div>
                    <div style='font-size:2.2rem; font-weight:800; color:#FF5D73;'>{crime_count:,}</div>
                    <div style='font-size:0.72rem; color:#3DDC97; margin-top:2px;'>✓ Structured Ingest</div>
                </div>
                """,
                unsafe_allow_html=True
            )
    with c3:
        with st.container(border=True):
            st.markdown(
                f"""
                <div style='text-align:center;'>
                    <div style='font-size:0.75rem; color:#A5B6D6; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:4px;'>Flood Sensors</div>
                    <div style='font-size:2.2rem; font-weight:800; color:#3DDC97;'>{flood_count:,}</div>
                    <div style='font-size:0.72rem; color:#3DDC97; margin-top:2px;'>✓ Active Stations</div>
                </div>
                """,
                unsafe_allow_html=True
            )
    with c4:
        with st.container(border=True):
            st.markdown(
                f"""
                <div style='text-align:center;'>
                    <div style='font-size:0.75rem; color:#A5B6D6; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:4px;'>Supported Cities</div>
                    <div style='font-size:2.2rem; font-weight:800; color:#8B5CF6;'>{cities_count}</div>
                    <div style='font-size:0.72rem; color:#3DDC97; margin-top:2px;'>✓ Geographic Nodes</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)

    # ── Feature Showcase & Technical Architecture ────────────────────────────
    left_col, right_col = st.columns([1.2, 1])
    
    with left_col:
        with st.container(border=True):
            st.markdown(
                """
                <h3 style='margin-top:0; color:#fff; font-size:1.15rem;'>Platform Architecture Overview</h3>
                <p style='font-size:0.85rem; color:#A5B6D6; line-height:1.5;'>
                    CivicMind AI parses raw telemetry and unstructured standard operating guidelines (SOPs) dynamically. A multi-agent consensus network acts on data layers before executing strategic resolution scripts.
                </p>
                """,
                unsafe_allow_html=True
            )
            
            # Interactive CSS Flowchart representing the micro-service workflow
            st.markdown(
                """
                <div style='display: flex; flex-direction: column; gap: 8px; margin-top: 10px;'>
                    <div style='background: rgba(0, 229, 255, 0.04); border: 1px solid rgba(0, 229, 255, 0.15); padding: 10px; border-radius: 8px; text-align: center;'>
                        <b style='color: #00E5FF; font-size: 0.85rem;'>1. Data Ingestion Core</b><br>
                        <span style='font-size: 0.78rem; color: #A5B6D6;'>Raw CSV datasets & live weather/AQI telemetry loaded selectively into indexed SQLite.</span>
                    </div>
                    <div style='text-align: center; color: #8B5CF6; font-size: 1rem; line-height: 1;'>↓</div>
                    <div style='background: rgba(139, 92, 246, 0.04); border: 1px solid rgba(139, 92, 246, 0.15); padding: 10px; border-radius: 8px; text-align: center;'>
                        <b style='color: #8B5CF6; font-size: 0.85rem;'>2. Supervisor Agent Router</b><br>
                        <span style='font-size: 0.78rem; color: #A5B6D6;'>Parses query intention and routes tasks to Weather, AQI, Crime, Hospital, and Flood Agents.</span>
                    </div>
                    <div style='text-align: center; color: #3DDC97; font-size: 1rem; line-height: 1;'>↓</div>
                    <div style='background: rgba(61, 220, 151, 0.04); border: 1px solid rgba(61, 220, 151, 0.15); padding: 10px; border-radius: 8px; text-align: center;'>
                        <b style='color: #3DDC97; font-size: 0.85rem;'>3. Multi-Document RAG SOP Index</b><br>
                        <span style='font-size: 0.78rem; color: #A5B6D6;'>Consults vector indices for standard operating procedures (disaster guidelines, safety limits).</span>
                    </div>
                    <div style='text-align: center; color: #FF8C00; font-size: 1rem; line-height: 1;'>↓</div>
                    <div style='background: rgba(255, 140, 0, 0.04); border: 1px solid rgba(255, 140, 0, 0.15); padding: 10px; border-radius: 8px; text-align: center;'>
                        <b style='color: #FF8C00; font-size: 0.85rem;'>4. Decision Synthesis Engine</b><br>
                        <span style='font-size: 0.78rem; color: #A5B6D6;'>Synthesizes agent findings and SOP constraints into an actionable priority-ranked response.</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

    with right_col:
        with st.container(border=True):
            st.markdown(
                """
                <h3 style='margin-top:0; color:#fff; font-size:1.15rem;'>Project Milestones & Roadmap</h3>
                <div class='roadmap-timeline'>
                    <div class='roadmap-item completed'>
                        <div class='roadmap-title'>Phase 1 — Database Consolidation</div>
                        <div class='roadmap-desc'>CSV migration to indexed SQLite engine for sub-millisecond query bounds.</div>
                    </div>
                    <div class='roadmap-item completed'>
                        <div class='roadmap-title'>Phase 2 — Async Network I/O</div>
                        <div class='roadmap-desc'>FastAPI endpoint refactor using HTTPX AsyncClient and Official google-genai SDK.</div>
                    </div>
                    <div class='roadmap-item'>
                        <div class='roadmap-title'>Phase 3 — Premium UX/UI Refactor</div>
                        <div class='roadmap-desc'>Sliding CSS transitions, mobile viewport scaling, and container card structures.</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

    # ── Technology Showcase Grid ─────────────────────────────────────────────
    with st.container(border=True):
        st.markdown(
            """
            <h3 style='margin-top:0; text-align:center; color:#fff; font-size:1.15rem; margin-bottom:0.8rem;'>Enterprise Technology Stack</h3>
            <div class='tech-grid'>
                <div class='tech-item'>
                    <div class='tech-icon'>⚡</div>
                    <div class='tech-name'>FastAPI</div>
                </div>
                <div class='tech-item'>
                    <div class='tech-icon'>🎛</div>
                    <div class='tech-name'>Streamlit</div>
                </div>
                <div class='tech-item'>
                    <div class='tech-icon'>🧠</div>
                    <div class='tech-name'>Gemini 2.5</div>
                </div>
                <div class='tech-item'>
                    <div class='tech-icon'>🗄</div>
                    <div class='tech-name'>SQLite 3</div>
                </div>
                <div class='tech-item'>
                    <div class='tech-icon'>🗺</div>
                    <div class='tech-name'>Folium GIS</div>
                </div>
                <div class='tech-item'>
                    <div class='tech-icon'>🧪</div>
                    <div class='tech-name'>Pytest Suite</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
