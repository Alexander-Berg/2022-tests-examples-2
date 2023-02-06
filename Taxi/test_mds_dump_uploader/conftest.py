# pylint: disable=redefined-outer-name
import pytest

import mds_dump_uploader.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['mds_dump_uploader.generated.service.pytest_plugins']


@pytest.fixture  # noqa: F405
def simple_secdist(simple_secdist):
    simple_secdist['settings_override'].update(
        {
            'DRIVER_STATUS_MDS_S3': {
                'url': 's3.mds.yandex.net',
                'bucket': 'driver-status-testing',
                'access_key_id': 'access_key',
                'secret_key': 'test_ket',
            },
        },
    )
    simple_secdist.update({'TEAMCITY_AUTH_TOKEN': 'valid_teamcity_token'})
    return simple_secdist
