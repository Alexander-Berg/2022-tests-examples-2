from tests_fleet_offers import utils

ENDPOINT = '/fleet/offers/v1/signers/by-id/offers/download'
OFFER_ID = '00000000-0000-0000-0000-000000000001'


def build_params(signer_id, offer_id):
    return {'id': signer_id, 'offer_id': offer_id}


async def test_ok(taxi_fleet_offers, mock_fleet_parks, mockserver, load):
    @mockserver.handler(f'/park1/{OFFER_ID}/0')
    def _mock_mds(request):
        return mockserver.make_response(utils.FILE_DATA, 200)

    @mockserver.json_handler('/personal/v1/identifications/retrieve')
    def _mock_personal(request):
        return {
            'id': request.json['id'],
            'value': (
                '{'
                '"signer_name": "Иванов Иван Иваныч", '
                '"signer_passport_number": "1221 123456", '
                '"signer_passport_issue_date": "16.02.2002"'
                '}'
            ),
        }

    response = await taxi_fleet_offers.get(
        ENDPOINT,
        headers=utils.build_fleet_headers(park_id='park1'),
        params=build_params('driver1', OFFER_ID),
    )

    assert response.status_code == 200, response.text
