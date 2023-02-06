import pytest


URI = 'v1/operators/check'


@pytest.mark.pgsql('workforce_management', files=['simple_operators.sql'])
@pytest.mark.parametrize(
    'tst_request, expected_status, expected_response',
    [
        (
            {'telegram': 'vasya_iz_derevni'},
            200,
            {'state': 'ready', 'yandex_uid': 'uid2', 'domain': 'taxi'},
        ),
        ({'telegram': 'damir'}, 404, None),
        ({'telegram': None}, 400, None),
        ({'telegram': 'Dota2Lover'}, 404, None),
    ],
)
async def test_operators_check(
        taxi_workforce_management_web,
        web_context,
        tst_request,
        expected_status,
        expected_response,
):
    res = await taxi_workforce_management_web.post(URI, json=tst_request)
    assert res.status == expected_status
    if res.status > 200:
        return

    assert await res.json() == expected_response
