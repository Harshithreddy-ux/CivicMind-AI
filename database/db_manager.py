import os
import sqlite3
import pandas as pd
import logging

logger = logging.getLogger("civicmind.database")

DB_PATH = os.path.join(os.path.dirname(__file__), "civicmind.db")
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "datasets")

class DatabaseManager:
    _connection = None

    @classmethod
    def get_connection(cls):
        if cls._connection is None:
            cls._connection = sqlite3.connect(DB_PATH, check_same_thread=False)
            cls._connection.row_factory = sqlite3.Row
        return cls._connection

    @classmethod
    def initialize_db(cls):
        """Initializes the database, creates tables, loads CSV files, and creates indexes."""
        conn = cls.get_connection()
        cursor = conn.cursor()

        # Check if already initialized with correct column casing (capital State)
        try:
            cursor.execute("SELECT State FROM hospitals LIMIT 1")
            return
        except Exception:
            logger.info("Database uninitialized or needs column normalization. Building SQLite DB...")

        try:
            # 1. Load and Clean Hospitals Directory
            hosp_csv = os.path.join(DATA_DIR, "hospital_directory.csv")
            if not os.path.exists(hosp_csv):
                hosp_csv = os.path.join(DATA_DIR, "hospitals.csv")
            
            if os.path.exists(hosp_csv):
                logger.info("Loading hospitals CSV...")
                hosp_df = pd.read_csv(hosp_csv, low_memory=False)
                # Keep original casing columns
                cols_to_keep = [
                    "Sr_No", "Location_Coordinates", "Hospital_Name", 
                    "Hospital_Category", "Hospital_Care_Type", "State", "District"
                ]
                existing_cols = [c for c in cols_to_keep if c in hosp_df.columns]
                hosp_df = hosp_df[existing_cols]
                
                logger.info("Writing hospitals to SQLite...")
                hosp_df.to_sql("hospitals", conn, if_exists="replace", index=False)
                cursor.execute("CREATE INDEX idx_hospitals_state ON hospitals(State)")
                cursor.execute("CREATE INDEX idx_hospitals_district ON hospitals(District)")
            
            # 2. Load Crime Dataset
            crime_csv = os.path.join(DATA_DIR, "crime_dataset_india.csv")
            if os.path.exists(crime_csv):
                logger.info("Loading crime CSV...")
                crime_df = pd.read_csv(crime_csv, nrows=20000, low_memory=False)
                cols_to_keep = ["Report Number", "Date Reported", "City", "Crime Description", "Crime Domain"]
                existing_cols = [c for c in cols_to_keep if c in crime_df.columns]
                crime_df = crime_df[existing_cols]
                
                logger.info("Writing crimes to SQLite...")
                crime_df.to_sql("crimes", conn, if_exists="replace", index=False)
                cursor.execute("CREATE INDEX idx_crimes_city ON crimes(City)")

            # 3. Load Flood Datasets
            flood_events_csv = os.path.join(DATA_DIR, "floodevents_indofloods.csv")
            if os.path.exists(flood_events_csv):
                logger.info("Loading flood events CSV...")
                events_df = pd.read_csv(flood_events_csv, nrows=1000, low_memory=False)
                cols_to_keep = ["EventID", "Start Date", "End Date", "Peak Flood Level (m)", "Flood Type"]
                existing_cols = [c for c in cols_to_keep if c in events_df.columns]
                events_df = events_df[existing_cols]
                events_df.to_sql("flood_events", conn, if_exists="replace", index=False)
                cursor.execute("CREATE INDEX idx_flood_events_id ON flood_events(EventID)")

            catchment_csv = os.path.join(DATA_DIR, "catchment_characteristics_indofloods.csv")
            if os.path.exists(catchment_csv):
                logger.info("Loading catchment CSV...")
                catchment_df = pd.read_csv(catchment_csv, nrows=1000, low_memory=False)
                cols_to_keep = ["GaugeID", "Annual Precipitation"]
                existing_cols = [c for c in cols_to_keep if c in catchment_df.columns]
                catchment_df = catchment_df[existing_cols]
                catchment_df.to_sql("catchment", conn, if_exists="replace", index=False)
                cursor.execute("CREATE INDEX idx_catchment_gauge ON catchment(GaugeID)")

            metadata_csv = os.path.join(DATA_DIR, "metadata_indofloods.csv")
            if os.path.exists(metadata_csv):
                logger.info("Loading metadata CSV...")
                metadata_df = pd.read_csv(metadata_csv, nrows=1000, low_memory=False)
                cols_to_keep = ["GaugeID", "Warning Level", "Danger Level", "Station", "Latitude", "Longitude", "State"]
                existing_cols = [c for c in cols_to_keep if c in metadata_df.columns]
                metadata_df = metadata_df[existing_cols]
                metadata_df.to_sql("metadata", conn, if_exists="replace", index=False)
                cursor.execute("CREATE INDEX idx_metadata_state ON metadata(State)")
                cursor.execute("CREATE INDEX idx_metadata_gauge ON metadata(GaugeID)")

            # 4. Load subdivision rainfall
            subdiv_csv = os.path.join(DATA_DIR, "Sub_Division_IMD_2017.csv")
            if os.path.exists(subdiv_csv):
                logger.info("Loading subdivision rainfall CSV...")
                subdiv_df = pd.read_csv(subdiv_csv, low_memory=False)
                cols_to_keep = ["SUBDIVISION", "YEAR", "ANNUAL"]
                existing_cols = [c for c in cols_to_keep if c in subdiv_df.columns]
                subdiv_df = subdiv_df[existing_cols]
                subdiv_df.to_sql("subdivision_rainfall", conn, if_exists="replace", index=False)
                cursor.execute("CREATE INDEX idx_subdiv_name ON subdivision_rainfall(SUBDIVISION)")

            conn.commit()
            logger.info("SQLite database initialization and casing normalization successful.")
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to initialize SQLite database: {e}")

    @classmethod
    def query(cls, sql: str, params: tuple = ()) -> list:
        """Executes a query and returns a list of Row dicts."""
        conn = cls.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(sql, params)
            return cursor.fetchall()
        except Exception as e:
            logger.error(f"Database query error: {e}")
            return []

    @classmethod
    def query_one(cls, sql: str, params: tuple = ()):
        """Executes a query and returns a single Row or None."""
        conn = cls.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(sql, params)
            return cursor.fetchone()
        except Exception as e:
            logger.error(f"Database query error: {e}")
            return None

# Auto-initialize on import
DatabaseManager.initialize_db()
