async def test_generate_new_handover_act(web_app_client):
    json_body = {
        'act': {'id': 'HOMEP AKTA', 'date': '2020-11-11'},
        'client': {
            'id': '7009213112331',
            'legal_name': 'Юр лицо/ИП, с кем заключен договор',
        },
        'performer': {'legal_name': 'ООО ЯндексЛогистика'},
        'consigner': {
            'legal_name': """кто фактически отгружает заказы может = либо
             ЮЛ/ИП Заказчика или же его представителя (например, поставщик)
             или клиента заказчика (если забираем заказы у клиента СД/ФФ
            оператора)""",
        },
        'consignee': {
            'legal_name': """Юр лицо/ИП, кто фактически заберет заказ
             (логистический партнер Яндекс.Логистики)""",
        },
        'parcels': {
            'total': {
                'weight_kg': 'Суммируем вес',
                'places_number': 'Суммируем кол-во грузовых мест',
            },
            'list': [
                {
                    'client_parcel_id': 'Номер B2B клиента - магазина',
                    'performer_parcel_id': (
                        '(субподрядчика – исполнителя, кто доставляет заказ)'
                    ),
                    'declared_value': ' заказа',
                    'weight_kg': ' создании заказа)',
                    'places_number': ' заказа)',
                },
                {
                    'client_parcel_id': 'ВТОРОЙ Номер B2B клиента',
                    'performer_parcel_id': 'ВТОРОЙ (субподрядчика)',
                    'declared_value': 'ВТОРОЙ тянем из данных',
                    'weight_kg': 'ВТОРОЙ (тянем из данных)',
                    'places_number': 'ВТОРОЙ (тянем из данных)',
                },
            ],
        },
    }

    response = await web_app_client.post(
        '/v1/log-platform/handover-act/generate-pdf', json=json_body,
    )
    assert response.status == 200
    content = await response.read()
    assert b'PDF-1.5' in content
