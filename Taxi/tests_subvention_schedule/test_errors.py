import pytest


@pytest.mark.now('2021-02-01T12:00:00+0300')
@pytest.mark.parametrize(
    'select_throw, match_throw, expected_code',
    [
        (None, None, 200),
        (500, None, 500),
        (None, 500, 500),
        (429, None, 429),
        (None, 429, 429),
    ],
)
async def test_schedule(
        taxi_subvention_schedule,
        mockserver,
        load_json,
        select_throw,
        match_throw,
        expected_code,
):
    @mockserver.json_handler('/billing-subventions-x/v2/rules/select')
    async def _mock_rules_select(request_data):
        if select_throw:
            return mockserver.make_response(status=select_throw)
        return load_json('simple_rule.json')

    @mockserver.json_handler('/billing-subventions-x/v2/rules/match')
    async def _mock_match(request_data):
        if match_throw:
            return mockserver.make_response(status=match_throw)
        return {'matches': []}

    request = {
        'types': ['single_ride'],
        'ignored_restrictions': [],
        'time_range': {
            'from': '2021-02-01T12:00:00+0300',
            'to': '2021-02-06T12:00:00+0300',
        },
        'activity_points': 12,
        'branding': {'has_lightbox': False, 'has_sticker': False},
        'tags': [],
        'tariff_classes': ['eco'],
        'zones': ['moscow'],
    }

    response = await taxi_subvention_schedule.post(
        '/internal/subvention-schedule/v1/schedule', json=request,
    )

    assert response.status_code == expected_code


@pytest.mark.now('2021-02-01T12:00:00+0300')
async def test_mixed_timezones_error(taxi_subvention_schedule):
    request = {
        'types': ['single_ride'],
        'ignored_restrictions': [],
        'time_range': {
            'from': '2021-02-01T12:00:00+0300',
            'to': '2021-02-06T12:00:00+0300',
        },
        'activity_points': 12,
        'branding': {'has_lightbox': False, 'has_sticker': False},
        'tags': [],
        'tariff_classes': ['eco'],
        'zones': ['moscow', 'almaty'],
    }

    response = await taxi_subvention_schedule.post(
        '/internal/subvention-schedule/v1/schedule', json=request,
    )

    assert response.status_code == 400
