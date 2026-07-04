import re
from typing import Dict, Any, List

class SupervisorAgent:
    def __init__(self):
        # Maps domain keywords to agent names
        self.agent_triggers = {
            "Weather Agent": ["weather", "rain", "monsoon", "temperature", "temp", "hot", "cold", "climate", "precipitation", "average rainfall"],
            "AQI Agent": ["aqi", "air quality", "pollution", "pm2.5", "pm10", "smog", "carbon", "sensor"],
            "Crime Agent": ["crime", "police", "security", "safe", "theft", "assault", "robbery", "incident"],
            "Hospital Agent": ["hospital", "hospitals", "medical", "triage", "doctor", "beds", "clinic", "healthcare", "emergency room"],
            "Flood Agent": ["flood", "flooding", "water level", "river", "inundation", "hydrology", "catchment", "wettest month"],
            "Population Agent": ["population", "people", "demographics", "density", "residents", "inhabitants"],
            "GIS Agent": ["gis", "map", "coordinates", "location", "spatial", "district", "bounds", "layer", "osm"],
            "Traffic Agent": ["traffic", "congestion", "route", "road", "block", "jam", "speed", "vehicle"],
            "Environment Agent": ["environment", "green", "carbon", "ecological", "forest", "tree", "air exposure"]
        }

    def route_query(self, query: str) -> Dict[str, Any]:
        """
        Determines which agents are required, routing mode (edge vs cloud), 
        and whether RAG is necessary.
        """
        query_lower = query.lower()
        required_agents = []

        # 1. Match agents by keywords
        for agent_name, keywords in self.agent_triggers.items():
            if any(re.search(rf"\b{kw}\b", query_lower) for kw in keywords):
                required_agents.append(agent_name)

        # Fallback: if no specific agents matched, run minimal standard ones (e.g. Weather, AQI, GIS)
        if not required_agents:
            required_agents = ["Weather Agent", "AQI Agent", "GIS Agent"]

        # 2. Determine routing mode (edge vs cloud)
        # Edge mode for specific direct telemetries/commands, cloud for complex reasoning
        edge_keywords = ["what is", "get current", "show map", "list", "status of", "how many"]
        is_edge = any(query_lower.startswith(kw) or re.search(rf"\b{kw}\b", query_lower) for kw in edge_keywords)
        routing_mode = "edge" if is_edge else "cloud"

        # 3. Determine if RAG should be triggered (Fallback logic: only if structured datasets do not answer)
        # Structured keywords map to local datasets. If queries ask for policy, guidelines, procedures, trigger RAG.
        rag_keywords = ["manual", "policy", "guidelines", "protocol", "procedure", "how to deal", "regulation", "handbook"]
        trigger_rag = any(re.search(rf"\b{kw}\b", query_lower) for kw in rag_keywords)

        return {
            "required_agents": required_agents,
            "routing_mode": routing_mode,
            "trigger_rag": trigger_rag
        }
