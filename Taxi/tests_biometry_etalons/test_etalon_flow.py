import pytest


PARK_ID = 'park00000000000000000003'
DRIVER_PROFILE_ID = 'driver000000000000000003'


def prepare_response(response):
    etalon_media = response['etalon_media']
    for media_type in etalon_media:
        etalon_media[media_type] = sorted(
            etalon_media[media_type], key=lambda x: x['storage_id'],
        )
        for value in etalon_media[media_type]:
            del value['created']
    return response


async def post_retrieve(taxi_biometry_etalons):
    response = await taxi_biometry_etalons.post(
        'service/v1/retrieve',
        json={'park_id': PARK_ID, 'driver_profile_id': DRIVER_PROFILE_ID},
    )

    assert response.status_code == 200
    return prepare_response(response.json())


async def post_store(
        taxi_biometry_etalons, version, etalon_media, expected_code,
):
    response = await taxi_biometry_etalons.post(
        'service/v1/store',
        json={
            'source': 'test',
            'park_id': PARK_ID,
            'driver_profile_id': DRIVER_PROFILE_ID,
            'version': version,
            'etalon_media': etalon_media,
        },
    )

    assert response.status_code == expected_code


@pytest.mark.pgsql(
    'biometry_etalons', files=['etalons.sql', 'drivers.sql', 'media.sql'],
)
async def test_etalons_flow(taxi_biometry_etalons):
    retrieve_response = await post_retrieve(taxi_biometry_etalons)
    assert retrieve_response == {'version': 0, 'etalon_media': {}}

    # store new etalon media: add new driver etalon + etalon media
    etalon_media = {
        'selfie': [
            {
                'storage_id': 'ms0000000000000000000011',
                'storage_bucket': 'driver_photo',
            },
            {
                'storage_id': 'ms0000000000000000000012',
                'storage_bucket': 'driver_photo',
            },
        ],
    }

    await post_store(
        taxi_biometry_etalons, retrieve_response['version'], etalon_media, 200,
    )

    retrieve_response = await post_retrieve(taxi_biometry_etalons)
    assert retrieve_response == {'version': 1, 'etalon_media': etalon_media}

    # store a new etalon media voice:ms0000000000000000000013 and
    # deactivate an old etalon media photo:ms0000000000000000000012
    # with wrong version
    etalon_media = {
        'selfie': [
            {
                'storage_id': 'ms0000000000000000000011',
                'storage_bucket': 'driver_photo',
            },
        ],
        'voice': [
            {
                'storage_id': 'ms0000000000000000000013',
                'storage_bucket': 'driver_photo',
            },
        ],
    }

    await post_store(
        taxi_biometry_etalons,
        retrieve_response['version'] + 1,
        etalon_media,
        409,
    )

    # store a new etalon media voice:ms0000000000000000000013 and
    # deactivate an old etalon media photo:ms0000000000000000000012
    await post_store(
        taxi_biometry_etalons, retrieve_response['version'], etalon_media, 200,
    )

    retrieve_response = await post_retrieve(taxi_biometry_etalons)
    assert retrieve_response == {'version': 2, 'etalon_media': etalon_media}

    etalon_media = {}
    # deactivate all etalon's media
    await post_store(
        taxi_biometry_etalons, retrieve_response['version'], etalon_media, 200,
    )

    retrieve_response = await post_retrieve(taxi_biometry_etalons)
    assert retrieve_response == {'version': 3, 'etalon_media': etalon_media}
