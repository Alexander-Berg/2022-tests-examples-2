import dataclasses
from typing import Optional

import pytest


@dataclasses.dataclass()
class AwacsRequest:
    create: Optional[dict] = None
    update: Optional[dict] = None
    delete: Optional[dict] = None


@pytest.fixture(name='make_get_domain_mock')
def _make_get_domain_mock(mockserver):
    def _wrapper(not_existing=None):
        if not not_existing:
            not_existing = []

        @mockserver.json_handler('/client-awacs/api/GetDomain/')
        def _get_domain_handler(request):
            if request.json['id'] in not_existing:
                return mockserver.make_response(status=404)
            active = False
            if request.json['id'] == 'existing':
                active = True
            return {
                'domain': {
                    'meta': {
                        'id': 'domain1',
                        'namespaceId': 'ns1',
                        'version': 'abc',
                    },
                    'spec': {
                        'yandexBalancer': {'config': {'fqdns': ['fqdn-1']}},
                    },
                    'some_unknown_field': 1,
                    'statuses': [
                        {
                            'active': {
                                'namespace_id:balancer_id': {
                                    'status': str(active),
                                },
                            },
                        },
                    ],
                },
            }

        return _get_domain_handler

    return _wrapper


@pytest.mark.parametrize(
    'cube_name, input_data, payload, extras, awacs_request',
    [
        (
            'AwacsDomainWaitFor',
            {'entry_point_id': 2, 'domain_id': 'non-existing'},
            None,
            {
                'error_message': (
                    'domain non-existing (namespace ns1) not found'
                ),
                'status': 'failed',
            },
            None,
        ),
        (
            'AwacsDomainWaitFor',
            {'entry_point_id': 2, 'domain_id': 'non-finished'},
            None,
            {'sleep_duration': 10, 'status': 'in_progress'},
            None,
        ),
        (
            'AwacsDomainWaitFor',
            {'entry_point_id': 2, 'domain_id': 'non-finished', 'wait_for': 1},
            None,
            {'sleep_duration': 1, 'status': 'in_progress'},
            None,
        ),
        (
            'AwacsDomainWaitFor',
            {'entry_point_id': 2, 'domain_id': 'existing'},
            None,
            {},
            None,
        ),
        (
            'AwacsDomainsWaitFor',
            {'namespace_id': 'ns-1', 'domain_ids': []},
            None,
            {},
            None,
        ),
        (
            'AwacsDomainChange',
            {'awacs_namespace_id': 'ns1', 'awacs_domain_id': 'domain1'},
            None,
            {},
            None,
        ),
        (
            'AwacsDomainChange',
            {
                'awacs_namespace_id': 'ns1',
                'awacs_domain_id': 'domain1',
                'new_upstreams': ['up_1', 'up_2'],
            },
            None,
            {},
            AwacsRequest(
                update={
                    'meta': {
                        'id': 'domain1',
                        'namespaceId': 'ns1',
                        'version': 'abc',
                    },
                    'order': {
                        'setUpstreams': {
                            'includeUpstreams': {
                                'ids': ['up_1', 'up_2'],
                                'type': 'BY_ID',
                            },
                        },
                    },
                },
            ),
        ),
        (
            'AwacsDomainChange',
            {
                'awacs_namespace_id': 'ns1',
                'awacs_domain_id': 'domain1',
                'new_protocol': 'https_only',
            },
            None,
            {},
            AwacsRequest(
                update={
                    'meta': {
                        'id': 'domain1',
                        'namespaceId': 'ns1',
                        'version': 'abc',
                    },
                    'order': {'setProtocol': {'protocol': 'HTTPS_ONLY'}},
                },
            ),
        ),
        (
            'AwacsDomainChange',
            {
                'awacs_namespace_id': 'ns1',
                'awacs_domain_id': 'domain1',
                'order_new_certificate': {
                    'type': 'internal',
                    'abc_service_name': 'serviceslug',
                    'name': 'abc',
                },
            },
            None,
            {},
            AwacsRequest(
                update={
                    'meta': {
                        'id': 'domain1',
                        'namespaceId': 'ns1',
                        'version': 'abc',
                    },
                    'order': {
                        'setCert': {
                            'certOrder': {
                                'content': {
                                    'caName': 'InternalCA',
                                    'commonName': 'abc',
                                },
                            },
                        },
                    },
                },
            ),
        ),
        (
            'AwacsDomainsDelete',
            {'namespace_id': 'ns1', 'domain_ids': ['domain1']},
            {'domain_ids': ['domain1']},
            {},
            AwacsRequest(
                delete={
                    'id': 'domain1',
                    'namespaceId': 'ns1',
                    'version': 'abc',
                },
            ),
        ),
        (
            'AwacsDomainChangeProtocol',
            {
                'entry_point_id': 2,
                'namespace_id': 'ns1',
                'domain_id': 'domain1',
                'new_protocol': 'https_and_http',
            },
            {'new_cert_id': 'fqdn-1'},
            {},
            AwacsRequest(
                update={
                    'meta': {
                        'id': 'domain1',
                        'namespaceId': 'ns1',
                        'version': 'abc',
                    },
                    'order': {
                        'setProtocol': {
                            'protocol': 'HTTP_AND_HTTPS',
                            'certOrder': {
                                'id': 'fqdn-1',
                                'content': {
                                    'caName': 'InternalCA',
                                    'abcServiceId': 123,
                                    'commonName': 'fqdn-1',
                                },
                            },
                            'setRedirectToHttps': {
                                'redirectToHttps': {'permanent': True},
                            },
                        },
                    },
                },
            ),
        ),
        (
            'AwacsDomainChangeProtocol',
            {
                'entry_point_id': 2,
                'namespace_id': 'ns1',
                'domain_id': 'domain1',
                'new_protocol': 'https_only',
            },
            {'new_cert_id': 'fqdn-1'},
            {},
            AwacsRequest(
                update={
                    'meta': {
                        'id': 'domain1',
                        'namespaceId': 'ns1',
                        'version': 'abc',
                    },
                    'order': {
                        'setProtocol': {
                            'protocol': 'HTTPS_ONLY',
                            'certOrder': {
                                'id': 'fqdn-1',
                                'content': {
                                    'caName': 'CertumProductionCA',
                                    'abcServiceId': 123,
                                    'commonName': 'fqdn-1',
                                },
                            },
                            'setRedirectToHttps': {
                                'redirectToHttps': {'permanent': True},
                            },
                        },
                    },
                },
            ),
        ),
    ],
)
async def test_cube(
        abc_mockserver,
        mockserver,
        get_entry_point,
        call_cube,
        cube_name,
        input_data,
        payload,
        extras,
        awacs_request,
        make_get_domain_mock,
):
    abc_mockserver()
    make_get_domain_mock(['non-existing'])

    @mockserver.json_handler('/client-awacs/api/CreateDomain/')
    def _create_domain_handler(request):
        if awacs_request is not None:
            assert awacs_request.create == request.json
        return {}

    @mockserver.json_handler('/client-awacs/api/CreateDomainOperation/')
    def _update_domain_handler(request):
        if awacs_request is not None:
            assert awacs_request.update == request.json
        return {}

    @mockserver.json_handler('/client-awacs/api/RemoveDomain/')
    def _remove_domain_handler(request):
        if awacs_request is not None:
            assert awacs_request.delete == request.json
        return {}

    @mockserver.json_handler('/client-awacs/api/GetNamespace/')
    def _get_namespace_handler(_):
        return {'namespace': {'meta': {'abcServiceId': 123}}}

    response = await call_cube(cube_name, input_data, retries=123)
    result = {'status': 'success'}
    if payload is not None:
        result['payload'] = payload
    result.update(extras)
    assert response == result

    if cube_name == 'AwacsDomainChangeProtocol':
        entry_point = await get_entry_point(input_data['entry_point_id'])
        assert entry_point.protocol.value == 'https'


@pytest.mark.parametrize(
    ['input_data', 'payload', 'awacs_request'],
    [
        (
            {'entry_point_id': 2},
            {'domain_id': 'fqdn.net'},
            AwacsRequest(
                create={
                    'meta': {'id': 'fqdn.net', 'namespaceId': 'ns1'},
                    'order': {
                        'fqdns': ['fqdn.net'],
                        'includeUpstreams': {'ids': ['ns1'], 'type': 'BY_ID'},
                        'protocol': 'HTTP_ONLY',
                    },
                },
            ),
        ),
        (
            {'entry_point_id': 2, 'domain_id': 'custom-domain-id'},
            {'domain_id': 'custom-domain-id'},
            AwacsRequest(
                create={
                    'meta': {'id': 'custom-domain-id', 'namespaceId': 'ns1'},
                    'order': {
                        'fqdns': ['fqdn.net'],
                        'includeUpstreams': {'ids': ['ns1'], 'type': 'BY_ID'},
                        'protocol': 'HTTP_ONLY',
                    },
                },
            ),
        ),
        (
            {'entry_point_id': 2, 'origin_fqdn': 'fqdn.origin.net'},
            {'domain_id': 'fqdn.net'},
            AwacsRequest(
                create={
                    'meta': {'id': 'fqdn.net', 'namespaceId': 'ns1'},
                    'order': {
                        'fqdns': ['fqdn.origin.net'],
                        'includeUpstreams': {'ids': ['ns1'], 'type': 'BY_ID'},
                        'protocol': 'HTTP_ONLY',
                    },
                },
            ),
        ),
        (
            {'entry_point_id': 2, 'domain_id': 'already-exists'},
            {'domain_id': 'already-exists'},
            AwacsRequest(),
        ),
    ],
)
async def test_awacs_domain_create(
        call_cube,
        input_data,
        payload,
        awacs_request,
        make_get_domain_mock,
        mockserver,
):
    @mockserver.json_handler('/client-awacs/api/CreateDomain/')
    def _create_domain_handler(_request):
        return {}

    get_domain_mock = make_get_domain_mock(
        ['fqdn.net', 'custom-domain-id', 'fqdn.net'],
    )
    response = await call_cube('AwacsDomainCreate', input_data)
    result = {'status': 'success', 'payload': payload}
    assert response == result
    assert get_domain_mock.times_called == 1
    if awacs_request.create:
        call = _create_domain_handler.next_call()
        assert call['_request'].json == awacs_request.create
    else:
        assert not _create_domain_handler.times_called
