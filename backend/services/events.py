import pandas as pd
from sodapy import Socrata

def get_nyc_events(limit=100, borough=None, min_attendance=None):
    """
    Fetches event data from NYC Open Data.
    :param limit: Number of records to return.
    :param borough: Filter by 'Manhattan', 'Brooklyn', 'Queens', 'Bronx', or 'Staten Island'.
    :param min_attendance: Filter for events with at least this many people.
    """
    DOMAIN = "data.cityofnewyork.us"
    DATASET_ID = "tvpp-9vvx"
    
    # Use None for public access, or your App Token string
    client = Socrata(DOMAIN, None) 
    
    # Build the query
    where_clauses = []
    if borough:
        where_clauses.append(f"event_borough = '{borough}'")
    if min_attendance:
        where_clauses.append(f"event_attendance >= {min_attendance}")
    
    where_query = " AND ".join(where_clauses) if where_clauses else None

    try:
        results = client.get(
            DATASET_ID, 
            limit=limit, 
            where=where_query,
            order="start_date_time DESC"
        )
        
        df = pd.DataFrame.from_records(results)
        
        # Ensure numeric types for attendance
        if 'event_attendance' in df.columns:
            df['event_attendance'] = pd.to_numeric(df['event_attendance'], errors='coerce')
            
        return df
    
    except Exception as e:
        print(f"Error fetching data: {e}")
        return pd.DataFrame()

if __name__ == "__main__":
    df = get_nyc_events(limit=100, borough="Manhattan", min_attendance=1000)
    print(df.head())
    