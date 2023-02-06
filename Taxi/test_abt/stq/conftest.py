import pytest


class StqContextMock:
    def __init__(self, env_context, chyt_clients_mock):
        self.pg = env_context.pg  # pylint: disable=invalid-name
        self.sqlt = env_context.sqlt
        self.yt_queries = env_context.yt_queries
        self.chyt_clients = chyt_clients_mock
        self.config = env_context.config
        self.yt_wrapper = env_context.yt_wrapper
        self.client_archive_api = env_context.client_archive_api
        self.client_taxi_exp = env_context.client_taxi_exp


@pytest.fixture
def mocked_stq_context(stq_context, chyt_clients_mock):
    return StqContextMock(stq_context, chyt_clients_mock)


@pytest.fixture(name='simple_secdist')
def simple_secdist_fixture(simple_secdist):
    simple_secdist['settings_override'].update({'DAAS_TOKEN': 'oauth-token'})
    return simple_secdist
