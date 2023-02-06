import random

import pytest

from test_abt import utils


class WebContextMock:
    def __init__(self, context, chyt_clients_mock):
        self.pg = context.pg  # pylint: disable=invalid-name
        self.sqlt = context.sqlt
        self.yt_queries = context.yt_queries
        self.chyt_clients = chyt_clients_mock
        self.config = context.config
        self.yt_wrapper = context.yt_wrapper
        self.client_taxi_exp = context.client_taxi_exp


@pytest.fixture
def mocked_web_context(web_context, chyt_clients_mock):
    return WebContextMock(web_context, chyt_clients_mock)


class RequestMock:
    def __init__(self, body):
        self.body = body


@pytest.fixture(name='mocked_web_request')
def mocked_web_request_fixture():
    def _inner(body):
        return RequestMock(body)

    return _inner


@pytest.fixture
def build_create_request(abt):
    def _inner(config_source=None):
        config_builder = None

        if config_source is None:
            config_builder = (
                abt.builders.get_mg_config_builder()
                .add_value_metric()
                .add_precomputes()
                .add_observations()
            )
            config_source = config_builder.build_yaml()

        body = {
            'metrics_group': {
                'title': 'title',
                'description': 'description',
                'owners': ['owner'],
                'scopes': ['scope_for_create'],
                'is_collapsed': False,
                'enabled': True,
                'position': 100,
                'config': config_source,
            },
        }

        return body, config_builder.build() if config_builder else None

    return _inner


@pytest.fixture
def build_update_request(abt):
    def _inner(metrics_group, config_source=None, version=None):
        new_config_builder = None

        if config_source is None:
            new_config_builder = (
                abt.builders.get_mg_config_builder()
                .add_precomputes()
                .add_ratio_metric('new_best_ratio_metric')
                .add_observations()
            )
            config_source = new_config_builder.build_yaml()

        body = {
            'metrics_group': {
                'id': metrics_group.id,
                'title': utils.add_random_prefix(metrics_group.title),
                'description': utils.add_random_prefix(
                    metrics_group.description,
                ),
                'owners': [utils.random_string()],
                'scopes': ['scope_for_update'],
                'updated_at': metrics_group.updated_at_timestring,
                'created_at': metrics_group.created_at_timestring,
                'is_collapsed': not metrics_group.is_collapsed,
                'enabled': metrics_group.enabled,
                'version': (
                    metrics_group.version if version is None else version
                ),
                'position': metrics_group.position + random.randrange(1, 1000),
                'config': config_source,
            },
        }

        return body, new_config_builder.build() if new_config_builder else None

    return _inner
