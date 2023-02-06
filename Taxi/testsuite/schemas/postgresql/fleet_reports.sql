CREATE SCHEMA fleet_reports_storage;

CREATE TABLE fleet_reports_storage.operations
(
	id TEXT NOT NULL PRIMARY KEY,
	park_id TEXT NOT NULL,
	client_type TEXT NOT NULL,
	client_id TEXT NOT NULL,
	name TEXT NOT NULL,
	status TEXT NOT NULL,
	locale TEXT,
	created_at TIMESTAMPTZ NOT NULL,
	updated_at TIMESTAMPTZ NOT NULL,
	file_name TEXT,
	deleted_at TIMESTAMPTZ,
	uploaded_at TIMESTAMPTZ
);

CREATE TABLE fleet_reports_storage.distlock
(
    key             TEXT PRIMARY KEY,
    owner           TEXT,
    expiration_time TIMESTAMPTZ
);

CREATE INDEX operations_park_id ON fleet_reports_storage.operations (park_id);
CREATE INDEX operations_client ON fleet_reports_storage.operations (client_id, client_type);
CREATE INDEX operations_name ON fleet_reports_storage.operations (name);
