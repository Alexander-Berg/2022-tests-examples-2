import urllib.parse

import multidict
import pytest


def _form(request):
    charset = 'utf-8'
    items = urllib.parse.parse_qsl(
        request.get_data().rstrip().decode(charset),
        keep_blank_values=True,
        encoding=charset,
    )
    return multidict.MultiDict(items)


@pytest.fixture
def allocate_l3_addresses_mocks(mockserver):
    l3mgr_vs = [
        {
            'id': 1,
            'ip': '2a02:6b8:0:3400:0:71d:0:4af',
            'port': 80,
            'rs': [1, 2],
            'group': ['group1', 'group2'],
        },
    ]

    @mockserver.json_handler(r'/l3mgr/service/(?P<service_id>\d+)', regex=True)
    def _l3mgr_service(_, service_id):
        assert service_id == '123'
        return {'vs': l3mgr_vs, 'fqdn': 'service-fqdn.net'}

    @mockserver.json_handler(
        r'/l3mgr/abc/(?P<abc_service>\w+)/getip', regex=True,
    )
    def _get_ip(request, abc_service):
        assert abc_service == 'taxi_abc_service'
        form = _form(request)
        assert form['external'] == 'True'
        assert form['fqdn'] == 'service-fqdn.net'
        if form['v4'] == 'True':
            return {'object': '127.0.0.1'}
        return {'object': '2a02:6b8::330'}

    @mockserver.json_handler(
        r'/l3mgr/service/(?P<service_id>\d+)/vs', regex=True,
    )
    def _add_vs(request, service_id):
        assert service_id == '123'
        next_id = max(x['id'] for x in l3mgr_vs) + 1
        form = _form(request)
        form['port'] = int(form['port'])
        assert form['config-CHECK_TYPE'] == (
            'SSL_GET' if form['port'] == 443 else 'HTTP_GET'
        ), form
        l3mgr_vs.append(
            {
                'id': next_id,
                'ip': form['ip'],
                'port': form['port'],
                'rs': [int(x) for x in form.getall('rs')],
                'group': form.getall('group'),
            },
        )
        return {'object': l3mgr_vs[-1]}

    @mockserver.json_handler(
        r'/l3mgr/service/(?P<service_id>\d+)/config', regex=True,
    )
    def _create_configuration(request, service_id):
        assert service_id == '123'
        form = _form(request)
        assert form.getall('vs') == ['1', '2', '3', '4', '5']
        return {'object': {'id': 1}}

    @mockserver.json_handler(
        r'/l3mgr/service/(?P<service_id>\d+)'
        r'/config/(?P<config_id>\d+)/process',
        regex=True,
    )
    def _deploy_config(_, service_id, config_id):
        assert service_id == '123'
        assert config_id == '1'

    @mockserver.json_handler(
        r'/l3mgr/service/(?P<service_id>\d+)/config/(?P<config_id>\d+)',
        regex=True,
    )
    def _config_status(_, service_id, config_id):
        assert service_id == '123'
        assert config_id == '1'
        return {'state': 'ACTIVE'}


@pytest.fixture
def reallocate_balancer_pods_mocks(mockserver):
    @mockserver.json_handler(
        r'^/client-nanny/v2/services/(?P<service_id>[\w_-]+)/current_state/',
        regex=True,
    )
    def _state_handler(_, service_id: str):
        if service_id == 'some-long-name_man':
            return {
                'reallocation': {'state': {'message': 'DONE'}, 'id': '123abc'},
                'content': {},
                '_id': '',
                'entered': 0,
            }
        return mockserver.make_response(status=404)

    @mockserver.json_handler('/client-awacs/api/ListBalancers/')
    def _list_balancers_handler(request):
        if request.json['namespaceId'] == 'non-existing':
            return {'balancers': []}
        return {
            'balancers': [
                {
                    'meta': {
                        'id': 'existing_man',
                        'location': {
                            'yp_cluster': 'MAN',
                            'type': 'YP_CLUSTER',
                        },
                    },
                    'spec': {
                        'configTransport': {
                            'nannyStaticFile': {
                                'serviceId': 'some-long-name_man',
                            },
                        },
                    },
                },
            ],
        }

    @mockserver.json_handler(
        '/client-nanny-yp/api/yplite/pod-sets/ListPodsGroups/',
    )
    def _list_pods_groups(_):
        return {
            'podsGroups': [
                {'allocationRequest': {}, 'summaries': [{'id': 'pod-1'}]},
            ],
        }

    @mockserver.json_handler(
        '/client-nanny-yp/api/yplite/pod-reallocation/GetPodReallocationSpec/',
    )
    def _reallocation_spec(request):
        if request.json['serviceId'] == 'balancer_service_man':
            return mockserver.make_response(status=400)
        return {
            'spec': {
                'id': 'reallocation-id',
                'snapshotId': 'snapshot-id',
                'degradeParams': {
                    'maxUnavailablePods': 1,
                    'minUpdateDelaySeconds': 300,
                },
            },
        }

    @mockserver.json_handler(
        '/client-nanny-yp/api/yplite/pod-reallocation/StartPodReallocation/',
    )
    def _start_reallocation(_):
        return {'reallocationId': '123abc'}


@pytest.fixture
def open_to_world_mocks(mockserver):
    @mockserver.json_handler('/startrek/issues/TAXIADMIN-1/comments')
    def _st_create_comment(_):
        pass

    @mockserver.json_handler('/startrek/issues/TAXIADMIN-1/links')
    def _add_link(request):
        return

    @mockserver.json_handler('/client-awacs/api/GetNamespace/')
    def _awacs_get_namespace(_):
        return {
            'namespace': {
                'meta': {
                    'abcServiceId': 123,
                    'auth': {
                        'type': 'STAFF',
                        'staff': {
                            'owners': {
                                'logins': ['user1', 'user2'],
                                'groupIds': ['group1', 'group2'],
                            },
                        },
                    },
                },
            },
        }

    @mockserver.json_handler('/client-awacs/api/OrderCertificate/')
    def _awacs_order_new_certificate(request):
        assert request.json == {
            'meta': {
                'id': 'existing-cert-ext',
                'namespaceId': 'awacs-ns-1',
                'auth': {
                    'type': 'STAFF',
                    'staff': {
                        'owners': {
                            'logins': ['user1', 'user2'],
                            'groupIds': ['group1', 'group2'],
                        },
                    },
                },
            },
            'order': {
                'caName': 'CertumProductionCA',
                'commonName': 'service-fqdn.net',
                'abcServiceId': 123,
                'subjectAlternativeNames': ['external-yandex.ru'],
            },
        }
        return {'certificate': {}}

    @mockserver.json_handler('/client-awacs/api/GetCertificate/')
    def _awacs_get_cert(_):
        return {
            'certificate': {
                'order': {'status': {'status': 'FINISHED'}},
                'spec': {
                    'certificator': {
                        'caName': 'InternalCA',
                        'approval': {'startrek': {'issueId': 'SECTASK-1'}},
                    },
                },
            },
        }

    @mockserver.json_handler('/startrek/issues/SECTASK-1')
    def _st_get_ticket(_):
        return {'status': {'key': 'closed'}}

    @mockserver.json_handler('/client-awacs/api/GetDomain/')
    def _awacs_get_domain(_):
        return {
            'domain': {
                'meta': {'id': 'awacs-domain-1'},
                'spec': {
                    'yandexBalancer': {
                        'config': {'cert': {'id': 'existing-cert'}},
                    },
                },
                'statuses': [
                    {
                        'active': {
                            'awacs-ns-1:awacs-balancer-1': {'status': 'True'},
                        },
                    },
                ],
            },
        }

    @mockserver.json_handler('/client-awacs/api/CreateDomainOperation/')
    def _awacs_change_domain(_):
        return {}

    @mockserver.json_handler('/dns_api/robot-taxi-clown/primitives')
    def _dns_primitive(_):
        pass
