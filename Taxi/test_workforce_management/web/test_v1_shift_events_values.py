import pytest

from workforce_management.storage.postgresql import db

URI = 'v1/shift/event/values'
DELETE_URI = 'v1/shift/event/delete'
MODIFY_URI = 'v1/shift/event/modify'
HEADERS = {'X-Yandex-UID': 'uid1'}


@pytest.mark.pgsql('workforce_management', files=['simple_shift_events.sql'])
@pytest.mark.parametrize(
    'tst_request, expected_status,',
    [
        ({'alias': 'brainstorm', 'description': 'storm of brains'}, 200),
        (
            {
                'id': 1,
                'alias': 'fishing',
                'description': 'relax by fishing',
                'properties': {
                    'distribute_breaks_inside': True,
                    'is_training': False,
                },
            },
            409,
        ),
        (
            {
                'id': 1,
                'alias': 'fishing',
                'description': 'relax by fishing',
                'revision_id': '2020-11-16T11:10:00.000000 +0000',
                'properties': {
                    'distribute_breaks_inside': True,
                    'is_training': False,
                },
            },
            200,
        ),
        (
            {
                'id': 2,
                'alias': 'with_breaks',
                'description': 'training with its own breaks inside',
                'revision_id': '2020-11-16T11:10:00.000000 +0000',
                'properties': {
                    'distribute_breaks_inside': False,
                    'is_training': True,
                },
            },
            200,
        ),
    ],
)
async def test_base(
        taxi_workforce_management_web,
        web_context,
        tst_request,
        expected_status,
):
    res = await taxi_workforce_management_web.post(
        MODIFY_URI, json=tst_request, headers=HEADERS,
    )
    assert res.status == expected_status

    if expected_status > 200:
        return

    data = await res.json()

    for key_to_pop in ('revision_id', 'id'):
        assert data.pop(key_to_pop)
        tst_request.pop(key_to_pop, None)
    assert data == tst_request


@pytest.mark.pgsql('workforce_management', files=['simple_shift_events.sql'])
@pytest.mark.parametrize(
    'tst_request, expected_status,',
    [
        ({'id': 1}, 400),
        ({'id': 1, 'revision_id': '2020-11-16T11:11:00.000000 +0000'}, 409),
        ({'id': 1, 'revision_id': '2020-11-16T11:10:00.000000 +0000'}, 200),
    ],
)
async def test_delete(
        taxi_workforce_management_web,
        web_context,
        tst_request,
        expected_status,
):
    res = await taxi_workforce_management_web.post(
        DELETE_URI, json=tst_request, headers=HEADERS,
    )
    assert res.status == expected_status
    success = True
    if expected_status > 200:
        success = False

    res = await taxi_workforce_management_web.get(URI, json=tst_request)
    assert res.status == 200

    data = await res.json()

    found = any(
        [
            shift_events['id'] == tst_request['id']
            for shift_events in data['shift_events']
        ],
    )

    assert not found or not success

    operators_db = db.OperatorsRepo(web_context)
    master_pool = await operators_db.master
    async with master_pool.acquire() as conn:
        res = await operators_db.get_deleted_shift_events(
            conn, ids=[tst_request['id']],
        )
        if success:
            assert res
        else:
            assert not res
