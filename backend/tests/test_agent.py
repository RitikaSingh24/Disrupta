"""
tests/test_agent.py

Tests for the AI reasoning layer agent functions.

These tests verify that the agent functions exist and have the correct signatures.
They do not require OpenAI API calls or database connection for basic structure verification.
"""

import pytest
from uuid import uuid4

from app.agent.state import AgentState
from app.agent.graph import run_ai_analysis, create_rebooking_graph
from app.agent.tools import (
    tool_get_passenger,
    tool_get_booking,
    tool_get_booking_by_passenger_and_flight,
    tool_get_connecting_flights,
    tool_get_available_flights,
    tool_update_rebooking,
)
from app.agent.prompts import REASON_GENERATION_SYSTEM_PROMPT, NOTIFICATION_GENERATION_SYSTEM_PROMPT


def test_agent_state_structure():
    """Test that AgentState has the required fields."""
    import inspect
    
    state_fields = list(AgentState.__annotations__.keys())
    
    required_fields = [
        "passenger_id",
        "flight_id",
        "passenger_data",
        "booking_data",
        "connections",
        "candidates",
        "priority",
        "priority_reason",
        "recommended_flight",
        "notification_en",
        "notification_local",
        "local_language",
        "human_decision",
        "error",
    ]
    
    for field in required_fields:
        assert field in state_fields, f"Missing required field: {field}"


def test_agent_functions_exist():
    """Test that agent functions are defined and callable."""
    assert callable(run_ai_analysis)
    assert callable(create_rebooking_graph)


def test_agent_tools_exist():
    """Test that agent tool functions are defined and callable."""
    assert callable(tool_get_passenger)
    assert callable(tool_get_booking)
    assert callable(tool_get_booking_by_passenger_and_flight)
    assert callable(tool_get_connecting_flights)
    assert callable(tool_get_available_flights)
    assert callable(tool_update_rebooking)


def test_prompts_exist():
    """Test that prompts are defined and contain required grounding rule."""
    assert isinstance(REASON_GENERATION_SYSTEM_PROMPT, str)
    assert isinstance(NOTIFICATION_GENERATION_SYSTEM_PROMPT, str)
    
    # Verify mandatory fact-grounding rule is present
    grounding_rule = "You may only use facts explicitly present in the provided passenger/booking/flight JSON"
    assert grounding_rule in REASON_GENERATION_SYSTEM_PROMPT
    assert grounding_rule in NOTIFICATION_GENERATION_SYSTEM_PROMPT


def test_prompts_dont_invent_facts():
    """Test that prompts explicitly forbid inventing facts."""
    # Check for anti-hallucination rules
    anti_hallucination_rules = [
        "do not assume or invent a value",
        "never invent a medical, business, or family circumstance",
        "never invent missing information",
    ]
    
    reason_lower = REASON_GENERATION_SYSTEM_PROMPT.lower()
    notification_lower = NOTIFICATION_GENERATION_SYSTEM_PROMPT.lower()
    
    for rule in anti_hallucination_rules:
        assert rule.lower() in reason_lower or rule.lower() in notification_lower


def test_ai_analysis_signature():
    """Test that run_ai_analysis has the expected signature."""
    import inspect
    
    sig = inspect.signature(run_ai_analysis)
    params = list(sig.parameters.keys())
    
    assert "passenger_id" in params
    assert "flight_id" in params
    assert "db" in params


def test_graph_returns_none():
    """Test that create_rebooking_graph returns None (due to LangGraph compatibility issues)."""
    graph = create_rebooking_graph()
    assert graph is None