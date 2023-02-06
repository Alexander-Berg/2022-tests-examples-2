import pytest


def get_fallback_switcher(pgsql):
    with pgsql['pricing_data_preparer'].cursor() as cursor:
        cursor.execute('SELECT is_on FROM fallbacks.switchers')
        result = cursor.fetchall()
        return result[0][0]


@pytest.mark.parametrize(
    'file, is_on',
    [
        ('solomon_response_prod.json', True),
        ('solomon_response_testing.json', False),
    ],
)
@pytest.mark.now('2021-05-31T15:00:00Z')
async def test_receipt_md_auto_fallback(
        taxi_pricing_admin,
        pgsql,
        taxi_config,
        mockserver,
        load_json,
        file,
        is_on,
):
    with pgsql['pricing_data_preparer'].cursor() as cursor:
        cursor.execute(
            'INSERT INTO fallbacks.switchers (name)' 'VALUES (\'md\');',
        )

    taxi_config.set(PRICING_ADMIN_RECEIPT_MD_AUTO_FALLBACK_LIMIT=5)

    @mockserver.json_handler('/solomon/api/v2/projects/taxi/sensors/data')
    def _mock_solomon(request):
        data = request.json
        assert data == {
            'downsampling': {'disabled': True},
            'from': '2021-05-31T14:55:00+00:00',
            'program': (
                '{cluster=\'testsuite_uservices\', '
                'service=\'uservices\', '
                'sensor=\'custom-receipt-retries\', '
                'application=\'pricing-admin\', '
                'group=\'*\', '
                'host=\'cluster\'}'
            ),
            'to': '2021-05-31T15:00:00+00:00',
            'version': 'GROUP_LINES_RETURN_VECTOR_2',
        }
        return load_json(file)

    response = await taxi_pricing_admin.post(
        'service/cron', json={'task_name': 'receipt-md-auto-fallback'},
    )
    assert response.status_code == 200
    switcher = get_fallback_switcher(pgsql)
    assert switcher == is_on
