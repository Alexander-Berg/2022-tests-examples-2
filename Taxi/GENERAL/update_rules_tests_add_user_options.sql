UPDATE price_modifications.tests SET
    trip_details=jsonb_set(trip_details::jsonb, '{user_options}', '{}', true)
WHERE
    trip_details -> 'user_options' IS NULL;
