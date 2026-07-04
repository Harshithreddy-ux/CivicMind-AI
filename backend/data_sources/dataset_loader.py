import pandas as pd
import os
from typing import Dict, Any, List

# Global cache for datasets and validation status
_CACHE = {}
_VALIDATION_STATUS = {}
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'datasets')

REQUIRED_COLUMNS = {
    'crime_dataset_india.csv': ['City', 'Crime Description', 'Crime Domain'],
    'hospital_directory.csv': ['Hospital_Name', 'State', 'District'],
    'hospitals.csv': ['City', 'Hospital', 'Latitude', 'Longitude'],
    'floodevents_indofloods.csv': ['EventID', 'Peak Flood Level (m)'],
    'catchment_characteristics_indofloods.csv': ['GaugeID', 'Annual Precipitation'],
    'precipitation_variables_indofloods.csv': ['EventID', 'T1d'],
    'metadata_indofloods.csv': ['GaugeID', 'Latitude', 'Longitude'],
    'Sub_Division_IMD_2017.csv': ['SUBDIVISION', 'YEAR', 'ANNUAL']
}

def validate_dataset(filename: str) -> Dict[str, Any]:
    """Validates a dataset's existence, readability, and column correctness."""
    filepath = os.path.join(DATA_DIR, filename)
    if not os.path.exists(filepath):
        return {"status": "missing", "error": "File not found"}
        
    try:
        if filename.endswith('.csv'):
            df = pd.read_csv(filepath, nrows=5)
            cols = df.columns.tolist()
            req_cols = REQUIRED_COLUMNS.get(filename, [])
            missing_cols = [c for c in req_cols if c not in cols]
            if missing_cols:
                return {"status": "corrupted", "error": f"Missing columns: {missing_cols}"}
            return {"status": "valid", "readable": True}
        else:
            # For non-csv like .tif or .pbf, just verify existence and basic readability
            with open(filepath, 'rb') as f:
                f.read(100)
            return {"status": "valid", "readable": True}
    except Exception as e:
        return {"status": "error", "error": str(e)}

def verify_all_datasets() -> Dict[str, Any]:
    """Startup verification suite for all datasets."""
    files_to_check = [
        'crime_dataset_india.csv',
        'hospital_directory.csv',
        'hospitals.csv',
        'floodevents_indofloods.csv',
        'catchment_characteristics_indofloods.csv',
        'precipitation_variables_indofloods.csv',
        'metadata_indofloods.csv',
        'Sub_Division_IMD_2017.csv',
        'ind_pop_2026_CN_100m_R2025A_v1.tif',
        'india-260701.osm.pbf'
    ]
    
    global _VALIDATION_STATUS
    for filename in files_to_check:
        _VALIDATION_STATUS[filename] = validate_dataset(filename)
        
    return _VALIDATION_STATUS

def get_validation_warnings() -> List[str]:
    """Returns lists of user-friendly warnings for UI warning banners."""
    warnings = []
    for filename, val in _VALIDATION_STATUS.items():
        if val.get("status") != "valid":
            warnings.append(f"Warning: Dataset '{filename}' is {val.get('status')} ({val.get('error', 'unknown error')}). Platform will fallback gracefully.")
    return warnings

def _load_csv(filename: str, limit: int = 1000) -> pd.DataFrame:
    """Loads a CSV gracefully with a row limit and caching."""
    filepath = os.path.join(DATA_DIR, filename)
    if not os.path.exists(filepath):
        print(f"Dataset {filename} missing. Returning empty fallback DataFrame.")
        return pd.DataFrame()
        
    if filename in _CACHE:
        return _CACHE[filename]
        
    try:
        df = pd.read_csv(filepath, nrows=limit, low_memory=False)
        _CACHE[filename] = df
        return df
    except Exception as e:
        print(f"Error loading {filename}: {e}. Falling back.")
        return pd.DataFrame()

def load_crime_data():
    return _load_csv('crime_dataset_india.csv')

def load_hospital_data():
    df = _load_csv('hospital_directory.csv')
    if df.empty:
        df = _load_csv('hospitals.csv')
    return df

def load_flood_data():
    return {
        "events": _load_csv('floodevents_indofloods.csv', limit=500),
        "catchment": _load_csv('catchment_characteristics_indofloods.csv', limit=500),
        "precipitation": _load_csv('precipitation_variables_indofloods.csv', limit=500),
        "metadata": _load_csv('metadata_indofloods.csv', limit=500)
    }

def check_heavy_datasets():
    """Returns the cached verification status of TIFF, OSM, etc."""
    return {
        "population": _VALIDATION_STATUS.get("ind_pop_2026_CN_100m_R2025A_v1.tif", {}).get("status") == "valid",
        "gis": _VALIDATION_STATUS.get("india-260701.osm.pbf", {}).get("status") == "valid",
        "subdivision": _VALIDATION_STATUS.get("Sub_Division_IMD_2017.csv", {}).get("status") == "valid"
    }

# Automatically run startup verification when module is imported
verify_all_datasets()
