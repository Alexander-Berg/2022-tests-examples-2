import bson
import pytest


PARK_ID = 'park_id1'
DRIVER_PROFILE_ID = 'driver_profile_id1'
SELFREG_ID_OK = '1111350a0f6995f754083693'
SELFREG_ID_ALREADY_COMMITTED_SAME = '4444350a0f6995f754083693'
SELFREG_ID_ALREADY_COMMITTED_DIFFER_WITH_PARK = '2222350a0f6995f754083693'
SELFREG_ID_ALREADY_COMMITTED_DIFFER_WITH_SE = '5555350a0f6995f754083693'
SELFREG_ID_MISSING = '000000000000000000000000'


async def get_profile(selfreg_id, selfreg_profiles):
    return await selfreg_profiles.find_one({'_id': bson.ObjectId(selfreg_id)})


@pytest.mark.config(SELFREG_NEW_CONTRACTOR_ALLOWED_SOURCES=['selfemployed'])
@pytest.mark.parametrize(
    'selfreg_id, expect_status',
    [
        (SELFREG_ID_OK, 200),
        (SELFREG_ID_ALREADY_COMMITTED_SAME, 200),
        (SELFREG_ID_ALREADY_COMMITTED_DIFFER_WITH_PARK, 200),
        (SELFREG_ID_ALREADY_COMMITTED_DIFFER_WITH_SE, 404),
        (SELFREG_ID_MISSING, 404),
    ],
)
async def test_new_contractor_callback(
        taxi_selfreg, mongo, mock_client_notify, selfreg_id, expect_status,
):
    @mock_client_notify('/v1/unsubscribe')
    async def _del_token(request):
        assert request.method == 'POST'
        assert request.json == {
            'client': {'client_id': f'selfreg-{selfreg_id}'},
            'service': 'taximeter',
        }
        return {}

    before_profile = await get_profile(selfreg_id, mongo.selfreg_profiles)
    if selfreg_id != SELFREG_ID_MISSING:
        before_modified_date = before_profile['modified_date']
    if selfreg_id in (
            SELFREG_ID_ALREADY_COMMITTED_DIFFER_WITH_PARK,
            SELFREG_ID_ALREADY_COMMITTED_DIFFER_WITH_SE,
    ):
        before_park_id = before_profile['park_id']
        before_driver_id = before_profile['driver_profile_id']

    request_body = {
        'selfreg_id': selfreg_id,
        'park_id': PARK_ID,
        'driver_profile_id': DRIVER_PROFILE_ID,
        'source': 'selfemployed',
    }
    response = await taxi_selfreg.post(
        '/internal/selfreg/v1/new-contractor-callback', json=request_body,
    )
    assert response.status == expect_status
    if selfreg_id == SELFREG_ID_MISSING:
        return

    after_profile = await get_profile(selfreg_id, mongo.selfreg_profiles)
    assert after_profile['is_committed'] is True

    if selfreg_id == SELFREG_ID_OK:
        assert after_profile['park_id'] == PARK_ID
        assert after_profile['driver_profile_id'] == DRIVER_PROFILE_ID
        assert after_profile['modified_date'] != before_modified_date
        assert _del_token.times_called == 1
    elif selfreg_id == SELFREG_ID_ALREADY_COMMITTED_SAME:
        assert after_profile['park_id'] == PARK_ID
        assert after_profile['driver_profile_id'] == DRIVER_PROFILE_ID
        assert after_profile['modified_date'] == before_modified_date
        assert _del_token.times_called == 1
    elif selfreg_id == SELFREG_ID_ALREADY_COMMITTED_DIFFER_WITH_PARK:
        assert after_profile['park_id'] == before_park_id
        assert after_profile['driver_profile_id'] == before_driver_id
        assert after_profile['modified_date'] == before_modified_date
        assert _del_token.times_called == 1
    elif selfreg_id == SELFREG_ID_ALREADY_COMMITTED_DIFFER_WITH_SE:
        assert after_profile['park_id'] == before_park_id
        assert after_profile['driver_profile_id'] == before_driver_id
        assert after_profile['modified_date'] == before_modified_date
        assert _del_token.times_called == 0
