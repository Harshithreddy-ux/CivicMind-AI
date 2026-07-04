from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATASETS_ROOT = ROOT.parent / "datasets"


@lru_cache(maxsize=1)
def load_all_datasets() -> Dict[str, pd.DataFrame]:
    datasets: Dict[str, pd.DataFrame] = {}
    if not DATASETS_ROOT.exists():
        return datasets

    for csv_path in sorted(DATASETS_ROOT.rglob("*.csv")):
        try:
            key = csv_path.stem.lower()
            datasets[key] = pd.read_csv(csv_path, low_memory=False)
        except Exception:
            continue

    return datasets


def get_dataset(name: str) -> Optional[pd.DataFrame]:
    return load_all_datasets().get(name.lower())


def get_city_facilities(city: str, dataset_name: str) -> List[Dict[str, str]]:
    frame = get_dataset(dataset_name)
    if frame is None:
        return []

    if "City" not in frame.columns:
        return []

    city_matches = []
    for _, row in frame.iterrows():
        if str(row["City"]).strip().lower() == city.strip().lower():
            city_matches.append({key: str(value) for key, value in row.items()})

    return city_matches


def get_city_population(city: str) -> Optional[int]:
    frame = get_dataset("population")
    if frame is None:
        return None

    if "City" not in frame.columns or "Population" not in frame.columns:
        return None

    matches = frame[frame["City"].astype(str).str.strip().str.lower() == city.strip().lower()]
    if matches.empty:
        return None

    value = matches.iloc[0]["Population"]
    try:
        return int(float(value))
    except Exception:
        return None


def get_city_rainfall(city: str) -> Optional[float]:
    frame = get_dataset("rainfall")
    if frame is None:
        return None

    if "City" not in frame.columns or "Rainfall" not in frame.columns:
        return None

    matches = frame[frame["City"].astype(str).str.strip().str.lower() == city.strip().lower()]
    if matches.empty:
        return None

    value = matches.iloc[0]["Rainfall"]
    try:
        return float(value)
    except Exception:
        return None
