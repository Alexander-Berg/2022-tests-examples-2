import pytest


@pytest.mark.suspend_periodic_tasks('transfer-cashbacks-request-body')
@pytest.mark.config(
    EATS_PLUS_TRANSFER_CASHBACKS_SETTINGS={
        'enabled': True,
        'update_period_ms': 10,
        'chunk_size': 100,
    },
)
async def test_transfer_cashbacks_periodic(
        taxi_eats_plus, testpoint, mockserver, eats_order_stats,
):
    @testpoint('cashback-settings-request-body')
    def transfer_cashbacks(data):
        assert data['len'] == 6
        places_settings = data['places_settings']
        cb0 = [
            places_settings[0]['place_id'],
            places_settings[0]['place_has_plus'],
            places_settings[0].get('yandex_cashback'),
            places_settings[0].get('place_cashback'),
        ]
        assert cb0 == [
            '1',
            True,
            None,
            {'cashback': '1.1', 'starts': '2020-11-25T15:43:00+00:00'},
        ]

        cb1 = [
            places_settings[1]['place_id'],
            places_settings[1]['place_has_plus'],
            places_settings[1].get('yandex_cashback'),
            places_settings[1].get('place_cashback'),
        ]
        assert cb1 == [
            '1',
            True,
            {'cashback': '5', 'starts': '2020-11-25T15:43:00+00:00'},
            None,
        ]

        cb2 = [
            places_settings[2]['place_id'],
            places_settings[2]['place_has_plus'],
            places_settings[2].get('yandex_cashback'),
            places_settings[2].get('place_cashback'),
        ]
        assert cb2 == [
            '2',
            True,
            None,
            {'cashback': '2', 'starts': '2020-11-25T15:43:00+00:00'},
        ]

        cb3 = [
            places_settings[3]['place_id'],
            places_settings[3]['place_has_plus'],
            places_settings[3].get('yandex_cashback'),
            places_settings[3].get('place_cashback'),
        ]
        assert cb3 == [
            '2',
            True,
            {'cashback': '5', 'starts': '2020-11-25T15:43:00+00:00'},
            None,
        ]

        cb4 = [
            places_settings[4]['place_id'],
            places_settings[4]['place_has_plus'],
            places_settings[4].get('yandex_cashback'),
            places_settings[4].get('place_cashback'),
        ]
        assert cb4 == [
            '3',
            True,
            None,
            {
                'cashback': '5.5',
                'starts': '2020-11-25T15:43:00+00:00',
                'ends': '2021-11-25T15:43:00+00:00',
            },
        ]

        cb5 = [
            places_settings[5]['place_id'],
            places_settings[5]['place_has_plus'],
            places_settings[5].get('yandex_cashback'),
            places_settings[5].get('place_cashback'),
        ]
        assert cb5 == [
            '3',
            True,
            {
                'cashback': '4.5',
                'starts': '2020-11-25T15:43:00+00:00',
                'ends': '2021-11-25T15:43:00+00:00',
            },
            None,
        ]

    await taxi_eats_plus.run_periodic_task('transfer-cashbacks')

    assert await transfer_cashbacks.wait_call()
