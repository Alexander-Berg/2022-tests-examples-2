SELECT
       E.*,
       F.message as fail_message,
       F.occurred_at as fail_occurred_at
FROM hiring_sf_events.events_queue E
         LEFT JOIN hiring_sf_events.failures F on F.id = E.id;
