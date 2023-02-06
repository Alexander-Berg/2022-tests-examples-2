import pytest

from workforce_management.storage.postgresql import absence as absences_repo


URI = 'v1/absence-types/values'
DELETE_URI = 'v1/absence-types/delete'
MODIFY_URI = 'v1/absence-types/modify'
HEADERS = {'X-Yandex-UID': 'uid1', 'X-WFM-Domain': 'taxi'}


def pop_not_modified_fields(provided_data, result):
    return {
        key: value for key, value in result.items() if key in provided_data
    }


@pytest.mark.pgsql('workforce_management', files=['simple_absence_types.sql'])
@pytest.mark.parametrize(
    'tst_request, expected_status,',
    [
        (
            {'alias': 'new_absence_types', 'description': 'new description'},
            200,
        ),
        (
            {
                'id': 1,
                'description': 'change existing description',
                'revision_id': '2020-08-25T21:00:00.000000 +0000',
            },
            409,
        ),
        (
            {
                'id': 1,
                'description': 'change existing description',
                'revision_id': '2020-10-22T12:00:00.000000 +0000',
            },
            200,
        ),
        (
            {
                'alias': 'new_absence_type_color',
                'description': 'new white color',
                'color_code': '000000',
            },
            200,
        ),
    ],
)
async def test_modify(
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
    for field_to_pop in ('revision_id', 'id'):
        data.pop(field_to_pop)
        tst_request.pop(field_to_pop, None)
    data = pop_not_modified_fields(tst_request, data)
    assert data == tst_request


@pytest.mark.pgsql('workforce_management', files=['simple_absence_types.sql'])
@pytest.mark.parametrize(
    'tst_request, expected_status,',
    [
        ({'id': 1}, 400),
        ({'id': 1, 'revision_id': '2020-08-25T21:00:00.000000 +0000'}, 409),
        ({'id': 1, 'revision_id': '2020-10-22T12:00:00.000000 +0000'}, 200),
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
    await taxi_workforce_management_web.invalidate_caches()
    res = await taxi_workforce_management_web.get(URI, json=tst_request)
    assert res.status == 200

    data = await res.json()

    found = any(
        [
            absence_types['id'] == tst_request['id']
            for absence_types in data['absence_types']
        ],
    )

    assert not found or not success

    absences_db = absences_repo.AbsencesRepo(web_context)
    master_pool = await absences_db.master
    async with master_pool.acquire() as conn:
        res = await absences_db.get_deleted_absence_types(
            conn, ids=[tst_request['id']],
        )
        if success:
            assert res
        else:
            assert not res


@pytest.mark.config(WORKFORCE_MANAGEMENT_DOMAIN_FILTER_ENABLED=True)
@pytest.mark.pgsql('workforce_management', files=['simple_absence_types.sql'])
@pytest.mark.parametrize(
    'headers, expected_len',
    [({'X-WFM-Domain': 'taxi'}, 3), (None, 0), ({'X-WFM-Domain': 'eda'}, 0)],
)
async def test_get(taxi_workforce_management_web, headers, expected_len):
    res = await taxi_workforce_management_web.get(URI, headers=headers)
    assert res.status == 200

    data = await res.json()

    assert len(data['absence_types']) == expected_len
