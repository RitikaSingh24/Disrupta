"""
backend/app/models/base.py

Shared SQLAlchemy 2.0 declarative base.
Import Base from here in every model file — never redefine it.
This file contains NO table definition; it is pure ORM infrastructure.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Project-wide declarative base for all ORM models."""
    pass
