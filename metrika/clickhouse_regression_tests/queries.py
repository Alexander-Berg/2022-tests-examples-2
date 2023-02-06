class Query:
    def __init__(self, ticket, query, query_params={}, success=True, expected=None):
        self.ticket = ticket
        self.query = query
        self.query_params = query_params
        self.success = success
        self.expected = expected


QUERIES = [
    Query(
        'CLICKHOUSE-4993',
        'SELECT 42 AS result',
        {'profile': 'default'},
    ),

    Query(
        'CLICKHOUSE-4994',
        """\
        SELECT toDate(x) AS result
        FROM
        (
            SELECT NULL AS x
            UNION ALL
            SELECT '2020-01-01'
        )
        ORDER BY result
        """,
        expected=[{'result': '2020-01-01'}, {'result': None}]
    ),

    Query(
        'CLICKHOUSE-4817',
        """\
        SELECT 0
        FROM default.hits_layer AS `default.hits_layer`
        PREWHERE WatchID IN
        (
            SELECT 0
            FROM default.visits_layer AS `default.visits_layer`
            WHERE StartDate = toDate('2000-01-01')
        )
        WHERE EventDate = toDate('2000-01-01');
        """,
    ),

    Query(
        'CLICKHOUSE-4871',
        """\
        SELECT
            (
                SELECT 1
            ) AS all_clicks
        FROM visits_all
        WHERE StartDate = '2020-04-23'
        """,
    ),

    Query(
        'CLICKHOUSE-4880',
        """\
        SELECT *
        FROM system.query_log
        WHERE (query LIKE '%miptgirl.pub_hits%') AND (event_date = today()) AND (event_time >= '2020-05-26 18:00:00') AND (query NOT LIKE '%system.query_log%')
        ORDER BY event_time ASC
        """,
    ),

    Query(
        'MOBMET-12799',
        """\
        SELECT DeviceIDHash
        FROM mobile.total_push_token_events_all
        GROUP BY
            DeviceIDHash,
            PushTokenType
        HAVING notEmpty(argMax(EventValue, Version)) AND (argMax(EventType, (Version, EventType = 0)) != 0)
        """,
    ),

    Query(
        'CLICKHOUSE-4959',
        """\
        SELECT 1
        FROM default.visits_all AS `default.visits_all`
        WHERE (StartDate = toDate('2015-09-01')) AND length(`PublisherEvents.Chars`) > 0
        """,
    ),

    Query(
        'CLICKHOUSE-5055',
        """\
        SELECT toUInt32(1 / 0)
        """,
        success=False,
        expected='Unexpected inf or nan to integer conversion'
    ),

    Query(
        'CLICKHOUSE-5120',
        """\
        SELECT 'x'
        FROM numbers(2)
        GROUP BY number
        WITH TOTALS
        HAVING count(number)>0
        """
    ),

    Query(
        'https://github.com/ClickHouse/ClickHouse/issues/31687',
        """\
        explain syntax select if((select hasColumnInTable('system', 'tables', 'x')), x, 1) from system.tables;
        """
    ),
]
