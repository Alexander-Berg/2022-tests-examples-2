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
def validate_tariff_mock(patch):
    @patch('taxi_corp_admin.api.common.tariffs.validate_tariff')
    async def _validate_tariff(
            request, tariff, countries, areas, series_id=None,
    ):
        return []

    return _validate_tariff


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
        ['tariffs_1.csv'],
        ['tariffs_1.csv', 'tariff_plans_1.csv', 'something_else.jpg'],
    ],
    indirect=['startrack'],
)
@pytest.mark.parametrize('endpoint', ['dry-run', 'run'])
async def test_ok(
        taxi_corp_admin_client,
        validate_tariff_mock,
        startrack,
        endpoint,
        ticket_checker_mock,
        territories_mock,
):
    response = await taxi_corp_admin_client.post(
        f'/v1/tariffs/import/{endpoint}', json={'ticket': 'TAXIRATE-1'},
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
            'attachment_id': hash('tariffs_1.csv'),
            'attachment_name': 'tariffs_1.csv',
        },
    ]

    assert len(validate_tariff_mock.calls) == 1

    assert response.status == 200
    assert await response.json() == {
        'name': 'tariffs_1.csv',
        'tariffs': [{'home_zone': 'obninsk', 'name': 'TEST_obninsk'}],
        'errors': [],
    }
    assert len(ticket_checker_mock.calls) == 1


@pytest.mark.parametrize(
    'startrack', [['tariffs_1.csv']], indirect=['startrack'],
)
@pytest.mark.parametrize('endpoint', ['dry-run', 'run'])
async def test_fail_attachment_updated(
        taxi_corp_admin_client,
        validate_tariff_mock,
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
        f'/v1/tariffs/import/{endpoint}', json={'ticket': 'TAXIRATE-1'},
    )

    assert len(_last_approved_at.calls) == 1
    assert not validate_tariff_mock.calls

    assert response.status == 400
    assert await response.json() == {
        'code': 'invalid-input',
        'details': {'ticket': ['ticket attachments updated after approve']},
        'message': 'Invalid input',
        'status': 'error',
    }


@pytest.mark.parametrize(
    'startrack',
    [[], ['tariffs_1.csv', 'tariffs_2.csv']],
    indirect=['startrack'],
)
@pytest.mark.parametrize('endpoint', ['dry-run', 'run'])
async def test_fail_attacments(
        taxi_corp_admin_client, validate_tariff_mock, startrack, endpoint,
):
    response = await taxi_corp_admin_client.post(
        f'/v1/tariffs/import/{endpoint}', json={'ticket': 'TAXIRATE-1'},
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

    assert not validate_tariff_mock.calls

    assert response.status == 400
    assert await response.json() == {
        'code': 'invalid-input',
        'details': {
            'ticket': [
                'ticket must contains one ^tariffs[\\-\\w]*\\.csv$ file',
            ],
        },
        'message': 'Invalid input',
        'status': 'error',
    }


@pytest.mark.parametrize(
    'startrack', [['tariffs_2.csv']], indirect=['startrack'],
)
@pytest.mark.parametrize('endpoint', ['dry-run', 'run'])
async def test_dry_run_fail_schema(
        taxi_corp_admin_client,
        validate_tariff_mock,
        startrack,
        endpoint,
        ticket_checker_mock,
):
    response = await taxi_corp_admin_client.post(
        f'/v1/tariffs/import/{endpoint}', json={'ticket': 'TAXIRATE-1'},
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

    assert not validate_tariff_mock.calls

    assert response.status == 200
    response = await response.json()
    assert response['name'] == 'tariffs_2.csv'
    assert response['tariffs'] == []
    assert len(response['errors']) == 1
    assert 'row 2 has errors' in response['errors'][0]


@pytest.fixture
def create_id_mock(patch):
    gen = (x for x in range(1, 10))

    @patch('taxi_corp_admin.api.handlers.v1.tariffs_import.create_id')
    def _create_id():
        return f'_id_{next(gen)}'


@pytest.fixture
def create_interval_id_mock(request, patch):
    gen = (x for x in range(1, 10))

    @patch(
        'taxi_corp_admin.api.common.tariffs_import.TariffsAttachment.'
        '_create_id',
    )
    def _create_id():
        return f'interval_id_{next(gen)}'


@pytest.fixture
def create_series_id_mock(request, patch):
    gen = (x for x in range(1, 10))

    @patch('taxi_corp_admin.api.handlers.v1.tariffs_import.create_series_id')
    def _create_id():
        return f'tariff_series_id_{next(gen)}'


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'startrack', [['tariffs_1.csv']], indirect=['startrack'],
)
async def test_import_ok(
        taxi_corp_admin_client,
        db,
        load_json,
        validate_tariff_mock,
        ticket_checker_mock,
        create_id_mock,
        create_series_id_mock,
        create_interval_id_mock,
        territories_mock,
        startrack,
):
    response = await taxi_corp_admin_client.post(
        '/v1/tariffs/import/run', json={'ticket': 'TAXIRATE-1'},
    )

    assert response.status == 200, await response.json()
    assert await db.corp_tariffs.count() == 1
    for name in ['TEST_obninsk']:
        db_tariff = await db.corp_tariffs.find_one(
            {'name': name, 'date_to': None},
        )
        expected_tariff = load_json(f'{name}.json')
        expected_tariff['date_from'] = NOW
        expected_tariff['created'] = NOW
        expected_tariff['updated'] = NOW
        assert db_tariff == expected_tariff


@pytest.mark.parametrize(
    'startrack', [['tariffs_2.csv']], indirect=['startrack'],
)
async def test_import_fail(
        taxi_corp_admin_client,
        db,
        validate_tariff_mock,
        ticket_checker_mock,
        startrack,
):
    response = await taxi_corp_admin_client.post(
        '/v1/tariffs/import/run', json={'ticket': 'TAXIRATE-1'},
    )

    assert response.status == 200, await response.json()
    assert not await db.corp_tariffs.count()


@pytest.mark.parametrize(
    'startrack', [['tariffs_3.csv']], indirect=['startrack'],
)
async def test_import_fail_for_day_type(
        taxi_corp_admin_client,
        db,
        validate_tariff_mock,
        ticket_checker_mock,
        startrack,
):
    response = await taxi_corp_admin_client.post(
        '/v1/tariffs/import/run', json={'ticket': 'TAXIRATE-1'},
    )

    assert response.status == 200, await response.json()
    assert not await db.corp_tariffs.count()
