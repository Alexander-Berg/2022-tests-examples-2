-- function to make operator substatus from operator_status and operator_talking_status tables
CREATE FUNCTION callcenter_stats.operator_substatus(
    now TIMESTAMPTZ,
    show_disconnected BOOLEAN,
    disconnected_time_depth TIMESTAMPTZ
)
    RETURNS TABLE(
                     agent_id                VARCHAR,
                     substatus               VARCHAR,
                     substatus_updated_at    TIMESTAMPTZ,
                     current_queue           VARCHAR
                 ) AS $$
BEGIN
    RETURN QUERY
        -- determine operator status and substatus regardless of queue
        SELECT
            os.agent_id,
            -- substatus: talking/postcall/waiting for 'connected', pause type for 'paused', disconnect reason for 'disconnected'
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
                END AS substatus,
            CASE
                WHEN os.status = 'connected' AND (ots.is_talking = false AND now < ots.postcall_until OR os.sub_status = 'postcall')
                    THEN GREATEST(os.sub_status_updated_at, ots.updated_at)
                WHEN os.status = 'connected' AND ots.is_talking = true
                    THEN ots.updated_at
                WHEN os.status = 'connected'
                    THEN GREATEST(os.sub_status_updated_at, ots.updated_at, ots.postcall_until)
                ELSE os.sub_status_updated_at
                END AS substatus_updated_at,
            -- talking/postcall queue
            CASE
                -- connected and have postcall_until from timer or ui status -> queue
                WHEN os.status = 'connected' AND (ots.is_talking = false AND now < ots.postcall_until OR os.sub_status = 'postcall')
                    THEN ots.queue
                -- connected and talking -> queue
                WHEN os.status = 'connected' AND ots.is_talking = true
                    THEN ots.queue
                -- for all other statuses -> NULL
                END AS current_queue

        FROM callcenter_stats.operator_status AS os
                 LEFT JOIN callcenter_stats.operator_talking_status AS ots
                           ON os.agent_id = ots.agent_id
        -- get connected and paused
        WHERE os.status != 'disconnected'
           -- and recent disconnected
           OR (show_disconnected AND (disconnected_time_depth IS NULL OR disconnected_time_depth <= os.status_updated_at));

END
$$ LANGUAGE plpgsql;
