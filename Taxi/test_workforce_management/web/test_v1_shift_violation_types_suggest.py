import pytest

URI = 'v1/shift-violation-types/suggest'
HEADERS = {'X-Yandex-UID': 'uid1'}

SUGGEST_ITEMS = [
    'working_on_break',
    'late',
    'absent',
    'not_working',
    'not_working_break',
    'late_from_break',
    'shift_paused',
    'overtime',
]


@pytest.mark.parametrize(
    'tst_request, expected_status, expected_res', [({}, 200, SUGGEST_ITEMS)],
)
async def test_suggest(
        taxi_workforce_management_web,
        web_context,
        tst_request,
        expected_status,
        expected_res,
):
    res = await taxi_workforce_management_web.get(
        URI, json=tst_request, headers=HEADERS,
    )
    assert res.status == expected_status

    if expected_status > 200:
        return

    data = await res.json()
    assert flatten_response(data) == expected_res


def flatten_response(data):
    return [row['name'] for row in data['shift_violation_types']]
