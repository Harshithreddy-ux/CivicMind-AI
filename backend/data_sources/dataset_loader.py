import pandas as pd
import os
import logging
from typing import Dict, Any, List
from database.db_manager import DatabaseManager

logger = logging.getLogger("civicmind.loader")

# Global cache for datasets and validation status
_VALIDATION_STATUS = {}
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'datasets')

# Comprehensive alias map to normalize India state/UT names (matching dataset_service.py)
_STATE_ALIASES = {
    "jammu & kashmir": "Jammu and Kashmir",
    "jammu and kashmir": "Jammu and Kashmir",
    "j&k": "Jammu and Kashmir",
    "jk": "Jammu and Kashmir",
    "andaman & nicobar islands": "Andaman and Nicobar Islands",
    "andaman and nicobar islands": "Andaman and Nicobar Islands",
    "andaman & nicobar": "Andaman and Nicobar Islands",
    "andaman nicobar": "Andaman and Nicobar Islands",
    "dadra & nagar haveli": "Dadra and Nagar Haveli",
    "dadra and nagar haveli": "Dadra and Nagar Haveli",
    "dadra & nagar haveli and daman & diu": "Dadra and Nagar Haveli",
    "daman & diu": "Daman and Diu",
    "daman and diu": "Daman and Diu",
    "orissa": "Odisha",
    "odisha": "Odisha",
    "pondicherry": "Puducherry",
    "puducherry": "Puducherry",
    "uttaranchal": "Uttarakhand",
    "uttarakhand": "Uttarakhand",
    "ua": "Uttarakhand",
    "north twenty four parganas": "West Bengal",
    "nct of delhi": "Delhi",
    "new delhi": "Delhi",
    "ncr": "Delhi",
    "delhi": "Delhi",
    "ladakh": "Ladakh",
    "lakshadweep": "Lakshadweep",
    "chandigarh": "Chandigarh",
}

def normalize_state_name(state: str) -> str:
    if not state or str(state).strip().lower() in ("nan", "none", ""):
        return ""
    val = str(state).strip().lower()
    if val in _STATE_ALIASES:
        return _STATE_ALIASES[val]
    val = val.replace("&", "and")
    val = " ".join(val.split())
    return val.title()

def verify_all_datasets() -> Dict[str, Any]:
    """Startup verification suite to check if SQLite is ready."""
    global _VALIDATION_STATUS
    try:
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        for tab in ["hospitals", "crimes", "flood_events", "catchment", "metadata", "subdivision_rainfall"]:
            if tab in tables:
                _VALIDATION_STATUS[tab] = {"status": "valid", "readable": True}
            else:
                _VALIDATION_STATUS[tab] = {"status": "missing", "error": "Table not found"}
    except Exception as e:
        logger.error(f"Dataset verification failed: {e}")
        
    return _VALIDATION_STATUS

def get_validation_warnings() -> List[str]:
    warnings = []
    for tab, val in _VALIDATION_STATUS.items():
        if val.get("status") != "valid":
            warnings.append(f"Warning: Database table '{tab}' is {val.get('status')} ({val.get('error', 'unknown error')}).")
    return warnings

def _query_to_df(sql: str, params: tuple = ()) -> pd.DataFrame:
    """Loads a DataFrame directly from SQLite."""
    conn = DatabaseManager.get_connection()
    try:
        return pd.read_sql_query(sql, conn, params=params)
    except Exception as e:
        logger.error(f"Error executing database DataFrame query: {e}")
        return pd.DataFrame()

def load_crime_data(location: str = None) -> pd.DataFrame:
    """Loads crime data. If location is provided, queries SQLite selectively."""
    if location:
        # Resolve location mapping to city
        from backend.agents.crime_agent import STATE_TO_CRIME_CITY
        crime_city = STATE_TO_CRIME_CITY.get(location)
        if crime_city:
            return _query_to_df("SELECT * FROM crimes WHERE lower(city) = ?", (crime_city.lower(),))
        else:
            return _query_to_df("SELECT * FROM crimes WHERE lower(city) = ?", (location.lower(),))
    return _query_to_df("SELECT * FROM crimes")

def load_hospital_data(location: str = None) -> pd.DataFrame:
    """Loads hospital directory data. If location is provided, queries SQLite selectively."""
    if location:
        norm_loc = normalize_state_name(location)
        df = _query_to_df("SELECT * FROM hospitals WHERE state = ?", (norm_loc,))
        if df.empty and norm_loc:
            first_word = norm_loc.split()[0].lower()
            df = _query_to_df("SELECT * FROM hospitals WHERE lower(state) LIKE ?", (f"%{first_word}%",))
        return df
    return _query_to_df("SELECT * FROM hospitals")

def load_flood_data(location: str = None) -> dict:
    """Loads flood events, metadata, and catchment characteristics for a specific location."""
    if location:
        state_norm = normalize_state_name(location)
        
        # Filter metadata by state
        metadata_df = _query_to_df("SELECT * FROM metadata WHERE State = ?", (location,))
        if metadata_df.empty and state_norm:
            first_word = state_norm.split()[0].lower()
            metadata_df = _query_to_df("SELECT * FROM metadata WHERE lower(State) LIKE ?", (f"%{first_word}%",))
            
        if not metadata_df.empty:
            gauge_ids = tuple(metadata_df["GaugeID"].tolist())
            if len(gauge_ids) == 1:
                catchment_df = _query_to_df("SELECT * FROM catchment WHERE GaugeID = ?", (gauge_ids[0],))
                # Event ID starts with GaugeID, e.g. INDOFLOODS-gauge-1010-1
                events_df = _query_to_df("SELECT * FROM flood_events WHERE EventID LIKE ?", (f"{gauge_ids[0]}%",))
            elif len(gauge_ids) > 1:
                placeholders = ",".join("?" for _ in gauge_ids)
                catchment_df = _query_to_df(f"SELECT * FROM catchment WHERE GaugeID IN ({placeholders})", gauge_ids)
                
                # Construct query for events matching these gauge ids
                like_clauses = " OR ".join("EventID LIKE ?" for _ in gauge_ids)
                like_params = tuple(f"{gid}%" for gid in gauge_ids)
                events_df = _query_to_df(f"SELECT * FROM flood_events WHERE {like_clauses}", like_params)
            else:
                catchment_df = pd.DataFrame()
                events_df = pd.DataFrame()
        else:
            catchment_df = pd.DataFrame()
            events_df = pd.DataFrame()
            
        return {
            "events": events_df,
            "catchment": catchment_df,
            "metadata": metadata_df
        }

    return {
        "events": _query_to_df("SELECT * FROM flood_events"),
        "catchment": _query_to_df("SELECT * FROM catchment"),
        "metadata": _query_to_df("SELECT * FROM metadata")
    }

def check_heavy_datasets():
    """Returns DB readiness indicators."""
    conn = DatabaseManager.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    return {
        "population": True,  # Fallback lookup exists
        "gis": "metadata" in tables,
        "subdivision": "subdivision_rainfall" in tables
    }

# Automatically run startup verification
verify_all_datasets()

