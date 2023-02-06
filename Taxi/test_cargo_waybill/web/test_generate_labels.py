async def test_generate_barcode(web_app_client):
    json_body = {
        'requests': [
            {
                'delivery_data': {
                    'operator_barcode': {'text': f'barcode{j}'},
                    'sort_center': 'Sort Center',
                    'operator_name': 'OperatorName',
                    'reciever': 'Иванов Иван',
                    'address': 'Улица Улица',
                    'phone': '88004057623',
                    'brand_name': f'Brand Name {j}',
                    'order_id': '123456789',
                },
                'parcels': [
                    {'barcode': {'text': f'parcel{i}barcode'}, 'weight': 2500}
                    for i in range(3)
                ],
            }
            for j in range(3)
        ],
        'generate_type': 'many',
    }
    response = await web_app_client.post(
        '/v1/barcode/generate-pdf', json=json_body,
    )
    assert response.status == 200
    content = await response.read()
    assert b'PDF-1.5' in content
