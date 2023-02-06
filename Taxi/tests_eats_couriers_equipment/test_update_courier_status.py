import datetime

import pytest

LIST_CORE_COURIERS_HANDLER_PATH = (
    '/couriers-core/api/v1/general-information/couriers/catalog/list'
)

CORE_COURIER_SERVICES_HANDLER_PATH = (
    '/couriers-core/api/v1/general-information/courier-services'
)

TASK_CONFIG = {
    'enabled': True,
    'batch_size': 1000,
    'request_delay_ms': 1,
    'meta_operations_pg_timeout': {'network': 1000, 'statement': 1000},
}
CORE_COURIERS_LIST = {
    'couriers': [
        {
            'id': 123456,
            'first_name': 'Рафаил',
            'last_name': 'Фролов',
            'phone_number': '72616df729374c6f9e661ee503ad94e2',
            'project_type': 'new_super_project',
            'work_status': 'super_strange_status',
            'work_region': {'id': 75, 'name': 'Тюмень'},
            'billing_type': 'self_employed',
            'courier_service_id': 1,
            'updated_at': '2020-07-03T16:37:10+03:00',
        },
        {
            'id': 123457,
            'first_name': 'Курьер',
            'last_name': 'Лавкович',
            'middle_name': 'Бутербродович',
            'phone_number': '72616df729374c6f9e661ee503ad94e2',
            'project_type': 'lavka',
            'work_status': 'active',
            'work_region': {'id': 75, 'name': 'Тюмень'},
            'billing_type': 'courier_service',
            'courier_service_id': 2,
            'updated_at': '2020-07-03T16:37:10+03:00',
        },
        {
            'id': 592726,
            'first_name': 'Леха',
            'middle_name': 'eeeee',
            'last_name': 'asdasd',
            'phone_number': '9cff43d9642341eba99c4368117cbb13',
            'project_type': 'eda',
            'work_status': 'active',
            'work_region': {'id': 1, 'name': 'Москва'},
            'updated_at': '2020-07-06T13:53:54+03:00',
        },
    ],
}


CORE_COURIER_SERVICES = {
    'courier_services': [
        {
            'id': 1,
            'name': 'service-1-name',
            'region_ids': [1],
            'inn': '123456789',
        },
        {
            'id': 2,
            'name': 'service-2-name',
            'region_ids': [2],
            'inn': '987654321',
        },
    ],
}

EXPECTED_META = [
    (
        1,
        datetime.datetime(2019, 9, 8, 8, 15, 15),
        False,
        datetime.datetime(2019, 9, 8, 8, 15, 15),
    ),
    (
        2,
        datetime.datetime(2019, 9, 8, 8, 15, 15),
        False,
        datetime.datetime(2019, 9, 8, 10, 15, 15),
    ),
    (
        3,
        datetime.datetime(2019, 9, 8, 10, 15, 15),
        False,
        datetime.datetime(2019, 9, 8, 13, 15, 15),
    ),
]

EXPECTED_COURIERS = [
    (
        1,
        'Рафаил',
        None,
        'Фролов',
        '72616df729374c6f9e661ee503ad94e2',
        123456,
        'Тюмень',
        'new_super_project',
        'new_super_project',
        'super_strange_status',
        'super_strange_status',
        1,
        'self_employed',
        1,
        'service-1-name',
    ),
    (
        2,
        'Курьер',
        'Бутербродович',
        'Лавкович',
        '72616df729374c6f9e661ee503ad94e2',
        123457,
        'Тюмень',
        'lavka',
        'Лавка',
        'active',
        'Активен',
        2,
        'courier_service',
        2,
        'service-2-name',
    ),
]

EXPECTED_SERVICES = [
    (1, 'service-1-name', [1], '123456789'),
    (2, 'service-2-name', [2], '987654321'),
]

READ_SERVICES_SQL = (
    'select id, name, region_ids, inn from courier_services order by id'
)

READ_COURIERS_SQL = """
        select
            c.id,
            c.first_name,
            c.middle_name,
            c.last_name,
            c.phone_pd_id,
            c.eda_id,
            r.name,
            cpt.name,
            cpt.description,
            cws.name,
            cws.description,
            cbt.id billing_type_id,
            cbt.name billing_type_name,
            cs.id service_id,
            cs.name service_name
        from
            couriers c
            join regions r
                on c.work_region_id = r.id
            join courier_work_statuses cws
                on c.courier_work_status_id = cws.id
            left join courier_project_types cpt
                on c.courier_project_type_id = cpt.id
            left join courier_billing_types cbt
                on c.courier_billing_type_id = cbt.id
            left join courier_services cs
                on c.courier_service_id = cs.id
        order by c.id;
    """

READ_META_SQL = """
        select
            id, sync_ts, in_progress, created_at
        from
            couriers_update_meta
        ;
    """

ADD_META_SQL = """
    insert into
        couriers_update_meta (sync_ts, in_progress, created_at)
    values
        ('{}'::timestamp, {}, '{}'::timestamp)
    ;
"""


@pytest.fixture(name='core_couriers_services_mock')
async def courier_service_server(mockserver):
    @mockserver.json_handler(CORE_COURIER_SERVICES_HANDLER_PATH)
    def _mock_courier_service(request):
        return mockserver.make_response(json=CORE_COURIER_SERVICES, status=200)

    return _mock_courier_service


@pytest.mark.config(
    EATS_COURIERS_EQUIPMENT_UPDATE_COURIERS_CONFIGURATION=TASK_CONFIG,
)
@pytest.mark.pgsql(
    'outsource-lavka-transport',
    files=[
        'add_courier_relations.sql',
        'add_courier.sql',
        'add_couriers_update_meta.sql',
    ],
)
@pytest.mark.now('2019-11-08T04:30:50Z')
async def test_task(
        testpoint,
        taxi_eats_couriers_equipment,
        mockserver,
        pgsql,
        core_couriers_services_mock,
):
    @testpoint('update_courier_status::update-courier-status-finished')
    def handle_finished(arg):
        pass

    @mockserver.json_handler(LIST_CORE_COURIERS_HANDLER_PATH)
    def _mock_couriers_list(request):
        if request.query.get('min_id'):
            return {'couriers': []}
        return CORE_COURIERS_LIST

    await taxi_eats_couriers_equipment.run_distlock_task(
        'update-courier-status',
    )

    _assert_couriers_list_call(_mock_couriers_list, '2019-09-08T13:15:15Z')
    result = handle_finished.next_call()
    assert result == {'arg': 'finish'}

    await _assert_meta(
        pgsql,
        (
            datetime.datetime(2019, 9, 8, 13, 15, 15),
            False,
            datetime.datetime(2019, 11, 8, 4, 30, 50),
        ),
    )

    services_result = await _read_services(pgsql)
    assert services_result == EXPECTED_SERVICES

    couriers_result = await _read_couriers(pgsql)
    assert couriers_result == EXPECTED_COURIERS


@pytest.mark.config(
    EATS_COURIERS_EQUIPMENT_UPDATE_COURIERS_CONFIGURATION=TASK_CONFIG,
)
@pytest.mark.pgsql(
    'outsource-lavka-transport',
    files=[
        'add_courier_relations.sql',
        'add_courier.sql',
        'add_couriers_update_meta.sql',
    ],
)
@pytest.mark.parametrize('expired_meta', [True, False])
@pytest.mark.now('2019-11-08T04:30:50Z')
async def test_meta_in_progress(
        testpoint,
        taxi_eats_couriers_equipment,
        mockserver,
        pgsql,
        expired_meta,
        core_couriers_services_mock,
):
    @testpoint('update_courier_status::update-courier-status-finished')
    def handle_finished(arg):
        pass

    sync_ts = datetime.datetime(2019, 9, 9, 15, 0, 5)
    if expired_meta:
        created_at = datetime.datetime(2019, 11, 8, 1, 30, 50)
    else:
        created_at = datetime.datetime(2019, 11, 8, 4, 30, 20)
    new_meta = (sync_ts, True, created_at)
    await _add_meta(pgsql, *new_meta)

    @mockserver.json_handler(LIST_CORE_COURIERS_HANDLER_PATH)
    def _mock_couriers_list(request):
        if request.query.get('min_id'):
            return {'couriers': []}
        return CORE_COURIERS_LIST

    await taxi_eats_couriers_equipment.run_distlock_task(
        'update-courier-status',
    )

    result = handle_finished.next_call()
    if expired_meta:
        assert result == {'arg': 'finish'}
        _assert_couriers_list_call(_mock_couriers_list, '2019-09-09T15:00:05Z')
        new_meta = (new_meta[0], False, new_meta[2])
    else:
        assert result == {'arg': 'Another update status process in progress'}
        assert not _mock_couriers_list.times_called

    await _assert_meta(pgsql, new_meta)


@pytest.mark.config(
    EATS_COURIERS_EQUIPMENT_UPDATE_COURIERS_CONFIGURATION=TASK_CONFIG,
)
@pytest.mark.pgsql(
    'outsource-lavka-transport',
    files=[
        'add_courier_relations.sql',
        'add_courier.sql',
        'add_old_meta.sql',
        'add_couriers_update_meta.sql',
    ],
)
@pytest.mark.now('2019-11-08T04:30:50Z')
async def test_clear_old_meta(
        testpoint,
        taxi_eats_couriers_equipment,
        mockserver,
        pgsql,
        core_couriers_services_mock,
):
    @testpoint('update_courier_status::update-courier-status-finished')
    def handle_finished(arg):
        pass

    @mockserver.json_handler(LIST_CORE_COURIERS_HANDLER_PATH)
    def _mock_couriers_list(request):
        if request.query.get('min_id'):
            return {'couriers': []}
        return CORE_COURIERS_LIST

    await taxi_eats_couriers_equipment.run_distlock_task(
        'update-courier-status',
    )
    assert _mock_couriers_list.has_calls
    result = handle_finished.next_call()
    assert result == {'arg': 'finish'}
    meta_result = await _read_meta(pgsql)
    assert [meta[0] for meta in meta_result] == [4, 5, 6, 7, 8]


@pytest.mark.pgsql(
    'outsource-lavka-transport',
    files=[
        'add_courier_relations.sql',
        'add_courier.sql',
        'add_couriers_update_meta.sql',
    ],
)
@pytest.mark.now('2019-11-08T04:30:50Z')
async def test_meta_bad_request(
        testpoint,
        taxi_eats_couriers_equipment,
        mockserver,
        pgsql,
        core_couriers_services_mock,
):
    @testpoint('update_courier_status::update-courier-status-finished')
    def handle_finished(arg):
        pass

    @mockserver.json_handler(LIST_CORE_COURIERS_HANDLER_PATH)
    def _mock_couriers_list(request):
        return mockserver.make_response(
            json={
                'domain': 'UserData',
                'code': 5,
                'err': 'Неверный формат',
                'errors': ['Empty input'],
            },
            status=400,
        )

    await taxi_eats_couriers_equipment.run_distlock_task(
        'update-courier-status',
    )

    assert handle_finished.times_called == 1

    assert _mock_couriers_list.times_called == 1
    call = _mock_couriers_list.next_call()
    assert dict(call['request'].query) == {
        'limit': '1000',
        'updated_at': '2019-09-08T13:15:15Z',
    }

    await _assert_meta(
        pgsql,
        (
            datetime.datetime(2019, 9, 8, 13, 15, 15),
            True,
            datetime.datetime(2019, 11, 8, 4, 30, 50),
        ),
    )


@pytest.mark.config(
    EATS_COURIERS_EQUIPMENT_UPDATE_COURIERS_CONFIGURATION=TASK_CONFIG,
)
@pytest.mark.pgsql(
    'outsource-lavka-transport',
    files=[
        'add_courier_relations.sql',
        'add_courier.sql',
        'add_couriers_update_meta.sql',
    ],
)
@pytest.mark.now('2019-11-08T04:30:50Z')
async def test_meta_many_requests(
        testpoint,
        taxi_eats_couriers_equipment,
        mockserver,
        pgsql,
        core_couriers_services_mock,
):
    @testpoint('update_courier_status::update-courier-status-finished')
    def handle_finished(arg):
        pass

    @mockserver.json_handler(LIST_CORE_COURIERS_HANDLER_PATH)
    def _mock_couriers_list(request):
        couriers = []
        ids = []
        if request.query.get('min_id') is None:
            ids = list(range(1, 1001))
        elif request.query['min_id'] == '1000':
            ids = list(range(1001, 2001))
        elif request.query['min_id'] == '2000':
            ids = list(range(2001, 3001))
        for courier_id in ids:
            courier = CORE_COURIERS_LIST['couriers'][0].copy()
            courier['id'] = courier_id
            couriers.append(courier)
        return {'couriers': couriers}

    await taxi_eats_couriers_equipment.run_distlock_task(
        'update-courier-status',
    )

    result = handle_finished.next_call()
    assert result == {'arg': 'finish'}
    assert _mock_couriers_list.times_called == 4
    for call_num in range(4):
        call = _mock_couriers_list.next_call()
        min_id = call_num * 1000
        expected = {'limit': '1000', 'updated_at': '2019-09-08T13:15:15Z'}
        if min_id:
            expected['min_id'] = str(min_id)
        assert dict(call['request'].query) == expected

    await _assert_meta(
        pgsql,
        (
            datetime.datetime(2019, 9, 8, 13, 15, 15),
            False,
            datetime.datetime(2019, 11, 8, 4, 30, 50),
        ),
    )


@pytest.mark.pgsql(
    'outsource-lavka-transport', files=['add_couriers_update_meta.sql'],
)
@pytest.mark.parametrize('in_progress', [True, False])
async def test_get_status(taxi_eats_couriers_equipment, pgsql, in_progress):
    if in_progress:
        sync_ts = datetime.datetime(2019, 9, 9, 15, 0, 5)
        await _add_meta(pgsql, sync_ts, True, sync_ts)

    await _get_status_handle(taxi_eats_couriers_equipment, in_progress)


async def test_get_status_empty_db(taxi_eats_couriers_equipment):
    await _get_status_handle(taxi_eats_couriers_equipment, False)


async def _get_status_handle(taxi_eats_couriers_equipment, in_progress):
    create_response = await taxi_eats_couriers_equipment.get(
        '/v1.0/couriers/eda/update/status',
    )
    assert create_response.status_code == 200, create_response.text
    data = create_response.json()
    assert data == {
        'meta': {'updateStatus': 'in-progress' if in_progress else 'updated'},
    }


def _assert_couriers_list_call(_mock_couriers_list, updated_at):
    assert _mock_couriers_list.times_called == 2
    call = _mock_couriers_list.next_call()
    assert dict(call['request'].query) == {
        'limit': '1000',
        'updated_at': updated_at,
    }
    call = _mock_couriers_list.next_call()
    assert dict(call['request'].query) == {
        'limit': '1000',
        'updated_at': updated_at,
        'min_id': '592726',
    }


async def _assert_meta(pgsql, new_meta):
    meta_result = await _read_meta(pgsql)
    expected_meta = EXPECTED_META + [
        (4, new_meta[0], new_meta[1], new_meta[2]),
    ]
    assert meta_result == expected_meta


async def _add_meta(pgsql, sync_ts, in_progress, created_at):
    cursor = pgsql['outsource-lavka-transport'].cursor()
    cursor.execute(
        ADD_META_SQL.format(
            sync_ts, 'true' if in_progress else 'false', created_at,
        ),
    )
    cursor.close()


async def _read_meta(pgsql):
    cursor = pgsql['outsource-lavka-transport'].cursor()
    cursor.execute(READ_META_SQL)
    meta_result = cursor.fetchall()
    cursor.close()
    return meta_result


async def _read_couriers(pgsql):
    cursor = pgsql['outsource-lavka-transport'].cursor()
    cursor.execute(READ_COURIERS_SQL)
    couriers_result = cursor.fetchall()
    cursor.close()
    return couriers_result


async def _read_services(pgsql):
    cursor = pgsql['outsource-lavka-transport'].cursor()
    cursor.execute(READ_SERVICES_SQL)
    services_result = cursor.fetchall()
    cursor.close()
    return services_result
