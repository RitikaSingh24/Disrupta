"""
backend/app/seed/verify_data.py

Quick verification script to check if seed data was successfully inserted.
"""

import asyncio
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.user import User
from app.models.flight import Flight
from app.models.passenger import Passenger
from app.models.booking import Booking
from app.models.connecting_flight import ConnectingFlight
from app.models.alternative_flight import AlternativeFlight


async def verify_data():
    print("Verifying seed data...")
    
    async with AsyncSessionLocal() as session:
        # Check counts
        tables = [
            (User, 3, "Users"),
            (Flight, 10, "Flights"),
            (Passenger, 100, "Passengers"),
            (Booking, 150, "Bookings"),
            (ConnectingFlight, 100, "Connecting Flights"),
            (AlternativeFlight, 30, "Alternative Flights"),
        ]
        
        all_correct = True
        for model, expected, name in tables:
            result = await session.execute(select(model))
            count = len(result.fetchall())
            status = "[OK]" if count == expected else "[FAIL]"
            print(f"{status} {name}: {count} (expected {expected})")
            if count != expected:
                all_correct = False
        
        # Check demo passengers
        print("\nVerifying demo passengers...")
        
        # Get demo flight
        result = await session.execute(
            select(Flight).where(Flight.flight_number == "AA-100")
        )
        demo_flight = result.scalar_one_or_none()
        
        if demo_flight:
            print(f"[OK] Demo flight AA-100 found (status: {demo_flight.status})")
            
            # Check Rahul Sharma
            result = await session.execute(
                select(Passenger).where(Passenger.name == "Rahul Sharma")
            )
            rahul = result.scalar_one_or_none()
            
            if rahul:
                print(f"[OK] Rahul Sharma found")
                
                # Check Rahul's booking
                result = await session.execute(
                    select(Booking).where(
                        Booking.passenger_id == rahul.passenger_id,
                        Booking.flight_id == demo_flight.flight_id
                    )
                )
                rahul_booking = result.scalar_one_or_none()
                
                if rahul_booking:
                    print(f"[OK] Rahul has booking on AA-100")
                    
                    # Check connecting flight
                    result = await session.execute(
                        select(ConnectingFlight).where(
                            ConnectingFlight.passenger_id == rahul.passenger_id
                        )
                    )
                    rahul_connection = result.scalar_one_or_none()
                    
                    if rahul_connection:
                        time_diff = rahul_connection.departure_time - demo_flight.departure_time
                        hours_diff = time_diff.total_seconds() / 3600
                        print(f"[OK] Rahul has connecting flight departing {hours_diff:.1f} hours after AA-100")
                    else:
                        print("[FAIL] Rahul missing connecting flight")
                else:
                    print("[FAIL] Rahul missing booking on AA-100")
            else:
                print("[FAIL] Rahul Sharma not found")
            
            # Check Priya
            result = await session.execute(
                select(Passenger).where(Passenger.name == "Priya")
            )
            priya = result.scalar_one_or_none()
            
            if priya:
                print(f"[OK] Priya found (special_requirement: {priya.special_requirement})")
                
                result = await session.execute(
                    select(Booking).where(
                        Booking.passenger_id == priya.passenger_id,
                        Booking.flight_id == demo_flight.flight_id
                    )
                )
                priya_booking = result.scalar_one_or_none()
                
                if priya_booking:
                    print(f"[OK] Priya has booking on AA-100")
                    
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
            
            # Check Amit
            result = await session.execute(
                select(Passenger).where(Passenger.name == "Amit")
            )
            amit = result.scalar_one_or_none()
            
            if amit:
                print(f"[OK] Amit found (special_requirement: {amit.special_requirement})")
                
                result = await session.execute(
                    select(Booking).where(
                        Booking.passenger_id == amit.passenger_id,
                        Booking.flight_id == demo_flight.flight_id
                    )
                )
                amit_booking = result.scalar_one_or_none()
                
                if amit_booking:
                    print(f"[OK] Amit has booking on AA-100")
                    
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
            
            # Check Neha
            result = await session.execute(
                select(Passenger).where(Passenger.name == "Neha")
            )
            neha = result.scalar_one_or_none()
            
            if neha:
                print(f"[OK] Neha found")
                
                result = await session.execute(
                    select(Booking).where(
                        Booking.passenger_id == neha.passenger_id,
                        Booking.flight_id == demo_flight.flight_id
                    )
                )
                neha_booking = result.scalar_one_or_none()
                
                if neha_booking:
                    print(f"[OK] Neha has booking on AA-100")
                    
                    result = await session.execute(
                        select(ConnectingFlight).where(
                            ConnectingFlight.passenger_id == neha.passenger_id
                        )
                    )
                    neha_connection = result.scalar_one_or_none()
                    
                    if neha_connection:
                        time_diff = neha_connection.departure_time - demo_flight.departure_time
                        hours_diff = time_diff.total_seconds() / 3600
                        print(f"[OK] Neha has connecting flight departing {hours_diff:.1f} hours after AA-100")
                    else:
                        print("[FAIL] Neha missing connecting flight")
                else:
                    print("[FAIL] Neha missing booking on AA-100")
            else:
                print("[FAIL] Neha not found")
            
            # Check demo users
            print("\nVerifying demo users...")
            demo_emails = ["admin@airline.com", "agent@airline.com", "supervisor@airline.com"]
            for email in demo_emails:
                result = await session.execute(select(User).where(User.email == email))
                user = result.scalar_one_or_none()
                if user:
                    print(f"[OK] {email} found (role: {user.role})")
                else:
                    print(f"[FAIL] {email} not found")
        else:
            print("[FAIL] Demo flight AA-100 not found")
    
    print("\nVerification complete!")


if __name__ == "__main__":
    asyncio.run(verify_data())