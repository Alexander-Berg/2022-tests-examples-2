import pytest


@pytest.mark.now('2020-07-21T10:00:00')
async def test_v1_blocks(taxi_quality_control_cpp):
    response = await taxi_quality_control_cpp.post(
        '/v1/blocks',
        params=dict(consumer='test'),
        json=dict(entity_id_in_set=['park_car_id', 'park_driver_id']),
    )
    assert response.status_code == 200
    data = response.json()
    assert data == dict(
        entities_by_id=[
            dict(
                entity_id='park_car_id',
                entities=[
                    dict(
                        data=dict(
                            blocks=dict(
                                rqc=['orders_off'],
                                branding=['sticker_off', 'lightbox_off'],
                                disinfection=['orders_off'],
                                sts=['orders_off'],
                            ),
                            id='park_car_id',
                            type='car',
                        ),
                        object_id='5c40b2024d7216d7297717b4',
                        revision='0_1594973578_12',
                    ),
                ],
            ),
            dict(
                entity_id='park_driver_id',
                entities=[
                    dict(
                        data=dict(
                            blocks=dict(
                                rqc=['rqc_comfort_plus_off', 'orders_off'],
                                biometry=['orders_off'],
                                dkvu=['orders_off'],
                                identity=['orders_off'],
                                thermobag=['thermobag_off'],
                            ),
                            id='park_driver_id',
                            type='driver',
                        ),
                        object_id='5bf6fd244d7216d729d67e1c',
                        revision='0_1595148783_24',
                    ),
                ],
            ),
        ],
    )
