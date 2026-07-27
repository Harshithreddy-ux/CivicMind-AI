from backend.agents.base import BaseAgent
from google import genai
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
                return self.format_success(data=self._mock_decision(context, agent_results), summary="Decision Engine completed local mock synthesis.")
            
            client = genai.Client(api_key=api_key)
            model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
            
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
            
            response = await client.aio.models.generate_content(
                model=model_name,
                contents=prompt
            )
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
            return self.format_success(data=self._mock_decision(context, agent_results), summary="Decision Engine fell back to local synthesis.")

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

    def _mock_decision(self, context: dict, agent_results: dict) -> dict:
        """Fully compliant schema mock decision fallback."""
        location = context.get("location", "Unknown City")
        risk_level = "Medium"
        priority = "P2"
        emergency_flag = False
        evidence = []
        recommended_actions = []
        sources = ["Local Telemetry"]
        
        # Check if any agent reported indicators
        for agent_name, result in agent_results.items():
            if result.get("status") == "success":
                data = result.get("data", {})
                sources.append(agent_name)
                
                # Weather data parsing
                if agent_name == "Weather Agent":
                    current = data.get("current", {})
                    temp = current.get("temperature_2m")
                    wind = current.get("wind_speed_10m")
                    if temp is not None:
                        evidence.append(f"Temperature recorded at {temp}°C")
                        if temp >= 38:
                            risk_level = "High"
                            priority = "P1"
                            recommended_actions.append("Issue heat warnings and prepare hydration spots.")
                    if wind is not None:
                        evidence.append(f"Wind speed observed at {wind} km/h")
                        if wind > 30:
                            recommended_actions.append("Advise residents against high-wind exposure.")
                            
                # AQI data parsing
                elif agent_name == "AQI Agent":
                    current = data.get("current", {})
                    aqi_val = current.get("us_aqi")
                    if aqi_val is not None:
                        evidence.append(f"Air quality index reported at {aqi_val}")
                        if aqi_val > 150:
                            risk_level = "High"
                            priority = "P1"
                            recommended_actions.append("Recommend N95 masks for outdoor workers.")
                        elif aqi_val > 100:
                            recommended_actions.append("Sensitive groups should limit prolonged outdoor time.")
                            
                # Crime data parsing
                elif agent_name == "Crime Agent":
                    total_records = data.get("total_records")
                    if total_records is not None:
                        evidence.append(f"Recent crime index has {total_records} local cases.")
                        
                # Hospital data parsing
                elif agent_name == "Hospital Agent":
                    total_hosp = data.get("total_hospitals")
                    if total_hosp is not None:
                        evidence.append(f"Healthcare grid contains {total_hosp} hospital facility hubs.")

        # Default cleanups
        if not evidence:
            evidence = [f"Retrieved baseline indicators for {location}"]
        if not recommended_actions:
            recommended_actions = ["Maintain normal monitoring of emergency networks."]
            
        reasoning = f"Synthesized telemetry indicators for {location} resulting in a {risk_level.lower()}-risk level status."
        
        return {
            "Risk Level": risk_level,
            "Confidence Score": 0.80,
            "Evidence": evidence,
            "Reasoning": reasoning,
            "Priority": priority,
            "Affected Areas": [location],
            "Recommended Actions": recommended_actions,
            "Sources Used": list(set(sources)),
            "Emergency Level": emergency_flag
        }
