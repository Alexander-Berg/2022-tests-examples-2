import pytest

from sandbox.projects.common.testenv_client.api_client import TestenvApiClient


class TestUrl(object):
    @pytest.mark.issue('BSSERVER-15394')
    @pytest.mark.issue('RMINCIDENTS-523')
    def test_projects(self):
        testenv_api_client = TestenvApiClient(base_url='http://testenv.net')
        assert testenv_api_client.projects.url == "http://testenv.net/projects/"
        assert testenv_api_client['projects/'].url == "http://testenv.net/projects/"

    def test_projects_incorrect_url(self):
        testenv_api_client = TestenvApiClient(base_url='http://testenv.net')
        assert testenv_api_client['projects'].url == "http://testenv.net/projects"

    @pytest.mark.issue('RMINCIDENTS-523')
    def test_projects_workaround(self):
        testenv_api_client = TestenvApiClient(base_url='http://testenv.net')
        # ugly `projects[""]` was left here to check backwards compatibility
        assert testenv_api_client.projects[""].url == "http://testenv.net/projects/"

    def test_project_problems(self):
        testenv_api_client = TestenvApiClient(base_url='http://testenv.net')
        assert (
            testenv_api_client.projects['yabs-2.0']['problems'].url
            == "http://testenv.net/projects/yabs-2.0/problems"
        )

    def test_lstrip_slash(self):
        testenv_api_client = TestenvApiClient(base_url='http://testenv.net')
        assert testenv_api_client.projects['/yabs-2.0'].url == "http://testenv.net/projects/yabs-2.0"
