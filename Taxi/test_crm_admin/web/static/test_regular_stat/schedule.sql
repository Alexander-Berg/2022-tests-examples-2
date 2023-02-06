INSERT INTO crm_admin.segment
(
    id,
    yql_shared_url,
    yt_table,
    mode,
    control,
    created_at
)
VALUES
(
    1,
    'yql_shared_url_1',
    'yt_table_1',
    'Share',
    10,
    '2021-01-27 01:00:00'
),
(
    2,
    'yql_shared_url_2',
    'yt_table_2',
    'Share',
    10,
    '2021-01-27 01:00:00'
),
(
    3,
    'yql_shared_url_3',
    'yt_table_3',
    'Share',
    10,
    '2021-01-27 01:00:00'
),
(
    4,
    'yql_shared_url_4',
    'yt_table_4',
    'Share',
    10,
    '2021-01-27 01:00:00'
),
(
    5,
    'yql_shared_url_5',
    'yt_table_5',
    'Share',
    10,
    '2021-01-27 01:00:00'
),
(
    6,
    'yql_shared_url_6',
    'yt_table_6',
    'Share',
    10,
    '2021-01-27 01:00:00'
),
(
    7,
    'yql_shared_url_7',
    'yt_table_7',
    'Share',
    10,
    '2021-01-27 01:00:00'
);


INSERT INTO crm_admin.campaign
(
    id,
    segment_id,
    name,
    entity_type,
    trend,
    discount,
    state,
    is_regular,
    is_active,
    schedule,
    regular_start_time,
    regular_stop_time,
    created_at,
    root_id
)
VALUES
(
    1,
    1,
    'name_1',
    'User',
    'trend',
    True,
    'CAMPAIGN_APPROVED',
    True,
    True,
    '0 12 * * *',
    '2021-01-01T00:00:00',
    '2021-10-31T00:00:00',
    '2021-01-26 01:00:00',
    1
),
(
    2,
    2,
    'name_2',
    'User',
    'trend',
    True,
    'CAMPAIGN_APPROVED',
    True,
    True,
    '0 12 * * *',
    '2021-01-01T00:00:00',
    '2021-10-31T00:00:00',
    '2021-01-26 01:00:00',
    2
),
(
    3,
    3,
    'name_3',
    'User',
    'trend',
    True,
    'CAMPAIGN_APPROVED',
    True,
    True,
    '0 12 * * *',
    '2021-01-01T00:00:00',
    '2021-10-31T00:00:00',
    '2021-01-26 01:00:00',
    3
),
(
    4,
    4,
    'name_4',
    'User',
    'trend',
    True,
    'CAMPAIGN_APPROVED',
    True,
    True,
    '0 12 * * *',
    '2021-01-01T00:00:00',
    '2021-10-31T00:00:00',
    '2021-01-26 01:00:00',
    4
),
(
    5,
    5,
    'name_5',
    'User',
    'trend',
    True,
    'CAMPAIGN_APPROVED',
    True,
    True,
    '0 12 * * *',
    '2021-01-01T00:00:00',
    '2021-10-31T00:00:00',
    '2021-01-26 01:00:00',
    5
),
(
    6,
    6,
    'name_6',
    'User',
    'trend',
    True,
    'CAMPAIGN_APPROVED',
    True,
    True,
    '0 12 * * *',
    '2021-01-01T00:00:00',
    '2021-10-31T00:00:00',
    '2021-01-26 01:00:00',
    6
),
(
    7,
    7,
    'name_7',
    'User',
    'trend',
    True,
    'CAMPAIGN_APPROVED',
    True,
    True,
    '0 12 * * *',
    '2021-01-01T00:00:00',
    '2021-10-31T00:00:00',
    '2021-01-26 01:00:00',
    7
);


INSERT INTO crm_admin.schedule
(
    campaign_id,
    final_state,
    sending_stats,
    scheduled_for
)
VALUES
(
    1,
    'SCHEDULED',
    ('{
	    "1": {
		    "sent": 400,
            "failed": 0,
            "planned": 400,
            "skipped": 0,
            "finished_at": "2021-03-26T00:00:24.227266+03:00"
        },
        "2": {
		    "sent": 300,
            "failed": 0,
            "planned": 300,
            "skipped": 0,
            "finished_at": "2021-03-26T00:00:24.227266+03:00"
        }
    }')::jsonb,
    '2021-01-21 12:00:00'
),
(
    1,
    'SCHEDULED',
    ('{
	    "1": {
		    "sent": 100,
            "failed": 100,
            "planned": 200,
            "skipped": 0,
            "finished_at": "2021-03-26T00:00:24.227266+03:00"
        },
        "2": {
		    "sent": 0,
            "failed": 100,
            "planned": 100,
            "skipped": 0,
            "finished_at": "2021-03-26T00:00:24.227266+03:00"
        }
    }')::jsonb,
    '2021-01-21 13:00:00'
),
(
    2,
    'SCHEDULED',
    ('{
	    "1": {
		    "sent": 100,
            "failed": 0,
            "planned": 100,
            "skipped": 0,
            "finished_at": "2021-03-26T00:00:24.227266+03:00"
        }
    }')::jsonb,
    '2021-01-22 12:00:00'
),
(
    2,
    'SEGMENT_EMPTY',
    ('{}')::jsonb,
    '2021-01-22 13:00:00'
),
(
    3,
    'SCHEDULED',
    ('{
	    "1": {
		    "sent": 300,
            "failed": 0,
            "planned": 400,
            "skipped": 0,
            "finished_at": "2021-03-26T00:00:24.227266+03:00"
        }
    }')::jsonb,
    '2021-01-23 12:00:00'
),
(
    3,
    'SEGMENT_ERROR',
    ('{}')::jsonb,
    '2021-01-23 13:00:00'
),
(
    4,
    'GROUPS_ERROR',
    ('{}')::jsonb,
    '2021-01-24 12:00:00'
),
(
    4,
    'SCHEDULED',
    ('{
	    "1": {
		    "sent": 200,
            "failed": 0,
            "planned": 200,
            "skipped": 0,
            "finished_at": "2021-03-26T00:00:24.227266+03:00"
        }
    }')::jsonb,
    '2021-01-24 13:00:00'
),
(
    5,
    'GROUPS_ERROR',
    null,
    '2021-01-25 12:00:00'
),
(
    6,
    'SCHEDULED',
    ('{
	    "1": {
		    "sent": 100,
            "failed": 0,
            "planned": 200,
            "skipped": 0,
            "denied": 100,
            "finished_at": "2021-03-26T00:00:24.227266+03:00"
        }
    }')::jsonb,
    '2021-01-24 13:00:00'
),
(
    7,
    'SCHEDULED',
    ('{
	    "1": {
		    "sent": 100,
            "failed": 0,
            "planned": 200,
            "skipped": 100,
            "denied": 0,
            "finished_at": "2021-03-26T00:00:24.227266+03:00"
        }
    }')::jsonb,
    '2021-01-24 13:00:00'
)
;
