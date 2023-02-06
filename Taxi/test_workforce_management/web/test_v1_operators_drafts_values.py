import pytest


URI = 'v1/operators/drafts/values'
HEADERS = {'X-Yandex-UID': 'uid1', 'X-WFM-Domain': 'taxi'}
UDID_1_DRAFT = {
    'approvals_draft_id': '1',
    'breaks': [],
    'duration_minutes': 30,
    'events': [],
    'id': 1,
    'shift_id': 1,
    'start': '2020-07-26T15:00:00+03:00',
    'status': 'need_approval',
}
UDID_2_DRAFT = {
    'approvals_draft_id': '2',
    'breaks': [],
    'duration_minutes': 600,
    'events': [],
    'id': 2,
    'shift_id': 3,
    'start': '2020-07-26T21:00:00+03:00',
    'status': 'approved',
}


@pytest.mark.pgsql(
    'workforce_management',
    files=[
        'simple_operators.sql',
        'simple_shifts.sql',
        'allowed_periods.sql',
        'simple_shifts_drafts.sql',
    ],
)
@pytest.mark.parametrize(
    'tst_request, expected_status, expected_drafts',
    [
        pytest.param(
            {
                'skill': 'tatarin',
                'limit': 10,
                'offset': 0,
                'period_filter': {
                    'period_filter_type': 'intersects',
                    'datetime_from': '2020-01-01T00:00:00Z',
                    'datetime_to': '2023-01-01T00:00:00Z',
                },
            },
            200,
            {'uid1': [UDID_1_DRAFT], 'uid2': [UDID_2_DRAFT]},
            id='request_without_additional_filter',
        ),
        pytest.param(
            {
                'skill': 'tatarin',
                'limit': 10,
                'offset': 0,
                'statuses': ['need_approval'],
                'period_filter': {
                    'period_filter_type': 'intersects',
                    'datetime_from': '2020-01-01T00:00:00Z',
                    'datetime_to': '2023-01-01T00:00:00Z',
                },
            },
            200,
            {'uid1': [UDID_1_DRAFT], 'uid2': []},
            id='request_status_filter',
        ),
        pytest.param(
            {
                'skill': 'tatarin',
                'limit': 10,
                'offset': 0,
                'period_filter': {
                    'period_filter_type': 'intersects',
                    'datetime_from': '2020-01-01T00:00:00Z',
                    'datetime_to': '2020-07-26T17:00:00Z',
                },
            },
            200,
            {'uid1': [UDID_1_DRAFT], 'uid2': []},
            id='request_without_additional_filter_lower_bounds',
        ),
    ],
)
async def test_base(
        taxi_workforce_management_web,
        web_context,
        tst_request,
        expected_status,
        expected_drafts,
        mock_effrat_employees,
):
    mock_effrat_employees()
    res = await taxi_workforce_management_web.post(
        URI, json=tst_request, headers=HEADERS,
    )
    assert res.status == expected_status
    success = res.status == 200
    if not success:
        return
    data = await res.json()
    for record, drafts in zip(data['records'], expected_drafts.items()):
        uid, expected_draft = drafts
        assert record['operator']['yandex_uid'] == uid
        assert record['drafts'] == expected_draft
