# pylint: disable=unused-variable
import pytest

from testsuite.utils import http

from fleet_rent.generated.cron import cron_context as context
from fleet_rent.generated.cron import run_cron


@pytest.fixture(name='fleet_parks_v1_parks_list')
def _v1_parks_list(mock_fleet_parks):
    @mock_fleet_parks('/v1/parks/list')
    async def v1_parks_list(request: http.Request):
        return {
            'parks': [
                {
                    'id': 'park_id',
                    'login': 'park_login',
                    'name': 'Sea',
                    'is_active': True,
                    'city_id': 'Gotham',
                    'locale': 'ru',
                    'is_billing_enabled': True,
                    'is_franchising_enabled': True,
                    'country_id': 'RUR',
                    'demo_mode': False,
                    'provider_config': {'type': 'none', 'clid': '555'},
                    'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
                },
            ],
        }


@pytest.mark.now('2020-01-20T15:30:00+00:00')
@pytest.mark.pgsql(
    'fleet_rent',
    files=['init_db_data.sql'],
    queries=(
        """INSERT INTO rent.external_debt_cancellations(
id, record_id, created_at, payment_doc_ids, created_by_json)
VALUES ('a', 'record_id1', '2020-01-20 12:12:12+00:00',
ARRAY [15::BIGINT, 17, 18],
'{"kind":"dispatcher", "passport_uid":"user_id"}');""",
    ),
)
@pytest.mark.config(
    FLEET_RENT_PARK_NOTIFICATIONS={
        'rent_url_template': '/{rent_id}/{park_id}/{serial_id}',
        'cancellation_url_template': (
            '/regular-charges/{record_id}/parks/{park_id}'
            '/edit/?cancellation_id={cancellation_id}&serial_id={serial_id}'
        ),
    },
)
@pytest.mark.translations(
    taximeter_backend_fleet_rent={
        'debt_cancellation_finished_title': {
            'ru': 'Запрос на отмену удержания обработан',
        },
        'debt_cancellation_finished_text': {'ru': 'Списание №{0}'},
    },
    tariff={
        'currency_with_sign.default': {'ru': '$VALUE$ $SIGN$$CURRENCY$'},
        'currency_sign.rub': {'ru': '₽'},
    },
    cities={'Москва': {'ru': 'Москва'}},
)
async def test_ready_case(
        load_json,
        cron_context: context.Context,
        fleet_parks_v1_parks_list,
        mock_billing_reports,
        mock_fleet_notifications,
):
    @mock_billing_reports('/v1/docs/select')
    async def _get_docs(request: http.Request):
        assert request.json == load_json('billing_reports_base_doc_req.json')
        return load_json('billing_reports_ready_case_resp.json')

    notifications = []

    @mock_fleet_notifications('/v1/notifications/create')
    async def _handle_notification(request: http.Request):
        jss = request.json
        notifications.append(jss)
        return {}

    await run_cron.main(
        ['fleet_rent.crontasks.process_cancelled_debts', '-t', '0'],
    )
    transactions = await cron_context.pg.master.fetch(
        'SELECT * FROM rent.external_debt_cancellations ORDER BY record_id;',
    )
    payment_doc_ids = [
        (t['id'], t['is_complete'], t['payment_doc_ids']) for t in transactions
    ]
    assert payment_doc_ids == [('a', True, [15, 17, 18])]
    for notif in notifications:
        del notif['request_id']
    assert notifications == [
        {
            'destinations': [{'park_id': 'park_id', 'user_id': 'user_id'}],
            'payload': {
                'entity': {
                    'type': 'fleet-rent/debt-cancellation',
                    'url': (
                        '/regular-charges/record_id1/parks'
                        '/park_id/edit/?cancellation_id=a&serial_id=1'
                    ),
                },
                'text': 'Списание №1',
                'title': 'Запрос на отмену удержания обработан',
            },
        },
    ]


@pytest.mark.now('2020-01-20T15:30:00+00:00')
@pytest.mark.pgsql(
    'fleet_rent',
    files=['init_db_data.sql'],
    queries=(
        """INSERT INTO rent.external_debt_cancellations(
id, record_id, created_at, payment_doc_ids, created_by_json)
VALUES ('d', 'record_id1', '2020-01-20 12:12:13+00:00',
ARRAY []::BIGINT[], '{"kind":"dispatcher", "passport_uid":"user_id"}');""",
    ),
)
async def test_no_docs_billing(
        load_json,
        cron_context: context.Context,
        fleet_parks_v1_parks_list,
        mock_billing_reports,
):
    @mock_billing_reports('/v1/docs/select')
    async def _get_docs(request: http.Request):
        assert request.json == load_json('billing_reports_base_doc_req.json')
        return load_json('billing_reports_no_docs_case_resp.json')

    await run_cron.main(
        ['fleet_rent.crontasks.process_cancelled_debts', '-t', '0'],
    )
    transactions = await cron_context.pg.master.fetch(
        'SELECT * FROM rent.external_debt_cancellations ORDER BY record_id;',
    )
    payment_doc_ids = [
        (t['id'], t['is_complete'], t['payment_doc_ids']) for t in transactions
    ]
    assert payment_doc_ids == [('d', True, [])]


@pytest.mark.now('2020-01-20T15:30:00+00:00')
@pytest.mark.pgsql(
    'fleet_rent',
    files=['init_db_data.sql'],
    queries=(
        """INSERT INTO rent.external_debt_cancellations(
id, record_id, created_at, payment_doc_ids, created_by_json)
VALUES ('e', 'record_id1', '2020-01-20 12:12:13+00:00',
ARRAY []::BIGINT[], '{"kind":"dispatcher", "passport_uid":"user_id"}');""",
    ),
)
async def test_no_new_docs_billing(
        load_json,
        cron_context: context.Context,
        fleet_parks_v1_parks_list,
        mock_billing_reports,
):
    @mock_billing_reports('/v1/docs/select')
    async def _get_docs(request: http.Request):
        assert request.json == load_json('billing_reports_base_doc_req.json')
        return load_json('billing_reports_no_new_docs_case_resp.json')

    await run_cron.main(
        ['fleet_rent.crontasks.process_cancelled_debts', '-t', '0'],
    )
    transactions = await cron_context.pg.master.fetch(
        'SELECT * FROM rent.external_debt_cancellations ORDER BY record_id;',
    )
    payment_doc_ids = [
        (t['id'], t['is_complete'], t['payment_doc_ids']) for t in transactions
    ]
    assert payment_doc_ids == [('e', True, [])]


@pytest.mark.now('2020-01-20T15:30:00+00:00')
@pytest.mark.pgsql(
    'fleet_rent',
    files=['init_db_data.sql'],
    queries=(
        """INSERT INTO rent.external_debt_cancellations(
id, record_id, created_at, payment_doc_ids, created_by_json)
VALUES ('f', 'record_id1', '2020-01-20 15:00:00+00:00',
ARRAY []::BIGINT[], '{"kind":"dispatcher", "passport_uid":"user_id"}');""",
    ),
)
async def test_wait_for_stq(
        load_json,
        cron_context: context.Context,
        fleet_parks_v1_parks_list,
        mock_billing_reports,
):
    await run_cron.main(
        ['fleet_rent.crontasks.process_cancelled_debts', '-t', '0'],
    )
    transactions = await cron_context.pg.master.fetch(
        'SELECT * FROM rent.external_debt_cancellations ORDER BY record_id;',
    )
    payment_doc_ids = [
        (t['id'], t['is_complete'], t['payment_doc_ids']) for t in transactions
    ]
    assert payment_doc_ids == [('f', False, [])]


@pytest.mark.now('2020-01-20T15:30:00+00:00')
@pytest.mark.pgsql(
    'fleet_rent',
    files=['init_db_data.sql'],
    queries=(
        """INSERT INTO rent.external_debt_cancellations(
id, record_id, created_at, payment_doc_ids, created_by_json)
VALUES ('b', 'record_id1', '2020-01-20 12:12:13+00:00',
ARRAY []::BIGINT[], '{"kind":"dispatcher", "passport_uid":"user_id"}');""",
    ),
)
async def test_start_in_cron(
        load_json,
        cron_context: context.Context,
        fleet_parks_v1_parks_list,
        mock_billing_reports,
        mock_billing_orders,
):
    @mock_billing_reports('/v1/docs/select')
    async def _get_docs(request: http.Request):
        assert request.json == load_json('billing_reports_base_doc_req.json')
        return load_json('billing_reports_create_cancel_case_resp.json')

    @mock_billing_orders('/v2/process/async')
    async def _v2_process_async(request: http.Request):
        assert request.json == load_json(
            'billing_orders_create_cancel_request.json',
        )
        return load_json('billing_orders_create_cancel_response.json')

    await run_cron.main(
        ['fleet_rent.crontasks.process_cancelled_debts', '-t', '0'],
    )
    transactions = await cron_context.pg.master.fetch(
        'SELECT * FROM rent.external_debt_cancellations ORDER BY record_id;',
    )
    payment_doc_ids = [
        (t['id'], t['is_complete'], t['payment_doc_ids']) for t in transactions
    ]
    assert payment_doc_ids == [('b', False, [20, 21, 22])]


@pytest.mark.now('2020-01-20T15:30:00+00:00')
@pytest.mark.pgsql(
    'fleet_rent',
    files=['init_db_data.sql'],
    queries=(
        """INSERT INTO rent.external_debt_cancellations(
id, record_id, created_at, payment_doc_ids, created_by_json)
VALUES ('b', 'record_id1', '2020-01-20 12:12:13+00:00',
ARRAY []::BIGINT[], '{"kind":"platform"}');""",
    ),
)
async def test_cancellation_by_platform(
        load_json,
        cron_context: context.Context,
        fleet_parks_v1_parks_list,
        mock_billing_reports,
        mock_billing_orders,
):
    @mock_billing_reports('/v1/docs/select')
    async def _get_docs(request: http.Request):
        assert request.json == load_json('billing_reports_base_doc_req.json')
        return load_json('billing_reports_create_cancel_case_resp.json')

    @mock_billing_orders('/v2/process/async')
    async def _v2_process_async(request: http.Request):
        assert request.json == load_json(
            'billing_orders_create_cancel_request_platform.json',
        )
        return load_json('billing_orders_create_cancel_response.json')

    await run_cron.main(
        ['fleet_rent.crontasks.process_cancelled_debts', '-t', '0'],
    )
    transactions = await cron_context.pg.master.fetch(
        'SELECT * FROM rent.external_debt_cancellations ORDER BY record_id;',
    )
    payment_doc_ids = [
        (t['id'], t['is_complete'], t['payment_doc_ids']) for t in transactions
    ]
    assert payment_doc_ids == [('b', False, [20, 21, 22])]


@pytest.mark.now('2020-01-20T15:30:00+00:00')
@pytest.mark.pgsql(
    'fleet_rent',
    files=['init_db_data.sql'],
    queries=(
        """INSERT INTO rent.external_debt_cancellations(
id, record_id, created_at, payment_doc_ids, created_by_json)
VALUES ('b', 'record_id1', '2020-01-20 12:12:13+00:00',
ARRAY []::BIGINT[], '{"kind":"dispatcher", "passport_uid":"user_id"}');""",
        """UPDATE rent.records SET start_clid = '555'
         WHERE record_id = 'record_id1'""",
        """UPDATE rent.rent_history SET start_clid = '555'
         WHERE rent_id = 'record_id1'""",
    ),
)
async def test_usage_of_old_clid(
        load_json,
        cron_context: context.Context,
        fleet_parks_v1_parks_list,
        mock_billing_reports,
        mock_billing_orders,
        mock_fleet_parks,
):
    @mock_fleet_parks('/v1/parks/list')
    async def v1_parks_list(request: http.Request):
        return {
            'parks': [
                {
                    'id': 'park_id',
                    'login': 'park_login',
                    'name': 'Sea',
                    'is_active': True,
                    'city_id': 'Gotham',
                    'locale': 'ru',
                    'is_billing_enabled': True,
                    'is_franchising_enabled': True,
                    'country_id': 'RUR',
                    'demo_mode': False,
                    'provider_config': {
                        'type': 'none',
                        'clid': 'updated_clid',
                    },
                    'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
                },
            ],
        }

    @mock_billing_reports('/v1/docs/select')
    async def _get_docs(request: http.Request):
        assert request.json == load_json('billing_reports_base_doc_req.json')
        return load_json('billing_reports_create_cancel_case_resp.json')

    @mock_billing_orders('/v2/process/async')
    async def _v2_process_async(request: http.Request):
        assert request.json == load_json(
            'billing_orders_create_cancel_request.json',
        )
        return load_json('billing_orders_create_cancel_response.json')

    await run_cron.main(
        ['fleet_rent.crontasks.process_cancelled_debts', '-t', '0'],
    )
    transactions = await cron_context.pg.master.fetch(
        'SELECT * FROM rent.external_debt_cancellations ORDER BY record_id;',
    )
    payment_doc_ids = [
        (t['id'], t['is_complete'], t['payment_doc_ids']) for t in transactions
    ]
    assert payment_doc_ids == [('b', False, [20, 21, 22])]


@pytest.mark.now('2020-01-20T15:30:00+00:00')
@pytest.mark.pgsql(
    'fleet_rent',
    files=['init_db_data.sql'],
    queries=(
        """INSERT INTO rent.external_debt_cancellations(
id, record_id, created_at, payment_doc_ids, created_by_json)
VALUES ('c', 'record_id1', '2020-01-20 12:12:14+00:00',
ARRAY [31::BIGINT, 32, 33],
 '{"kind":"dispatcher", "passport_uid":"user_id"}');""",
    ),
)
async def test_not_ready_case(
        load_json,
        cron_context: context.Context,
        fleet_parks_v1_parks_list,
        mock_billing_reports,
):
    @mock_billing_reports('/v1/docs/select')
    async def _get_docs(request: http.Request):
        topic_map = {
            'taxi/periodic_payment/clid/555/park_id_1': (
                'billing_reports_base_doc_req.json',
                'billing_reports_not_ready_case_resp.json',
            ),
            'taxi/periodic_payment_cancel/clid/555/park_id_1': (
                'billing_reports_not_ready_case_rejects_req.json',
                'billing_reports_not_ready_case_rejects_resp.json',
            ),
        }
        topic = request.json['external_obj_id']
        assert request.json['external_obj_id'] in topic_map
        if topic == 'taxi/periodic_payment_cancel/clid/555/park_id_1':
            assert request.json['external_event_ref'] in {'31', '32', '33'}
            del request.json['external_event_ref']
        assert request.json == load_json(topic_map[topic][0])
        return load_json(topic_map[topic][1])

    await run_cron.main(
        ['fleet_rent.crontasks.process_cancelled_debts', '-t', '0'],
    )
    transactions = await cron_context.pg.master.fetch(
        'SELECT * FROM rent.external_debt_cancellations ORDER BY record_id;',
    )
    payment_doc_ids = [
        (t['id'], t['is_complete'], t['payment_doc_ids']) for t in transactions
    ]
    assert payment_doc_ids == [('c', False, [31, 32, 33])]


@pytest.mark.now('2020-01-20T15:30:00+00:00')
@pytest.mark.pgsql(
    'fleet_rent',
    files=['init_db_data.sql'],
    queries=(
        """INSERT INTO rent.external_debt_cancellations(
id, record_id, created_at, payment_doc_ids, created_by_json)
VALUES ('bb', 'record_id1', '2020-01-20 12:12:13+00:00',
ARRAY [31,32,33,34,35]::BIGINT[],
 '{"kind":"dispatcher", "passport_uid":"user_id"}');""",
    ),
)
async def test_retry_reject(
        load_json,
        cron_context: context.Context,
        fleet_parks_v1_parks_list,
        mock_billing_reports,
        mock_billing_orders,
):
    ext_event_ref_requests = set()

    @mock_billing_reports('/v1/docs/select')
    async def _get_docs(request: http.Request):
        if 'external_event_ref' in request.json:
            assert request.json['external_event_ref'] in {
                '31',
                '31^1',
                '32',
                '32^1',
                '32^2',
                '34',
                '35',
                '35^1',
            }
            ext_event_ref_requests.add(request.json['external_event_ref'])
            del request.json['external_event_ref']
            assert request.json == load_json(
                'rejects/billing_reports_secondary_request.json',
            )
            return load_json('rejects/billing_reports_secondary_response.json')

        assert request.json == load_json('billing_reports_base_doc_req.json')
        return load_json('rejects/billing_reports_basic_response.json')

    is_retried = [False]

    @mock_billing_orders('/v2/process/async')
    async def _v2_process_async(request: http.Request):
        is_retried[0] = True
        assert request.json == load_json(
            'rejects/billing_orders_retry_request.json',
        )
        return load_json('rejects/billing_orders_retry_response.json')

    await run_cron.main(
        ['fleet_rent.crontasks.process_cancelled_debts', '-t', '0'],
    )
    transactions = await cron_context.pg.master.fetch(
        'SELECT * FROM rent.external_debt_cancellations ORDER BY record_id;',
    )
    payment_doc_ids = [
        (t['id'], t['is_complete'], t['payment_doc_ids']) for t in transactions
    ]
    assert payment_doc_ids == [('bb', False, [31, 32, 33, 34, 35])]
    assert ext_event_ref_requests == {
        '31',
        '31^1',
        '32',
        '32^1',
        '32^2',
        '34',
        '35',
        '35^1',
    }
    assert is_retried[0], 'Must call process/async on rejects'
