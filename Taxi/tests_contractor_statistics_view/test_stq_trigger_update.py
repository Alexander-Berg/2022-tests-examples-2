import pytest


def get_query(*args, **kwargs):
    conditions = ';'
    query = f"""
    SELECT
        {', '.join(kwargs['params'])}
    FROM contractor_statistics_view.triggers
    WHERE trigger_name = \'{kwargs['trigger_name']}\'
    """
    if kwargs.get('park_id') and kwargs.get('driver_profile_id'):
        conditions = (
            f' AND park_id = \'{kwargs["park_id"]}\''
            f' AND driver_profile_id = \'{kwargs["driver_profile_id"]}\';'
        )
    elif kwargs.get('unique_driver_id'):
        conditions = (
            f' AND unique_driver_id = \'{kwargs["unique_driver_id"]}\';'
        )

    return query + conditions


@pytest.mark.parametrize(
    'park_id, driver_profile_id, '
    'unique_driver_id, expected_counter, expected_status',
    [
        (None, None, 'udid1', 3, 'active'),
        ('p2', 'd2', None, 2, 'waiting'),
        ('p3', 'd3', None, 3, 'active'),
    ],
)
@pytest.mark.pgsql('contractor_statistics_view', files=['insert_triggers.sql'])
@pytest.mark.experiments3(
    filename='contractor_statistics_view_trigger_settings.json',
)
async def test_existed_trigger_update(
        pgsql,
        stq_runner,
        client_events,
        unique_drivers,
        park_id,
        driver_profile_id,
        unique_driver_id,
        expected_counter,
        expected_status,
        mockserver,
):
    @mockserver.json_handler('/tags/v1/upload')
    def _v1_upload(request):
        return {'status': 'ok'}

    client_events.status_code = 200
    client_events.response = {'items': [{'status': 'ok', 'version': '777'}]}
    unique_drivers.set_retrieve_by_uniques(
        unique_driver_id, driver_profile_id, park_id,
    )

    await stq_runner.contractor_statistics_view_trigger_update.call(
        task_id='task_id',
        args=[],
        kwargs={
            'trigger_name': 'skip_chain_order',
            'driver_profile_id': driver_profile_id,
            'park_id': park_id,
            'unique_driver_id': unique_driver_id,
        },
    )
    trigger_name = 'skip_chain_order'

    query = get_query(
        params=['counter', 'trigger_status'],
        trigger_name=trigger_name,
        driver_profile_id=driver_profile_id,
        park_id=park_id,
        unique_driver_id=unique_driver_id,
    )

    cursor = pgsql['contractor_statistics_view'].cursor()
    cursor.execute(query)
    rows = cursor.fetchall()

    assert rows == [(expected_counter, expected_status)]

    assert unique_drivers.retrieve_by_uniques.times_called == (
        1 if unique_driver_id else 0
    )


@pytest.mark.parametrize(
    'park_id, driver_profile_id, unique_driver_id, '
    'expected_counter, expected_status',
    [
        (None, None, 'udid2', 1, 'waiting'),
        ('p4', 'd4', None, 1, 'active'),
        (None, None, 'udid3', 1, 'active'),
    ],
)
@pytest.mark.pgsql('contractor_statistics_view', files=['insert_triggers.sql'])
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='contractor_statistics_view_trigger_settings',
    consumers=['contractor_statistics_view'],
    clauses=[
        {
            'predicate': {
                'init': {
                    'value': 'd4',
                    'arg_name': 'driver_profile_id',
                    'arg_type': 'string',
                },
                'type': 'eq',
            },
            'value': {'skip_chain_order': {'counter_to_active': 1}},
        },
        {
            'predicate': {
                'init': {
                    'value': 'udid3',
                    'arg_name': 'unique_driver_id',
                    'arg_type': 'string',
                },
                'type': 'eq',
            },
            'value': {'skip_chain_order': {'counter_to_active': 1}},
        },
    ],
    default_value={'skip_chain_order': {'counter_to_active': 2}},
    is_config=True,
)
async def test_new_trigger_update(
        pgsql,
        stq_runner,
        client_events,
        unique_drivers,
        park_id,
        driver_profile_id,
        unique_driver_id,
        expected_counter,
        expected_status,
        mockserver,
):
    @mockserver.json_handler('/tags/v1/upload')
    def _v1_upload(request):
        return {'status': 'ok'}

    client_events.status_code = 200
    client_events.response = {'items': [{'status': 'ok', 'version': '777'}]}
    unique_drivers.set_retrieve_by_uniques(
        unique_driver_id, driver_profile_id, park_id,
    )
    await stq_runner.contractor_statistics_view_trigger_update.call(
        task_id='task_id',
        args=[],
        kwargs={
            'trigger_name': 'skip_chain_order',
            'driver_profile_id': driver_profile_id,
            'park_id': park_id,
            'unique_driver_id': unique_driver_id,
        },
    )
    trigger_name = 'skip_chain_order'
    query = get_query(
        params=[
            'unique_driver_id',
            'park_id',
            'driver_profile_id',
            'trigger_name',
            'counter',
            'trigger_status',
        ],
        trigger_name=trigger_name,
        driver_profile_id=driver_profile_id,
        park_id=park_id,
        unique_driver_id=unique_driver_id,
    )

    cursor = pgsql['contractor_statistics_view'].cursor()
    cursor.execute(query)
    rows = cursor.fetchall()

    assert rows == [
        (
            unique_driver_id,
            park_id,
            driver_profile_id,
            trigger_name,
            expected_counter,
            expected_status,
        ),
    ]

    if expected_status == 'active':
        assert unique_drivers.retrieve_by_uniques.times_called == (
            1 if unique_driver_id else 0
        )
        assert client_events.bulk_push.times_called == 1


@pytest.mark.parametrize(
    'park_id, driver_profile_id, unique_driver_id, '
    'expected_counter, expected_status',
    [('p2', 'd2', None, 1, 'waiting')],
)
@pytest.mark.pgsql('contractor_statistics_view', files=['insert_triggers.sql'])
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='contractor_statistics_view_trigger_settings',
    consumers=['contractor_statistics_view'],
    clauses=[],
    default_value={'skip_chain_order': {'counter_to_active': 1}},
    is_config=True,
)
async def test_client_events_fail(
        pgsql,
        stq_runner,
        client_events,
        unique_drivers,
        park_id,
        driver_profile_id,
        unique_driver_id,
        expected_counter,
        expected_status,
        mockserver,
):
    @mockserver.json_handler('/tags/v1/upload')
    def _v1_upload(request):
        return {'status': 'ok'}

    client_events.status_code = 500
    client_events.response = {}
    unique_drivers.set_retrieve_by_uniques(
        unique_driver_id, driver_profile_id, park_id,
    )

    await stq_runner.contractor_statistics_view_trigger_update.call(
        task_id='task_id',
        args=[],
        kwargs={
            'trigger_name': 'skip_chain_order',
            'driver_profile_id': driver_profile_id,
            'park_id': park_id,
            'unique_driver_id': unique_driver_id,
        },
        expect_fail=True,
    )
    trigger_name = 'skip_chain_order'

    query = get_query(
        params=['counter', 'trigger_status'],
        trigger_name=trigger_name,
        driver_profile_id=driver_profile_id,
        park_id=park_id,
        unique_driver_id=unique_driver_id,
    )

    cursor = pgsql['contractor_statistics_view'].cursor()
    cursor.execute(query)
    rows = cursor.fetchall()

    assert rows == [(expected_counter, expected_status)]
