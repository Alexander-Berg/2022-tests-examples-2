import pytest


BASE_AUTOTARIFF_CONFIG = {
    'enabled': True,
    'zones': {
        'accra': [{'src_category': 'econom', 'dst_category': 'premium_suv'}],
    },
    'draft_settings': {
        'set_tariff': {
            'manager_login': 'manager',
            'summon_users': ['user'],
            'attach_tickets': ['RUPRICING-777'],
        },
        'commissions_create': {
            'manager_login': 'manager',
            'summon_users': ['user'],
            'attach_tickets': ['RUPRICING-777'],
        },
        'set_tariff_settings': {
            'manager_login': 'manager',
            'summon_users': ['user'],
            'attach_tickets': ['RUPRICING-777'],
            'enabled': True,
        },
    },
    'category_settings': {
        'premium_suv': {'tariff_settings_reference_zone': 'kazan'},
        'suv': {'tariff_settings_reference_zone': 'kazan'},
    },
}


@pytest.mark.now('2020-05-02T12:00:00+0')
@pytest.mark.config(PERSEY_PAYMENTS_AUTOTARIFF=BASE_AUTOTARIFF_CONFIG)
@pytest.mark.parametrize(
    [
        'tariffs_resp',
        'tariff_settings_resp',
        'rules_list_resp',
        'exp_drafts',
        'approvals_times_called',
    ],
    [
        (
            'tariff_current_resp_simple.json',
            'tariff_settings_resp_simple.json',
            'rules_list_resp_simple.json',
            'exp_draft_simple.json',
            3,
        ),
        (
            'tariff_current_resp_idempotency.json',
            'tariff_settings_resp_simple.json',
            'rules_list_resp_simple.json',
            'exp_draft_simple.json',
            2,
        ),
        (
            'tariff_current_resp_kopejka.json',
            'tariff_settings_resp_simple.json',
            'rules_list_resp_simple.json',
            'exp_draft_simple.json',
            3,
        ),
        (
            'tariff_current_resp_idempotency.json',
            'tariff_settings_resp_idempotency.json',
            'rules_list_resp_idempotency.json',
            None,
            0,
        ),
    ],
)
async def test_simple(
        cron_runner,
        load_json,
        mock_taxi_tariffs,
        mock_taxi_tariffs_py3,
        mock_billing_commissions,
        mock_taxi_approvals,
        tariffs_resp,
        tariff_settings_resp,
        rules_list_resp,
        exp_drafts,
        approvals_times_called,
):
    @mock_taxi_tariffs_py3('/v1/tariff/current')
    def _tariffs_mock(request):
        assert request.query['zone'] == 'accra'

        return load_json(tariffs_resp)

    @mock_billing_commissions('/v1/rules/list')
    def _billing_commissions_mock(request):
        assert request.query['tariff_zone'] == 'accra'

        return load_json(rules_list_resp)

    @mock_taxi_tariffs('/v1/tariff_settings/bulk_retrieve')
    def _tariff_settings_mock(request):
        assert set(request.query['zone_names'].split(',')) == {
            'accra',
            'kazan',
        }

        return load_json(tariff_settings_resp)

    @mock_taxi_approvals('/drafts/create/')
    def _taxi_approvals_mock(request):
        assert request.headers['X-Yandex-Login'] == 'manager'
        del request.json['request_id']

        assert request.json in load_json(exp_drafts)

        return {'id': 1, 'version': 1}

    await cron_runner.autotariff()

    assert _tariffs_mock.times_called == 1
    assert _billing_commissions_mock.times_called == 1
    assert _tariff_settings_mock.times_called == 1
    assert _taxi_approvals_mock.times_called == approvals_times_called


@pytest.mark.now('2020-05-02T12:00:00+0')
@pytest.mark.config(
    PERSEY_PAYMENTS_AUTOTARIFF={
        **BASE_AUTOTARIFF_CONFIG,
        **{
            'category_settings': {
                'premium_suv': {
                    'tariff_settings_reference_zone': 'kazan',
                    'allowed_requirements': ['childchair', '^own_chair$'],
                },
            },
        },
    },
)
async def test_requirements_filter(
        cron_runner,
        load_json,
        mock_taxi_tariffs,
        mock_taxi_tariffs_py3,
        mock_billing_commissions,
        mock_taxi_approvals,
):
    @mock_taxi_tariffs_py3('/v1/tariff/current')
    def _tariffs_mock(request):
        return load_json('tariff_current_resp_simple.json')

    @mock_billing_commissions('/v1/rules/list')
    def _billing_commissions_mock(request):
        return load_json('rules_list_resp_simple.json')

    @mock_taxi_tariffs('/v1/tariff_settings/bulk_retrieve')
    def _tariff_settings_mock(request):
        return load_json('tariff_settings_resp_simple.json')

    @mock_taxi_approvals('/drafts/create/')
    def _taxi_approvals_mock(request):
        if request.json['api_path'] == 'set_tariff':
            premium_suv = None
            for category in request.json['data']['categories']:
                if category['category_name'] == 'premium_suv':
                    premium_suv = category

            assert premium_suv is not None

            assert {
                r['type'] for r in premium_suv['summable_requirements']
            } == {'some_childchair', 'own_chair'}

        return {'id': 1, 'version': 1}

    await cron_runner.autotariff()

    assert _taxi_approvals_mock.times_called == 3
