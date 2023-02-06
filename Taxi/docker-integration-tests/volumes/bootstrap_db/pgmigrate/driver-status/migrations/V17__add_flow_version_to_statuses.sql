ALTER TABLE ds.statuses
    ADD COLUMN flow_version ds.flow_version NOT NULL DEFAULT 'v0';
