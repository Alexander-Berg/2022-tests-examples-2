-- function to return operator status time intervals (when he was connected, paused or talking)
-- from operator_status and operator_talking_status tables

-- It is copy of operator_status_times_v2 but w/o group by agent_id, and with METAqueues filter instead of queues filter
CREATE FUNCTION callcenter_stats.operator_status_intervals(
    metaqueues_patterns VARCHAR[], -- or NULL
    past_limit TIMESTAMPTZ,
    from_limit TIMESTAMPTZ,
    to_limit TIMESTAMPTZ
)
    RETURNS TABLE(
                     agent_id        VARCHAR,
                     connected_time  INTERVAL,
                     paused_time     INTERVAL,
                     queues          VARCHAR[]
                 ) AS $$
BEGIN
    RETURN QUERY
        -- Для каждого оператора считаем интервалы статусов
        SELECT ut.agent_id as agent_id,
               ut.connected_time as connected_time,
               ut.paused_time as paused_time,
               ut.op_queues as queues
        FROM (
                 (
                     -- Берем только те кусочки, которые заканчиваются в рассматриваемом диапазоне
                     -- и пересекатся по очередям.
                     -- Для каждого кусочка времени в зависимости от состояния prev_status
                     -- раскладываем время на два поля: connected_time или paused_time,
                     -- а также учитываем то, что наш кусочек может пересекать левую границу диапазона (from).
                     SELECT op_h.agent_id as agent_id,
                            CASE
                                WHEN op_h.prev_status = 'connected'
                                    THEN op_h.created_at - GREATEST(op_h.prev_created_at, from_limit)
                                ELSE interval '0'
                                END AS connected_time,
                            CASE
                                WHEN op_h.prev_status = 'paused'
                                    THEN op_h.created_at - GREATEST(op_h.prev_created_at, from_limit)
                                ELSE interval '0'
                                END AS paused_time,
                            prev_queues as op_queues
                     FROM callcenter_stats.operator_history as op_h
                     WHERE from_limit < created_at AND created_at < to_limit
                       AND (
                            metaqueues_patterns IS NULL OR (
                                prev_queues != ARRAY[]::VARCHAR[] AND
                                (
                                     SELECT count(queue)
                                     FROM UNNEST(prev_queues) AS queue
                                     WHERE queue LIKE ANY(metaqueues_patterns)
                                ) > 0
                            )
                       )
                 )
                 UNION
                 (
                     -- Добавляем учет последнего состояния оператора,
                     -- которое будет пересекать правую границу диапазона (to),
                     -- т.е. считаем время от начала состояния (created_at) до правой границы диапазона (to),
                     -- но не забываем учесть случай когда последнее состояние было до рассматриваемого диапазона
                     SELECT t1.agent_id as agent_id,
                            CASE
                                WHEN t1.status = 'connected'
                                    THEN to_limit - GREATEST(t1.created_at, from_limit)
                                ELSE interval '0'
                                END AS connected_time,
                            CASE
                                WHEN t1.status = 'paused'
                                    THEN to_limit - GREATEST(t1.created_at, from_limit)
                                ELSE interval '0'
                                END AS paused_time,
                            t1.queues as op_queues
                     FROM callcenter_stats.operator_history as t1
                     WHERE (t1.agent_id, t1.created_at) IN (
                         -- Находим последние состояния для каждого оператора
                         SELECT t2.agent_id, MAX(t2.created_at) AS created_at
                         FROM callcenter_stats.operator_history as t2
                         WHERE past_limit < t2.created_at AND t2.created_at < to_limit
                         GROUP BY t2.agent_id
                     )
                     AND (
                        metaqueues_patterns IS NULL OR
                            (
                                t1.queues != ARRAY []::VARCHAR[] AND
                                (
                                     SELECT count(queue)
                                     FROM UNNEST(t1.queues) AS queue
                                     WHERE queue LIKE ANY(metaqueues_patterns)
                                ) > 0
                            )
                        )
                 )
             ) as ut; -- union table
END
$$ LANGUAGE plpgsql;
