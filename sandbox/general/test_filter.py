import pytest

from sandbox.projects.yabs.release.tasks.DeployYabsCS.util.filter import get_filtered_version


FIRST_LABEL = 'first_label'
SERVICE_INFO = {
    'service_1': {
        FIRST_LABEL: True,
    },
    'service_2': {
        FIRST_LABEL: False,
    },
    'service_3': {},
}
VERSIONS_INFO = {
    'service_0': 'ver_0',
    'service_1': 'ver_1',
    'service_2': 'ver_0',
    'service_3': 'ver_1',
    'service_4': 'ver_2',
}


def _change_result(results):
    return {
        k: set(v)
        for k, v in results.items()
    }


class TestFilter(object):
    @pytest.mark.parametrize(('whitelist_labels', 'results'), [
        (
            {},
            {
                'ver_0': {'service_2'},
                'ver_1': {'service_1', 'service_3'},
                'ver_2': {'service_4'},
            },
        ),
        (
            {
                FIRST_LABEL: True,
            },
            {
                'ver_1': {'service_1'},
            },
        ),
        (
            {
                FIRST_LABEL: False,
            },
            {
                'ver_0': {'service_2'},
            },
        ),
    ])
    def test_filter_versions(self, whitelist_labels, results):
        ignored_services = ['service_0']
        res = get_filtered_version(
            versions_info=VERSIONS_INFO,
            service_labels=SERVICE_INFO,
            whitelist_labels=whitelist_labels,
            ignored_server_services=ignored_services,
        )
        assert(results == _change_result(res))
