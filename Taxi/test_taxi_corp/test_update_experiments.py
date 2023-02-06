import pytest


@pytest.mark.usefixtures('simple_secdist')
async def test_ok(db, patch, exp_client_mock, config_patcher, load_json):
    @patch('taxi.clients.taxi_exp.TaxiExpClient.get_config')
    async def _get_experiment(name):
        return await exp_client_mock.get_config(name)

    @patch('taxi.clients.taxi_exp.TaxiExpClient.update_config')
    async def _update_experiment(name, last_modified_at, data):
        return await exp_client_mock.update_config(
            name, last_modified_at, data,
        )

    @patch('taxi.clients.taxi_exp.TaxiExpClient.load_file')
    async def _load_file(
            data,
            file_name,
            experiment_name,
            *args,
            transform=None,
            phone_type=None,
            content_type=None,
            arg_type=None,
            **kwargs,
    ):
        files = load_json('files_data.json')
        assert file_name in files.keys()
        assert experiment_name == files[file_name]['exp_name']
        assert data == files[file_name]['data']
        return {
            'id': files[file_name]['file_id'],
            'lines': 1,
            'hash': 'test_hash',
        }

    @patch('taxi.clients.taxi_exp.TaxiExpClient.create_config')
    async def _create_config(exp_name, exp_body):
        return await exp_client_mock.create_config(exp_name, exp_body)

    @patch('taxi.clients.personal.PersonalApiClient.bulk_find')
    async def _personal_bulk_find(data_type, request_values, *args, **kwargs):
        return map(
            lambda x: {'phone': x, 'id': f'personal_{x[1:]}'}, request_values,
        )

    @patch('taxi.clients.user_api.UserApiClient.get_phones_info_by_personal')
    async def _user_api_get_phones_info_by_personal(
            personal_phone_ids, timeout_ms, *args, **kwargs,
    ):
        return map(
            lambda x: {
                'id': f'phone_id_{x}',
                'personal_phone_id': x,
                'type': 'yandex',
            },
            personal_phone_ids,
        )

    config_patcher(CORP_CLIENTS_EXPERIMENTS=load_json('corp_config.json'))

    from taxi_corp import cron_run

    module = 'taxi_corp.stuff.update_experiments'
    await cron_run.main([module, '-t', 0])
