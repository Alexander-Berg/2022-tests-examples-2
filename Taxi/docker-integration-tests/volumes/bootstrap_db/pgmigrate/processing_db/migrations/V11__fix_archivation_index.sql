DROP INDEX IF EXISTS processing.processing_events_for_archivation_idx;
CREATE INDEX processing_events_for_archivation_idx ON processing.events(updated, is_archivable);
