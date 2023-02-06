async def test_offers(logistic_platform_client, rt_robot_execute):
    await rt_robot_execute('supply_reservation')

    refresh_caches_response = await logistic_platform_client.post(
        'testsuite/refresh-caches',
    )
    if refresh_caches_response.status_code != 200:
        raise RuntimeError(refresh_caches_response.content)

    response = await logistic_platform_client.post(
        '/api/b2b/platform/offers/create',
        json={
            "info": {
                "operator_request_id": "test_for_nds-8",
                "comment": "",
                "referral_source": "RetailCRM_NDD"
            },
            "source": {
                "type": 1,
                "platform_station": {
                    "platform_id": "2c20f2d5-2d02-46a9-9ca5-f5fb0e3c0d4f"
                }
            },
            "destination": {
                "type": 2,
                "custom_location": {
                    "details": {
                        "full_address": "Москва, Часовая улица, 10"
                    }
                }
            },
            "last_mile_policy": 0,
            "billing_info": {
                "payment_method": "already_paid"
            },
            "recipient_info": {
                "first_name": "Тест",
                "last_name": "Калькулятор",
                "phone": "79219999999"
            },
            "places": [
                {
                    "physical_dims": {
                        "dx": 10,
                        "dy": 10,
                        "dz": 10,
                        "weight_gross": 200
                    },
                    "description": "",
                    "barcode": "place_0"
                }
            ],
            "items": [
                {
                    "count": 1,
                    "name": "Товар",
                    "article": "2175",
                    "barcode": "2175",
                    "billing_details": {
                        "unit_price": 1000,
                        "assessed_unit_price": 1000,
                        "nds": 20
                    },
                    "place_barcode": "place_0",
                    "physical_dims": {}
                }
            ]
        },
    )

    assert response.json() == {
        'error': {
            'details': {
                'unknown_geo_id': ['delivery to geo_id 225 is unavailable']},
                'message': 'cannot build user request'
            }
        }
