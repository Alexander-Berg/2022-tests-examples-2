import pytest


@pytest.mark.config(
    TALARIA_PAYMENTS_CARDS_MIGRATION_SETTINGS={
        'cards_batch_size': 3,
        'cards_batch_interval_ms': 1000,
        'transfer_tranzila_card_attempts': 1,
        'transfer_wind_cards_attempts': 1,
    },
)
@pytest.mark.now('2021-01-01T00:00:00Z')
async def test_main(mockserver, stq_runner, load_json):
    @mockserver.json_handler('/wind-pd/pf/server/v1/payment/getTranzilaCards')
    def wind_mock(request):
        assert request.json == {
            'wind_user_ids': [
                'wind_user_1',
                'wind_user_2',
                'wind_user_3',
                'wind_user_4',
            ],
        }
        return load_json('wind_get_tranzila_cards_request.json')

    @mockserver.json_handler(
        '/talaria-misc/talaria/v1/wind-user-is-card-migrated',
    )
    def talaria_misc_mock(request):
        assert request.json == {'wind_user_ids': ['wind_user_4']}
        return mockserver.make_response(status=200)

    @mockserver.json_handler(
        (
            '/stq-agent/queues/api/add/'
            'talaria_payments_transfer_tranzila_card/bulk'
        ),
    )
    def transfer_tranzila_card_bulk(request):
        expected_request = load_json('stq_bulk_request.json')
        for i, task in enumerate(request.json['tasks']):
            task['kwargs'].pop('log_extra')
            assert expected_request['tasks'][i] == task
        return {'tasks': []}

    kwargs = {
        'users': [
            {
                'yandex_uid': '4019697866',
                'login_id': 'login_1',
                'wind_user_id': 'wind_user_1',
            },
            {
                'yandex_uid': '2',
                'login_id': 'login_2',
                'wind_user_id': 'wind_user_2',
            },
            {
                'yandex_uid': '3',
                'login_id': 'login_3',
                'wind_user_id': 'wind_user_3',
            },
            {
                'yandex_uid': '4',
                'login_id': 'login_4',
                'wind_user_id': 'wind_user_4',
            },
        ],
    }

    await stq_runner.talaria_payments_transfer_wind_cards.call(
        task_id='task_id', kwargs=kwargs,
    )

    assert wind_mock.times_called == 1
    assert transfer_tranzila_card_bulk.times_called == 1
    assert talaria_misc_mock.times_called == 1
