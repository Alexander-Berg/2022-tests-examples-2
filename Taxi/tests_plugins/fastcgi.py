import copy
import inspect
import os

import pytest

from taxi_tests.environment.services import postgresql
from taxi_tests.utils import gensecdist
from taxi_tests.utils import service_config
from taxi_tests.utils import tracing
from taxi_tests.utils import yaml_util
from tests_plugins.daemons import service_client


def create_client_fixture(
        name,
        *,
        scope='session',
        daemon_deps=(),
        client_deps=(),
        client_class=None,
        service_headers=None,
        secdist_vars=None,
        module=None,
):
    """Creates fastcgi daemon fixture.

    Returns client fixture and installs daemon fixture into module referenced
    by modname.

    :param service_headers: request headers default to service client
    :param client_class: custom service client factory
    :param name: module name to inject fixtures into
    :param scope: daemon fixture scope, session by default
    :param daemon_deps: daemon fixture dependencies
    :param client_deps: client fixture dependencies
    :param secdist_vars: kwargs for substitution in secdist_template
    :param module: module where fixtures will be installed
    :return: client fixture
    """
    if module is None:
        module = inspect.getmodule(inspect.stack()[1][0])
    if service_headers is None:
        service_headers = {}
    if secdist_vars is None:
        secdist_vars = {}
    if client_class is None:
        client_class = service_client.ServiceClientTestsControl
    dashed = name.replace('_', '-')

    # pylint: disable=unused-variable
    @_install_fixture(module, scope='session')
    def service_yaml():
        service_yaml_path = os.path.abspath(
            os.path.join(
                os.path.dirname(module.__file__), '../../service.yaml',
            ),
        )
        return yaml_util.load_file(service_yaml_path)

    @_install_fixture(module, scope='session')
    def mongodb_local(mongodb_local_create, service_yaml):
        return mongodb_local_create(
            service_yaml.get('mongo', {}).get('collections', []),
        )

    @_install_fixture(module, scope=scope)
    def _daemon_fixture(
            register_daemon_scope,
            settings,
            request,
            mongo_host,
            mongo_collections_settings,
            redis_sentinels,
            nginx_service,
            regenerate_config,
            testsuite_session_context,
            service_spawner,
            worker_id,
    ):
        for dep in daemon_deps:
            request.getfuncargvalue(dep)

        service_desc = service_config.service_config(
            dashed, settings.TAXI_BUILD_DIR,
        )
        baseurl = _get_baseurl(settings, dashed)

        secdist_path = _make_secdist_path(
            service_desc.output_secdist_path, worker_id,
        )
        fcgi_config_path = regenerate_config(service_desc.config, secdist_path)

        updated_vars = copy.deepcopy(secdist_vars)
        updated_vars.update(
            {
                'mockserver_host': (
                    testsuite_session_context.mockserver.base_url
                ),
                'pg_connstring': postgresql.get_connection_string(worker_id),
            },
        )

        secdist = gensecdist.create_secdist(
            secdist_dev=service_desc.secdist_dev,
            secdist_template=service_desc.secdist_template,
            source_dir=service_desc.source_dir,
            mongo_host=mongo_host,
            mongo_collections_settings=mongo_collections_settings,
            redis_sentinels=redis_sentinels,
            secdist_vars=updated_vars,
        )
        gensecdist.dump_secdist(secdist_path, secdist)

        with register_daemon_scope(
                name=name,
                spawn=service_spawner(
                    ['--config=' + fcgi_config_path],
                    baseurl + 'ping',
                    settings=getattr(settings, 'fastcgi', None),
                ),
        ) as daemon_scope:
            yield daemon_scope

    @pytest.fixture
    def client_fixture(
            request,
            taxi_config,
            translations,
            settings,
            mocked_time,
            ensure_daemon_started,
            service_client_options,
            _daemon_fixture,
            trace_id,
            testpoint,
            mongodb,
            pgsql,
    ):
        for dep in client_deps:
            request.getfuncargvalue(dep)

        baseurl = _get_baseurl(settings, dashed)
        ensure_daemon_started(_daemon_fixture)

        headers = service_headers.copy()
        headers[tracing.TRACE_ID_HEADER] = trace_id

        client = client_class(
            baseurl,
            mocked_time=mocked_time,
            service_headers=headers,
            **service_client_options,
        )
        return client

    return client_fixture


def _get_baseurl(settings, name):
    return '%s%s/' % (settings.TAXI_BASE_URL, name)


def _make_secdist_path(base_path, worker_id):
    path, ext = os.path.splitext(base_path)
    return '%s_%s%s' % (path, worker_id, ext)


def _install_fixture(module, **kwargs):
    def decorator(func):
        wrapped = pytest.fixture(**kwargs)(func)
        name = kwargs.get('name', wrapped.__name__)
        if hasattr(module, name):
            raise RuntimeError(
                'Name %r is already defined in %s' % (name, module),
            )
        setattr(module, name, wrapped)
        return wrapped

    return decorator
