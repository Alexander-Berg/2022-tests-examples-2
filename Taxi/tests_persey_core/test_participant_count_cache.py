from tests_persey_core import utils


async def test_participant_count_cache(
        taxi_persey_core,
        persey_core_internal,
        pgsql,
        taxi_persey_core_monitor,
):
    cursor = pgsql['persey_payments'].cursor()
    utils.fill_db(
        cursor,
        {
            'persey_payments.fund': [
                {
                    'fund_id': 'sample_fund_id',
                    'name': 'sample_name',
                    'offer_link': 'sample_offer_link',
                    'operator_uid': 'sample_operator_uid',
                    'balance_client_id': 'sample_balance_client_id',
                    'trust_partner_id': 'sample_trust_partner_id',
                    'trust_product_id': 'sample_trust_product_id',
                    'is_hidden': False,
                    'created_at': '2020-01-01T00:00:00+00:00',
                    'available_amount': '0',
                    'exclude_from_sampling': False,
                },
            ],
            'persey_payments.ride_subs': [
                {
                    'id': 90000,
                    'yandex_uid': '100',
                    'brand': 'yataxi',
                    'fund_id': 'sample_fund_id',
                    'mod': 10,
                    'created_at': '2022-02-01T10:00:00+00:00',
                    'updated_at': '2022-02-01T10:00:00+00:00',
                    'locale': 'ru',
                },
                {
                    'id': 90010,
                    'yandex_uid': '100',
                    'brand': 'market',
                    'fund_id': 'sample_fund_id',
                    'mod': 10,
                    'created_at': '2022-02-01T10:00:00+00:00',
                    'updated_at': '2022-02-01T10:00:00+00:00',
                    'locale': 'ru',
                },
                {
                    'id': 90020,
                    'yandex_uid': '100',
                    'brand': 'eats',
                    'fund_id': 'sample_fund_id',
                    'mod': 20,
                    'created_at': '2022-02-09T10:00:00+00:00',
                    'updated_at': '2022-02-09T11:00:00+00:00',
                    'hidden_at': '2022-02-09T11:00:00+00:00',
                    'locale': 'ru',
                },
                {
                    'id': 90030,
                    'yandex_uid': '101',
                    'brand': 'eats',
                    'fund_id': 'sample_fund_id',
                    'mod': 30,
                    'created_at': '2022-02-09T10:00:00+00:00',
                    'updated_at': '2022-02-11T10:00:00+00:00',
                    'locale': 'ru',
                },
                {
                    'id': 90040,
                    'yandex_uid': '102',
                    'brand': 'eats',
                    'fund_id': 'sample_fund_id',
                    'mod': 50,
                    'created_at': '2022-02-09T10:00:00+00:00',
                    'updated_at': '2022-02-11T10:00:00+00:00',
                    'locale': 'ru',
                },
                {
                    'id': 90050,
                    'yandex_uid': '103',
                    'brand': 'eats',
                    'fund_id': 'sample_fund_id',
                    'mod': 50,
                    'created_at': '2022-02-09T10:00:00+00:00',
                    'hidden_at': '2022-02-11T10:00:00+00:00',
                    'updated_at': '2022-02-11T10:00:00+00:00',
                    'locale': 'ru',
                },
            ],
            'persey_payments.bound_uids': [
                {
                    'phonish_yandex_uid': '104',
                    'portal_yandex_uid': '105',
                    'updated_at': '2022-02-01T00:00:00+00:00',
                },
            ],
        },
    )
    await taxi_persey_core.invalidate_caches(
        clean_update=True, cache_names=['ride-subs-cache', 'bound-uids-cache'],
    )
    await taxi_persey_core.run_periodic_task('update_participant_count_cache')
    result = await persey_core_internal.call('GetParticipantCount')
    assert result == {
        'by_brand': {'eats': 2, 'market': 1, 'yataxi': 1},
        'overall': 3,
    }

    utils.fill_db(
        cursor,
        {
            'persey_payments.ride_subs': [
                {
                    'id': 90021,
                    'yandex_uid': '100',
                    'brand': 'eats',
                    'fund_id': 'sample_fund_id',
                    'mod': 20,
                    'created_at': '2022-02-25T10:00:00+00:00',
                    'updated_at': '2022-02-25T13:00:00+03:00',
                    'locale': 'ru',
                },
                {
                    'id': 90060,
                    'yandex_uid': '104',
                    'brand': 'market',
                    'fund_id': 'sample_fund_id',
                    'mod': 20,
                    'created_at': '2022-02-25T10:00:00+00:00',
                    'updated_at': '2022-02-25T13:00:00+03:00',
                    'locale': 'ru',
                },
                {
                    'id': 90070,
                    'yandex_uid': '105',
                    'brand': 'market',
                    'fund_id': 'sample_fund_id',
                    'mod': 20,
                    'created_at': '2022-02-24T10:00:00+00:00',
                    'updated_at': '2022-02-25T13:00:00+03:00',
                    'locale': 'ru',
                },
            ],
            'persey_payments.bound_uids': [
                {
                    'phonish_yandex_uid': '101',
                    'portal_yandex_uid': '102',
                    'updated_at': '2022-02-01T00:00:00+00:00',
                },
            ],
        },
    )
    await taxi_persey_core.invalidate_caches(
        clean_update=True, cache_names=['ride-subs-cache', 'bound-uids-cache'],
    )
    await taxi_persey_core.run_periodic_task('update_participant_count_cache')
    result = await persey_core_internal.call('GetParticipantCount')
    assert result == {
        'by_brand': {'eats': 2, 'market': 2, 'yataxi': 1},
        'overall': 3,
    }
    result = await taxi_persey_core_monitor.get_metric(
        'participant-count-cache',
    )
    assert result == {
        'stats': {
            '$meta': {'solomon_children_labels': 'brand'},
            '__overall__': 3,
            'eats': 2,
            'market': 2,
            'yataxi': 1,
        },
    }
    response = await taxi_persey_core.get('/persey-core/participant-count')
    assert response.status_code == 200
    assert response.json() == {
        'by_brand': {'eats': 2, 'market': 2, 'yataxi': 1},
        'overall': 3,
    }
