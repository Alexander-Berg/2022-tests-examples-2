ALTER TABLE processing.events
  ADD COLUMN is_malformed BOOLEAN NOT NULL DEFAULT FALSE;

CREATE FUNCTION processing.discard_events_v1(
    IN item_locator processing.item_locator_v1)
RETURNS VOID AS $$
BEGIN
    UPDATE processing.events
      SET is_archivable = TRUE,
          is_malformed = TRUE,
          updated = NOW()
     WHERE scope = item_locator.scope
       AND queue = item_locator.queue
       AND item_id = item_locator.item_id;
END;
$$ LANGUAGE plpgsql;
