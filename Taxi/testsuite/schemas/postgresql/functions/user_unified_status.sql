-- function to make unified user status from user_status, user_queues and operator_talking_status tables
-- also it uses tel_state to o deal with substatus
CREATE FUNCTION callcenter_stats.user_unified_status(
    now TIMESTAMPTZ,
    queue_delimiter VARCHAR
)
    RETURNS TABLE(
                     sip_username            VARCHAR,
                     metaqueue               VARCHAR,
                     subcluster              VARCHAR,
                     status                  VARCHAR,
                     substatus               VARCHAR,
                     delimiter               VARCHAR
                 ) AS $$
BEGIN
    RETURN QUERY
        -- determine user status and substatus regardless of queue
        WITH uus AS (
            SELECT
                us.sip_username,
                -- status: connected/paused (disconnected is filtered out)
                us.status,
                -- substatus: talking/postcall/waiting for 'connected', pause type for 'paused'
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
                    END as substatus,
                -- connected metaqueues
                CASE WHEN uq.metaqueues IS NULL THEN ARRAY[]::VARCHAR[] ELSE uq.metaqueues END as connected_metaqueues,  -- change LEFT JOIN's NULL to {}
                uts.subcluster as subcluster,
                -- talking queue
                ots.queue as talking_queue
            FROM callcenter_stats.user_status as us
                     LEFT JOIN callcenter_stats.operator_talking_status as ots
                               ON us.sip_username = ots.agent_id
                             LEFT JOIN callcenter_stats.user_queues as uq
                                       ON us.sip_username = uq.sip_username
                                     LEFT JOIN callcenter_stats.tel_state as uts
                                               ON us.sip_username = uts.sip_username
            WHERE us.status != 'disconnected'
        )
             -- determine operator status and substatus in context of a queue
        SELECT
            uus_unnested.sip_username,
            uus_unnested.connected_metaqueue as metaqueue,
            uus_unnested.subcluster as subcluster,
            uus_unnested.status,
            CASE
                -- connected and talking or postcall processing on the different queue -> busy
                WHEN uus_unnested.status = 'connected'
                    AND uus_unnested.substatus = ANY('{talking, postcall}')
                    AND uus_unnested.subcluster IS NOT NULL
                    AND  uus_unnested.connected_metaqueue || queue_delimiter || uus_unnested.subcluster != uus_unnested.talking_queue
                    THEN 'busy'
                ELSE uus_unnested.substatus
                END as substatus,
            queue_delimiter
        FROM (
                 -- unnest queues
                 SELECT
                     uus.sip_username,
                     uus.status,
                     uus.substatus,
                     unnest(uus.connected_metaqueues) as connected_metaqueue,
                     uus.subcluster,
                     uus.talking_queue
                 FROM uus
             ) AS uus_unnested;

END
$$ LANGUAGE plpgsql;
