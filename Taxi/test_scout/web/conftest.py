import asyncio
import logging
import os
import shutil
import sys
import tempfile
import time
from typing import Any
from typing import Dict
from typing import List
from typing import NamedTuple
from typing import Tuple

import grpc
import pytest

from taxi.pytest_plugins.blacksuite import service_client as blacksuite_client
from yandex.yp.service_discovery import api_pb2 as yp
from yandex.yp.service_discovery import api_pb2_grpc as yp_grpc


logger = logging.getLogger(__name__)

YP_MOCK_ADDRESS = '127.0.0.1:6500'
YP_MOCK_SECONDS_TO_STOP = None

SCOUT_GRPC_ADDRESS = '127.0.0.1:12033'

ENDPOINT_ALPHA_ADDRS_MAP = {
    'vla': [('2a02:6b8:c07:a2b:0:1315:d338:0', True)],
    'sas': [('2aff:6b8:c07:a2b:0:1315:d338:0', True)],
    'man': [
        ('ffff:6b8:c07:a2b:0:1315:d338:0', True),
        ('cccc:6b8:c07:a2b:0:1315:d338:0', False),
    ],
}
ENDPOINT_BRAVO_ADDRS_MAP = {
    'vla': [('1a02:6b8:c07:a2b:0:1315:d338:0', False)],
    'sas': [
        ('1aff:6b8:c07:a2b:0:1315:d338:0', True),
        ('11ff:6b8:c07:a2b:0:1315:d338:0', True),
        ('12ff:6b8:c07:a2b:0:1315:d338:0', True),
    ],
    'man': [
        ('1fff:6b8:c07:a2b:0:1315:d338:0', True),
        ('1ccc:6b8:c07:a2b:0:1315:d338:0', False),
    ],
}

# direct_link from tvm_get_services missmatch direct_link from tvm_get_branches
DO_NOT_USE_DIRECT_LINK_SUFFIX = 'tvm_get_services-direct_link-DONT'

CLOWNY_PERFORATOR_DATA = {
    'lxc-service': {
        'id': 1,
        'is_internal': True,
        'tvm_name': 'lxc-service',
        'direct_link': f'lxc-service-{DO_NOT_USE_DIRECT_LINK_SUFFIX}',
        'environments': [{'id': 1, 'env_type': 'production', 'tvm_id': 11}],
        'clown_service': {'clown_id': 111, 'project_id': 2111},
    },
    'multiple-endpointsets': {
        'id': 2,
        'is_internal': True,
        'tvm_name': 'multiple-endpointsets',
        'direct_link': (
            f'multiple-endpointsets-{DO_NOT_USE_DIRECT_LINK_SUFFIX}'
        ),
        'environments': [{'id': 2, 'env_type': 'production', 'tvm_id': 22}],
        'clown_service': {'clown_id': 222, 'project_id': 2111},
    },
    'no-endpointsets': {
        'id': 3,
        'is_internal': True,
        'tvm_name': 'no-endpointsets',
        'direct_link': f'no-endpointsets-{DO_NOT_USE_DIRECT_LINK_SUFFIX}',
        'environments': [{'id': 3, 'env_type': 'production', 'tvm_id': 33}],
        'clown_service': {'clown_id': 333, 'project_id': 2111},
    },
    'different-network': {
        'id': 4,
        'is_internal': True,
        'tvm_name': 'different-network',
        'direct_link': f'different-network-{DO_NOT_USE_DIRECT_LINK_SUFFIX}',
        'environments': [{'id': 4, 'env_type': 'production', 'tvm_id': 44}],
        'clown_service': {'clown_id': 444, 'project_id': 2112},
    },
    'no-network': {
        'id': 5,
        'is_internal': True,
        'tvm_name': 'no-network',
        'direct_link': f'no-network-{DO_NOT_USE_DIRECT_LINK_SUFFIX}',
        'environments': [{'id': 5, 'env_type': 'production', 'tvm_id': 55}],
        'clown_service': {'clown_id': 555, 'project_id': 2113},
    },
    'envoy-exp-alpha': {
        'id': 6,
        'is_internal': True,
        'tvm_name': 'envoy-exp-alpha',
        'direct_link': f'envoy-exp-alpha-{DO_NOT_USE_DIRECT_LINK_SUFFIX}',
        'environments': [{'id': 1, 'env_type': 'production', 'tvm_id': 66}],
        'clown_service': {'clown_id': 666, 'project_id': 2111},
    },
    'envoy-exp-bravo': {
        'id': 7,
        'is_internal': True,
        'tvm_name': 'envoy-exp-bravo',
        'direct_link': f'envoy-exp-bravo-{DO_NOT_USE_DIRECT_LINK_SUFFIX}',
        'environments': [{'id': 1, 'env_type': 'production', 'tvm_id': 77}],
        'clown_service': {'clown_id': 777, 'project_id': 2111},
    },
    'envoy-exp-charlie': {
        'id': 8,
        'is_internal': True,
        'tvm_name': 'envoy-exp-charlie',
        'direct_link': f'envoy-exp-charlie-{DO_NOT_USE_DIRECT_LINK_SUFFIX}',
        'environments': [{'id': 1, 'env_type': 'production', 'tvm_id': 88}],
        'clown_service': {'clown_id': 888, 'project_id': 2111},
    },
    'envoy-exp-delta': {
        'id': 9,
        'is_internal': True,
        'tvm_name': 'envoy-exp-delta',
        'direct_link': f'envoy-exp-delta-{DO_NOT_USE_DIRECT_LINK_SUFFIX}',
        'environments': [{'id': 1, 'env_type': 'production', 'tvm_id': 99}],
        'clown_service': {'clown_id': 999, 'project_id': 2111},
    },
}

CLOWNDUCTOR_SERVICE_INFO = {
    111: [
        {'name': 'clownductor_project', 'value': 'taxi-devops'},
        {'name': 'design_review', 'value': 'https://st.yandex-team.ru'},
        {
            'name': 'hostnames',
            'value': {
                'testing': ['lxc-service.taxi.tst.yandex.net'],
                'unstable': ['lxc-service.taxi.dev.yandex.net'],
                'production': ['lxc-service.taxi.yandex.net'],
            },
        },
        {'name': 'service_name', 'value': 'lxc-service-service-name'},
        {'name': 'service_type', 'value': 'backendpy3'},
        {
            'name': 'service_yaml_url',
            'value': 'https://github.yandex-team.ru/bla.yaml',
        },
        {'name': 'tvm_name', 'value': 'lxc-service'},
        {'name': 'wiki_path', 'value': 'https://wiki.yandex-team.ru/bla'},
    ],
    222: [
        {'name': 'clownductor_project', 'value': 'taxi-devops'},
        {'name': 'design_review', 'value': 'https://st.yandex-team.ru'},
        {
            'name': 'hostnames',
            'value': {
                'testing': ['multiple-endpointsets.taxi.tst.yandex.net'],
                'unstable': ['multiple-endpointsets.taxi.dev.yandex.net'],
                'production': ['multiple-endpointsets.taxi.yandex.net'],
            },
        },
        {
            'name': 'service_name',
            'value': 'multiple-endpointsets-service-name',
        },
        {'name': 'service_type', 'value': 'backendpy3'},
        {
            'name': 'service_yaml_url',
            'value': 'https://github.yandex-team.ru/bla.yaml',
        },
        {'name': 'tvm_name', 'value': 'multiple-endpointsets'},
        {'name': 'wiki_path', 'value': 'https://wiki.yandex-team.ru/bla'},
    ],
    333: [
        {'name': 'clownductor_project', 'value': 'taxi-devops'},
        {'name': 'design_review', 'value': 'https://st.yandex-team.ru'},
        {
            'name': 'hostnames',
            'value': {
                'testing': ['no-endpointsets.taxi.tst.yandex.net'],
                'unstable': ['no-endpointsets.taxi.dev.yandex.net'],
                'production': ['no-endpointsets.taxi.yandex.net'],
            },
        },
        {'name': 'service_name', 'value': 'no-endpointsets-service-name'},
        {'name': 'service_type', 'value': 'backendpy3'},
        {
            'name': 'service_yaml_url',
            'value': 'https://github.yandex-team.ru/bla.yaml',
        },
        {'name': 'tvm_name', 'value': 'no-endpointsets'},
        {'name': 'wiki_path', 'value': 'https://wiki.yandex-team.ru/bla'},
    ],
    444: [
        {'name': 'clownductor_project', 'value': 'taxi-devops'},
        {'name': 'design_review', 'value': 'https://st.yandex-team.ru'},
        {
            'name': 'hostnames',
            'value': {
                'testing': ['different-network.taxi.tst.yandex.net'],
                'unstable': ['different-network.taxi.dev.yandex.net'],
                'production': ['different-network.taxi.yandex.net'],
            },
        },
        {'name': 'service_name', 'value': 'different-network-service-name'},
        {'name': 'service_type', 'value': 'backendpy3'},
        {
            'name': 'service_yaml_url',
            'value': 'https://github.yandex-team.ru/bla.yaml',
        },
        {'name': 'tvm_name', 'value': 'different-network'},
        {'name': 'wiki_path', 'value': 'https://wiki.yandex-team.ru/bla'},
    ],
    555: [
        {'name': 'clownductor_project', 'value': 'taxi-devops'},
        {'name': 'design_review', 'value': 'https://st.yandex-team.ru'},
        {
            'name': 'hostnames',
            'value': {
                'testing': ['no-network.taxi.tst.yandex.net'],
                'unstable': ['no-network.taxi.dev.yandex.net'],
                'production': ['no-network.taxi.yandex.net'],
            },
        },
        {'name': 'service_name', 'value': 'no-network-service-name'},
        {'name': 'service_type', 'value': 'backendpy3'},
        {
            'name': 'service_yaml_url',
            'value': 'https://github.yandex-team.ru/bla.yaml',
        },
        {'name': 'tvm_name', 'value': 'no-network'},
        {'name': 'wiki_path', 'value': 'https://wiki.yandex-team.ru/bla'},
    ],
    666: [
        {'name': 'clownductor_project', 'value': 'taxi-devops'},
        {'name': 'design_review', 'value': 'https://st.yandex-team.ru'},
        {
            'name': 'hostnames',
            'value': {
                'testing': ['envoy-exp-alpha.taxi.tst.yandex.net'],
                'unstable': ['envoy-exp-alpha.taxi.dev.yandex.net'],
                'production': ['envoy-exp-alpha.taxi.yandex.net'],
            },
        },
        {'name': 'service_name', 'value': 'envoy-exp-alpha-service-name'},
        {'name': 'service_type', 'value': 'backendpy3'},
        {
            'name': 'service_yaml_url',
            'value': 'https://github.yandex-team.ru/bla.yaml',
        },
        {'name': 'tvm_name', 'value': 'envoy-exp-alpha'},
        {'name': 'wiki_path', 'value': 'https://wiki.yandex-team.ru/bla'},
    ],
    777: [
        {'name': 'clownductor_project', 'value': 'taxi-devops'},
        {'name': 'design_review', 'value': 'https://st.yandex-team.ru'},
        {
            'name': 'hostnames',
            'value': {
                'testing': ['envoy-exp-bravo.taxi.tst.yandex.net'],
                'unstable': ['envoy-exp-bravo.taxi.dev.yandex.net'],
                'production': ['envoy-exp-bravo.taxi.yandex.net'],
            },
        },
        {'name': 'service_name', 'value': 'envoy-exp-bravo-service-name'},
        {'name': 'service_type', 'value': 'backendpy3'},
        {
            'name': 'service_yaml_url',
            'value': 'https://github.yandex-team.ru/bla.yaml',
        },
        {'name': 'tvm_name', 'value': 'envoy-exp-bravo'},
        {'name': 'wiki_path', 'value': 'https://wiki.yandex-team.ru/bla'},
    ],
    888: [
        {'name': 'clownductor_project', 'value': 'taxi-devops'},
        {'name': 'design_review', 'value': 'https://st.yandex-team.ru'},
        {
            'name': 'hostnames',
            'value': {
                'testing': ['envoy-exp-charlie.taxi.tst.yandex.net'],
                'unstable': ['envoy-exp-charlie.taxi.dev.yandex.net'],
                'production': ['envoy-exp-charlie.taxi.yandex.net'],
            },
        },
        {'name': 'service_name', 'value': 'envoy-exp-charlie-service-name'},
        {'name': 'service_type', 'value': 'backendpy3'},
        {
            'name': 'service_yaml_url',
            'value': 'https://github.yandex-team.ru/bla.yaml',
        },
        {'name': 'tvm_name', 'value': 'envoy-exp-charlie'},
        {'name': 'wiki_path', 'value': 'https://wiki.yandex-team.ru/bla'},
    ],
    999: [
        {'name': 'clownductor_project', 'value': 'taxi-devops'},
        {'name': 'design_review', 'value': 'https://st.yandex-team.ru'},
        {
            'name': 'hostnames',
            'value': {
                'testing': ['envoy-exp-delta.taxi.tst.yandex.net'],
                'unstable': ['envoy-exp-delta.taxi.dev.yandex.net'],
                'production': ['envoy-exp-delta.taxi.yandex.net'],
            },
        },
        {'name': 'service_name', 'value': 'envoy-exp-delta-service-name'},
        {'name': 'service_type', 'value': 'backendpy3'},
        {
            'name': 'service_yaml_url',
            'value': 'https://github.yandex-team.ru/bla.yaml',
        },
        {'name': 'tvm_name', 'value': 'envoy-exp-delta'},
        {'name': 'wiki_path', 'value': 'https://wiki.yandex-team.ru/bla'},
    ],
}

CLOWNDUCTOR_SERVICE_ID_TO_TVM_NAME = {
    111: 'lxc-service',
    222: 'multiple-endpointsets',
    333: 'no-endpointsets',
    444: 'different-network',
    555: 'no-network',
    666: 'envoy-exp-alpha',
    777: 'envoy-exp-bravo',
    888: 'envoy-exp-charlie',
    999: 'envoy-exp-delta',
}

PERSISTENT_STORAGE_CONTETNT = """
tvm_name_to_endpoints:
  envoy-exp-alpha: !!python/object:scout.endpoints_cache.ClusterEndpoints
    endpoints:
    - !!python/object:scout.endpoints_cache.HostPortZone
      host: 2a02:6b8:c07:a2b:0:1315:d338:0
      port: 80
      zone: vla
      env: stable
    - !!python/object:scout.endpoints_cache.HostPortZone
      host: 2aff:6b8:c07:a2b:0:1315:d338:0
      port: 80
      zone: sas
      env: stable
    - !!python/object:scout.endpoints_cache.HostPortZone
      host: ffff:6b8:c07:a2b:0:1315:d338:0
      port: 80
      zone: man
      env: stable
    - !!python/object:scout.endpoints_cache.HostPortZone
      host: cccc:6b8:c07:a2b:0:1315:d338:0
      port: 80
      zone: man
      env: stable
    location_timestamps:
      man_stable: 1146016315935442
      sas_stable: 1146016317296681
      vla_stable: 1146016318635822
    version: 3438048951867945
tvm_name_to_domains:
  envoy-exp-bravo:
  - envoy-exp-bravo.taxi.yandex.net
  envoy-exp-charlie:
  - envoy-exp-charlie.taxi.yandex.net
  envoy-exp-delta:
  - envoy-exp-delta.taxi.yandex.net
direct_link_to_tvm_name_and_env:
  taxi_tst_envoy-exp-alpha_pre_stable: !!python/object:scout.utils.TvmEnv
    env: pre_stable
    tvm_name: envoy-exp-alpha
  taxi_tst_envoy-exp-alpha_testing: !!python/object:scout.utils.TvmEnv
    env: testing
    tvm_name: envoy-exp-alpha
  taxi_tst_envoy-exp-bravo_testing: !!python/object:scout.utils.TvmEnv
    env: testing
    tvm_name: envoy-exp-bravo
  taxi_tst_envoy-exp-charlie_testing: !!python/object:scout.utils.TvmEnv
    env: testing
    tvm_name: envoy-exp-charlie
  taxi_tst_envoy-exp-delta_testing: !!python/object:scout.utils.TvmEnv
    env: testing
    tvm_name: envoy-exp-delta
tvm_name_env_to_endpointsets:
  envoy-exp-alpha:
      pre_stable:
        - taxi_envoy_exp_alpha_service_name_pre_stable
      stable:
        - taxi_envoy_exp_alpha_service_name_stable
      testing:
        - taxi_envoy_exp_alpha_service_name_testing
direct_link_to_network:
  taxi_tst_envoy-exp-alpha_pre_stable: __stable_network_macro_project1__
  taxi_tst_envoy-exp-alpha_testing: __testing_network_macro_project1__
  taxi_tst_envoy-exp-bravo_testing: __testing_network_macro_project1__
  taxi_tst_envoy-exp-charlie_testing: __testing_network_macro_project1__
  taxi_tst_envoy-exp-delta_testing: __testing_network_macro_project1__
"""


class ClownyPerforatorMock:
    def __init__(self) -> None:
        self.non_nany_services = {111}


EndpointsMap = Dict[str, List[Tuple[str, bool]]]


# To change the endpoints map use the following code:
#   yp_discovery_mock.alpha_endpoints_map = new_map
#   yp_discovery_mock.bravo_endpoints_map = bravo_map
class YpDiscoveryMock(yp_grpc.TServiceDiscoveryServiceServicer):
    def __init__(self, address: str) -> None:
        super().__init__()
        self._grpc_server = None
        self._address = address
        self._invoked_event = asyncio.Event()
        self.alpha_timer = lambda clust_name: time.monotonic_ns()
        self.alpha_endpoints_map = ENDPOINT_ALPHA_ADDRS_MAP
        self.alpha_timer_pre = lambda clust_name: time.monotonic_ns()
        self.alpha_endpoints_map_pre: Dict = {'sas': [], 'man': [], 'vla': []}
        self.bravo_timer = lambda clust_name: time.monotonic_ns()
        self.bravo_endpoints_map = ENDPOINT_BRAVO_ADDRS_MAP

    def ResolveEndpoints(self, request, context):
        # suppress false positive pylint error
        # pylint: disable=no-member

        logger.info(f'ResolveEndpoints: "{request.endpoint_set_id}"')
        if request.endpoint_set_id == 'taxi_grpc_exception_stable':
            raise RuntimeError('Emulating gRPC server side error')

        if (
                request.endpoint_set_id
                == 'taxi_envoy_exp_alpha_service_name_stable'
        ):
            endpoints_map = self.alpha_endpoints_map
            timer = self.alpha_timer
        elif (
            request.endpoint_set_id
            == 'taxi_envoy_exp_bravo_service_name_stable'
        ):
            endpoints_map = self.bravo_endpoints_map
            timer = self.bravo_timer
        elif (
            request.endpoint_set_id
            == 'taxi_envoy_exp_alpha_service_name_pre_stable'
        ):
            endpoints_map = self.alpha_endpoints_map_pre
            timer = self.alpha_timer_pre
        else:
            return yp.TRspResolveEndpoints()

        cluster_name = request.cluster_name

        response = yp.TRspResolveEndpoints()
        response.timestamp = timer(cluster_name)
        response.endpoint_set.endpoint_set_id = request.endpoint_set_id

        if cluster_name not in endpoints_map:
            raise RuntimeError(
                'Emulating gRPC server side error for a single location. '
                'Used by the "test_endpoints_dead_locations" tests.',
            )
        for yp_address, yp_ready in endpoints_map[cluster_name]:
            addr = response.endpoint_set.endpoints.add()
            addr.id = 'unpredictable-id'
            addr.protocol = 'TCP'
            addr.fqdn = 'unpredicatble-dns-name.gencfg-c.yandex.net'
            addr.ip6_address = yp_address
            addr.port = 80
            addr.ready = yp_ready

        self._invoked_event.set()
        self._invoked_event.clear()
        return response

    def wait_for_invoke(self):
        return asyncio.create_task(self._invoked_event.wait())

    async def stop(self) -> None:
        if self._grpc_server:
            await self._grpc_server.stop(YP_MOCK_SECONDS_TO_STOP)
            self._grpc_server = None

    async def restart(self) -> None:
        await self.stop()

        self._grpc_server = grpc.aio.server()
        assert self._grpc_server

        self._grpc_server.add_insecure_port(self._address)
        yp_grpc.add_TServiceDiscoveryServiceServicer_to_server(
            self, self._grpc_server,
        )
        await self._grpc_server.start()


@pytest.fixture
async def yp_discovery_mock():
    mock = YpDiscoveryMock(YP_MOCK_ADDRESS)
    await mock.restart()
    logger.info('YpDiscovery mock server started')
    try:
        yield mock
    finally:
        await mock.stop()
        logger.info('YpDiscovery mock server stopped')


class ClownyPerforator:
    @staticmethod
    def retrieve_handler(request):
        services = []
        for tvm_name in request.json.get('tvm_names'):
            if tvm_name in CLOWNY_PERFORATOR_DATA:
                services.append(CLOWNY_PERFORATOR_DATA[tvm_name])
        return {'services': services}


class Clownductor:
    @staticmethod
    def service_values_handler(request):
        service_id = int(request.args.getone('service_id'))
        assert service_id != 0
        return {
            'subsystems': [
                {
                    'subsystem_name': 'service_info',
                    'parameters': CLOWNDUCTOR_SERVICE_INFO[service_id],
                },
            ],
        }

    @staticmethod
    def services_handler(request, non_nany_services):
        service_id = int(request.args.getone('service_id'))
        tvm_name = CLOWNDUCTOR_SERVICE_ID_TO_TVM_NAME[service_id]
        if service_id in non_nany_services:
            return [
                {
                    'id': service_id,
                    'cluster_type': 'lxc',
                    'name': '???',
                    'project_id': 2111,
                    'direct_link': (
                        f'{tvm_name}-{DO_NOT_USE_DIRECT_LINK_SUFFIX}'
                    ),
                },
            ]
        return [
            {
                'id': service_id,
                'cluster_type': 'nanny',
                'name': '???',
                'project_id': 2111,
                'direct_link': f'{tvm_name}-{DO_NOT_USE_DIRECT_LINK_SUFFIX}',
            },
        ]

    @staticmethod
    def form_branches_response(
            service_id: int,
            yp_cluster_name: str,
            add_extra_endpointset: bool,
            skip_endpointsets: bool,
    ):
        tvm_name = CLOWNDUCTOR_SERVICE_ID_TO_TVM_NAME[service_id]

        if skip_endpointsets:
            assert not add_extra_endpointset
            return [
                {
                    'id': service_id * 42,
                    'service_id': service_id,
                    'name': '???',
                    'direct_link': f'taxi_tst_{tvm_name}_{env}',
                    # clownductor uses 'prestable' env  name for pre_stable
                    'env': env.replace('_', ''),
                    'endpointsets': [],
                }
                for env in {'stable', 'testing', 'pre_stable'}
            ]

        additional_endpointsets = []
        if add_extra_endpointset:
            additional_endpointsets = [
                {
                    'id': f'taxi_{yp_cluster_name}_service_name_additional',
                    'regions': ['MAN', 'SAS', 'VLA'],
                },
            ]

        return [
            {
                'id': service_id * 42,
                'service_id': service_id,
                'name': '???',
                'direct_link': f'taxi_tst_{tvm_name}_{env}',
                # clownductor uses 'prestable' env name for pre_stable
                'env': env.replace('_', ''),
                'endpointsets': [
                    {
                        'id': f'taxi_{yp_cluster_name}_service_name_{env}',
                        'regions': ['MAN', 'SAS', 'VLA'],
                    },
                ] + additional_endpointsets,
            }
            for env in {'stable', 'testing', 'pre_stable'}
        ]

    @staticmethod
    def branches_handler(request):
        service_id = int(request.args.getone('service_id'))
        tvm_name = CLOWNDUCTOR_SERVICE_ID_TO_TVM_NAME[service_id]
        yp_cluster_name = tvm_name.replace('-', '_')
        add_extra_endpointset = service_id == 222
        skip_endpointset = service_id == 333
        return Clownductor.form_branches_response(
            service_id,
            yp_cluster_name,
            add_extra_endpointset,
            skip_endpointset,
        )

    @staticmethod
    def projects_handler(request):
        return [
            {
                'id': 2111,
                'name': 'project 1',
                'namespace_id': -1,
                'network_testing': '__testing_network_macro_project1__',
                'network_stable': '__stable_network_macro_project1__',
            },
            {
                'id': 2112,
                'name': 'project 2',
                'namespace_id': -2,
                'network_testing': '__testing_network_macro_project2__',
                'network_stable': '__stable_network_macro_project2__',
            },
            {'id': 2113, 'name': 'project 3', 'namespace_id': -3},
        ]


# pylint: disable=unused-variable
@pytest.fixture(name='mock_clowny_perforator', scope='function')
def _mock_clowny_perforator(mockserver):
    data = ClownyPerforatorMock()

    @mockserver.json_handler('/clowny-perforator/v1.0/services/retrieve')
    def retrieve_handler(request):
        return ClownyPerforator.retrieve_handler(request)

    @mockserver.json_handler('/clownductor/v1/parameters/service_values/')
    def service_values_handler(request):
        return Clownductor.service_values_handler(request)

    @mockserver.json_handler('/clownductor/v1/services/')
    def services_handler(request):
        return Clownductor.services_handler(request, data.non_nany_services)

    @mockserver.json_handler('/clownductor/v1/branches/')
    def branches_handler(request):
        return Clownductor.branches_handler(request)

    @mockserver.json_handler('/clownductor/v1/projects/')
    def projects_handler(request):
        return Clownductor.projects_handler(request)

    return data


@pytest.fixture
async def grpc_scout_channel():
    async with grpc.aio.insecure_channel(SCOUT_GRPC_ADDRESS) as channel:
        logger.info('gRPC channel opened')
        yield channel
    logger.info('gRPC channel closed')


@pytest.fixture(name='mock_tvm_rules', scope='function')
async def _mock_tvm_rules(taxi_config):
    taxi_config.set_values(
        {
            'TVM_RULES': [
                {'src': 'some', 'dst': 'envoy-exp-alpha'},
                {'src': 'envoy-exp-alpha', 'dst': 'envoy-exp-bravo'},
                {'src': 'envoy-exp-bravo', 'dst': 'envoy-exp-charlie'},
                {'src': 'envoy-exp-bravo', 'dst': 'envoy-exp-delta'},
                {'src': 'envoy-exp-bravo', 'dst': 'lxc-service'},
                {'src': 'envoy-exp-bravo', 'dst': 'multiple-endpointsets'},
                {'src': 'envoy-exp-bravo', 'dst': 'no-endpointsets'},
                {'src': 'envoy-exp-bravo', 'dst': 'different-network'},
                {'src': 'envoy-exp-bravo', 'dst': 'no-network'},
                {'src': 'scout', 'dst': 'clowny-perforator'},
                {'src': 'scout', 'dst': 'clownductor'},
                {'src': 'scout', 'dst': 'statistics'},
            ],
        },
    )


class ScoutDeps(NamedTuple):
    ensure_daemon_started: Any
    scout_web_descriptor: Any
    mocked_time: Any
    mockserver: Any
    testpoint: Any
    service_client_default_headers: Any
    service_client_options: Any
    register_daemon_scope: Any
    service_spawner: Any
    service_environment_variables: Any


@pytest.fixture(name='scout_deps', scope='function')
def _scout_deps(
        ensure_daemon_started,
        scout_web_descriptor,
        mocked_time,
        mockserver,
        testpoint,
        service_client_default_headers,
        service_client_options,
        register_daemon_scope,
        service_spawner,
        service_environment_variables,
        mock_tvm_rules,
        mock_clowny_perforator,
) -> ScoutDeps:
    return ScoutDeps(
        ensure_daemon_started=ensure_daemon_started,
        scout_web_descriptor=scout_web_descriptor,
        mocked_time=mocked_time,
        mockserver=mockserver,
        testpoint=testpoint,
        service_client_default_headers=service_client_default_headers,
        service_client_options=service_client_options,
        register_daemon_scope=register_daemon_scope,
        service_spawner=service_spawner,
        service_environment_variables=service_environment_variables,
    )


def scoped_scout(scout_deps):
    args = [
        sys.executable,
        '-m',
        'taxi.pytest_plugins.blacksuite.service_sentinel',
        'web',
        '--host',
        scout_deps.scout_web_descriptor.host,
        '--port',
        str(scout_deps.scout_web_descriptor.port),
        '--service-module',
        'scout.generated.web.run_web',
    ]

    subprocess_options = {'env': scout_deps.service_environment_variables}

    return scout_deps.register_daemon_scope(
        name=scout_deps.scout_web_descriptor.service_name,
        spawn=scout_deps.service_spawner(
            args,
            check_url=(scout_deps.scout_web_descriptor.get_url('/ping')),
            subprocess_options=subprocess_options,
        ),
    )


class PersistentStorage:
    @staticmethod
    def drop():
        shutil.rmtree(
            '/tmp/taxi-scout/persistent-storage/', ignore_errors=True,
        )

    @staticmethod
    def rewrite_to_default() -> None:
        path = '/tmp/taxi-scout/persistent-storage/v8/'
        os.makedirs(path, exist_ok=True)

        with open(os.path.join(path, 'ps_instance_0.yaml'), 'w') as file:
            file.write(PERSISTENT_STORAGE_CONTETNT)


# pylint: disable=invalid-name
@pytest.fixture(name='oneshot_service_daemon_scout_web', scope='function')
async def _oneshot_service_daemon_scout_web(scout_deps):
    # clean up before usage for more safety
    PersistentStorage.drop()

    async with scoped_scout(scout_deps) as scope:
        yield scope

    # clean up after usage
    PersistentStorage.drop()


async def taxi_scout_web_oneshot_starter(
        scout_deps, oneshot_service_daemon_scout_web,
):
    await scout_deps.ensure_daemon_started(oneshot_service_daemon_scout_web)

    headers = {
        **scout_deps.service_client_default_headers,
        scout_deps.mockserver.trace_id_header: scout_deps.mockserver.trace_id,
    }
    return blacksuite_client.AiohttpClientTestsControl(
        scout_deps.scout_web_descriptor.get_url(),
        mocked_time=scout_deps.mocked_time,
        headers=headers,
        **scout_deps.service_client_options,
    )


@pytest.fixture(scope='function')
async def taxi_scout_web_oneshot(
        mock_clowny_perforator,
        scout_deps,
        oneshot_service_daemon_scout_web,
        mock_tvm_rules,
):
    return await taxi_scout_web_oneshot_starter(
        scout_deps, oneshot_service_daemon_scout_web,
    )


@pytest.fixture(name='storage_dir')
def _storage_dir(tmpdir):
    with tempfile.TemporaryDirectory() as temp_dir:
        path = os.path.join(temp_dir, 'persistent-storage')
        os.mkdir(path)
        yield path

    assert not os.path.exists(temp_dir)
