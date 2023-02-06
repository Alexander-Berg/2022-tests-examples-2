DROP TRIGGER update_archivable_after_handling ON processing.events;

DROP FUNCTION processing.update_is_archivable();

CREATE FUNCTION processing.mark_handled(
  IN item_locator processing.item_locator_v1,
  IN event_ids TEXT[])
RETURNS VOID AS $$
BEGIN
  UPDATE processing.events SET need_handle = FALSE, updated = NOW()
  WHERE scope = item_locator.scope
    AND queue = item_locator.queue
    AND item_id = item_locator.item_id
    AND event_id IN (SELECT(UNNEST(event_ids)));

  IF processing.is_can_be_archived(item_locator.scope,
                                   item_locator.queue,
                                   item_locator.item_id)
  THEN
    UPDATE processing.events
    SET is_archivable = TRUE
    WHERE scope = item_locator.scope
      AND queue = item_locator.queue
      AND item_id = item_locator.item_id;
  END IF;
END;
$$ LANGUAGE plpgsql;
