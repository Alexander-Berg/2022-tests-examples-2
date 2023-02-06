import pytest

URI = 'v1/allowed-period'
DELETE_URI = 'v1/allowed-period/delete'
MODIFY_URI = 'v1/allowed-period/modify'
HEADERS = {'X-Yandex-UID': 'uid1', 'X-WFM-Domain': 'taxi'}


@pytest.mark.pgsql('workforce_management', files=['allowed_periods.sql'])
@pytest.mark.parametrize(
    'tst_request, expected_status, headers_override',
    [
        (
            {
                'comment': 'active period',
                'datetime_from': '2020-01-01T03:00:00+03:00',
            },
            400,
            None,
        ),
        (
            {
                'id': 1,
                'comment': 'wow, new comment',
                'datetime_from': '2020-01-01T03:00:00+03:00',
                'revision_id': '2020-10-22T12:00:00.000000 +0000',
            },
            200,
            None,
        ),
        (
            {
                'id': 1,
                'comment': 'wow, new comment',
                'datetime_from': '2020-01-01T03:00:00+03:00',
                'revision_id': '1111-11-11T11:11:11.111111 +1111',
            },
            409,
            None,
        ),
    ],
)
async def test_base(
        taxi_workforce_management_web,
        tst_request,
        expected_status,
        headers_override,
        mock_effrat_employees,
):
    headers = {**HEADERS, **(headers_override or {})}
    res = await taxi_workforce_management_web.post(
        MODIFY_URI, json=tst_request, headers=headers,
    )
    assert res.status == expected_status

    if expected_status > 200:
        return
    res = await taxi_workforce_management_web.get(URI, headers=headers)
    data = await res.json()

    for key_to_pop in ('revision_id', 'id'):
        assert data.pop(key_to_pop)
        tst_request.pop(key_to_pop, None)
    assert data == tst_request


@pytest.mark.pgsql('workforce_management', files=['allowed_periods.sql'])
@pytest.mark.parametrize(
    'tst_request, expected_status,',
    [
        ({'id': 1}, 400),
        ({'id': 1, 'revision_id': '2020-11-16T11:11:00.000000 +0000'}, 409),
        ({'id': 1, 'revision_id': '2020-10-22T12:00:00.000000 +0000'}, 200),
    ],
)
async def test_delete(
        taxi_workforce_management_web, tst_request, expected_status,
):
    res = await taxi_workforce_management_web.post(
        DELETE_URI, json=tst_request, headers=HEADERS,
    )
    assert res.status == expected_status
    success = True
    if expected_status > 200:
        success = False

    res = await taxi_workforce_management_web.get(URI, headers=HEADERS)
    assert res.status == 200

    data = await res.json()

    assert not data or not success
