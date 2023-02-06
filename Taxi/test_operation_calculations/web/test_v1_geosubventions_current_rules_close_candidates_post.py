import datetime
import json

from aiohttp import web
import pytest


@pytest.fixture(name='test_data')
def test_data_fixture(open_file):
    with open_file('test_data_common.json') as fp:
        test_data = json.load(fp)
    with open_file('test_data.json') as data_json:
        test_data.update(json.load(data_json))
    return test_data


@pytest.fixture(name='mock_thirdparty_servers')
def mock_thirdparty_servers_fixture(
        web_app_client,
        mock_taxi_tariffs,
        mock_geoareas,
        mock_billing_subventions_x,
        patch_aiohttp_session,
        response_mock,
        mock_taxi_approvals,
        mockserver,
        patch,
        test_data,
):
    @mock_taxi_tariffs('/v1/tariff_settings/bulk_retrieve')
    def _tariff_settings_handler(request):
        return web.json_response(test_data['tariff_settings'])

    @mock_billing_subventions_x('/v2/rules/by_filters')
    def _bsx_select_handler(request):
        return web.json_response(test_data['current_rules'])

    @mockserver.json_handler('/taxi-exp-py3/v1/experiments/')
    def _handler_exp(request):
        exp_name = request.query.get('name')
        return test_data['current_experiments'][exp_name]

    @mockserver.json_handler('/taxi-exp-py3/v1/experiments/list/')
    def _handler_exp_list(request):
        offset = request.query.get('offset')
        return (
            test_data['current_experiments_list']
            if offset == '0'
            else {'experiments': []}
        )

    @mock_taxi_approvals('/drafts/list/')
    def _taxi_approvals_drafts_list(request):
        return test_data['drafts']


async def test_current_rules_close_candidates(
        web_app_client, mock_thirdparty_servers, test_data, monkeypatch,
):
    monkeypatch.setattr(
        datetime.datetime,
        'now',
        lambda tz=None: datetime.datetime(
            2020, 10, 16, 13, 32, 41, 123456, tzinfo=tz,
        ),
    )

    response = await web_app_client.post(
        '/v1/geosubventions/current_rules/close_candidates/',
        json=test_data['request'],
    )
    assert response.status == test_data['status'], await response.text()
    response = await response.json()
    assert response['conflicting_rules'] == []
    assert response['non_confflicting_rules'] == test_data['expected_response']
    assert response['state_hash']
