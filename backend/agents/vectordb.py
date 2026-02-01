"""
MongoDB Vector Database Manager
Handles all vector database operations and data storage
"""

from pymongo import MongoClient
import openai
from datetime import datetime
from typing import List, Dict


class MongoVectorDB:
    """MongoDB Atlas Vector Database for historical patterns"""
    
    def __init__(self, mongo_uri: str, openai_key: str):
        self.client = MongoClient(mongo_uri)
        self.db = self.client['nyc_business_optimizer']
        
        # Collections
        self.historical_patterns = self.db['historical_patterns']  # Vector DB
        self.events = self.db['events']  # Events collection
        self.businesses = self.db['businesses']  # Business info
        
        openai.api_key = openai_key
        
        # Create indexes
        self._create_indexes()
    
    def _create_indexes(self):
        """Create necessary indexes for efficient queries"""
        # Geospatial index for events
        self.events.create_index([("location", "2dsphere")])
        print("✓ Database indexes created")
    
    def create_embedding(self, text: str) -> List[float]:
        """
        Generate embeddings using OpenAI
        
        Args:
            text: Text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        response = openai.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding
    
    def prepare_historical_record(self, record: Dict) -> Dict:
        """
        Prepare a historical record for vector storage
        
        Args:
            record: Raw historical data point
            
        Returns:
            Processed record with embedding
        """
        # Create rich text description for embedding
        text_description = f"""
        Day: {record['day_of_week']} at {record['hour']}:00
        Weather: {record['weather_condition']}, Temperature: {record['temperature']}F
        Borough: {record['borough']}
        Events nearby: {record.get('nearby_events', 'None')}
        Business type: {record['business_type']}
        Season: {record.get('season', 'Unknown')}
        Holiday: {record.get('is_holiday', False)}
        Foot traffic level: {record['foot_traffic']} people per hour
        """
        
        # Generate embedding
        embedding = self.create_embedding(text_description)
        
        # Return complete document
        return {
            "date": record['date'],
            "day_of_week": record['day_of_week'],
            "hour": record['hour'],
            "weather_condition": record['weather_condition'],
            "temperature": record['temperature'],
            "borough": record['borough'],
            "nearby_events": record.get('nearby_events', ''),
            "business_type": record['business_type'],
            "season": record.get('season', ''),
            "is_holiday": record.get('is_holiday', False),
            "foot_traffic": record['foot_traffic'],
            "text_description": text_description,
            "embedding": embedding,
            "created_at": datetime.now()
        }
    
    def add_historical_data_bulk(self, historical_records: List[Dict]) -> List:
        """
        Add multiple historical records to vector DB
        
        Args:
            historical_records: List of historical data points
            
        Returns:
            List of inserted IDs
        """
        print(f"\n📥 Processing {len(historical_records)} historical records...")
        
        prepared_records = []
        for i, record in enumerate(historical_records):
            if i % 10 == 0:
                print(f"   Processing record {i+1}/{len(historical_records)}...")
            
            prepared_record = self.prepare_historical_record(record)
            prepared_records.append(prepared_record)
        
        # Bulk insert
        result = self.historical_patterns.insert_many(prepared_records)
        print(f"✓ Inserted {len(result.inserted_ids)} records into Vector DB")
        
        return result.inserted_ids
    
    def vector_search(
        self, 
        query_embedding: List[float], 
        limit: int = 10, 
        filter_criteria: Dict = None
    ) -> List[Dict]:
        """
        Perform vector similarity search using MongoDB Atlas Vector Search
        
        Args:
            query_embedding: Query vector
            limit: Number of results to return
            filter_criteria: Optional MongoDB query filters
            
        Returns:
            List of similar documents with scores
        """
        pipeline = [
            {
                "$vectorSearch": {
                    "index": "vector_index",  # Atlas Search index name
                    "path": "embedding",
                    "queryVector": query_embedding,
                    "numCandidates": 100,
                    "limit": limit
                }
            },
            {
                "$project": {
                    "date": 1,
                    "day_of_week": 1,
                    "hour": 1,
                    "weather_condition": 1,
                    "temperature": 1,
                    "borough": 1,
                    "nearby_events": 1,
                    "business_type": 1,
                    "foot_traffic": 1,
                    "score": { "$meta": "vectorSearchScore" }
                }
            }
        ]
        
        # Add filter criteria if provided
        if filter_criteria:
            pipeline.insert(1, {"$match": filter_criteria})
        
        results = list(self.historical_patterns.aggregate(pipeline))
        return results
    
    def add_event(self, event_data: Dict) -> str:
        """
        Add an event to the events collection
        
        Args:
            event_data: Event information with location
            
        Returns:
            Inserted event ID
        """
        # Ensure proper GeoJSON format
        if 'location' in event_data:
            if 'type' not in event_data['location']:
                event_data['location'] = {
                    "type": "Point",
                    "coordinates": [
                        event_data['location']['lng'],
                        event_data['location']['lat']
                    ]
                }
        
        result = self.events.insert_one(event_data)
        return str(result.inserted_id)
    
    def add_events_bulk(self, events: List[Dict]) -> List:
    """
    Add multiple events to the database
    Handles your existing event format
    """
    print(f"\n📍 Adding {len(events)} events to database...")
    
    # Transform your events to the format we need
    for event in events:
        # Your events have latitude/longitude as separate fields
        # We need to convert to GeoJSON format
        if 'latitude' in event and 'longitude' in event:
            event['location'] = {
                "type": "Point",
                "coordinates": [
                    float(event['longitude']),  # longitude first!
                    float(event['latitude'])
                ]
            }
        
        # Rename fields to match our system (optional, for consistency)
        if 'event_name' in event and 'name' not in event:
            event['name'] = event['event_name']
        
        if 'event_borough' in event and 'borough' not in event:
            event['borough'] = event['event_borough']
        
        if 'start_date_time' in event and 'start_time' not in event:
            # Convert string to datetime if needed
            if isinstance(event['start_date_time'], str):
                from dateutil import parser
                event['start_time'] = parser.parse(event['start_date_time'])
            else:
                event['start_time'] = event['start_date_time']
        
        # Add end_time if not present (estimate 3 hours)
        if 'start_time' in event and 'end_time' not in event:
            from datetime import timedelta
            event['end_time'] = event['start_time'] + timedelta(hours=3)
    
        result = self.events.insert_many(events)
        print(f"✓ Inserted {len(result.inserted_ids)} events")



        
        return result.inserted_ids
    def add_business(self, business_data: Dict) -> str:
        """
        Add a business to the database
        
        Args:
            business_data: Business information
            
        Returns:
            Inserted business ID
        """
        # Ensure proper GeoJSON format
        if 'location' in business_data:
            if 'type' not in business_data['location']:
                business_data['location'] = {
                    "type": "Point",
                    "coordinates": [
                        business_data['location']['lng'],
                        business_data['location']['lat']
                    ],
                    "lat": business_data['location']['lat'],
                    "lng": business_data['location']['lng'],
                    "borough": business_data['location']['borough']
                }
        
        result = self.businesses.insert_one(business_data)
        return str(result.inserted_id)
    
    def get_business(self, business_id: str) -> Dict:
        """Get business by ID"""
        return self.businesses.find_one({"_id": business_id})
    
    def clear_historical_data(self):
        """Clear all historical pattern data (for reloading)"""
        result = self.historical_patterns.delete_many({})
        print(f"✓ Cleared {result.deleted_count} historical records")
    
    def get_stats(self) -> Dict:
        """Get database statistics"""
        return {
            "historical_patterns": self.historical_patterns.count_documents({}),
            "events": self.events.count_documents({}),
            "businesses": self.businesses.count_documents({})
        }

    


def load_sample_events() -> List[Dict]:
    """
    Sample NYC events data
    In production, this would come from your events API/scraper
    """
    return [
        {
            "name": "Madison Square Garden Concert",
            "venue": "Madison Square Garden",
            "location": {
                "lat": 40.7505,
                "lng": -73.9934
            },
            "start_time": datetime(2024, 2, 5, 19, 30),
            "end_time": datetime(2024, 2, 5, 22, 30),
            "category": "Concert",
            "expected_attendance": 18000
        },
        {
            "name": "Broadway Show - Hamilton",
            "venue": "Richard Rodgers Theatre",
            "location": {
                "lat": 40.7590,
                "lng": -73.9845
            },
            "start_time": datetime(2024, 2, 5, 20, 0),
            "end_time": datetime(2024, 2, 5, 22, 45),
            "category": "Theater",
            "expected_attendance": 1300
        },
        {
            "name": "Knicks Game",
            "venue": "Madison Square Garden",
            "location": {
                "lat": 40.7505,
                "lng": -73.9934
            },
            "start_time": datetime(2024, 2, 6, 19, 30),
            "end_time": datetime(2024, 2, 6, 22, 0),
            "category": "Sports",
            "expected_attendance": 19000
        },
        {
            "name": "Brooklyn Flea Market",
            "venue": "Prospect Park",
            "location": {
                "lat": 40.6602,
                "lng": -73.9690
            },
            "start_time": datetime(2024, 2, 10, 10, 0),
            "end_time": datetime(2024, 2, 10, 17, 0),
            "category": "Market",
            "expected_attendance": 5000
        },
        {
            "name": "Museum Late Night",
            "venue": "Metropolitan Museum of Art",
            "location": {
                "lat": 40.7794,
                "lng": -73.9632
            },
            "start_time": datetime(2024, 2, 7, 18, 0),
            "end_time": datetime(2024, 2, 7, 21, 0),
            "category": "Cultural",
            "expected_attendance": 3000
        }
    ]


def load_historical_data() -> List[Dict]:
    """
    📝 MANUAL HISTORICAL DATA
    Add your training data here for the RAG system
    """
    return [
        # Manhattan Restaurant - Monday evening with MSG concert
        {
            "date": datetime(2024, 1, 15, 18, 0),
            "day_of_week": "Monday",
            "hour": 18,
            "weather_condition": "Rainy",
            "temperature": 45,
            "borough": "Manhattan",
            "nearby_events": "Madison Square Garden Concert - 7:30 PM",
            "business_type": "restaurant",
            "season": "Winter",
            "is_holiday": False,
            "foot_traffic": 850
        },
        {
            "date": datetime(2024, 1, 22, 18, 0),
            "day_of_week": "Monday",
            "hour": 18,
            "weather_condition": "Clear",
            "temperature": 52,
            "borough": "Manhattan",
            "nearby_events": "Madison Square Garden Concert - 7:30 PM",
            "business_type": "restaurant",
            "season": "Winter",
            "is_holiday": False,
            "foot_traffic": 920
        },
        # Friday night - high traffic
        {
            "date": datetime(2024, 1, 19, 19, 0),
            "day_of_week": "Friday",
            "hour": 19,
            "weather_condition": "Clear",
            "temperature": 48,
            "borough": "Manhattan",
            "nearby_events": "Broadway Shows nearby",
            "business_type": "restaurant",
            "season": "Winter",
            "is_holiday": False,
            "foot_traffic": 1100
        },
        # Tuesday lunch - moderate
        {
            "date": datetime(2024, 1, 16, 12, 0),
            "day_of_week": "Tuesday",
            "hour": 12,
            "weather_condition": "Cloudy",
            "temperature": 42,
            "borough": "Manhattan",
            "nearby_events": "None",
            "business_type": "restaurant",
            "season": "Winter",
            "is_holiday": False,
            "foot_traffic": 450
        },
        # Wednesday dinner - cold weather
        {
            "date": datetime(2024, 1, 17, 19, 0),
            "day_of_week": "Wednesday",
            "hour": 19,
            "weather_condition": "Snowy",
            "temperature": 28,
            "borough": "Manhattan",
            "nearby_events": "None",
            "business_type": "restaurant",
            "season": "Winter",
            "is_holiday": False,
            "foot_traffic": 320
        },
        # Thursday evening - moderate
        {
            "date": datetime(2024, 1, 18, 18, 0),
            "day_of_week": "Thursday",
            "hour": 18,
            "weather_condition": "Clear",
            "temperature": 50,
            "borough": "Manhattan",
            "nearby_events": "None",
            "business_type": "restaurant",
            "season": "Winter",
            "is_holiday": False,
            "foot_traffic": 620
        },
        # Saturday night - high traffic
        {
            "date": datetime(2024, 1, 20, 20, 0),
            "day_of_week": "Saturday",
            "hour": 20,
            "weather_condition": "Clear",
            "temperature": 45,
            "borough": "Manhattan",
            "nearby_events": "Knicks Game - 7:30 PM",
            "business_type": "restaurant",
            "season": "Winter",
            "is_holiday": False,
            "foot_traffic": 1250
        },
        # Sunday brunch
        {
            "date": datetime(2024, 1, 21, 11, 0),
            "day_of_week": "Sunday",
            "hour": 11,
            "weather_condition": "Cloudy",
            "temperature": 40,
            "borough": "Manhattan",
            "nearby_events": "None",
            "business_type": "restaurant",
            "season": "Winter",
            "is_holiday": False,
            "foot_traffic": 580
        },
        # Brooklyn cafe - weekend morning
        {
            "date": datetime(2024, 1, 20, 10, 0),
            "day_of_week": "Saturday",
            "hour": 10,
            "weather_condition": "Clear",
            "temperature": 55,
            "borough": "Brooklyn",
            "nearby_events": "Farmers Market - Prospect Park",
            "business_type": "cafe",
            "season": "Winter",
            "is_holiday": False,
            "foot_traffic": 320
        },
        # Brooklyn cafe - weekday morning
        {
            "date": datetime(2024, 1, 16, 8, 0),
            "day_of_week": "Tuesday",
            "hour": 8,
            "weather_condition": "Clear",
            "temperature": 38,
            "borough": "Brooklyn",
            "nearby_events": "None",
            "business_type": "cafe",
            "season": "Winter",
            "is_holiday": False,
            "foot_traffic": 180
        },
    ]