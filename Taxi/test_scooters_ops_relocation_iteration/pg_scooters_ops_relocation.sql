CREATE EXTENSION IF NOT EXISTS "postgis";

CREATE INDEX IF NOT EXISTS events_location_gist_idx_fixed
    ON scooters_ops_relocation.events USING gist (
      ST_MakePoint(location[0], location[1])
    );
