import pytest


@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=[
                pytest.mark.config(
                    CARGO_CLAIMS_DENORM_READ_SETTINGS_V2={
                        '__default__': {
                            'enabled': True,
                            'yt-use-runtime': False,
                            'yt-timeout-ms': 1000,
                            'ttl-days': 3650,
                        },
                    },
                ),
            ],
        ),
        pytest.param(
            marks=[
                pytest.mark.config(
                    CARGO_CLAIMS_DENORM_READ_SETTINGS_V2={
                        '__default__': {'enabled': False},
                    },
                ),
            ],
        ),
    ],
)
async def test_segment(
        taxi_cargo_claims,
        create_segment_with_performer,
        create_default_documents,
        mds_s3_storage,
):
    segment = await create_segment_with_performer()

    create_default_documents(segment.claim_id)
    mds_s3_storage.put_object('/mds-s3/documents/someuuid', b'PDF FILE MOCK')

    response = await taxi_cargo_claims.post(
        '/v1/segments/get-document',
        json={
            'driver': {
                'driver_profile_id': 'driver_id1',
                'park_id': 'park_id1',
            },
            'document_type': 'act',
            'point_id': 1,
        },
    )
    assert response.status_code == 200
