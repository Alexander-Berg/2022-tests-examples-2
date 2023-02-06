import pytest

pytest.mark.now('2020-01-01T09:00:00+00:00')


async def test_get_cards_qiwi(pro_v1, mock_api, pg_dump):
    response = await pro_v1.get_cards(
        park_id='48b7b5d81559460fb1766938f94009c1',
        contractor_id='48b7b5d81559460fb176693800000001',
    )
    assert response.status_code == 200, response.text

    assert response.json()['items'][0]['masked_pan'] == '************1234'
    assert response.json()['items'][1]['masked_pan'] == '123456******7890'

    assert pg_dump()['card'][1][3] == '48b7b5d81559460fb1766938f94009c1'
    assert pg_dump()['card'][1][4] == '48b7b5d81559460fb176693800000001'
    assert pg_dump()['card'][1][6] == 'qiwi'
    assert pg_dump()['card'][1][7] == 'active'
    assert pg_dump()['card'][1][8] == '123456******7890'
    assert pg_dump()['card'][1][17] == '11111111-1111-1111-1111-111111111111'
