import pytest


@pytest.mark.parametrize(
    ['phone_pd_id', 'lead_id'],
    [
        ('ce4db5ccb4bcaf8f7cfb9d752172a1c5', 'lead_0000_2'),
        ('ae65aa5bd9a4d47ce21169b9dbaac896', 'lead_0001_1'),
    ],
)
async def test_eda_channel_post_200(
        taxi_hiring_candidates_web, phone_pd_id, lead_id,
):
    # arrange
    data = {'phone_pd_id': phone_pd_id}

    # act
    response = await taxi_hiring_candidates_web.post(
        '/v1/eda/main-lead', json=data,
    )

    # assert
    assert response.status == 200
    response_data = await response.json()
    assert response_data == {'lead_id': lead_id}


async def test_eda_channel_post_not_found(taxi_hiring_candidates_web):
    # arrange
    data = {'phone_pd_id': '5e88de1a146747723b28a7d13d8f8ddf'}

    # act
    response = await taxi_hiring_candidates_web.post(
        '/v1/eda/main-lead', json=data,
    )

    # assert
    assert response.status == 400
