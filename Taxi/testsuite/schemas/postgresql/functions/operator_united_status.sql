-- function to make unified operator status from operator_status and operator_talking_status tables
CREATE FUNCTION callcenter_stats.operator_united_status(
    now TIMESTAMPTZ
)
    RETURNS TABLE(
                     agent_id                VARCHAR,
                     queue                   VARCHAR,
                     status                  VARCHAR,
                     substatus               VARCHAR
                 ) AS $$
BEGIN
    RETURN QUERY
        -- determine operator status and substatus regardless of queue
        WITH ous AS (
            SELECT
                os.agent_id,
                -- status: connected/paused (disconnected is filtered out)
                os.status,
                -- substatus: talking/postcall/waiting for 'connected', pause type for 'paused'
                CASE
                    -- connected and have postcall_until from timer or ui status ->postcall
                    WHEN os.status = 'connected' AND (ots.is_talking = false AND now < ots.postcall_until OR os.sub_status = 'postcall')
                        THEN 'postcall'
                    -- connected and talking -> talking
                    WHEN os.status = 'connected' AND ots.is_talking = true
                        THEN 'talking'
                    -- just connected -> waiting
                    WHEN os.status = 'connected'
                        THEN 'waiting'
                    -- for all other statuses -> see sub_status
                    ELSE os.sub_status
                    END as substatus,
                -- connected queues
                os.queues as connected_queues,
                -- talking queue
                ots.queue as talking_queue

            FROM callcenter_stats.operator_status as os
                     LEFT JOIN callcenter_stats.operator_talking_status as ots
                               ON os.agent_id = ots.agent_id
            WHERE os.status != 'disconnected'
        )
             -- determine operator status and substatus in context of a queue
        SELECT
            ous_unnested.agent_id,
            ous_unnested.connected_queue as queue,
            ous_unnested.status,
            CASE
                -- connected and talking or postcall processing on the different queue -> busy
                WHEN ous_unnested.status = 'connected'
                    AND ous_unnested.substatus = ANY('{talking, postcall}')
                    AND ous_unnested.talking_queue != ous_unnested.connected_queue
                    THEN 'busy'
                ELSE ous_unnested.substatus
                END as substatus
        FROM (
                 -- unnest queues
                 SELECT
                     ous.agent_id,
                     ous.status,
                     ous.substatus,
                     unnest(ous.connected_queues) as connected_queue,
                     ous.talking_queue
                 FROM ous
             ) AS ous_unnested;

END
$$ LANGUAGE plpgsql;
