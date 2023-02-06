CREATE INDEX processing_events_for_archivation_idx
ON processing.events(updated ASC)
WHERE is_archivable;
