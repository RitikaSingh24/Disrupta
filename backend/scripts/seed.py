"""
backend/scripts/seed.py

Database Seed Script for IROP Passenger Rebooking Copilot.

Populates Supabase / PostgreSQL with initial demo data:
  - 3 User accounts (admin, ops agent, supervisor) with password "Password123!"
  - Sample disrupted & alternative flights
  - Sample passengers & bookings covering HIGH / MEDIUM / NORMAL priority

Usage:
    cd backend
    python -m scripts.seed
"""

import asyncio
from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.core.security import hash_password
from app.db.session import AsyncSessionLocal
from app.models.alternative_flight import AlternativeFlight
from app.models.booking import Booking
from app.models.connecting_flight import ConnectingFlight
from app.models.enums import BookingStatus, FlightStatus, UserRole
from app.models.flight import Flight
from app.models.passenger import Passenger
from app.models.user import User


async def seed_data():
    print("Starting Supabase / Database seeding...")

    async with AsyncSessionLocal() as session:
        # 1. Seed Users (Employees)
        existing_user = await session.execute(select(User).where(User.email == "agent@airline.com"))
        if existing_user.scalar_one_or_none():
            print("Users already exist in database. Skipping user seed.")
        else:
            default_password_hash = hash_password("Password123!")
            users = [
                User(
                    name="Operations Agent",
                    email="agent@airline.com",
                    password_hash=default_password_hash,
                    role=UserRole.OPERATIONS_AGENT,
                ),
                User(
                    name="Ops Supervisor",
                    email="supervisor@airline.com",
                    password_hash=default_password_hash,
                    role=UserRole.SUPERVISOR,
                ),
                User(
                    name="System Administrator",
                    email="admin@airline.com",
                    password_hash=default_password_hash,
                    role=UserRole.ADMIN,
                ),
            ]
            session.add_all(users)
            print("[SUCCESS] Inserted 3 employee user accounts.")

        # 2. Seed Flights
        now = datetime.now(timezone.utc)

        # Cancelled flight departs in 2 hours
        flight_cancelled = Flight(
            flight_number="AA-100",
            airline="American Airlines",
            origin="JFK",
            destination="LHR",
            departure_time=now + timedelta(hours=2),
            arrival_time=now + timedelta(hours=9),
            status=FlightStatus.CANCELLED,
            cancellation_reason="Severe weather at origin airport",
            total_seats=180,
        )
        session.add(flight_cancelled)
        await session.flush()

        # 3. Seed Alternative Candidate Flights
        alt_flights = [
            AlternativeFlight(
                flight_number="BA-178",
                origin="JFK",
                destination="LHR",
                departure_time=now + timedelta(hours=5),
                arrival_time=now + timedelta(hours=12),
                available_seats=25,
                linked_original_flight_id=flight_cancelled.flight_id,
            ),
            AlternativeFlight(
                flight_number="VS-004",
                origin="JFK",
                destination="LHR",
                departure_time=now + timedelta(hours=7),
                arrival_time=now + timedelta(hours=14),
                available_seats=12,
                linked_original_flight_id=flight_cancelled.flight_id,
            ),
        ]
        session.add_all(alt_flights)

        # 4. Seed Passengers
        # HIGH priority: has special requirement (wheelchair)
        p1 = Passenger(
            name="Robert Miller",
            email="robert.miller@example.com",
            phone="+1-555-0192",
            preferred_language="English",
            special_requirement="Wheelchair assistance required",
            requirement_type="MOBILITY",
        )

        # MEDIUM priority: has a connecting flight 8 hours after cancelled departure
        # Cancelled departs +2h, connecting departs +10h → gap = 8h ≤ 18h → MEDIUM
        p2 = Passenger(
            name="Priya Sharma",
            email="priya.sharma@example.com",
            phone="+1-555-0201",
            preferred_language="English",
        )

        # NORMAL priority: no special requirement, no connecting flight
        p3 = Passenger(
            name="Maria Garcia",
            email="maria.garcia@example.com",
            phone="+1-555-0143",
            preferred_language="Spanish",
        )

        # NORMAL priority: no special requirement, no connecting flight
        p4 = Passenger(
            name="James Chen",
            email="james.chen@example.com",
            phone="+1-555-0177",
            preferred_language="English",
        )

        session.add_all([p1, p2, p3, p4])
        await session.flush()

        # 5. Seed Bookings on cancelled flight
        b1 = Booking(
            passenger_id=p1.passenger_id,
            flight_id=flight_cancelled.flight_id,
            seat_number="2A",
            booking_class="Business",
            booking_status=BookingStatus.CONFIRMED,
        )
        b2 = Booking(
            passenger_id=p2.passenger_id,
            flight_id=flight_cancelled.flight_id,
            seat_number="15C",
            booking_class="Economy",
            booking_status=BookingStatus.CONFIRMED,
        )
        b3 = Booking(
            passenger_id=p3.passenger_id,
            flight_id=flight_cancelled.flight_id,
            seat_number="24F",
            booking_class="Economy",
            booking_status=BookingStatus.CONFIRMED,
        )
        b4 = Booking(
            passenger_id=p4.passenger_id,
            flight_id=flight_cancelled.flight_id,
            seat_number="30B",
            booking_class="Economy",
            booking_status=BookingStatus.CONFIRMED,
        )
        session.add_all([b1, b2, b3, b4])
        await session.flush()

        # 6. Seed connecting flight record for Priya Sharma (gives her MEDIUM priority)
        # Departs ~10 hours from now → gap from cancelled departure (+2h) = 8h → MEDIUM
        cf_priya = ConnectingFlight(
            passenger_id=p2.passenger_id,
            booking_id=b2.booking_id,
            flight_number="LH-401",
            departure_time=now + timedelta(hours=10),
            destination="MUC",
        )
        session.add(cf_priya)

        await session.commit()
        print("[SUCCESS] Inserted demo cancelled flight (AA-100), alternative flights, 4 passengers, and bookings.")
        print("  → Robert Miller  : 🔴 HIGH   (wheelchair assistance)")
        print("  → Priya Sharma   : 🟠 MEDIUM (connecting LH-401 in ~8h gap)")
        print("  → Maria Garcia   : 🟢 NORMAL (no special needs)")
        print("  → James Chen     : 🟢 NORMAL (no special needs)")

    print("\n[SUCCESS] Database seeding completed successfully!")


if __name__ == "__main__":
    asyncio.run(seed_data())
