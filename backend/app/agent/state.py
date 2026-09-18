"""
backend/app/agent/state.py

Agent state for the AI reasoning layer.
"""

from typing import TypedDict, Optional


class AgentState(TypedDict):
    """State for the rebooking reasoning agent."""
    passenger_id: str
    flight_id: str
    passenger_data: Optional[dict]
    booking_data: Optional[dict]
    connections: Optional[list]
    candidates: Optional[list]
    priority: Optional[str]
    priority_reason: Optional[str]
    recommended_flight: Optional[dict]
    notification_en: Optional[str]
    notification_local: Optional[str]
    local_language: Optional[str]
    human_decision: Optional[str]  # "approve" | "edit" | "reject" | None (pending)
    error: Optional[str]