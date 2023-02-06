import pytest

from hiring_tariffs.internal import mass_fix_subscriptions_periods

PASTE_FILE = 'paste_responses.json'


class Context:
    def __init__(self):
        self.data = 'initial value'

    def set_data(self, data):
        self.data = data


@pytest.fixture
def _paste_context():
    return Context()


@pytest.fixture
def _mock_paste(mockserver, _paste_context):
    class Mocks:
        @mockserver.handler('/download')
        @staticmethod
        async def paste_handler(request):
            return mockserver.make_response(_paste_context.data)

    return Mocks()


@pytest.fixture
def _fetch_table(pgsql):
    async def _fetch(table: str):
        with pgsql['hiring_misc'].cursor() as cursor:
            cursor.execute(f'SELECT * FROM "hiring_tariffs"."{table}"')
            raw_events = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, raw_event)) for raw_event in raw_events]

    return _fetch


def _check_result(task, subs, periods, updates):
    mapper = {
        'subs': (subs, 'id'),
        'periods': (periods, 'id'),
        'updates': (updates, 'subscription_id'),
    }
    for key in ('subs', 'periods', 'updates'):
        if task.get(key):
            check_array = mapper[key][0]
            check_key = mapper[key][1]
            for item in task[key]:
                assert item.items() <= check_array[item[check_key]].items()


@pytest.mark.parametrize(
    'case, request_name, error',
    [
        ('valid', 'TWO_SUBS', None),
        (
            'invalid',
            'MISSING_REQUIRED_FIELDS',
            mass_fix_subscriptions_periods.MissingRequiredFields,
        ),
        (
            'invalid',
            'MISSING_REQUIRED_VALUES',
            mass_fix_subscriptions_periods.EmptyValue,
        ),
        (
            'invalid',
            'EXCESSIVE_FIELDS',
            mass_fix_subscriptions_periods.ExcessiveFields,
        ),
        (
            'invalid',
            'NON_EXISTENT_SUB',
            mass_fix_subscriptions_periods.NonExistentSub,
        ),
        (
            'invalid',
            'NON_EXISTENT_PERIOD',
            mass_fix_subscriptions_periods.NonExistentPeriod,
        ),
        (
            'invalid',
            'NO_UPDATE_REQUIRED',
            mass_fix_subscriptions_periods.NoUpdateRequired,
        ),
        (
            'invalid',
            'INVALID_DATE',
            mass_fix_subscriptions_periods.InvalidDate,
        ),
        (
            'invalid',
            'INVALID_STARTS_AT_IN_UPDATE',
            mass_fix_subscriptions_periods.InvalidDate,
        ),
        (
            'invalid',
            'INVALID_STARTS_AT_IN_PERIOD',
            mass_fix_subscriptions_periods.InvalidDate,
        ),
        (
            'invalid',
            'INVALID_COMMENT',
            mass_fix_subscriptions_periods.InvalidComment,
        ),
    ],
)
async def test_mass_create_users(
        _paste_context,
        _mock_paste,
        cron_context,
        load_json,
        _fetch_table,
        case,
        request_name,
        error,
):
    task = load_json(PASTE_FILE)[case][request_name]
    _paste_context.set_data(task['text'])
    if error:
        valid_error = False
        try:
            await mass_fix_subscriptions_periods.run(
                cron_context, '$mockserver/download',
            )
        except error:
            valid_error = True
        assert valid_error
    else:
        await mass_fix_subscriptions_periods.run(
            cron_context, '$mockserver/download',
        )

    raw_periods = await _fetch_table('subscriptions_periods')
    raw_updates = await _fetch_table('subscriptions_updates')
    subs = {item['id']: item for item in await _fetch_table('subscriptions')}
    periods = {}
    for period in raw_periods:
        period.update(
            {
                'starts_at': str(period['starts_at']),
                'ends_at': str(period['ends_at']),
            },
        )
        periods[period['id']] = period
    updates = {}
    for update in raw_updates:
        update['data'].update(
            {
                'starts_at': str(update['data']['starts_at']),
                'ends_at': str(update['data']['ends_at']),
            },
        )
        updates[update['subscription_id']] = update
    _check_result(task, subs, periods, updates)
