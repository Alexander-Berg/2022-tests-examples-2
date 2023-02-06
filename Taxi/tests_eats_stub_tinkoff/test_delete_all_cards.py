HEADERS = {'Authorization': 'Bearer TestToken'}


async def test_delete_all_cards(taxi_eats_stub_tinkoff, create_card):
    first_ucid = '10000000'
    second_ucid = '10000001'
    create_card(ucid=first_ucid)
    create_card(ucid=second_ucid)

    response = await taxi_eats_stub_tinkoff.delete(f'/internal/api/v1/cards')
    assert response.status == 204

    response = await taxi_eats_stub_tinkoff.get(
        f'/api/v1/card/{first_ucid}/limits', headers=HEADERS,
    )
    assert response.status == 404

    response = await taxi_eats_stub_tinkoff.get(
        f'/api/v1/card/{second_ucid}/limits', headers=HEADERS,
    )
    assert response.status == 404
