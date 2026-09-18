"""
backend/app/agent/graph.py

AI reasoning orchestrator for the rebooking layer.

Due to LangGraph 0.1.5 dependency compatibility issues, this implementation
uses a simpler orchestrator pattern instead of LangGraph StateGraph.
The AI reasoning is added on top of the existing deterministic engines.
"""

import logging
from typing import Optional, Dict, Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.state import AgentState
from app.agent.tools import (
    tool_get_passenger,
    tool_get_booking_by_passenger_and_flight,
    tool_get_connecting_flights,
    tool_get_available_flights,
)
from app.agent.prompts import (
    REASON_GENERATION_SYSTEM_PROMPT,
    NOTIFICATION_GENERATION_SYSTEM_PROMPT,
)
from app.services.priority_engine import score_priority
from app.services.matching_engine import find_alternative
from app.models.alternative_flight import AlternativeFlight
from app.models.flight import Flight
from app.models.passenger import Passenger
from app.models.connecting_flight import ConnectingFlight
from app.models.enums import PriorityLevel, RecommendationStatus
from app.core.config import settings

logger = logging.getLogger(__name__)


async def generate_ai_reason(
    priority: str,
    priority_reason: str,
    passenger_data: Optional[dict],
    flight_data: Optional[dict],
    connections: Optional[list]
) -> str:
    """
    Generate natural-language explanation using OpenAI.
    
    This function calls OpenAI to convert the deterministic reason into
    a clear natural-language explanation.
    
    Args:
        priority: Deterministic priority level
        priority_reason: Deterministic priority reason
        passenger_data: Passenger information
        flight_data: Flight information
        connections: Connecting flights information
        
    Returns:
        Natural-language explanation or falls back to original reason
    """
    if not settings.OPENAI_API_KEY:
        logger.warning("OpenAI API key not configured, using deterministic reason")
        return priority_reason
    
    try:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Construct grounded prompt
        prompt_context = {
            "priority": priority,
            "priority_reason": priority_reason,
            "passenger": passenger_data or {},
            "flight": flight_data or {},
            "connections": connections or [],
        }
        
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": REASON_GENERATION_SYSTEM_PROMPT},
                {"role": "user", "content": f"Generate a clear explanation for this rebooking decision: {prompt_context}"}
            ],
            temperature=0.3,
            max_tokens=200,
        )
        
        ai_reason = response.choices[0].message.content.strip()
        logger.info(f"Generated AI reason: {ai_reason}")
        return ai_reason
        
    except Exception as e:
        logger.error(f"OpenAI API call failed: {e}, falling back to deterministic reason")
        return priority_reason


async def generate_ai_notification(
    passenger_data: Optional[dict],
    booking_data: Optional[dict],
    flight_data: Optional[dict],
    recommended_flight: Optional[dict],
    priority: str,
    reason: str
) -> Dict[str, Optional[str]]:
    """
    Generate bilingual notification using OpenAI.
    
    Args:
        passenger_data: Passenger information
        booking_data: Booking information
        flight_data: Original flight information
        recommended_flight: Recommended flight information
        priority: Priority level
        reason: Rebooking reason
        
    Returns:
        Dictionary with 'en' and 'local' notification messages
    """
    if not settings.OPENAI_API_KEY:
        logger.warning("OpenAI API key not configured, using template notification")
        return {
            "en": f"Flight {flight_data.get('flight_number') if flight_data else 'Unknown'} has been disrupted. {reason}",
            "local": None,
        }
    
    try:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Determine local language
        local_language = passenger_data.get("preferred_language") if passenger_data else None
        
        # Construct grounded prompt
        prompt_context = {
            "passenger": passenger_data or {},
            "booking": booking_data or {},
            "flight": flight_data or {},
            "recommended_flight": recommended_flight or {},
            "priority": priority,
            "reason": reason,
            "local_language": local_language,
        }
        
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": NOTIFICATION_GENERATION_SYSTEM_PROMPT},
                {"role": "user", "content": f"Generate a notification for this rebooking: {prompt_context}"}
            ],
            temperature=0.3,
            max_tokens=300,
            response_format={"type": "json_object"},
        )
        
        import json
        notification_data = json.loads(response.choices[0].message.content)
        
        result = {
            "en": notification_data.get("en"),
            "local": notification_data.get("local"),
        }
        
        logger.info(f"Generated AI notification: en={result['en']}, local={result['local']}")
        return result
        
    except Exception as e:
        logger.error(f"OpenAI notification generation failed: {e}, using template")
        return {
            "en": f"Flight {flight_data.get('flight_number') if flight_data else 'Unknown'} has been disrupted. {reason}",
            "local": None,
        }


async def run_ai_analysis(
    passenger_id: UUID,
    flight_id: UUID,
    db: AsyncSession
) -> AgentState:
    """
    Run the AI reasoning analysis for a passenger.
    
    This orchestrator follows the intended graph flow without using LangGraph:
    1. Load passenger data
    2. Analyze constraints (deterministic priority)
    3. Fetch alternatives
    4. Evaluate alternatives (deterministic matching)
    5. Generate AI reason
    6. Generate AI notification
    7. Return state for human review
    
    Args:
        passenger_id: UUID of the passenger
        flight_id: UUID of the cancelled flight
        db: Async database session
        
    Returns:
        AgentState with analysis results
    """
    state: AgentState = {
        "passenger_id": str(passenger_id),
        "flight_id": str(flight_id),
        "passenger_data": None,
        "booking_data": None,
        "connections": None,
        "candidates": None,
        "priority": None,
        "priority_reason": None,
        "recommended_flight": None,
        "notification_en": None,
        "notification_local": None,
        "local_language": None,
        "human_decision": None,
        "error": None,
    }
    
    try:
        # Node 1: Load passenger data
        state["passenger_data"] = await tool_get_passenger(passenger_id, db)
        state["booking_data"] = await tool_get_booking_by_passenger_and_flight(passenger_id, flight_id, db)
        state["connections"] = await tool_get_connecting_flights(passenger_id, db)
        
        if not state["passenger_data"] or not state["booking_data"]:
            state["error"] = "Passenger or booking not found"
            return state
        
        # Node 2: Analyze constraints (deterministic priority)
        # We need to reconstruct ORM objects for the deterministic engines
        from sqlalchemy import select
        passenger_stmt = select(Passenger).where(Passenger.passenger_id == passenger_id)
        passenger_result = await db.execute(passenger_stmt)
        passenger = passenger_result.scalar_one_or_none()
        
        flight_stmt = select(Flight).where(Flight.flight_id == flight_id)
        flight_result = await db.execute(flight_stmt)
        flight = flight_result.scalar_one_or_none()
        
        if not passenger or not flight:
            state["error"] = "Passenger or flight not found"
            return state
        
        # Fetch connecting flights as ORM objects
        connecting_flights = await get_connecting_flights(passenger_id, db)
        
        # Call deterministic priority engine
        priority, priority_reason = score_priority(passenger, connecting_flights, flight)
        state["priority"] = priority.value
        state["priority_reason"] = priority_reason
        
        # Node 3: Fetch alternatives
        state["candidates"] = await tool_get_available_flights(flight.origin, flight.destination, db)
        
        # Node 4: Evaluate alternatives (deterministic matching)
        # We need AlternativeFlight ORM objects for the matching engine
        from sqlalchemy import select
        alt_flights_stmt = select(AlternativeFlight).where(
            AlternativeFlight.origin == flight.origin,
            AlternativeFlight.destination == flight.destination
        )
        alt_flights_result = await db.execute(alt_flights_stmt)
        alternative_candidates = alt_flights_result.scalars().all()
        
        recommended_flight = find_alternative(passenger, connecting_flights, alternative_candidates)
        
        if recommended_flight:
            state["recommended_flight"] = {
                "alternative_flight_id": str(recommended_flight.alternative_flight_id),
                "flight_number": recommended_flight.flight_number,
                "airline": recommended_flight.airline,
                "origin": recommended_flight.origin,
                "destination": recommended_flight.destination,
                "departure_time": recommended_flight.departure_time.isoformat(),
                "arrival_time": recommended_flight.arrival_time.isoformat(),
                "available_seats": recommended_flight.available_seats,
            }
        else:
            state["recommended_flight"] = None
        
        # Node 5: Generate AI reason
        flight_data = {
            "flight_id": str(flight.flight_id),
            "flight_number": flight.flight_number,
            "origin": flight.origin,
            "destination": flight.destination,
            "departure_time": flight.departure_time.isoformat(),
            "arrival_time": flight.arrival_time.isoformat(),
        }
        
        ai_reason = await generate_ai_reason(
            state["priority"],
            state["priority_reason"],
            state["passenger_data"],
            flight_data,
            state["connections"]
        )
        state["priority_reason"] = ai_reason  # Use AI-generated reason
        
        # Node 6: Generate AI notification
        notifications = await generate_ai_notification(
            state["passenger_data"],
            state["booking_data"],
            flight_data,
            state["recommended_flight"],
            state["priority"],
            state["priority_reason"]
        )
        state["notification_en"] = notifications["en"]
        state["notification_local"] = notifications["local"]
        state["local_language"] = state["passenger_data"].get("preferred_language") if state["passenger_data"] else None
        
        # Human decision will be handled by existing FastAPI workflow
        state["human_decision"] = None
        
        return state
        
    except Exception as e:
        logger.error(f"AI analysis failed: {e}")
        state["error"] = str(e)
        return state


def create_rebooking_graph():
    """
    Placeholder for graph creation compatibility.
    
    Due to LangGraph 0.1.5 dependency issues, we use the simpler
    orchestrator pattern in run_ai_analysis instead.
    """
    return None