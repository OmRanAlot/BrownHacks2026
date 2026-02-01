"""
RAG-Based Foot Traffic Predictor
Uses vector search to find similar historical patterns
"""

from datetime import datetime
from typing import Dict, List


class RAGFootTrafficPredictor:
    """Main RAG-based prediction agent"""
    
    def __init__(self, vector_db, static_agent, dynamic_agent):
        """
        Initialize RAG predictor
        
        Args:
            vector_db: MongoVectorDB instance
            static_agent: StaticDataAgent instance
            dynamic_agent: DynamicDataAgent instance
        """
        self.vector_db = vector_db
        self.static_agent = static_agent
        self.dynamic_agent = dynamic_agent
    
    def predict(self, business_id: str, target_datetime: datetime) -> Dict:
        """
        🔥 MAIN RAG PREDICTION FUNCTION 🔥
        Predict foot traffic using RAG approach
        
        Args:
            business_id: Business ID to predict for
            target_datetime: Target date/time for prediction
        
        Returns:
            Prediction results with confidence and context
        """
        print(f"\n🤖 Starting RAG prediction for {target_datetime.strftime('%A, %B %d at %I:%M %p')}...")
        
        # Get business info
        business = self.vector_db.get_business(business_id)
        if not business:
            raise ValueError(f"Business {business_id} not found")
        
        # ============================================================
        # STEP 1: Gather Static Context (events + weather)
        # ============================================================
        static_context = self.static_agent.get_static_context(
            business_location=business['location'],
            target_datetime=target_datetime
        )
        
        # ============================================================
        # STEP 2: Gather Dynamic Context (current traffic + MTA)
        # ============================================================
        dynamic_context = self.dynamic_agent.get_dynamic_context(
            business_location=business['location'],
            nearby_stations=business.get('nearby_stations', [])
        )
        
        # ============================================================
        # STEP 3: Create Query Context for RAG
        # ============================================================
        query_context = {
            "day_of_week": target_datetime.strftime("%A"),
            "hour": target_datetime.hour,
            "weather_condition": static_context['weather']['condition'],
            "temperature": static_context['weather']['temp'],
            "borough": business['location']['borough'],
            "nearby_events": static_context['events_summary'],
            "business_type": business['type'],
            "season": self._get_season(target_datetime),
            "is_holiday": self._is_holiday(target_datetime)
        }
        
        # ============================================================
        # STEP 4: 🔍 RAG CALL - Query Vector DB for Similar Patterns
        # ============================================================
        print("\n🔍 Querying vector database for similar historical patterns...")
        
        query_text = self._format_query_text(query_context)
        query_embedding = self.vector_db.create_embedding(query_text)
        
        # Perform vector search with filters
        similar_patterns = self.vector_db.vector_search(
            query_embedding=query_embedding,
            limit=10,
            filter_criteria={
                "borough": business['location']['borough'],
                "business_type": business['type']
            }
        )
        
        print(f"✓ Found {len(similar_patterns)} similar historical patterns")
        
        # ============================================================
        # STEP 5: Calculate Prediction from Retrieved Patterns
        # ============================================================
        if similar_patterns:
            # Weight predictions by similarity score
            total_weight = sum(p['score'] for p in similar_patterns)
            weighted_traffic = sum(
                p['foot_traffic'] * p['score'] 
                for p in similar_patterns
            )
            predicted_traffic = int(weighted_traffic / total_weight)
            
            # Adjust based on current dynamic data
            if dynamic_context['current_foot_traffic'] > 0:
                # Use current traffic as adjustment factor
                baseline_current = 500  # Assumed baseline
                adjustment_factor = dynamic_context['current_foot_traffic'] / baseline_current
                predicted_traffic = int(predicted_traffic * adjustment_factor)
            
            confidence = min(len(similar_patterns) / 10, 1.0)  # 0-1 scale
        else:
            # Fallback if no patterns found
            print("⚠️  No similar patterns found, using baseline estimate")
            predicted_traffic = 300
            confidence = 0.3
        
        # ============================================================
        # STEP 6: Return Prediction Results
        # ============================================================
        return {
            "predicted_foot_traffic": predicted_traffic,
            "confidence": confidence,
            "similar_patterns": similar_patterns[:5],  # Top 5 for analysis
            "context": {
                "static": static_context,
                "dynamic": dynamic_context,
                "query": query_context
            },
            "timestamp": datetime.now()
        }
    
    def _format_query_text(self, context: Dict) -> str:
        """
        Format context into text for embedding
        
        Args:
            context: Query context dict
        
        Returns:
            Formatted text string
        """
        return f"""
        Day: {context['day_of_week']} at {context['hour']}:00
        Weather: {context['weather_condition']}, Temperature: {context['temperature']}F
        Borough: {context['borough']}
        Events nearby: {context['nearby_events']}
        Business type: {context['business_type']}
        Season: {context['season']}
        Holiday: {context['is_holiday']}
        """
    
    def _get_season(self, date: datetime) -> str:
        """Determine season from date"""
        month = date.month
        if month in [12, 1, 2]:
            return "Winter"
        elif month in [3, 4, 5]:
            return "Spring"
        elif month in [6, 7, 8]:
            return "Summer"
        else:
            return "Fall"
    
    def _is_holiday(self, date: datetime) -> bool:
        """Check if date is a major holiday"""
        # Simple check - expand with actual holiday calendar
        holidays = [
            (1, 1),   # New Year's Day
            (7, 4),   # Independence Day
            (12, 25), # Christmas
            (11, 28), # Thanksgiving (approximate - 4th Thursday)
        ]
        return (date.month, date.day) in holidays