-- function to make user substatus from user_status, user_queues and operator_talking_status tables
-- also it uses tel_state table to deal with subcluster
CREATE FUNCTION callcenter_stats.user_substatus(
    now TIMESTAMPTZ,
    show_disconnected BOOLEAN,
    disconnected_time_depth TIMESTAMPTZ
)
    RETURNS TABLE(
                     sip_username            VARCHAR,
                     substatus               VARCHAR,
                     substatus_updated_at    TIMESTAMPTZ,
                     current_queue           VARCHAR
                 ) AS $$
BEGIN
    RETURN QUERY
        -- determine user status and substatus regardless of queue
        SELECT
            us.sip_username,
            -- substatus: talking/postcall/waiting for 'connected', pause type for 'paused', disconnect reason for 'disconnected'
            CASE
                -- connected and have postcall_until from timer or ui status -> postcall
                WHEN us.status = 'connected' AND (
                            (ots.is_talking IS NOT NULL AND ots.postcall_until IS NOT NULL AND ots.is_talking = false AND now < ots.postcall_until) OR -- check NULLS cause LEFT JOIN
                            us.sub_status = 'postcall'
                            )
                    THEN 'postcall'
                -- connected and talking -> talking
                WHEN us.status = 'connected' AND ots.is_talking IS NOT NULL AND ots.is_talking = true -- check NULLS cause LEFT JOIN
                    THEN 'talking'
                -- just connected -> waiting
                WHEN us.status = 'connected'
                    THEN 'waiting'
                -- for all other statuses -> see sub_status
                ELSE us.sub_status
                END AS substatus,
            CASE
                WHEN us.status = 'connected' AND (
                            (ots.is_talking IS NOT NULL AND ots.postcall_until IS NOT NULL AND ots.is_talking = false AND now < ots.postcall_until) OR
                            us.sub_status = 'postcall'
                            )
                    THEN GREATEST(us.sub_status_updated_at, ots.updated_at)
                WHEN us.status = 'connected' AND ots.is_talking IS NOT NULL AND ots.is_talking = true
                    THEN ots.updated_at
                WHEN us.status = 'connected'
                    THEN GREATEST(us.sub_status_updated_at, ots.updated_at, ots.postcall_until)
                ELSE us.sub_status_updated_at
                END AS substatus_updated_at,
            -- talking/postcall queue
            CASE
                -- connected and have postcall_until from timer or ui status -> queue
                WHEN us.status = 'connected' AND (
                            (ots.is_talking IS NOT NULL AND ots.postcall_until IS NOT NULL AND ots.is_talking = false AND now < ots.postcall_until) OR
                            us.sub_status = 'postcall'
                            )
                    THEN ots.queue
                -- connected and talking -> queue
                WHEN us.status = 'connected' AND ots.is_talking IS NOT NULL AND ots.is_talking = true
                    THEN ots.queue
                -- for all other statuses -> NULL
                END AS current_queue

        FROM callcenter_stats.user_status AS us
                 LEFT JOIN callcenter_stats.operator_talking_status AS ots
                           ON us.sip_username = ots.agent_id
        -- get connected and paused
        WHERE us.status != 'disconnected'
           -- and recent disconnected
           OR (show_disconnected AND (disconnected_time_depth IS NULL OR disconnected_time_depth <= us.status_updated_at));

END
$$ LANGUAGE plpgsql;
