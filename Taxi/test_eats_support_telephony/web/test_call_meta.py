import http


async def test_empty_response(
        taxi_eats_support_telephony_web, mock_personal, mock_eats_support_misc,
):
    @mock_personal('/v1/phones/find')
    def _mock_phones_store(request):
        return {'value': request.json['value'], 'id': '1234567890'}

    @mock_eats_support_misc('/v1/phone-info')
    def _mock_phone_info(request):
        return {
            'has_more_than_one_active_order': True,
            'has_ultima_order': False,
            'active_order': {
                'order_id': '220401-046219',
                'order_city': 'Москва',
                'delivery_type': 'marketplace',
                'client_id': '177044934',
                'partner_id': '136015',
                'partner_name': 'Цурцум кафе Zurzum cafe',
                'brand_id': '1437',
                'business_type': 'undefined',
            },
            'courier_id': '127054',
        }

    body = {'phone_number': '+71234567890'}
    response = await taxi_eats_support_telephony_web.post(
        '/cc/v1/eats-support-telephony/v1/call-meta', json=body,
    )
    assert response.status == http.HTTPStatus.OK
    body = await response.json()
    assert body
