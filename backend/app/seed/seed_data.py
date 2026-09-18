"""
backend/app/seed/seed_data.py

Comprehensive Database Seed Script for IROP Passenger Rebooking Copilot.

Populates Supabase / PostgreSQL with deterministic test data for the rebooking engine:
  - 3 User accounts (admin, ops agent, supervisor) with password "Password123!"
  - 10 Flights (including AA-100 CANCELLED for demo scenarios)
  - 100 Passengers (including 4 specific demo passengers for testing)
  - 150 Bookings
  - 100 Connecting Flights
  - 30 Alternative Flights

Usage:
    cd backend
    python -m app.seed.seed_data

Seed strategy:
This script uses clear-and-reinsert.
Existing seed/demo records are removed before inserting
the deterministic demo dataset.
This makes repeated runs produce a clean predictable dataset.

Deletion order respects foreign-key constraints:
  1. Notifications (no FK constraints on others, but referenced by recommendations)
  2. Rebooking Recommendations (references passengers, bookings, flights, users, alternative_flights)
  3. Connecting Flights (references passengers, bookings)
  4. Bookings (references passengers, flights)
  5. Alternative Flights (references flights)
  6. Passengers (referenced by bookings, connecting flights, recommendations, notifications, access_tokens)
  7. Flights (referenced by bookings, alternative flights, recommendations, access_tokens)
  8. Users (referenced by recommendations)
  9. Passenger Access Tokens (references passengers, flights)
"""

import asyncio
from datetime import datetime, timedelta, timezone
from typing import Set

from faker import Faker
from sqlalchemy import delete, select
from sqlalchemy.orm import selectinload

from app.core.security import hash_password
from app.db.session import AsyncSessionLocal
from app.models.access_token import PassengerAccessToken
from app.models.alternative_flight import AlternativeFlight
from app.models.booking import Booking
from app.models.connecting_flight import ConnectingFlight
from app.models.enums import (
    BookingStatus,
    FlightStatus,
    NotificationStatus,
    PriorityLevel,
    RecommendationStatus,
    UserRole,
)
from app.models.flight import Flight
from app.models.notification import Notification
from app.models.passenger import Passenger
from app.models.recommendation import RebookingRecommendation
from app.models.user import User

# Use deterministic Faker seed for reproducible test data
Faker.seed(42)
fake = Faker()

# Target quantities
TARGET_FLIGHTS = 10
TARGET_PASSENGERS = 100
TARGET_BOOKINGS = 150
TARGET_CONNECTING_FLIGHTS = 100
TARGET_ALTERNATIVE_FLIGHTS = 30

# Demo flight constants
DEMO_FLIGHT_NUMBER = "AA-100"
DEMO_AIRLINE = "American Airlines"


async def clear_existing_data(session: AsyncSessionLocal) -> None:
    """Clear existing seed data in dependency-safe order."""
    print("Clearing existing seed data...")
    
    # Delete in order respecting foreign key constraints
    await session.execute(delete(Notification))
    await session.execute(delete(RebookingRecommendation))
    await session.execute(delete(ConnectingFlight))
    await session.execute(delete(Booking))
    await session.execute(delete(AlternativeFlight))
    await session.execute(delete(PassengerAccessToken))
    await session.execute(delete(Passenger))
    await session.execute(delete(Flight))
    await session.execute(delete(User))
    
    await session.commit()
    print("[SUCCESS] Cleared existing seed data.")


async def seed_users(session: AsyncSessionLocal) -> None:
    """Seed 3 employee users with known credentials."""
    print("Seeding users...")
    
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
    await session.flush()
    print(f"[SUCCESS] Inserted 3 employee user accounts.")


async def seed_flights(session: AsyncSessionLocal) -> dict:
    """Seed 10 flights including the mandatory AA-100 CANCELLED flight."""
    print("Seeding flights...")
    
    now = datetime.now(timezone.utc)
    
    # Create the mandatory demo flight AA-100 (CANCELLED)
    # Store departure time for calculating connecting flight scenarios
    demo_flight_departure = now + timedelta(hours=2)
    
    demo_flight = Flight(
        flight_number=DEMO_FLIGHT_NUMBER,
        airline=DEMO_AIRLINE,
        origin="JFK",
        destination="LHR",
        departure_time=demo_flight_departure,
        arrival_time=now + timedelta(hours=9),
        status=FlightStatus.CANCELLED,
        cancellation_reason="Severe weather at origin airport",
        total_seats=180,
    )
    session.add(demo_flight)
    await session.flush()
    
    # Generate 9 additional flights with varied statuses and routes
    airlines = ["Delta", "United", "British Airways", "Lufthansa", "Air France"]
    routes = [
        ("JFK", "LAX"), ("SFO", "ORD"), ("LHR", "CDG"), ("FRA", "MUC"), 
        ("DXB", "SIN"), ("HKG", "NRT"), ("SYD", "MEL"), ("YYZ", "YVR"), ("JNB", "CPT")
    ]
    
    for i in range(9):
        flight = Flight(
            flight_number=f"{fake.random_element(['AA', 'DL', 'UA', 'BA', 'LH', 'AF'])}-{fake.random_int(100, 999)}",
            airline=fake.random_element(airlines),
            origin=routes[i][0],
            destination=routes[i][1],
            departure_time=now + timedelta(days=fake.random_int(0, 3), hours=fake.random_int(0, 23)),
            arrival_time=now + timedelta(days=fake.random_int(0, 3), hours=fake.random_int(0, 23)),
            status=fake.random_element(list(FlightStatus)),
            cancellation_reason=fake.sentence() if fake.boolean() else None,
            total_seats=fake.random_int(120, 300),
        )
        session.add(flight)
    
    await session.flush()
    
    # Return demo flight info for passenger scenarios
    return {
        "demo_flight_id": demo_flight.flight_id,
        "demo_flight_departure": demo_flight_departure,
    }


async def seed_demo_passengers(session: AsyncSessionLocal, demo_flight_id: str, demo_flight_departure: datetime) -> dict:
    """Seed the 4 mandatory demo passengers with specific scenarios."""
    print("Seeding demo passengers...")
    
    # Rahul Sharma - Tight Connection Test Case
    # Rahul intentionally has a short connection window.
    # This gives the future rebooking engine a deterministic
    # tight-connection test case.
    rahul = Passenger(
        name="Rahul Sharma",
        email="rahul.sharma@example.com",
        phone=fake.phone_number(),
        preferred_language="English",
        special_requirement=None,
        requirement_type=None,
    )
    session.add(rahul)
    await session.flush()
    
    # Rahul's booking on AA-100
    rahul_booking = Booking(
        passenger_id=rahul.passenger_id,
        flight_id=demo_flight_id,
        seat_number="12A",
        booking_class="Economy",
        booking_status=BookingStatus.CONFIRMED,
    )
    session.add(rahul_booking)
    await session.flush()
    
    # Rahul's connecting flight departing ~2.5 hours after AA-100 departure
    rahul_connection = ConnectingFlight(
        passenger_id=rahul.passenger_id,
        booking_id=rahul_booking.booking_id,
        flight_number="BA-456",
        departure_time=demo_flight_departure + timedelta(hours=2, minutes=30),
        destination="FRA",
    )
    session.add(rahul_connection)
    
    # Priya - No Connection Test Case
    # Priya has no special requirements and no connecting flight.
    # This represents a passenger with no connection dependency.
    priya = Passenger(
        name="Priya",
        email="priya@example.com",
        phone=fake.phone_number(),
        preferred_language="English",
        special_requirement=None,  # Explicitly NULL
        requirement_type=None,
    )
    session.add(priya)
    await session.flush()
    
    # Priya's booking on AA-100 (no connecting flight record)
    priya_booking = Booking(
        passenger_id=priya.passenger_id,
        flight_id=demo_flight_id,
        seat_number="15B",
        booking_class="Economy",
        booking_status=BookingStatus.CONFIRMED,
    )
    session.add(priya_booking)
    
    # Amit - Fully Flexible Test Case
    # Amit has no special requirements and no connecting flight.
    # Amit represents the fully flexible passenger scenario.
    amit = Passenger(
        name="Amit",
        email="amit@example.com",
        phone=fake.phone_number(),
        preferred_language="English",
        special_requirement=None,  # Explicitly NULL
        requirement_type=None,
    )
    session.add(amit)
    await session.flush()
    
    # Amit's booking on AA-100 (no connecting flight record)
    amit_booking = Booking(
        passenger_id=amit.passenger_id,
        flight_id=demo_flight_id,
        seat_number="18C",
        booking_class="Economy",
        booking_status=BookingStatus.CONFIRMED,
    )
    session.add(amit_booking)
    
    # Neha - Next-Morning Connection Test Case
    # Neha has a next-morning connection (~14 hours after AA-100 departure).
    # This represents a passenger with a long connection window.
    neha = Passenger(
        name="Neha",
        email="neha@example.com",
        phone=fake.phone_number(),
        preferred_language="English",
        special_requirement=None,
        requirement_type=None,
    )
    session.add(neha)
    await session.flush()
    
    # Neha's booking on AA-100
    neha_booking = Booking(
        passenger_id=neha.passenger_id,
        flight_id=demo_flight_id,
        seat_number="22A",
        booking_class="Economy",
        booking_status=BookingStatus.CONFIRMED,
    )
    session.add(neha_booking)
    await session.flush()
    
    # Neha's connecting flight departing ~14 hours after AA-100 departure
    neha_connection = ConnectingFlight(
        passenger_id=neha.passenger_id,
        booking_id=neha_booking.booking_id,
        flight_number="LH-789",
        departure_time=demo_flight_departure + timedelta(hours=14),
        destination="CDG",
    )
    session.add(neha_connection)
    
    await session.flush()
    
    # Return demo passenger IDs for tracking
    return {
        "rahul_id": rahul.passenger_id,
        "priya_id": priya.passenger_id,
        "amit_id": amit.passenger_id,
        "neha_id": neha.passenger_id,
        "rahul_booking_id": rahul_booking.booking_id,
        "priya_booking_id": priya_booking.booking_id,
        "amit_booking_id": amit_booking.booking_id,
        "neha_booking_id": neha_booking.booking_id,
    }


async def seed_remaining_passengers(session: AsyncSessionLocal, flight_ids: list) -> dict:
    """Seed remaining passengers with Faker to reach 100 total."""
    print(f"Seeding remaining {TARGET_PASSENGERS - 4} passengers...")
    
    # Track used emails to ensure uniqueness
    used_emails: Set[str] = set()
    
    # Get existing emails from demo passengers
    demo_emails = {"rahul.sharma@example.com", "priya@example.com", "amit@example.com", "neha@example.com"}
    used_emails.update(demo_emails)
    
    passengers = []
    for i in range(TARGET_PASSENGERS - 4):
        # Generate unique email
        while True:
            email = fake.email()
            if email not in used_emails:
                used_emails.add(email)
                break
        
        passenger = Passenger(
            name=fake.name(),
            email=email,
            phone=fake.phone_number(),
            preferred_language=fake.random_element(["English", "Spanish", "French", "German", "Chinese"]),
            special_requirement=fake.sentence() if fake.boolean(25) else None,  # 25% chance of having requirement
            requirement_type=fake.random_element(["Medical", "Business", "Family Emergency", "Mobility"]) if fake.boolean(25) else None,
            requirement_declared_at=fake.date_time_between(start_date="-30d", end_date="now", tzinfo=timezone.utc) if fake.boolean(25) else None,
        )
        passengers.append(passenger)
    
    session.add_all(passengers)
    await session.flush()
    
    # Return all passenger IDs for booking creation
    result = await session.execute(select(Passenger.passenger_id))
    all_passenger_ids = [row[0] for row in result.fetchall()]
    
    return {"all_passenger_ids": all_passenger_ids}


async def seed_bookings(session: AsyncSessionLocal, passenger_ids: list, flight_ids: list, demo_booking_ids: list) -> None:
    """Seed bookings to reach 150 total (including 4 demo bookings)."""
    print(f"Seeding remaining {TARGET_BOOKINGS - 4} bookings...")
    
    # Get all flight IDs
    result = await session.execute(select(Flight.flight_id))
    all_flight_ids = [row[0] for row in result.fetchall()]
    
    # Filter out demo booking IDs to avoid duplicates
    remaining_passenger_ids = [pid for pid in passenger_ids if pid not in demo_booking_ids]
    
    bookings = []
    for i in range(TARGET_BOOKINGS - 4):
        booking = Booking(
            passenger_id=fake.random_element(remaining_passenger_ids),
            flight_id=fake.random_element(all_flight_ids),
            seat_number=fake.random_element([f"{row}{seat}" for row in ["A", "B", "C", "D", "E", "F"] for seat in range(1, 30)]),
            booking_class=fake.random_element(["Economy", "Business", "First"]),
            booking_status=fake.random_element(list(BookingStatus)),
        )
        bookings.append(booking)
    
    session.add_all(bookings)
    await session.flush()
    print(f"[SUCCESS] Inserted {TARGET_BOOKINGS} total bookings.")


async def seed_connecting_flights(session: AsyncSessionLocal, passenger_ids: list, booking_ids: list) -> None:
    """Seed connecting flights to reach 100 total (including 2 demo connections)."""
    print(f"Seeding remaining {TARGET_CONNECTING_FLIGHTS - 2} connecting flights...")
    
    # Get all booking IDs
    result = await session.execute(select(Booking.booking_id))
    all_booking_ids = [row[0] for row in result.fetchall()]
    
    # Get all passenger IDs
    result = await session.execute(select(Passenger.passenger_id))
    all_passenger_ids = [row[0] for row in result.fetchall()]
    
    connecting_flights = []
    for i in range(TARGET_CONNECTING_FLIGHTS - 2):
        connecting_flight = ConnectingFlight(
            passenger_id=fake.random_element(all_passenger_ids),
            booking_id=fake.random_element(all_booking_ids) if fake.boolean(80) else None,  # 80% chance of being linked to a booking
            flight_number=f"{fake.random_element(['AA', 'DL', 'UA', 'BA', 'LH', 'AF'])}-{fake.random_int(100, 999)}",
            departure_time=fake.date_time_between(start_date="+1d", end_date="+3d", tzinfo=timezone.utc),
            destination=fake.random_element(["FRA", "CDG", "AMS", "MUC", "DXB", "SIN", "HKG", "NRT"]),
        )
        connecting_flights.append(connecting_flight)
    
    session.add_all(connecting_flights)
    await session.flush()
    print(f"[SUCCESS] Inserted {TARGET_CONNECTING_FLIGHTS} total connecting flights.")


async def seed_alternative_flights(session: AsyncSessionLocal, demo_flight_id: str) -> None:
    """Seed 30 alternative flights including some for AA-100."""
    print(f"Seeding {TARGET_ALTERNATIVE_FLIGHTS} alternative flights...")
    
    now = datetime.now(timezone.utc)
    
    # Create some alternative flights specifically for AA-100
    demo_alternatives = [
        AlternativeFlight(
            flight_number="BA-178",
            origin="JFK",
            destination="LHR",
            departure_time=now + timedelta(hours=5),
            arrival_time=now + timedelta(hours=12),
            available_seats=25,
            linked_original_flight_id=demo_flight_id,
        ),
        AlternativeFlight(
            flight_number="VS-004",
            origin="JFK",
            destination="LHR",
            departure_time=now + timedelta(hours=7),
            arrival_time=now + timedelta(hours=14),
            available_seats=12,
            linked_original_flight_id=demo_flight_id,
        ),
        AlternativeFlight(
            flight_number="DL-234",
            origin="JFK",
            destination="LHR",
            departure_time=now + timedelta(hours=4),
            arrival_time=now + timedelta(hours=11),
            available_seats=8,
            linked_original_flight_id=demo_flight_id,
        ),
    ]
    
    session.add_all(demo_alternatives)
    
    # Generate remaining alternative flights
    airlines = ["Delta", "United", "British Airways", "Lufthansa", "Air France"]
    routes = [
        ("JFK", "LAX"), ("SFO", "ORD"), ("LHR", "CDG"), ("FRA", "MUC"), 
        ("DXB", "SIN"), ("HKG", "NRT"), ("SYD", "MEL"), ("YYZ", "YVR")
    ]
    
    for i in range(TARGET_ALTERNATIVE_FLIGHTS - 3):
        alt_flight = AlternativeFlight(
            flight_number=f"{fake.random_element(['AA', 'DL', 'UA', 'BA', 'LH', 'AF'])}-{fake.random_int(100, 999)}",
            origin=routes[i % len(routes)][0],
            destination=routes[i % len(routes)][1],
            departure_time=now + timedelta(days=fake.random_int(0, 2), hours=fake.random_int(0, 23)),
            arrival_time=now + timedelta(days=fake.random_int(0, 2), hours=fake.random_int(0, 23)),
            available_seats=fake.random_int(5, 50),
            linked_original_flight_id=None,  # Some alternatives are not linked to specific flights
        )
        session.add(alt_flight)
    
    await session.flush()
    print(f"[SUCCESS] Inserted {TARGET_ALTERNATIVE_FLIGHTS} alternative flights.")


async def verify_counts(session: AsyncSessionLocal) -> None:
    """Verify final database counts match targets."""
    print("\nVerifying database counts...")
    
    tables = [
        (User, 3, "Users"),
        (Flight, TARGET_FLIGHTS, "Flights"),
        (Passenger, TARGET_PASSENGERS, "Passengers"),
        (Booking, TARGET_BOOKINGS, "Bookings"),
        (ConnectingFlight, TARGET_CONNECTING_FLIGHTS, "Connecting Flights"),
        (AlternativeFlight, TARGET_ALTERNATIVE_FLIGHTS, "Alternative Flights"),
    ]
    
    all_correct = True
    for model, expected, name in tables:
        result = await session.execute(select(model))
        count = len(result.fetchall())
        status = "[OK]" if count == expected else "[FAIL]"
        print(f"{status} {name}: {count} (expected {expected})")
        if count != expected:
            all_correct = False
    
    if all_correct:
        print("\n[SUCCESS] All database counts match targets!")
    else:
        print("\n[WARNING] Some counts do not match targets.")


async def verify_demo_scenarios(session: AsyncSessionLocal) -> None:
    """Verify the 4 mandatory demo passenger scenarios."""
    print("\nVerifying demo passenger scenarios...")
    
    # Get demo flight
    result = await session.execute(
        select(Flight).where(Flight.flight_number == DEMO_FLIGHT_NUMBER)
    )
    demo_flight = result.scalar_one_or_none()
    
    if not demo_flight:
        print("[FAIL] Demo flight AA-100 not found")
        return
    
    print(f"[OK] Demo flight AA-100 found (status: {demo_flight.status})")
    
    # Verify Rahul Sharma
    result = await session.execute(
        select(Passenger).where(Passenger.name == "Rahul Sharma")
    )
    rahul = result.scalar_one_or_none()
    
    if rahul:
        print(f"[OK] Rahul Sharma found")
        
        # Check Rahul's booking on AA-100
        result = await session.execute(
            select(Booking).where(
                Booking.passenger_id == rahul.passenger_id,
                Booking.flight_id == demo_flight.flight_id
            )
        )
        rahul_booking = result.scalar_one_or_none()
        
        if rahul_booking:
            print(f"[OK] Rahul has booking on AA-100")
            
            # Check Rahul's connecting flight (~2.5 hours after AA-100 departure)
            result = await session.execute(
                select(ConnectingFlight).where(
                    ConnectingFlight.passenger_id == rahul.passenger_id
                )
            )
            rahul_connection = result.scalars().first()
            
            if rahul_connection:
                time_diff = rahul_connection.departure_time - demo_flight.departure_time
                hours_diff = time_diff.total_seconds() / 3600
                print(f"[OK] Rahul has connecting flight departing {hours_diff:.1f} hours after AA-100 (target: ~2.5 hours)")
            else:
                print("[FAIL] Rahul missing connecting flight")
        else:
            print("[FAIL] Rahul missing booking on AA-100")
    else:
        print("[FAIL] Rahul Sharma not found")
    
    # Verify Priya
    result = await session.execute(
        select(Passenger).where(Passenger.name == "Priya")
    )
    priya = result.scalar_one_or_none()
    
    if priya:
        print(f"[OK] Priya found (special_requirement: {priya.special_requirement})")
        
        # Check Priya's booking on AA-100
        result = await session.execute(
            select(Booking).where(
                Booking.passenger_id == priya.passenger_id,
                Booking.flight_id == demo_flight.flight_id
            )
        )
        priya_booking = result.scalar_one_or_none()
        
        if priya_booking:
            print(f"[OK] Priya has booking on AA-100")
            
            # Verify Priya has NO connecting flight
            result = await session.execute(
                select(ConnectingFlight).where(
                    ConnectingFlight.passenger_id == priya.passenger_id
                )
            )
            priya_connection = result.scalar_one_or_none()
            
            if not priya_connection:
                print(f"[OK] Priya has no connecting flight (as expected)")
            else:
                print("[FAIL] Priya should not have connecting flight")
        else:
            print("[FAIL] Priya missing booking on AA-100")
    else:
        print("[FAIL] Priya not found")
    
    # Verify Amit
    result = await session.execute(
        select(Passenger).where(Passenger.name == "Amit")
    )
    amit = result.scalar_one_or_none()
    
    if amit:
        print(f"[OK] Amit found (special_requirement: {amit.special_requirement})")
        
        # Check Amit's booking on AA-100
        result = await session.execute(
            select(Booking).where(
                Booking.passenger_id == amit.passenger_id,
                Booking.flight_id == demo_flight.flight_id
            )
        )
        amit_booking = result.scalar_one_or_none()
        
        if amit_booking:
            print(f"[OK] Amit has booking on AA-100")
            
            # Verify Amit has NO connecting flight
            result = await session.execute(
                select(ConnectingFlight).where(
                    ConnectingFlight.passenger_id == amit.passenger_id
                )
            )
            amit_connection = result.scalar_one_or_none()
            
            if not amit_connection:
                print(f"[OK] Amit has no connecting flight (as expected)")
            else:
                print("[FAIL] Amit should not have connecting flight")
        else:
            print("[FAIL] Amit missing booking on AA-100")
    else:
        print("[FAIL] Amit not found")
    
    # Verify Neha
    result = await session.execute(
        select(Passenger).where(Passenger.name == "Neha")
    )
    neha = result.scalar_one_or_none()
    
    if neha:
        print(f"[OK] Neha found")
        
        # Check Neha's booking on AA-100
        result = await session.execute(
            select(Booking).where(
                Booking.passenger_id == neha.passenger_id,
                Booking.flight_id == demo_flight.flight_id
            )
        )
        neha_booking = result.scalar_one_or_none()
        
        if neha_booking:
            print(f"[OK] Neha has booking on AA-100")
            
            # Check Neha's connecting flight (~14 hours after AA-100 departure)
            result = await session.execute(
                select(ConnectingFlight).where(
                    ConnectingFlight.passenger_id == neha.passenger_id
                )
            )
            neha_connection = result.scalar_one_or_none()
            
            if neha_connection:
                time_diff = neha_connection.departure_time - demo_flight.departure_time
                hours_diff = time_diff.total_seconds() / 3600
                print(f"[OK] Neha has connecting flight departing {hours_diff:.1f} hours after AA-100 (target: ~14 hours)")
            else:
                print("[FAIL] Neha missing connecting flight")
        else:
            print("[FAIL] Neha missing booking on AA-100")
    else:
        print("[FAIL] Neha not found")


async def seed_data():
    """Main seed function orchestrating all seeding operations."""
    print("Starting comprehensive database seeding...")
    
    async with AsyncSessionLocal() as session:
        # Clear existing data
        await clear_existing_data(session)
        
        # Seed users
        await seed_users(session)
        
        # Seed flights and get demo flight info
        flight_info = await seed_flights(session)
        
        # Seed demo passengers with specific scenarios
        demo_info = await seed_demo_passengers(
            session, 
            flight_info["demo_flight_id"], 
            flight_info["demo_flight_departure"]
        )
        
        # Seed remaining passengers
        passenger_info = await seed_remaining_passengers(session, [])
        
        # Seed bookings
        demo_booking_ids = [
            demo_info["rahul_booking_id"],
            demo_info["priya_booking_id"], 
            demo_info["amit_booking_id"],
            demo_info["neha_booking_id"]
        ]
        await seed_bookings(
            session, 
            passenger_info["all_passenger_ids"],
            [],
            demo_booking_ids
        )
        
        # Seed connecting flights
        await seed_connecting_flights(
            session,
            passenger_info["all_passenger_ids"],
            demo_booking_ids
        )
        
        # Seed alternative flights
        await seed_alternative_flights(session, flight_info["demo_flight_id"])
        
        # Commit all changes
        await session.commit()
        
        # Verify counts
        await verify_counts(session)
        
        # Verify demo scenarios
        await verify_demo_scenarios(session)
    
    print("\n[SUCCESS] Comprehensive database seeding completed successfully!")


if __name__ == "__main__":
    asyncio.run(seed_data())