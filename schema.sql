-- ============================================================
-- IROP Passenger Rebooking Copilot
-- Authoritative PostgreSQL Schema
-- Version: 1.0  |  September 2026
-- ============================================================
-- Run this file once against Supabase (or any PostgreSQL 14+)
-- via the SQL editor or psql before starting any backend phase.
-- ============================================================

-- ============================================================
-- ENUMS
-- ============================================================
CREATE TYPE flight_status AS ENUM ('SCHEDULED', 'DELAYED', 'CANCELLED', 'DEPARTED');
CREATE TYPE booking_status AS ENUM ('CONFIRMED', 'REBOOKED', 'CANCELLED');
CREATE TYPE priority_level AS ENUM ('HIGH', 'MEDIUM', 'NORMAL', 'REVIEW_REQUIRED');
CREATE TYPE recommendation_status AS ENUM ('PENDING', 'APPROVED', 'EDITED', 'REJECTED', 'ESCALATED');
CREATE TYPE notification_status AS ENUM ('DRAFT', 'PENDING_REVIEW', 'APPROVED', 'SENT', 'FAILED');
CREATE TYPE user_role AS ENUM ('ADMIN', 'OPERATIONS_AGENT', 'SUPERVISOR');

-- ============================================================
-- USERS (employees)
-- ============================================================
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(120) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role user_role NOT NULL DEFAULT 'OPERATIONS_AGENT',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================================================
-- FLIGHTS
-- ============================================================
CREATE TABLE flights (
    flight_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    flight_number VARCHAR(20) NOT NULL,
    airline VARCHAR(80) NOT NULL,
    origin VARCHAR(80) NOT NULL,
    destination VARCHAR(80) NOT NULL,
    departure_time TIMESTAMPTZ NOT NULL,
    arrival_time TIMESTAMPTZ NOT NULL,
    status flight_status NOT NULL DEFAULT 'SCHEDULED',
    cancellation_reason VARCHAR(255),
    total_seats INTEGER NOT NULL DEFAULT 150,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_flights_status ON flights(status);
CREATE INDEX idx_flights_route ON flights(origin, destination);

-- ============================================================
-- PASSENGERS
-- ============================================================
CREATE TABLE passengers (
    passenger_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(120) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(30),
    preferred_language VARCHAR(40) NOT NULL DEFAULT 'English',
    special_requirement TEXT,
    requirement_type VARCHAR(60),
    requirement_declared_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================================================
-- BOOKINGS (passenger <-> flight)
-- ============================================================
CREATE TABLE bookings (
    booking_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    passenger_id UUID NOT NULL REFERENCES passengers(passenger_id) ON DELETE CASCADE,
    flight_id UUID NOT NULL REFERENCES flights(flight_id) ON DELETE CASCADE,
    seat_number VARCHAR(10),
    booking_class VARCHAR(20) NOT NULL DEFAULT 'Economy',
    booking_status booking_status NOT NULL DEFAULT 'CONFIRMED',
    rebooked_flight_id UUID REFERENCES flights(flight_id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_bookings_flight ON bookings(flight_id);
CREATE INDEX idx_bookings_passenger ON bookings(passenger_id);

-- ============================================================
-- CONNECTING FLIGHTS (declared by/for a passenger)
-- ============================================================
CREATE TABLE connecting_flights (
    connection_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    passenger_id UUID NOT NULL REFERENCES passengers(passenger_id) ON DELETE CASCADE,
    booking_id UUID REFERENCES bookings(booking_id) ON DELETE CASCADE,
    flight_number VARCHAR(20) NOT NULL,
    departure_time TIMESTAMPTZ NOT NULL,
    destination VARCHAR(80) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_connections_passenger ON connecting_flights(passenger_id);

-- ============================================================
-- ALTERNATIVE FLIGHTS (candidate flights for rebooking)
-- ============================================================
CREATE TABLE alternative_flights (
    alternative_flight_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    flight_number VARCHAR(20) NOT NULL,
    origin VARCHAR(80) NOT NULL,
    destination VARCHAR(80) NOT NULL,
    departure_time TIMESTAMPTZ NOT NULL,
    arrival_time TIMESTAMPTZ NOT NULL,
    available_seats INTEGER NOT NULL DEFAULT 0,
    linked_original_flight_id UUID REFERENCES flights(flight_id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_alt_flights_route ON alternative_flights(origin, destination);

-- ============================================================
-- REBOOKING RECOMMENDATIONS
-- ============================================================
CREATE TABLE rebooking_recommendations (
    recommendation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    passenger_id UUID NOT NULL REFERENCES passengers(passenger_id) ON DELETE CASCADE,
    booking_id UUID NOT NULL REFERENCES bookings(booking_id) ON DELETE CASCADE,
    original_flight_id UUID NOT NULL REFERENCES flights(flight_id),
    recommended_flight_id UUID REFERENCES alternative_flights(alternative_flight_id),
    priority priority_level NOT NULL,
    reason TEXT NOT NULL,
    status recommendation_status NOT NULL DEFAULT 'PENDING',
    reviewed_by_user_id UUID REFERENCES users(user_id),
    reviewed_at TIMESTAMPTZ,
    version INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_recs_passenger ON rebooking_recommendations(passenger_id);
CREATE INDEX idx_recs_status ON rebooking_recommendations(status);

-- ============================================================
-- NOTIFICATIONS
-- ============================================================
CREATE TABLE notifications (
    notification_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    passenger_id UUID NOT NULL REFERENCES passengers(passenger_id) ON DELETE CASCADE,
    recommendation_id UUID REFERENCES rebooking_recommendations(recommendation_id),
    language VARCHAR(40) NOT NULL DEFAULT 'English',
    message TEXT NOT NULL,
    status notification_status NOT NULL DEFAULT 'DRAFT',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    sent_at TIMESTAMPTZ
);

CREATE INDEX idx_notifications_passenger ON notifications(passenger_id);

-- ============================================================
-- PASSENGER PORTAL ACCESS TOKENS (secure link, no login needed)
-- ============================================================
CREATE TABLE passenger_access_tokens (
    token VARCHAR(64) PRIMARY KEY,
    passenger_id UUID NOT NULL REFERENCES passengers(passenger_id) ON DELETE CASCADE,
    flight_id UUID NOT NULL REFERENCES flights(flight_id),
    expires_at TIMESTAMPTZ NOT NULL,
    used BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
