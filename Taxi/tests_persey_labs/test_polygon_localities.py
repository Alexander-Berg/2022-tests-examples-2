import pytest

URL = '/admin/v1/polygon-localities'

EXPECTED_RESPONSE = {
    'ids': [
        2,
        10865,
        117428,
        117534,
        118008,
        118515,
        118936,
        119217,
        119622,
        120523,
        120590,
        120612,
        121327,
        165864,
    ],
    'names': [
        'Бугры',
        'Виллози',
        'Всеволожск',
        'Заневка',
        'Ковалёво',
        'Кудрово',
        'Мурино',
        'Новосаратовка',
        'Парголово',
        'Порошкино',
        'Посёлок имени Свердлова',
        'Санкт-Петербург',
        'Шушары',
        'Янино-1',
    ],
}


# Fails on mac. The handler is not in use.
@pytest.mark.skip
async def test_available_tests_stub(taxi_persey_labs, load_json):
    response = await taxi_persey_labs.post(URL, load_json('spb.json'))
    assert response.status_code == 200
    print('XXXXX: ', response.json())
    assert response.json() == EXPECTED_RESPONSE
