\set role testsuite
\ir ../../../postgresql/driver_event_detector/migrations/V1__initial.sql
\ir ../../../postgresql/driver_event_detector/migrations/V2__tokens_and_limits.sql
\ir ../../../postgresql/driver_event_detector/migrations/V3__add_last_seen.sql
\ir ../../../postgresql/driver_event_detector/migrations/V4__add_udid_to_matched_drivers.sql
\ir ../../../postgresql/driver_event_detector/migrations/V5__add_dbid_uuids_to_matched_drivers.sql
\ir ../../../postgresql/driver_event_detector/migrations/V6__add_distlock.sql
