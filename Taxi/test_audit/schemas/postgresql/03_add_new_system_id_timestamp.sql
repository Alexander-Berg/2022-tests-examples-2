create index audit_events_logs_system_id_timestamp
    on audit_events.logs (system_id, timestamp);
