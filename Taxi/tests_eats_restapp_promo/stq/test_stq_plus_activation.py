import pytest


@pytest.mark.eats_catalog_storage_cache(
    file='eats_catalog_storage_cache_data.json',
)
@pytest.mark.parametrize(
    ['task_id', 'db_id', 'place_id', 'cashback', 'starts', 'expect_fail'],
    [
        ('1', 1, '1', '5.0', '2020-11-25T21:00:00+00:00', False),
        ('2', 2, '55', '5.0', '2020-11-25T20:00:00+00:00', False),
    ],
)
async def test_stq_plus_activation(
        stq_runner,
        pgsql,
        task_id,
        db_id,
        place_id,
        cashback,
        starts,
        expect_fail,
):

    cursor = pgsql['eats_restapp_promo'].cursor()
    cursor.execute(
        'SELECT * FROM eats_restapp_promo.place_plus_activation'
        f' WHERE place_id=\'{place_id}\'',
    )
    status_before_data = cursor.fetchall()

    await stq_runner.eats_restapp_promo_plus_activation.call(
        task_id=task_id, kwargs={'id': db_id}, expect_fail=expect_fail,
    )

    cursor.execute(
        'SELECT * FROM eats_restapp_promo.place_plus_activation'
        f' WHERE place_id=\'{place_id}\'',
    )
    status_after_data = cursor.fetchall()
    assert len(status_after_data) == 1
    assert status_after_data[0][0] == status_before_data[0][0]
    assert status_after_data[0][1] == status_before_data[0][1]
    assert status_after_data[0][2] == 'active'
    assert status_after_data[0][3] == status_before_data[0][3]
    assert status_after_data[0][4] == status_before_data[0][4]

    cursor.execute(
        'SELECT * FROM eats_restapp_promo.place_plus'
        f' WHERE place_id=\'{place_id}\'',
    )
    place_plus_data = cursor.fetchall()
    assert place_plus_data[0][0] == place_id
    assert float(place_plus_data[0][1]) == float(cashback)
    assert place_plus_data[0][2].strftime(
        '%Y-%m-%dT%H:%M:%S',
    ) == status_after_data[0][4].strftime('%Y-%m-%dT%H:%M:%S')
    assert place_plus_data[0][3] is None


async def test_stq_salesforce_double_create_commission_check(
        stq_runner, mockserver,
):
    @mockserver.json_handler(
        '/salesforce/services/apexrest/commission/getCommission',
    )
    def _mock_sf_get_commission(request):
        return mockserver.make_response(
            status=200,
            json=[
                {
                    'type': 'Кешбэк Плюс',
                    'status': 'Активна',
                    'startDate': '2020-11-26',
                    'placeId': 111,
                    'isEnabled': True,
                    'endDate': None,
                    'commissionFixed': None,
                    'commission': 11.1,
                    'acquiring': 0.0,
                },
            ],
        )

    @mockserver.json_handler(
        '/salesforce/services/apexrest/commission/createCommission',
    )
    def _mock_sf_create_commission(request):
        assert False

    await stq_runner.eats_restapp_promo_plus_activation.call(
        task_id='111', kwargs={'id': 3}, expect_fail=False,
    )


async def test_stq_incorrect_id_in_table(stq_runner, mockserver):
    await stq_runner.eats_restapp_promo_plus_activation.call(
        task_id='111', kwargs={'id': 12345}, expect_fail=True,
    )


async def test_stq_already_active_cashback(stq_runner, mockserver):
    @mockserver.json_handler(
        '/salesforce/services/apexrest/commission/getCommission',
    )
    def _mock_sf_get_commission(request):
        assert False

    @mockserver.json_handler(
        '/salesforce/services/apexrest/commission/createCommission',
    )
    def _mock_sf_create_commission(request):
        assert False

    await stq_runner.eats_restapp_promo_plus_activation.call(
        task_id='1234', kwargs={'id': 4}, expect_fail=False,
    )


async def test_stq_activation_with_sf_null_status(stq_runner, mockserver):
    @mockserver.json_handler(
        '/salesforce/services/apexrest/commission/getCommission',
    )
    def _mock_sf_get_commission(request):
        return mockserver.make_response(
            status=200,
            json=[
                {
                    'type': 'Кешбэк Плюс',
                    'status': None,
                    'startDate': '2020-11-26',
                    'placeId': 111,
                    'isEnabled': True,
                    'endDate': None,
                    'commissionFixed': None,
                    'commission': 11.1,
                    'acquiring': 0.0,
                },
            ],
        )

    await stq_runner.eats_restapp_promo_plus_activation.call(
        task_id='1', kwargs={'id': 1}, expect_fail=False,
    )


async def test_stq_activation_with_eats_plus_created(stq_runner, mockserver):
    @mockserver.json_handler('/eats-plus/internal/eats-plus/v1/place/cashback')
    def _mock_eats_plus_place_cashback(request):
        return mockserver.make_response(
            status=200,
            json={
                'place_id': 1,
                'active': True,
                'place_cashback': [
                    {
                        'cashback': 5.0,
                        'active_from': '2020-11-26T00:00:00+03:00',
                    },
                ],
                'eda_cashback': [],
            },
        )

    @mockserver.json_handler(
        '/eats-plus/internal/eats-plus/v1/settings/cashback',
    )
    def _mock_plus_settings_cashback(request):
        assert False

    await stq_runner.eats_restapp_promo_plus_activation.call(
        task_id='1', kwargs={'id': 1}, expect_fail=False,
    )
