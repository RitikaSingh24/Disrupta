"""
Quick verification using direct connection to check if data was seeded.
"""

import asyncio
import asyncpg
from app.core.config import settings


async def quick_verify():
    """Quick verification using direct asyncpg connection."""
    print("Quick verification of seeded data...")
    
    # Parse DATABASE_URL to get connection parameters
    db_url = settings.DATABASE_URL
    # Extract connection info from postgresql+asyncpg://user:pass@host:port/db
    db_url = db_url.replace("postgresql+asyncpg://", "")
    
    # Parse connection string
    # Format: user:pass@host:port/db
    creds_part, rest = db_url.split("@")
    username, password = creds_part.split(":")
    # URL decode the password (handle %40 for @ character)
    from urllib.parse import unquote
    password = unquote(password)
    host_port, database = rest.split("/")
    host, port = host_port.split(":")
    
    try:
        conn = await asyncpg.connect(
            user=username,
            password=password,
            host=host,
            port=int(port),
            database=database,
            statement_cache_size=0  # Required for pgBouncer
        )
        
        # Check counts
        tables = [
            ("users", 3, "Users"),
            ("flights", 10, "Flights"),
            ("passengers", 100, "Passengers"),
            ("bookings", 150, "Bookings"),
            ("connecting_flights", 100, "Connecting Flights"),
            ("alternative_flights", 30, "Alternative Flights"),
        ]
        
        all_correct = True
        for table, expected, name in tables:
            count = await conn.fetchval(f"SELECT COUNT(*) FROM {table}")
            status = "[OK]" if count == expected else "[FAIL]"
            print(f"{status} {name}: {count} (expected {expected})")
            if count != expected:
                all_correct = False
        
        # Check demo flight
        demo_flight = await conn.fetchrow("SELECT flight_number, status FROM flights WHERE flight_number = 'AA-100'")
        if demo_flight:
            print(f"[OK] Demo flight AA-100 found (status: {demo_flight['status']})")
        else:
            print("[FAIL] Demo flight AA-100 not found")
            all_correct = False
        
        # Check demo passengers
        demo_passengers = ["Rahul Sharma", "Priya", "Amit", "Neha"]
        for passenger_name in demo_passengers:
            passenger = await conn.fetchrow(f"SELECT name FROM passengers WHERE name = '{passenger_name}'")
            if passenger:
                print(f"[OK] {passenger_name} found")
            else:
                print(f"[FAIL] {passenger_name} not found")
                all_correct = False
        
        # Check demo users
        demo_emails = ["admin@airline.com", "agent@airline.com", "supervisor@airline.com"]
        for email in demo_emails:
            user = await conn.fetchrow(f"SELECT email, role FROM users WHERE email = '{email}'")
            if user:
                print(f"[OK] {email} found (role: {user['role']})")
            else:
                print(f"[FAIL] {email} not found")
                all_correct = False
        
        if all_correct:
            print("\n[SUCCESS] All verifications passed!")
        else:
            print("\n[WARNING] Some verifications failed.")
        
        await conn.close()
    
    except Exception as e:
        print(f"Error during verification: {e}")


if __name__ == "__main__":
    asyncio.run(quick_verify())