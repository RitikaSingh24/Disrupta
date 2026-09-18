"""
backend/app/agent/__init__.py

AI Reasoning Layer for the IROP Passenger Rebooking Copilot.

This layer sits on top of the existing deterministic rebooking engines.
The LLM is responsible only for:
- Converting deterministic reasons into natural language
- Generating passenger notifications

The deterministic engines remain the source of truth for:
- Priority calculation
- Alternative flight selection
"""

from app.agent.graph import create_rebooking_graph

__all__ = ["create_rebooking_graph"]