import textwrap


_YT_PROXY = "hahn"
_REQUEST_DATA_LOGS_ROOT = "logs/bs-proto-extstat-log/"

_HIT_MODELS_EXT_TAG = "rsya_hit_models_heavy_01"


def _make_limits_str(limits):
    return ','.join('("{}", {})'.format(key, int(int(limit) * 1.05)) for key, limit in limits.iteritems())


def make_aggregation_query(work_prefix, user_subquery, logs_interval_type="1d", interval_size=21):
    """
    Query that prepares aggregated data from logs for following selections of ammo according to limits.
    """

    user_filtration = ""
    if user_subquery:
        user_filtration = textwrap.dedent(
            """
            DEFINE SUBQUERY $select_user_request_ids($begin, $end) AS
                {user_subquery}
            END DEFINE;

            $user_graph_ids = select * from $select_user_request_ids($begin, $end);

            $user_graph_ids_path = $work_prefix || "/user_graph_ids";
            INSERT INTO $user_graph_ids_path WITH TRUNCATE
            SELECT * FROM $user_graph_ids;

            $select_request_filtered =
            SELECT
                *
            FROM
                $select_request_filtered
            WHERE
                GraphID in $user_graph_ids;
        """
        ).format(
            user_subquery=user_subquery,
        )

    return textwrap.dedent(
        """
        USE {yt_proxy};
        PRAGMA yt.ExpirationInterval = "14d";

        $log_interval = "{logs_interval_type}";

        $work_prefix = "{work_prefix}";
        $request_data_logs_root = "{request_data_logs_root}" || $log_interval;

        -- Select raw logs for requested period
        $end_datetime = DateTime::StartOf(CurrentTzDatetime("Europe/Moscow"), if($log_interval == "1h", DateTime::IntervalFromMinutes(30), DateTime::IntervalFromDays(1)));
        $interval = if($log_interval == "1h", DateTime::IntervalFromHours({interval_size}), DateTime::IntervalFromDays({interval_size}));
        $begin_datetime = DateTime::MakeTzTimestamp($end_datetime) - $interval;

        $format = DateTime::Format("%Y-%m-%dT%H:%M:%S");
        $end = $format($end_datetime);
        $begin = $format($begin_datetime);

        $select_request_filtered = (
            SELECT * FROM RANGE($request_data_logs_root, $begin, $end)
            WHERE Tag = "{hit_models_tag}"
        );

        -- User filtration
        {user_filtration}

        -- Write to cluster
        $request_data_range_path = $work_prefix || "/request_data_range";
        INSERT INTO $request_data_range_path WITH TRUNCATE
        SELECT $begin as begin, $end as end;
    """
    ).format(
        yt_proxy=_YT_PROXY,
        work_prefix=work_prefix,
        request_data_logs_root=_REQUEST_DATA_LOGS_ROOT,
        interval_size=interval_size,
        logs_interval_type=logs_interval_type,
        user_filtration=user_filtration,
        hit_models_tag=_HIT_MODELS_EXT_TAG,
    )


def make_select_query(
    work_prefix, handler_limits, logs_interval_type="1d", had_user_subquery=False, output_suffix=""
):
    handler_limits_str = _make_limits_str(handler_limits)

    user_filtration = ""
    if had_user_subquery:
        user_filtration = textwrap.dedent(
            """
            $user_graph_ids_path = $work_prefix || "/user_graph_ids";
            $user_graph_ids = SELECT * FROM $user_graph_ids_path;

            $request_data =
            SELECT
                *
            FROM
                $request_data
            WHERE
                GraphID in $user_graph_ids;
        """
        )

    return textwrap.dedent(
        """
        USE {yt_proxy};
        PRAGMA yt.ExpirationInterval = "14d";
        PRAGMA DqEngine = "disable";

        $log_interval = "{logs_interval_type}";

        $work_prefix = "{work_prefix}";

        $handler_limits = AsDict({handler_limits_str});

        -- Read request data
        $request_data_logs_root = "{request_data_logs_root}" || $log_interval;
        $request_data_range_path = $work_prefix || "/request_data_range";
        $begin = select some(begin) from $request_data_range_path;
        $end = select some(end) from $request_data_range_path;
        $request_data = (
            SELECT * FROM RANGE($request_data_logs_root, $begin, $end)
            WHERE Tag = "{hit_models_tag}" AND Request is not null AND Response is null
        );

        -- Apply user filtration
        {user_filtration}

        -- Handlers limits selection
        $other_handlers_limit = $handler_limits["OTHER"] ?? 0;
        $get_handler_limit = ($handler) -> {{
            RETURN $handler_limits[$handler] ?? $other_handlers_limit;
        }};

        -- Handlers random selection
        DEFINE ACTION $select_random() AS
            INSERT INTO @random_graphids
            SELECT GraphID FROM $request_data
            ORDER BY GraphID DESC
            LIMIT $get_handler_limit("RANDOM");
            COMMIT;

            INSERT INTO @graphids SELECT GraphID FROM @random_graphids;
            COMMIT;
        END DEFINE;

        EVALUATE IF DictContains($handler_limits, "RANDOM")
            DO $select_random();

        $fix_double_space_post = Re2::Replace("(^POST)  (/yabs_hit_models)");

        -- Write request-data for selected graph ids
        $output = $work_prefix || "/output" || "{output_suffix}";
        INSERT INTO $output WITH TRUNCATE
        SELECT
            F.GraphID as GraphID,
            DENSE_RANK(F.GraphID) over w as `X-Yabs-HitModels-Req-Id`,
            $fix_double_space_post(Request, "\\\\1 \\\\2") as Request,
            Timestamp,
            Response,
            Tag,
            HttpStatus
        FROM
            $request_data AS F
        INNER JOIN
            @graphids AS G
        ON
            F.GraphID == G.GraphID
        WINDOW w as
            (ORDER BY F.GraphID)
        ORDER BY
            GraphID;
    """
    ).format(
        yt_proxy=_YT_PROXY,
        logs_interval_type=logs_interval_type,
        work_prefix=work_prefix,
        handler_limits_str=handler_limits_str,
        request_data_logs_root=_REQUEST_DATA_LOGS_ROOT,
        user_filtration=user_filtration,
        output_suffix=output_suffix,
        hit_models_tag=_HIT_MODELS_EXT_TAG,
    )
