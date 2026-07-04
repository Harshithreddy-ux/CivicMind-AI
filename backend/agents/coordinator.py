import asyncio
import json
from typing import Dict, Any

from backend.agents.weather_agent import WeatherAgent
from backend.agents.aqi_agent import AQIAgent
from backend.agents.crime_agent import CrimeAgent
from backend.agents.hospital_agent import HospitalAgent
from backend.agents.flood_agent import FloodAgent
from backend.agents.other_agents import PopulationAgent, GISAgent
from backend.agents.traffic_agent import TrafficAgent
from backend.agents.environment_agent import EnvironmentAgent
from backend.agents.decision_agent import DecisionAgent
from backend.agents.supervisor import SupervisorAgent
from backend.rag.retriever import rag_system

class CoordinatorAgent:
    def __init__(self):
        self.agents = {
            "Weather Agent": WeatherAgent(),
            "AQI Agent": AQIAgent(),
            "Crime Agent": CrimeAgent(),
            "Hospital Agent": HospitalAgent(),
            "Flood Agent": FloodAgent(),
            "Population Agent": PopulationAgent(),
            "GIS Agent": GISAgent(),
            "Traffic Agent": TrafficAgent(),
            "Environment Agent": EnvironmentAgent()
        }
        self.decision_agent = DecisionAgent()
        self.supervisor = SupervisorAgent()
        
    async def process_query_stream(self, query: str, location: str = "Unknown"):
        """
        An async generator that yields progress updates formatted as SSE data,
        then finally yields the aggregated response.
        """
        context = {"query": query, "location": location}
        
        # 1. Run Supervisor Agent Routing
        yield '{"agent": "Supervisor Agent", "status": "running"}'
        routing = self.supervisor.route_query(query)
        context["routing"] = routing
        yield f'{{"agent": "Supervisor Agent", "status": "done", "routing": {json.dumps(routing)}}}'
        
        required_agents = routing["required_agents"]
        trigger_rag = routing["trigger_rag"]

        # 2. RAG System initialization and querying if triggered
        if trigger_rag:
            yield '{"agent": "RAG System", "status": "running"}'
            try:
                await rag_system.initialize_async()
                rag_context = await rag_system.query_async(query)
                context["rag_context"] = rag_context
                yield '{"agent": "RAG System", "status": "done"}'
            except Exception as e:
                yield '{"agent": "RAG System", "status": "error"}'
                print(f"RAG Error: {e}")
        else:
            context["rag_context"] = "RAG not required (structured data sufficient)."

        # 3. Run selected specialized agents concurrently
        tasks = []
        agent_names = []
        
        for name in required_agents:
            if name in self.agents:
                yield f'{{"agent": "{name}", "status": "running"}}'
                tasks.append(self.agents[name].process(context))
                agent_names.append(name)
            
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
        else:
            results = []
        
        agent_results = {}
        for name, result in zip(agent_names, results):
            if isinstance(result, Exception):
                agent_results[name] = {"status": "error", "message": str(result)}
                yield f'{{"agent": "{name}", "status": "error"}}'
            else:
                agent_results[name] = result
                yield f'{{"agent": "{name}", "status": "done"}}'
                
        # 4. Decision Engine
        yield '{"agent": "Decision Engine", "status": "running"}'
        context["agent_results"] = agent_results
        decision_result = await self.decision_agent.process(context)
        yield '{"agent": "Decision Engine", "status": "done"}'
        
        # 5. Final output
        final_payload = {
            "type": "final_decision",
            "data": decision_result.get("data", {})
        }
        yield json.dumps(final_payload)
