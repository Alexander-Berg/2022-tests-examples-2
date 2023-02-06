CREATE PROCEDURE bte.create_events_vshards_partitions(
    num_vshards INT,
    range_from TIMESTAMPTZ,
    range_to TIMESTAMPTZ,
    partition_postfix TEXT
) AS $$
DECLARE
    vshard_id INT;
    vshard_name TEXT;
BEGIN
    FOR vshard_id IN 0..num_vshards - 1 LOOP
        vshard_name := 'bte.events_' || vshard_id;
        PERFORM bte.create_events_vshard_partition(
            vshard_name, range_from, range_to, partition_postfix
        );
    END LOOP;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE PROCEDURE bte.insert_event(
    event_ref TEXT,
    created TIMESTAMPTZ,
    event_at TIMESTAMPTZ,
    driver_id TEXT,
    amount INTERVAL,
    payload JSONB
) AS $$
BEGIN
    WITH _ as (
        INSERT INTO bte.payloads (created, aggregation_key, payload)
            VALUES (created, md5(cast(payload as TEXT)), payload)
            ON CONFLICT DO NOTHING
    )
    INSERT INTO bte.events (event_ref, created, event_at, driver_id, amount, aggregation_key)
    VALUES (
               event_ref,
               created,
               event_at,
               driver_id,
               amount,
               md5(cast(payload as TEXT))
           );
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE PROCEDURE bte.insert_consumer_offset(
    vshard_id INTEGER,
    last_created TIMESTAMPTZ
) AS $$
BEGIN
    INSERT INTO bte.consumer_offsets (vshard_id, last_created)
    VALUES (vshard_id, last_created);
END;
$$ LANGUAGE plpgsql;
