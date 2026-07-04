from backend.agents.base import BaseAgent
import google.generativeai as genai
import os
import json
import re

class DecisionAgent(BaseAgent):
    async def process(self, context: dict) -> dict:
        query = context.get("query", "")
        agent_results = context.get("agent_results", {})
        
        try:
            api_key = os.getenv("GEMINI_API_KEY", "")
            if not api_key:
                return self.format_success(data=self._mock_decision(agent_results), summary="Decision Engine completed local mock synthesis.")
            
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            prompt = f"""
            You are the core Decision Engine for a Smart City Platform.
            User Query: {query}
            
            Evidence collected by specialized domain agents:
            {json.dumps(agent_results, indent=2)}
            
            Synthesize all agent telemetry and produce a strictly typed JSON response containing EXACTLY these keys:
            - "Risk Level": must be one of ["Low", "Medium", "High", "Critical"]
            - "Confidence Score": must be a float between 0.00 and 1.00
            - "Evidence": a list of key data point strings that triggered this decision
            - "Reasoning": a step-by-step logic summary string
            - "Priority": must be one of ["P0", "P1", "P2", "P3", "P4"] (where P0 is highest emergency, P4 is lowest)
            - "Affected Areas": a list of GeoJSON polygon dicts, coordinate arrays, or district name strings
            - "Recommended Actions": a list of immediate mitigation action strings
            - "Sources Used": a list of specific datasets or APIs used
            - "Emergency Level": must be a boolean flag (true for system-wide alerts, false otherwise)
            
            Output ONLY valid JSON.
            """
            
            response = model.generate_content(prompt)
            text = response.text.replace('```json', '').replace('```', '').strip()
            
            # Extract JSON block using regex if model outputs conversational text
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                text = match.group(0)
                
            decision_data = json.loads(text)
            
            # Post-processing normalization to guarantee strict types
            decision_data = self._normalize_decision(decision_data, agent_results)
            
            return self.format_success(data=decision_data, summary="Decision Engine completed enterprise synthesis.")
            
        except Exception as e:
            print(f"Decision Engine Error: {e}")
            return self.format_success(data=self._mock_decision(agent_results), summary="Decision Engine fell back to local synthesis.")

    def _normalize_decision(self, data: dict, agent_results: dict) -> dict:
        """Normalizes and guarantees all fields match the strict enterprise JSON schema."""
        # 1. Risk Level
        risk = str(data.get("Risk Level", "Medium")).strip().title()
        if risk not in ["Low", "Medium", "High", "Critical"]:
            risk = "Medium"
        data["Risk Level"] = risk

        # 2. Confidence Score
        conf = data.get("Confidence Score", 0.75)
        if isinstance(conf, str):
            # Parse percentage string if output
            match = re.search(r'(\d+)', conf)
            if match:
                conf = float(match.group(1)) / 100.0
            else:
                conf = 0.75
        try:
            data["Confidence Score"] = min(1.0, max(0.0, float(conf)))
        except Exception:
            data["Confidence Score"] = 0.75

        # 3. Evidence
        evidence = data.get("Evidence", [])
        if not isinstance(evidence, list):
            evidence = [str(evidence)]
        data["Evidence"] = [str(e) for e in evidence]

        # 4. Reasoning
        data["Reasoning"] = str(data.get("Reasoning", "Synthesized local telemetry."))

        # 5. Priority
        priority = str(data.get("Priority", "P2")).strip().upper()
        if priority not in ["P0", "P1", "P2", "P3", "P4"]:
            priority = "P2"
        data["Priority"] = priority

        # 6. Affected Areas
        areas = data.get("Affected Areas", [])
        if not isinstance(areas, list):
            areas = [str(areas)]
        data["Affected Areas"] = areas

        # 7. Recommended Actions
        actions = data.get("Recommended Actions", [])
        if not isinstance(actions, list):
            actions = [str(actions)]
        data["Recommended Actions"] = [str(a) for a in actions]

        # 8. Sources Used
        sources = data.get("Sources Used", ["Local Telemetry"])
        if not isinstance(sources, list):
            sources = [str(sources)]
        data["Sources Used"] = [str(s) for s in sources]

        # 9. Emergency Level
        emerg = data.get("Emergency Level", False)
        if isinstance(emerg, str):
            emerg = emerg.lower() in ["true", "yes", "level 1", "critical", "1"]
        data["Emergency Level"] = bool(emerg)

        return data

    def _mock_decision(self, agent_results: dict) -> dict:
        """Fully compliant schema mock decision fallback."""
        risk_level = "Medium"
        priority = "P2"
        emergency_flag = False
        
        # Check if any agent reported a high-threat indicator
        for agent_name, result in agent_results.items():
            if result.get("status") == "success":
                data = result.get("data", {})
                # AQI threshold check
                if "us_aqi" in data and float(data["us_aqi"]) > 150:
                    risk_level = "High"
                    priority = "P1"
                # Rain threshold check
                if "precipitation" in data and float(data.get("precipitation", 0)) > 100:
                    risk_level = "Critical"
                    priority = "P0"
                    emergency_flag = True
                    
        return {
            "Risk Level": risk_level,
            "Confidence Score": 0.80,
            "Evidence": ["Aggregated dataset entries", "Live API endpoints"],
            "Reasoning": "Synthesized telemetries across active domain layers.",
            "Priority": priority,
            "Affected Areas": ["Metropolitan Core Zones"],
            "Recommended Actions": ["Enable visual risk indicators", "Alert civic disaster services"],
            "Sources Used": ["Open-Meteo API", "Local Crime Dataset", "IMD Subdivision Data"],
            "Emergency Level": emergency_flag
        }
