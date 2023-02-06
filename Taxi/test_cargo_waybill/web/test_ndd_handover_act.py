import copy


JSON_BODY = {
    'operator_claims': [
        {
            'claims_count': 1,
            'claims': [
                {
                    'total_weight': '1',
                    'total_boxes': 1,
                    'external_order_id': '10686898927350392823',
                    'total_assessed_cost': '1',
                    'request_code': f'request{i}',
                }
                for i in range(30)
            ],
            'total_weight': '30',
            'total_boxes': 30,
            'brand_name': 'brand_name',
            'current_date': '03.03.2022',
            'sorting_center': 'strizh',
        },
        {
            'claims_count': 1,
            'claims': [
                {
                    'total_weight': '1',
                    'total_boxes': 1,
                    'external_order_id': '10686898927350392823',
                    'total_assessed_cost': '1',
                    'request_code': 'request',
                },
            ],
            'total_weight': '1',
            'total_boxes': 1,
            'brand_name': 'brand_name',
            'current_date': '03.03.2022',
            'sorting_center': 'strizh',
        },
        {
            'claims_count': 1,
            'claims': [
                {
                    'total_weight': '1',
                    'total_boxes': 1,
                    'external_order_id': '10686898927350392823',
                    'total_assessed_cost': '1',
                    'request_code': 'request',
                },
            ],
            'total_weight': '1',
            'total_boxes': 1,
            'brand_name': 'brand_name',
            'current_date': '03.03.2022',
            'sorting_center': 'strizh',
        },
    ],
}


async def test_generate_barcode_pdf(web_app_client):
    json_body = copy.deepcopy(JSON_BODY)
    response = await web_app_client.post(
        '/v1/ndd-handover-act/generate', json=json_body,
    )
    assert response.status == 200
    content = await response.read()
    assert b'PDF-1.5' in content


async def test_generate_barcode_pdf_old(web_app_client):
    json_body = copy.deepcopy(JSON_BODY)
    response = await web_app_client.post(
        '/v1/ndd-handover-act/generate-pdf', json=json_body,
    )
    assert response.status == 200
    content = await response.read()
    assert b'PDF-1.5' in content


async def test_generate_barcode_docx(web_app_client):
    json_body = copy.deepcopy(JSON_BODY)
    json_body['editable_format'] = True
    response = await web_app_client.post(
        '/v1/ndd-handover-act/generate', json=json_body,
    )
    assert response.status == 200
    content = await response.read()
    assert b'PK' in content
