CREATE SCHEMA scooter_accumulator;

CREATE TABLE scooter_accumulator.cabinets (
    cabinet_id TEXT NOT NULL PRIMARY KEY,
    depot_id TEXT NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE scooter_accumulator.bookings (
    booking_id TEXT NOT NULL PRIMARY KEY,
    contractor_id TEXT,
    cabinet_id TEXT NOT NULL REFERENCES scooter_accumulator.cabinets (cabinet_id),
    cells_count INTEGER NOT NULL CONSTRAINT booked_cells_count_check CHECK(cells_count > 0),
    cell_id TEXT NOT NULL,
    accumulator_id TEXT,
    booking_status TEXT NOT NULL DEFAULT 'CREATED',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS bookings_updated_at_idx ON scooter_accumulator.bookings (updated_at);
