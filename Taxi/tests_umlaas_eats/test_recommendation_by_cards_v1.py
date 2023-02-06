import json


URL = '/umlaas-eats/v1/recommendation-by-cards'


async def test_recommendation_by_card_default(taxi_umlaas_eats, load):

    request_body = load('request.json')
    response = await taxi_umlaas_eats.post(URL, data=request_body)
    assert response.status == 200
    data = json.loads(response.text)

    assert len(data['places']) == 2
    assert data['places'][0]['slug'] == 'mc_donalds_123'
    assert data['places'][0]['items'][0]['id'] == 123
