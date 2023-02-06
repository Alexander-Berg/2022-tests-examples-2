import copy
import json
import typing as tp
import uuid


def _create_query_param(name: str, casts: dict = None) -> str:
    casts = casts or {}
    if name not in casts:
        return '%s'
    return casts[name]()


def _get_query_with_args(
        item: dict,
        table: str,
        fields: tp.List[str],
        *,
        required: list = None,
        casts: dict = None,
) -> tp.Tuple[str, list]:
    required = required or []

    keys = []
    args = []

    for name in required:
        assert name in item, f'Field "{name}" is required'

    for key, value in item.items():
        assert key in fields, f'Field "{key}" not present in "{table}" table'
        keys.append(key)
        args.append(value)

    query = f"""
    INSERT INTO scooters_ops.{table} (
        {','.join(keys)}
    )
    VALUES (
        {','.join(_create_query_param(name, casts) for name in keys)}
    )
    RETURNING {','.join(fields)}
    """

    return query, args


def _merge_tuple_with_fields(fields, db_tuple) -> dict:
    assert len(fields) == len(db_tuple), 'len mismatch'
    return dict(zip(fields, db_tuple))


def _try_flatten(items: list, flatten: bool):
    if not flatten or not items:
        return items

    assert len(items[0]) == 1, 'Only one field can be flattened'

    field = list(items[0])[0]
    return [item[field] for item in items]


DRAFT_FIELDS = [
    'draft_id',
    'type',
    'status',
    'revision',
    'mission_id',
    'point_id',
    'job_id',
    'created_at',
    'updated_at',
    'typed_extra',
    'expires_at',
]

MISSION_FIELDS = [
    'mission_id',
    'status',
    'performer_id',
    'comment',
    'fail_reasons',
    'cargo_claim_id',
    'revision',
    'created_at',
]

POINT_FIELDS = [
    'point_id',
    'type',
    'status',
    'mission_id',
    'location',
    'address',
    'region_id',
    'cargo_point_id',
    'order_in_mission',
    'arrival_time',
    'eta',
    'typed_extra',
    'comment',
    'fail_reasons',
    'revision',
]

JOB_FIELDS = [
    'job_id',
    'type',
    'status',
    'point_id',
    'order_at_point',
    'expected_execution_time',
    'started_at',
    'performer_id',
    'comment',
    'fail_reasons',
    'typed_extra',
    'created_at',
    'updated_at',
    'revision',
]

MISSIONS_HISTORY_FIELDS = [
    'history_event_id',
    'history_timestamp',
    'mission_id',
    'point_id',
    'job_id',
    'type',
    'extra',
]

NOTIFICATIONS_FIELDS = [
    'idempotency_token',
    'mission_id',
    'point_id',
    'job_id',
    'type',
    'completed',
    'recipients',
    'created_at',
    'updated_at',
]

TAGS_FIELDS = ['tag', 'entity_id', 'entity_type']


def get_drafts(pgsql, ids=None, *, fields=None, flatten=False):
    fields = fields or DRAFT_FIELDS
    sql = f"""
    SELECT
        {','.join(fields)}
    FROM
        scooters_ops.drafts
    """
    if ids is not None:
        sql = sql + 'WHERE draft_id = ANY(%(ids)s)'
    sql += ' ORDER BY draft_id'
    cursor = pgsql['scooters_ops'].cursor()

    cursor.execute(sql, {'ids': ids or []})
    return _try_flatten(
        list(
            _merge_tuple_with_fields(fields, item_tuple)
            for item_tuple in cursor.fetchall()
        ),
        flatten,
    )


def get_draft(pgsql, draft_id: str, *, fields=None):
    drafts = get_drafts(pgsql, ids=[draft_id], fields=fields)
    assert len(drafts) == 1, f'Draft with id: {draft_id} not found'
    return drafts[0]


def get_jobs(pgsql, ids=None, points_ids=None, *, fields=None, flatten=False):
    fields = fields or JOB_FIELDS
    sql = f"""
    SELECT
        {','.join(fields)}
    FROM
        scooters_ops.jobs
    """
    if ids is not None:
        sql = sql + 'WHERE job_id = ANY(%(ids)s)'
    elif points_ids is not None:
        sql += 'WHERE point_id = ANY(%(ids)s)'
    sql += '\nORDER BY order_at_point'
    cursor = pgsql['scooters_ops'].cursor()

    cursor.execute(sql, {'ids': ids or points_ids or []})

    return _try_flatten(
        list(
            _merge_tuple_with_fields(fields, item_tuple)
            for item_tuple in cursor.fetchall()
        ),
        flatten,
    )


def get_points(
        pgsql,
        ids=None,
        missions_ids=None,
        *,
        fields=None,
        flatten=False,
        job_params=None,
):
    fields = fields or POINT_FIELDS
    sql = f"""
    SELECT
        {','.join(fields)}
    FROM
        scooters_ops.points
    """
    if ids is not None:
        sql = sql + 'WHERE point_id = ANY(%(ids)s)'
    elif missions_ids is not None:
        sql += 'WHERE mission_id = ANY(%(ids)s)'
    sql += '\nORDER BY order_in_mission'
    cursor = pgsql['scooters_ops'].cursor()

    cursor.execute(sql, {'ids': ids or missions_ids or []})

    result = _try_flatten(
        list(
            _merge_tuple_with_fields(fields, item_tuple)
            for item_tuple in cursor.fetchall()
        ),
        flatten,
    )

    assert (
        job_params is None or 'point_id' in fields
    ), 'Cannot get jobs without point_id in fields'
    if job_params is not None:
        for point in result:
            point['jobs'] = get_jobs(
                pgsql,
                points_ids=[point['point_id']],
                fields=job_params.get('fields', None),
                flatten=job_params.get('flatten', False),
            )

    return result


def get_missions(
        pgsql, ids=None, *, fields=None, flatten=False, point_params=None,
):
    fields = fields or MISSION_FIELDS
    sql = f"""
    SELECT
        {','.join(fields)}
    FROM
        scooters_ops.missions
    """
    if ids is not None:
        sql = sql + 'WHERE mission_id = ANY(%(ids)s)'
    cursor = pgsql['scooters_ops'].cursor()

    cursor.execute(sql, {'ids': ids or []})
    result = _try_flatten(
        list(
            _merge_tuple_with_fields(fields, item_tuple)
            for item_tuple in cursor.fetchall()
        ),
        flatten,
    )

    assert (
        point_params is None or 'mission_id' in fields
    ), 'Cannot get points without mission_id in fields'
    if point_params is not None:
        for mission in result:
            mission['points'] = get_points(
                pgsql,
                missions_ids=[mission['mission_id']],
                fields=point_params.get('fields', None),
                flatten=point_params.get('flatten', False),
                job_params=point_params.get('job_params', None),
            )

    return result


def add_history(pgsql, history_event):
    if 'extra' in history_event:
        history_event['extra'] = json.dumps(history_event['extra'])

    cursor = pgsql['scooters_ops'].cursor()
    query, args = _get_query_with_args(
        history_event,
        'missions_history',
        MISSIONS_HISTORY_FIELDS,
        required=['mission_id', 'type'],
    )
    cursor.execute(query, args)

    return _merge_tuple_with_fields(MISSIONS_HISTORY_FIELDS, cursor.fetchone())


def get_history(pgsql, mission_ids=None, *, fields=None, flatten=False):
    fields = fields or MISSIONS_HISTORY_FIELDS
    sql = f"""
    SELECT
        {','.join(fields)}
    FROM
        scooters_ops.missions_history
    """

    if mission_ids is not None:
        sql = sql + 'WHERE mission_id = ANY(%(mission_ids)s)'
    sql += '\nORDER BY history_timestamp'

    cursor = pgsql['scooters_ops'].cursor()

    cursor.execute(sql, {'mission_ids': mission_ids or []})

    return _try_flatten(
        list(
            _merge_tuple_with_fields(fields, item_tuple)
            for item_tuple in cursor.fetchall()
        ),
        flatten,
    )


def get_notifications(pgsql, mission_ids=None, *, fields=None, flatten=False):
    fields = fields or NOTIFICATIONS_FIELDS
    sql = f"""
    SELECT
        {','.join(fields)}
    FROM
        scooters_ops.monitoring_notifications
    """

    if mission_ids is not None:
        sql = sql + 'WHERE mission_id = ANY(%(mission_ids)s)'
    sql += '\nORDER BY created_at'

    cursor = pgsql['scooters_ops'].cursor()

    cursor.execute(sql, {'mission_ids': mission_ids or []})

    return _try_flatten(
        list(
            _merge_tuple_with_fields(fields, item_tuple)
            for item_tuple in cursor.fetchall()
        ),
        flatten,
    )


def add_draft(pgsql, draft):
    if 'typed_extra' in draft:
        draft['typed_extra'] = json.dumps(draft['typed_extra'])

    cursor = pgsql['scooters_ops'].cursor()
    query, args = _get_query_with_args(
        draft, 'drafts', DRAFT_FIELDS, required=['draft_id', 'type'],
    )
    cursor.execute(query, args)

    return _merge_tuple_with_fields(DRAFT_FIELDS, cursor.fetchone())


def add_job(pgsql, job):
    if 'typed_extra' in job:
        job['typed_extra'] = json.dumps(job['typed_extra'])

    cursor = pgsql['scooters_ops'].cursor()
    query, args = _get_query_with_args(
        job,
        'jobs',
        JOB_FIELDS,
        required=['type', 'point_id', 'order_at_point', 'typed_extra'],
    )
    cursor.execute(query, args)

    return _merge_tuple_with_fields(JOB_FIELDS, cursor.fetchone())


def add_point(pgsql, point):
    if 'point_id' not in point:
        point['point_id'] = uuid.uuid4().hex

    jobs = None
    if 'jobs' in point:
        jobs = point.pop('jobs')
        for idx, job in enumerate(jobs):
            job.setdefault('point_id', point['point_id'])
            job.setdefault('order_at_point', idx + 1)

    if 'typed_extra' in point:
        point['typed_extra'] = json.dumps(point['typed_extra'])

    cursor = pgsql['scooters_ops'].cursor()
    query, args = _get_query_with_args(
        point,
        'points',
        POINT_FIELDS,
        required=[
            'type',
            'location',
            'mission_id',
            'order_in_mission',
            'typed_extra',
        ],
        casts={'location': lambda: 'CAST(\'%s\' AS POINT)'},
    )
    cursor.execute(query, args)

    result = _merge_tuple_with_fields(POINT_FIELDS, cursor.fetchone())

    if jobs is not None:
        result['jobs'] = [add_job(pgsql, job) for job in jobs]

    return result


def add_mission(pgsql, mission):
    mission = copy.deepcopy(mission)
    points = None

    if 'tags' in mission and not mission['tags']:
        mission.pop('tags')

    if 'points' in mission:
        points = mission.pop('points')
        for idx, point in enumerate(points):
            point.setdefault('mission_id', mission['mission_id'])
            point.setdefault('location', (37, 55))
            point.setdefault('order_in_mission', idx + 1)
    if 'tags' in mission:
        tags = mission.pop('tags')
        add_tags(
            pgsql,
            {
                'tag': tags,
                'entity_id': mission['mission_id'],
                'entity_type': 'mission',
            },
        )

    query, args = _get_query_with_args(
        mission, 'missions', MISSION_FIELDS, required=['mission_id'],
    )
    cursor = pgsql['scooters_ops'].cursor()
    cursor.execute(query, args)

    result = _merge_tuple_with_fields(MISSION_FIELDS, cursor.fetchone())

    if points is not None:
        result['points'] = [add_point(pgsql, point) for point in points]

    return result


def add_notification(pgsql, notification):
    if 'recipients' in notification:
        notification['recipients'] = json.dumps(notification['recipients'])

    cursor = pgsql['scooters_ops'].cursor()
    query, args = _get_query_with_args(
        notification,
        'monitoring_notifications',
        NOTIFICATIONS_FIELDS,
        required=['idempotency_token', 'mission_id', 'type'],
    )
    cursor.execute(query, args)

    return _merge_tuple_with_fields(NOTIFICATIONS_FIELDS, cursor.fetchone())


def add_tags(pgsql, tags):
    if not tags:
        return []

    query, args = _get_query_with_args(
        tags,
        'tags',
        TAGS_FIELDS,
        required=TAGS_FIELDS,
        casts={'tag': lambda: 'UNNEST(%s)'},
    )

    cursor = pgsql['scooters_ops'].cursor()
    cursor.execute(query, args)

    result = _merge_tuple_with_fields(TAGS_FIELDS, cursor.fetchone())

    return result


def init_ui_status_by_job_type(job_type):
    return 'booked' if job_type == 'pickup_batteries' else 'pickuped'
