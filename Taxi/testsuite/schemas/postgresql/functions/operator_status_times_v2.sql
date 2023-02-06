-- function to make unified operator status from operator_status and operator_talking_status tables
CREATE FUNCTION callcenter_stats.operator_status_times_v2(
    queues_filter VARCHAR[], -- or NULL
    past_limit TIMESTAMPTZ,
    from_limit TIMESTAMPTZ,
    to_limit TIMESTAMPTZ
)
    RETURNS TABLE(
                     agent_id        VARCHAR,
                     connected_time  INTERVAL,
                     paused_time     INTERVAL
                 ) AS $$
BEGIN
    RETURN QUERY
        -- Для каждого оператора считаем суммарное время в состояниях
        SELECT ut.agent_id,
               SUM(ut.connected_time) AS connected_time,
               SUM(ut.paused_time)    AS paused_time
        FROM (
                 (
                     -- Берем только те кусочки, которые заканчиваются в рассматриваемом диапазоне
                     -- и пересекатся по очередям.
                     -- Для каждого кусочка времени в зависимости от состояния prev_status
                     -- раскладываем время на два поля: connected_time или paused_time,
                     -- а также учитываем то, что наш кусочек может пересекать левую границу диапазона (from).
                     SELECT op_h.agent_id,
                            CASE
                                WHEN op_h.prev_status = 'connected'
                                    THEN op_h.created_at - GREATEST(op_h.prev_created_at, from_limit)
                                ELSE interval '0'
                                END AS connected_time,
                            CASE
                                WHEN op_h.prev_status = 'paused'
                                    THEN op_h.created_at - GREATEST(op_h.prev_created_at, from_limit)
                                ELSE interval '0'
                                END AS paused_time
                     FROM callcenter_stats.operator_history as op_h
                     WHERE from_limit < created_at AND created_at < to_limit
                       AND (queues_filter IS NULL OR (prev_queues <> ARRAY[]::VARCHAR[] AND prev_queues && queues_filter::VARCHAR[]))
                 )
                 UNION
                 (
                     -- Добавляем учет последнего состояния оператора,
                     -- которое будет пересекать правую границу диапазона (to),
                     -- т.е. считаем время от начала состояния (created_at) до правой границы диапазона (to),
                     -- но не забываем учесть случай когда последнее состояние было до рассматриваемого диапазона
                     SELECT t1.agent_id,
                            CASE
                                WHEN t1.status = 'connected'
                                    THEN to_limit - GREATEST(t1.created_at, from_limit)
                                ELSE interval '0'
                                END AS connected_time,
                            CASE
                                WHEN t1.status = 'paused'
                                    THEN to_limit - GREATEST(t1.created_at, from_limit)
                                ELSE interval '0'
                                END AS paused_time
                     FROM callcenter_stats.operator_history as t1
                     WHERE (t1.agent_id, t1.created_at) IN (
                         -- Находим последние состояния для каждого оператора
                         SELECT t2.agent_id, MAX(t2.created_at) AS created_at
                         FROM callcenter_stats.operator_history as t2
                         WHERE past_limit < t2.created_at AND t2.created_at < to_limit
                         GROUP BY t2.agent_id
                     )
                     AND (queues_filter IS NULL OR (t1.queues <> ARRAY []::VARCHAR[] AND t1.queues && queues_filter::VARCHAR[]))
                 )
             ) as ut -- union table
        GROUP BY ut.agent_id;
END
$$ LANGUAGE plpgsql;
