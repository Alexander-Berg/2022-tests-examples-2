import pytest

from . import utils

DRAFT_HEADERS = {
    'X-YaTaxi-Draft-Author': 'vdovkin',
    'X-YaTaxi-Draft-Tickets': 'TAXI-1,TAXI-2',
}


@pytest.mark.pgsql('driver_promocodes', files=['series.sql'])
@pytest.mark.now('2020-06-01T12:00:00+0300')
@pytest.mark.parametrize(
    'request_create,response_create,response_list_after,'
    'response_check,is_good',
    [
        (
            'request_create_ok.json',
            'response_create.json',
            'response_list_after.json',
            'response_create_check.json',
            True,
        ),
        ('request_create_bad.json', None, None, None, False),
        ('request_create_unknown_tariff.json', None, None, None, False),
    ],
)
async def test_driver_promocodes_series(
        taxi_driver_promocodes,
        load_json,
        request_create,
        response_create,
        response_list_after,
        response_check,
        is_good,
):
    response = await taxi_driver_promocodes.post(
        'admin/v1/series/check',
        json=load_json(request_create),
        headers=DRAFT_HEADERS,
    )
    assert response.status_code == (200 if is_good else 400)
    if is_good:
        assert response.json() == load_json(response_check)

    response = await taxi_driver_promocodes.post(
        'admin/v1/series',
        json=load_json(request_create),
        headers=DRAFT_HEADERS,
    )
    assert response.status_code == (200 if is_good else 400)

    if is_good:
        assert utils.remove_not_testable(
            response.json(),
        ) == utils.remove_not_testable(load_json(response_create))

    if response_list_after:
        response = await taxi_driver_promocodes.get(
            'admin/v1/series/list', params={},
        )
        assert utils.remove_not_testable_series(
            response.json(),
        ) == utils.remove_not_testable_series(load_json(response_list_after))
