# pylint:disable=redefined-outer-name,invalid-name

import datetime
from unittest import mock

import pytest

from taxi.util import dates

NOW = datetime.datetime.utcnow().replace(microsecond=0)
ATTACHED_AT = '2019-01-01T01:02:03.004+0000'


@pytest.fixture
def startrack(request, load_binary, patch):

    attachments = [
        {'id': hash(name), 'name': name, 'createdAt': ATTACHED_AT}
        for name in request.param
    ]

    @patch('taxi.clients.startrack.StartrackAPIClient.get_all_attachments')
    async def _get_all_attachments(ticket, log_extra=None):
        return attachments

    @patch('taxi.clients.startrack.StartrackAPIClient.get_attachment_content')
    async def _get_attachment_content(
            ticket, attachment_id, attachment_name, log_extra=None,
    ):
        for att in attachments:
            if att['name'] == attachment_name and att['id'] == attachment_id:
                return load_binary(att['name'])

    return mock.Mock(
        names=request.param,
        get_all_attachments=_get_all_attachments,
        get_attachment_content=_get_attachment_content,
    )


@pytest.fixture
def validate_tariff_plan_mock(patch):
    @patch('taxi_corp_admin.api.common.tariff_plans.validate_tariff_plan')
    async def _validate_tariff_plan(request, tariff, series_id=None):
        return []

    return _validate_tariff_plan


@pytest.fixture
def ticket_checker_mock(patch):
    @patch('taxi.util.audit.TicketChecker.last_approved_at')
    async def _last_approved_at(*args, **kwargs):
        return dates.parse_timestring(ATTACHED_AT) + datetime.timedelta(
            seconds=1,
        )

    return _last_approved_at


@pytest.mark.parametrize(
    'startrack',
    [
        ['tariff_plans_1.csv'],
        ['tariff_plans_1.csv', 'tariffs_1.csv', 'something_else.jpg'],
    ],
    indirect=['startrack'],
)
@pytest.mark.parametrize('endpoint', ['dry-run', 'run'])
async def test_ok(
        taxi_corp_admin_client,
        validate_tariff_plan_mock,
        startrack,
        endpoint,
        ticket_checker_mock,
):
    response = await taxi_corp_admin_client.post(
        f'/v1/tariff-plans/import/{endpoint}', json={'ticket': 'TAXIRATE-1'},
    )

    get_all_attachments_calls = startrack.get_all_attachments.calls
    assert len(get_all_attachments_calls) == 1
    assert get_all_attachments_calls[0].pop('log_extra')
    assert get_all_attachments_calls == [{'ticket': 'TAXIRATE-1'}]

    get_attachment_calls = startrack.get_attachment_content.calls
    assert len(get_attachment_calls) == 1
    assert get_attachment_calls[0].pop('log_extra')
    assert get_attachment_calls == [
        {
            'ticket': 'TAXIRATE-1',
            'attachment_id': hash('tariff_plans_1.csv'),
            'attachment_name': 'tariff_plans_1.csv',
        },
    ]

    assert len(validate_tariff_plan_mock.calls) == 2

    assert response.status == 200
    assert await response.json() == {
        'name': 'tariff_plans_1.csv',
        'tariff_plans': [{'name': 'TEST_1'}, {'name': 'TEST_2'}],
        'errors': [],
    }


@pytest.mark.parametrize(
    'startrack',
    [[], ['tariff_plans_1.csv', 'tariff_plans_2.csv']],
    indirect=['startrack'],
)
@pytest.mark.parametrize('endpoint', ['dry-run', 'run'])
async def test_fail_attacments(
        taxi_corp_admin_client, validate_tariff_plan_mock, startrack, endpoint,
):
    response = await taxi_corp_admin_client.post(
        f'/v1/tariff-plans/import/{endpoint}', json={'ticket': 'TAXIRATE-1'},
    )

    get_all_attachments_calls = startrack.get_all_attachments.calls
    assert len(get_all_attachments_calls) == 1
    assert get_all_attachments_calls[0].pop('log_extra')
    assert get_all_attachments_calls == [{'ticket': 'TAXIRATE-1'}]

    get_attachment_calls = startrack.get_attachment_content.calls
    assert len(get_attachment_calls) == len(startrack.names)
    for i, name in enumerate(startrack.names):
        assert get_attachment_calls[i].pop('log_extra')
        assert get_attachment_calls[i] == {
            'ticket': 'TAXIRATE-1',
            'attachment_id': hash(name),
            'attachment_name': name,
        }

    assert not validate_tariff_plan_mock.calls

    assert response.status == 400
    assert await response.json() == {
        'code': 'invalid-input',
        'details': {
            'ticket': [
                'ticket must contains one ^tariff_plans[\\-\\w]*\\.csv$ file',
            ],
        },
        'message': 'Invalid input',
        'status': 'error',
    }


@pytest.mark.parametrize(
    'startrack', [['tariff_plans_1.csv']], indirect=['startrack'],
)
@pytest.mark.parametrize('endpoint', ['dry-run', 'run'])
async def test_fail_attachment_updated(
        taxi_corp_admin_client,
        validate_tariff_plan_mock,
        startrack,
        endpoint,
        patch,
):
    @patch('taxi.util.audit.TicketChecker.last_approved_at')
    async def _last_approved_at(*args, **kwargs):
        return dates.parse_timestring(ATTACHED_AT) - datetime.timedelta(
            seconds=1,
        )

    response = await taxi_corp_admin_client.post(
        f'/v1/tariff-plans/import/{endpoint}', json={'ticket': 'TAXIRATE-1'},
    )

    assert len(_last_approved_at.calls) == 1
    assert not validate_tariff_plan_mock.calls

    assert response.status == 400
    assert await response.json() == {
        'code': 'invalid-input',
        'details': {'ticket': ['ticket attachments updated after approve']},
        'message': 'Invalid input',
        'status': 'error',
    }


@pytest.mark.parametrize(
    'startrack', [['tariff_plans_2.csv']], indirect=['startrack'],
)
@pytest.mark.parametrize('endpoint', ['dry-run', 'run'])
async def test_fail_schema(
        taxi_corp_admin_client,
        validate_tariff_plan_mock,
        startrack,
        endpoint,
        ticket_checker_mock,
):
    response = await taxi_corp_admin_client.post(
        f'/v1/tariff-plans/import/{endpoint}', json={'ticket': 'TAXIRATE-1'},
    )

    get_all_attachments_calls = startrack.get_all_attachments.calls
    assert len(get_all_attachments_calls) == 1
    assert get_all_attachments_calls[0].pop('log_extra')
    assert get_all_attachments_calls == [{'ticket': 'TAXIRATE-1'}]

    get_attachment_calls = startrack.get_attachment_content.calls
    assert len(get_attachment_calls) == len(startrack.names)
    for i, name in enumerate(startrack.names):
        assert get_attachment_calls[i].pop('log_extra')
        assert get_attachment_calls[i] == {
            'ticket': 'TAXIRATE-1',
            'attachment_id': hash(name),
            'attachment_name': name,
        }

    assert not validate_tariff_plan_mock.calls

    assert response.status == 200
    response = await response.json()
    assert response['name'] == 'tariff_plans_2.csv'
    assert response['tariff_plans'] == []
    assert len(response['errors']) == 1
    assert 'row 2 has errors' in response['errors'][0]


@pytest.mark.parametrize(
    'startrack', [['tariff_plans_3.csv']], indirect=['startrack'],
)
@pytest.mark.parametrize('endpoint', ['dry-run', 'run'])
async def test_fail_parse(
        taxi_corp_admin_client,
        validate_tariff_plan_mock,
        startrack,
        endpoint,
        ticket_checker_mock,
):
    response = await taxi_corp_admin_client.post(
        f'/v1/tariff-plans/import/{endpoint}', json={'ticket': 'TAXIRATE-1'},
    )

    get_all_attachments_calls = startrack.get_all_attachments.calls
    assert len(get_all_attachments_calls) == 1
    assert get_all_attachments_calls[0].pop('log_extra')
    assert get_all_attachments_calls == [{'ticket': 'TAXIRATE-1'}]

    get_attachment_calls = startrack.get_attachment_content.calls
    assert len(get_attachment_calls) == len(startrack.names)
    for i, name in enumerate(startrack.names):
        assert get_attachment_calls[i].pop('log_extra')
        assert get_attachment_calls[i] == {
            'ticket': 'TAXIRATE-1',
            'attachment_id': hash(name),
            'attachment_name': name,
        }

    assert len(validate_tariff_plan_mock.calls) == 1

    assert response.status == 200
    response = await response.json()
    assert response['name'] == 'tariff_plans_3.csv'
    assert response['tariff_plans'] == [{'name': 'TEST_1'}]
    assert sorted(response['errors']) == sorted(
        [
            f'tariff plan TEST_1 has different values for field {field}'
            for field in [
                'country',
                'disable_tariff_fallback',
                'disable_fixed_price',
            ]
        ],
    )


@pytest.fixture
def create_id_mock(request, patch):
    gen = iter(request.param)

    @patch('taxi_corp_admin.api.handlers.v1.tariff_plans_import.create_id')
    def _create_id():
        return next(gen)


@pytest.fixture
def create_series_id_mock(request, patch):
    gen = iter(request.param)

    @patch(
        'taxi_corp_admin.api.handlers.v1.tariff_plans_import.create_series_id',
    )
    def _create_id():
        return next(gen)


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    ['startrack', 'ok', 'create_id_mock', 'create_series_id_mock'],
    [
        (
            ['tariff_plans_1.csv'],
            True,
            ['_id_1', '_id_2'],
            ['tariff_plan_series_id_1', 'tariff_plan_series_id_2'],
        ),
        (['tariff_plans_2.csv'], False, [], []),
        (['tariff_plans_3.csv'], False, [], []),
    ],
    indirect=['startrack', 'create_id_mock', 'create_series_id_mock'],
)
async def test_import(
        taxi_corp_admin_client,
        db,
        load_json,
        validate_tariff_plan_mock,
        startrack,
        create_id_mock,
        create_series_id_mock,
        ok,
        ticket_checker_mock,
):
    response = await taxi_corp_admin_client.post(
        '/v1/tariff-plans/import/run', json={'ticket': 'TAXIRATE-1'},
    )

    assert response.status == 200
    if ok:
        assert await db.corp_tariffs.count() == 4
        for name in ['TEST_1', 'TEST_2']:
            db_tariff_plan = await db.corp_tariff_plans.find_one(
                {'name': name, 'date_to': None},
            )
            expected_tariff_plan = load_json(f'{name}.json')
            expected_tariff_plan['date_from'] = NOW
            expected_tariff_plan['created'] = NOW
            expected_tariff_plan['updated'] = NOW
            assert db_tariff_plan == expected_tariff_plan
    else:
        assert not await db.corp_tariff_plans.count()
