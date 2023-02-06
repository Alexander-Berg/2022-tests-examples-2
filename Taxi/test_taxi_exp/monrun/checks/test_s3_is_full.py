# pylint: disable=protected-access
import pytest

from taxi_exp import settings
from taxi_exp.monrun.checks import s3_is_full


@pytest.mark.parametrize(
    'used_space, msg',
    [
        (None, '1; S3 stats not return used_space'),
        (
            97710505984,
            '1; S3 for taxi-exp filled is more than 90.00% (91.00%)',
        ),
        (
            103079215104,
            '2; S3 for taxi-exp filled is more than 95.00% (96.00%)',
        ),
        (10737418240, '0; S3 for taxi-exp filled 10.00% (10.00%)'),
    ],
)
async def test_check(
        used_space, msg, taxi_exp_client, patch_aiohttp_session, response_mock,
):
    taxi_exp_app = taxi_exp_client.app
    # pylint: disable=unused-variable
    @patch_aiohttp_session(settings.S3_STATS + s3_is_full.PATH_TO_STATS, 'GET')
    def mock_request(method, url, **kwargs):
        return response_mock(
            json={
                'objects_parts_count': 0,
                'updated_ts': '2019-07-30T11:14:01.932856+03:00',
                'used_space': used_space,
                'simple_objects_count': 1566,
                'name': 'taxi-experiments3',
                'service_id': 3651,
                'multipart_objects_count': 0,
                'objects_parts_size': 0,
                'simple_objects_size': used_space,
                'multipart_objects_size': 0,
            },
        )

    result = await s3_is_full._check(taxi_exp_app, s3_is_full.CHECK_NAME)
    assert result == msg
