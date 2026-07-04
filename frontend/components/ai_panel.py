import json
import requests
import streamlit as st
from components.cards import BACKEND

def show_ai_panel(weather, aqi, city, question=None):
    st.markdown(
        """
<style>
details {
    background: #1E1E1E;
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 8px;
    margin-bottom: 8px;
    padding: 12px;
}
summary {
    font-size: 0.85rem;
    font-weight: 600;
    color: #A5B6D6;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    cursor: pointer;
    outline: none;
}
summary:hover {
    color: #00FFFF;
}
details[open] summary {
    margin-bottom: 10px;
    color: #00E5FF;
}
</style>
<div class='ai-shell' style='background: #181818; border: 1px solid rgba(0, 229, 255, 0.15); border-radius: 12px; padding: 1.5rem; box-shadow: 0 10px 30px rgba(0,0,0,0.4);'>
<div class='ai-title-row' style='display:flex; align-items:center; gap:10px; margin-bottom:1.2rem;'>
<div class='title-icon' style='width:32px;height:32px;background:rgba(0, 229, 255, 0.1);color:#00E5FF;display:flex;align-items:center;justify-content:center;border-radius:8px;font-size:1.1rem;'>🤖</div>
<h4 style='margin:0; font-size:1.1rem; color:#fff;'>AI Command Center</h4>
</div>
        """,
        unsafe_allow_html=True,
    )
    
    status_placeholder = st.empty()
    results_placeholder = st.empty()
    
    agents_status = {}
    report = None
    
    try:
        with requests.post(
            f"{BACKEND}/ai/stream",
            json={
                "city": city,
                "weather": weather or {},
                "aqi": aqi or {},
                "risk_score": 50,
                "question": question,
            },
            stream=True,
            timeout=30,
        ) as r:
            for line in r.iter_lines():
                if line:
                    decoded = line.decode('utf-8')
                    if decoded.startswith('data: '):
                        data_str = decoded[6:]
                        try:
                            payload = json.loads(data_str)
                            if "agent" in payload:
                                agents_status[payload["agent"]] = payload["status"]
                                
                                # Render inline horizontal status checklist
                                checklist_items = []
                                for agent, status in agents_status.items():
                                    if status == "done":
                                        checklist_items.append(f"<span style='color:#00E5FF;'>[✓] {agent}</span>")
                                    elif status == "error":
                                        checklist_items.append(f"<span style='color:#FF5D73;'>[✗] {agent}</span>")
                                    else:
                                        checklist_items.append(f"<span style='color:#A5B6D6;'>[⏳] {agent}</span>")
                                        
                                checklist_html = f"""
                                <div style='font-size:0.8rem; line-height:1.6;'>
                                    <div style='color:#00FFFF; font-weight:600; margin-bottom:6px;'>Thinking...</div>
                                    <div style='display:flex; flex-wrap:wrap; gap:8px 12px; margin-bottom:8px;'>
                                        {" | ".join(checklist_items)}
                                    </div>
                                    <div style='color:#A5B6D6; font-style:italic;'>-> Synthesizing Final Recommendation</div>
                                </div>
                                """
                                status_placeholder.markdown(checklist_html, unsafe_allow_html=True)
                                
                            elif payload.get("type") == "final_decision":
                                report = payload.get("data", {})
                        except json.JSONDecodeError:
                            continue
    except Exception as e:
        status_placeholder.error(f"Error connecting to AI Orchestrator: {e}")
 
    if report:
        status_placeholder.empty()  # Clear checklist
        
        # Parse fields with robust fallbacks matching new Decision schema
        risk_level = report.get("Risk Level", "Medium")
        conf_score = report.get("Confidence Score", report.get("Confidence", 0.75))
        priority = report.get("Priority", "P2")
        reasoning = report.get("Reasoning", "No reasoning summary provided.")
        emerg_level = report.get("Emergency Level", False)
        
        # Color indicator based on Risk Level
        risk_colors = {"Low": "#00E5FF", "Medium": "#FFD700", "High": "#FF8C00", "Critical": "#FF5D73"}
        risk_color = risk_colors.get(risk_level, "#A5B6D6")
        
        # format emergency alert banner if critical
        alert_banner = ""
        if emerg_level:
            alert_banner = f"""
            <div style='background:rgba(255, 93, 115, 0.15); border:1px solid #FF5D73; border-radius:8px; padding:10px; margin-bottom:12px; color:#FF5D73; font-weight:bold; font-size:0.85rem; text-align:center;'>
                🚨 SYSTEM-WIDE EMERGENCY ALERT ACTIVE
            </div>
            """

        actions_markup = "".join(f"<li style='margin-bottom:6px; font-size:0.85rem; color:#fff;'>{action}</li>" for action in report.get("Recommended Actions", []))
        evidence_markup = "".join(f"<li style='margin-bottom:6px; font-size:0.85rem; color:#A5B6D6;'>{item}</li>" for item in report.get("Evidence", []))
        sources_markup = "".join(f"<span style='background:rgba(255,255,255,0.05); padding:3px 8px; border-radius:4px; margin-right:6px; font-size:0.75rem; color:#A5B6D6;'>{src}</span>" for src in report.get("Sources Used", ["Telemetry"]))

        results_placeholder.markdown(
            f"""
{alert_banner}
<div class='report-grid' style='display:grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 12px;'>
<div class='evidence-card' style='background:#1E1E1E; border:1px solid rgba(255,255,255,0.02); padding:10px; border-radius:8px; text-align:center;'>
<div class='report-label' style='font-size:0.75rem; color:#A5B6D6; text-transform:uppercase;'>Risk Level</div>
<div class='report-value' style='font-size:1.15rem; font-weight:bold; color:{risk_color};'>{risk_level}</div>
</div>
<div class='evidence-card' style='background:#1E1E1E; border:1px solid rgba(255,255,255,0.02); padding:10px; border-radius:8px; text-align:center;'>
<div class='report-label' style='font-size:0.75rem; color:#A5B6D6; text-transform:uppercase;'>Confidence</div>
<div class='report-value' style='font-size:1.15rem; font-weight:bold; color:#00E5FF;'>{int(conf_score * 100)}%</div>
</div>
</div>

<div class='report-grid' style='display:grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 12px;'>
<div class='evidence-card' style='background:#1E1E1E; border:1px solid rgba(255,255,255,0.02); padding:10px; border-radius:8px; text-align:center;'>
<div class='report-label' style='font-size:0.75rem; color:#A5B6D6; text-transform:uppercase;'>Priority</div>
<div class='report-value' style='font-size:1.1rem; font-weight:bold; color:#00FFFF;'>{priority}</div>
</div>
<div class='evidence-card' style='background:#1E1E1E; border:1px solid rgba(255,255,255,0.02); padding:10px; border-radius:8px; text-align:center;'>
<div class='report-label' style='font-size:0.75rem; color:#A5B6D6; text-transform:uppercase;'>Areas Affected</div>
<div class='report-value' style='font-size:0.9rem; font-weight:bold; color:#fff; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;'>{", ".join(map(str, report.get("Affected Areas", ["Region"])))}</div>
</div>
</div>

<details>
<summary>Telemetry Evidence</summary>
<ul class='ai-actions' style='margin:10px 0 0 15px; padding:0;'>{evidence_markup}</ul>
</details>

<details>
<summary>Reasoning Protocol</summary>
<div style='font-size:0.85rem; color:#A5B6D6; line-height:1.4;'>{reasoning}</div>
</details>

<details open>
<summary>Recommended Action Plan</summary>
<ul class='ai-actions' style='margin:10px 0 0 15px; padding:0;'>{actions_markup}</ul>
</details>

<div style='margin-top:12px; display:flex; flex-wrap:wrap; gap:4px;'>
{sources_markup}
</div>
</div>
            """,
            unsafe_allow_html=True,
        )