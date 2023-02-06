import pytest


@pytest.mark.parametrize('client_field', [True, False])
async def test_generate_new_handover_act(web_app_client, client_field):
    json_body = {
        'act': {'id': 'ТН100000001337', 'date': '2019-05-11'},
        'shipments': [
            {
                'id': '1',
                'shipment_items': [
                    {
                        'name': 'Холодильник Liebherr X2312LS',
                        'number_of_packages': 1,
                    },
                    {
                        'name': 'посудомоечная машина Samsung dw50h4030fw',
                        'number_of_packages': 1,
                    },
                    {
                        'name': 'Galaxy GL 4310 фен для волос',
                        'number_of_packages': 1,
                    },
                ],
                'address': (
                    'г. Москва, Садовническая набережная,' ' 62с2, БЦ Аврора'
                ),
            },
            {
                'id': '2',
                'shipment_items': [
                    {
                        'name': 'Хлебопечка MacBook Pro \'15 2018',
                        'number_of_packages': 1,
                    },
                ],
                'address': 'г. Москва, Духовской пер., д. 20кА, кв. 29',
            },
            {
                'id': '3',
                'shipment_items': [
                    {
                        'name': (
                            'Gektor (Гектор) средство против клопов,'
                            ' тараканов, муравьев, пауков, чешуйниц, 100 г'
                        ),
                        'number_of_packages': 4,
                    },
                ],
                'address': 'г. Москва, Духовской пер., д. 20кА, кв. 29',
            },
            {
                'id': '4',
                'shipment_items': [
                    {
                        'name': 'Galaxy GL 4310 фен для волос',
                        'number_of_packages': 1,
                    },
                ],
                'address': 'г. Москва, Садовническая набережная, д.12, кв. 19',
            },
        ],
        'driver': {
            'full_name': 'Кондаков Валерий Александрович',
            'passport_information': (
                'Серия 4611 номер 341757. Выдан ОУФМС России по'
                ' Московской области по  городскому округу  Жуковский.'
                ' Дата выдачи 24.07.2017. Код подразделения 500-037. '
            ),
            'park_name': 'Таксопарк ООО «Звездный»',
        },
        'source_points': [
            {
                'shipment_id': '1, 2, 3 ,4',
                'contact_signature': (
                    'Подписано Отправителем с '
                    'использованием простой электронной подписи'
                ),
                'contact_person': 'ООО «Интернет Решения»',
                'driver_signature': (
                    'Подписано Службой Такси с использованием'
                    ' простой электронной подписи'
                ),
            },
        ],
        'destination_points': [
            {
                'shipment_id': '2',
                'contact_signature': (
                    'Подписано Получателем с '
                    'использованием простой электронной подписи'
                ),
                'contact_person': 'ИП Федичкин Дмитрий Андреевич',
                'driver_signature': (
                    'Подписано Службой Такси с использованием'
                    ' простой электронной подписи'
                ),
            },
            {
                'shipment_id': '4',
                'contact_signature': (
                    'Подписано Получателем с '
                    'использованием простой электронной подписи'
                ),
                'contact_person': 'ИП Федичкин Дмитрий Андреевич',
                'driver_signature': (
                    'Подписано Службой Такси с использованием'
                    ' простой электронной подписи'
                ),
            },
        ],
        'return_points': [
            {
                'shipment_id': '1, 3',
                'contact_signature': (
                    'Подписано Отправителем с использованием'
                    ' простой электронной подписи'
                ),
                'contact_person': 'ООО «Интернет Решения»',
                'driver_signature': (
                    'Подписано Службой Такси с использованием'
                    ' простой электронной подписи'
                ),
            },
        ],
    }
    if client_field:
        json_body['client'] = {
            'contract_id': 'ABF23DD2332FfA34',
            'contract_date': '2020-01-23',
            'supplementary_agreement_id': 'AFB1231212121AF',
            'full_name': (
                'Общество с ограниченной ответственностью'
                ' «Интернет Решения»'
            ),
        }
    response = await web_app_client.post(
        '/v1/handover-act/generate-pdf', json=json_body,
    )
    assert response.status == 200
    content = await response.read()
    assert b'PDF-1.5' in content
