"""
Main Execution File
Orchestrates the entire RAG-based foot traffic prediction system
"""

import os
from datetime import datetime
from dotenv import load_dotenv

# Import all components
from vector_db import MongoVectorDB, load_historical_data, load_sample_events
from static_data_agent import StaticDataAgent, MockWeatherAPI
from dynamic_data_agent import DynamicDataAgent
from predictor import RAGFootTrafficPredictor
from mcp_agent import MCPExecutionAgent


def main():
    """Main orchestration function"""
    
    print("="*70)
    print("NYC BUSINESS OPTIMIZER - RAG-BASED FOOT TRAFFIC PREDICTION")
    print("="*70)
    
    # Load environment variables
    load_dotenv()
    
    MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://your-cluster.mongodb.net")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    MTA_API_KEY = os.getenv("MTA_API_KEY")
    
    # ==================================================================
    # STEP 1: Initialize Vector Database
    # ==================================================================
    print("\n" + "="*70)
    print("STEP 1: Initializing MongoDB Vector Database")
    print("="*70)
    
    vector_db = MongoVectorDB(
        mongo_uri=MONGO_URI,
        openai_key=OPENAI_API_KEY
    )
    
    # Check database stats
    stats = vector_db.get_stats()
    print(f"\nDatabase Statistics:")
    print(f"  - Historical patterns: {stats['historical_patterns']}")
    print(f"  - Events: {stats['events']}")
    print(f"  - Businesses: {stats['businesses']}")
    
    # ==================================================================
    # STEP 2: Load Events Data
    # ==================================================================
    print("\n" + "="*70)
    print("STEP 2: Loading Events Data")
    print("="*70)
    
    if stats['events'] == 0:
        sample_events = load_sample_events()
        vector_db.add_events_bulk(sample_events)
    else:
        print(f"✓ Events already loaded ({stats['events']} events)")
    
    # ==================================================================
    # STEP 3: Load Historical Training Data
    # ==================================================================
    print("\n" + "="*70)
    print("STEP 3: Loading Historical Training Data")
    print("="*70)
    
    if stats['historical_patterns'] == 0:
        historical_data = load_historical_data()
        vector_db.add_historical_data_bulk(historical_data)
    else:
        print(f"✓ Historical data already loaded ({stats['historical_patterns']} patterns)")
        reload = input("Reload historical data? (y/n): ")
        if reload.lower() == 'y':
            vector_db.clear_historical_data()
            historical_data = load_historical_data()
            vector_db.add_historical_data_bulk(historical_data)
    
    # ==================================================================
    # STEP 4: Initialize Agents
    # ==================================================================
    print("\n" + "="*70)
    print("STEP 4: Initializing Agents")
    print("="*70)
    
    # Static Data Agent (Events + Weather)
    weather_api = MockWeatherAPI()
    static_agent = StaticDataAgent(
        mongo_client=vector_db.client,
        weather_api=weather_api
    )
    print("✓ Static Data Agent initialized")
    
    # Dynamic Data Agent (Foot Traffic + MTA)
    dynamic_agent = DynamicDataAgent(
        google_api_key=GOOGLE_API_KEY,
        mta_api_key=MTA_API_KEY
    )
    print("✓ Dynamic Data Agent initialized")
    
    # RAG Predictor
    rag_predictor = RAGFootTrafficPredictor(
        vector_db=vector_db,
        static_agent=static_agent,
        dynamic_agent=dynamic_agent
    )
    print("✓ RAG Predictor initialized")
    
    # MCP Execution Agent
    mcp_agent = MCPExecutionAgent(vector_db=vector_db)
    print("✓ MCP Execution Agent initialized")
    
    # ==================================================================
    # STEP 5: Setup Business
    # ==================================================================
    print("\n" + "="*70)
    print("STEP 5: Setting Up Business")
    print("="*70)
    
    # Check if business exists
    existing_business = vector_db.businesses.find_one({"name": "Joe's Pizza"})
    
    if existing_business:
        business_id = str(existing_business['_id'])
        print(f"✓ Using existing business: {existing_business['name']}")
    else:
        business_id = vector_db.add_business({
            "name": "Joe's Pizza",
            "type": "restaurant",
            "location": {
                "lat": 40.7589,
                "lng": -73.9851,
                "borough": "Manhattan"
            },
            "nearby_stations": ["34th St - Penn Station", "Times Square-42nd St"]
        })
        print(f"✓ Created new business: Joe's Pizza (ID: {business_id})")
    
    # ==================================================================
    # STEP 6: Make Prediction (CALL THE RAG!)
    # ==================================================================
    print("\n" + "="*70)
    print("STEP 6: Making Prediction with RAG")
    print("="*70)
    
    # Target prediction: Next Monday at 6 PM
    target_datetime = datetime(2024, 2, 5, 18, 0)
    
    # 🔥 THIS IS THE MAIN RAG CALL 🔥
    prediction = rag_predictor.predict(
        business_id=business_id,
        target_datetime=target_datetime
    )
    
    # ==================================================================
    # STEP 7: Display Results
    # ==================================================================
    print("\n" + "="*70)
    print("📊 PREDICTION RESULTS")
    print("="*70)
    
    print(f"\n🏪 Business: Joe's Pizza")
    print(f"📅 Target: {target_datetime.strftime('%A, %B %d, %Y at %I:%M %p')}")
    print(f"\n🎯 Predicted Foot Traffic: {prediction['predicted_foot_traffic']} people/hour")
    print(f"📈 Confidence: {prediction['confidence']:.1%}")
    print(f"📚 Based on {len(prediction['similar_patterns'])} similar patterns")
    
    print(f"\n🌤️  Context:")
    print(f"   Weather: {prediction['context']['query']['weather_condition']}, "
          f"{prediction['context']['query']['temperature']}°F")
    print(f"   Events: {prediction['context']['query']['nearby_events']}")
    print(f"   Day: {prediction['context']['query']['day_of_week']}")
    print(f"   Current Traffic: {prediction['context']['dynamic']['current_foot_traffic']} people/hour")
    print(f"   MTA Entries: {prediction['context']['dynamic']['mta_data']['total_entries']}")
    
    # Display top similar patterns
    if prediction['similar_patterns']:
        print(f"\n📊 Top Similar Patterns:")
        for i, pattern in enumerate(prediction['similar_patterns'][:3], 1):
            print(f"   {i}. {pattern['day_of_week']} at {pattern['hour']}:00 - "
                  f"{pattern['foot_traffic']} people "
                  f"(similarity: {pattern['score']:.3f})")
    
    # ==================================================================
    # STEP 8: Execute Actions via MCP
    # ==================================================================
    print("\n" + "="*70)
    print("STEP 8: Executing Actions via MCP")
    print("="*70)
    
    # Execute staffing
    staffing_result = mcp_agent.execute_staffing_adjustment(
        business_id=business_id,
        predicted_traffic=prediction['predicted_foot_traffic'],
        target_date=target_datetime
    )
    
    # Execute restocking
    restock_result = mcp_agent.execute_restocking(
        business_id=business_id,
        predicted_traffic=prediction['predicted_foot_traffic']
    )
    
    # Execute marketing (if needed)
    marketing_result = mcp_agent.execute_marketing_campaign(
        business_id=business_id,
        predicted_traffic=prediction['predicted_foot_traffic'],
        target_date=target_datetime
    )
    
    # ==================================================================
    # FINAL SUMMARY
    # ==================================================================
    print("\n" + "="*70)
    print("✅ EXECUTION COMPLETE")
    print("="*70)
    
    print(f"\nActions taken:")
    print(f"  1. ✓ Staffing: {staffing_result['staff_count']} employees scheduled")
    print(f"  2. ✓ Inventory: {restock_result['multiplier']:.2f}x baseline ordered")
    
    if marketing_result['status'] != 'not_needed':
        print(f"  3. ✓ Marketing: {marketing_result.get('discount_percent', 0)}% discount campaign")
    
    print(f"\n🎉 Hackathon demo complete!")
    print("="*70)


if __name__ == "__main__":
    main()
"""

## Project Structure:
```
nyc-business-optimizer/
├── vector_db.py              # Vector DB + data loading
├── static_data_agent.py      # Events + weather handling
├── dynamic_data_agent.py     # Real-time foot traffic + MTA
├── predictor.py              # RAG prediction logic
├── mcp_agent.py              # MCP execution (staffing, inventory)
├── main.py                   # Main orchestration
├── .env                      # Environment variables
└── requirements.txt          # Dependencies

"""