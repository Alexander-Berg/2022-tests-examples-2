import pytest


@pytest.mark.parametrize(
    'cube_name, input_data, payload, extras',
    [
        (
            'AwacsCertificateOrderNew',
            {
                'namespace_id': 'ns1',
                'cert_id': 'cert1',
                'type': 'EXTERNAL',
                'fqdn': 'fqdn.net',
            },
            None,
            None,
        ),
        (
            'AwacsCertificateWaitFor',
            {'namespace_id': 'ns1', 'cert_id': 'cert1'},
            None,
            None,
        ),
        (
            'AwacsCertificateWaitFor',
            {'namespace_id': 'ns1', 'cert_id': 'cert2'},
            None,
            {'status': 'in_progress', 'sleep_duration': 10},
        ),
        (
            'AwacsCertificateMetaInfo',
            {'namespace_id': 'ns1', 'cert_id': 'cert1'},
            {'sectask_ticket': 'SECTASK-1'},
            None,
        ),
        pytest.param(
            'AwacsCertificatesManyDelete',
            {'namespace_id': 'ns1', 'certificate_ids': []},
            {'deleting_certificate_ids': []},
            None,
        ),
    ],
)
async def test_cubes(
        mockserver, call_cube, cube_name, input_data, payload, extras,
):
    @mockserver.json_handler('/client-awacs/api/GetNamespace/')
    def _get_namespace_handler(_):
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

    @mockserver.json_handler('/client-awacs/api/GetCertificate/')
    def _get_certificate_handler(request):
        cert_id = request.json['id']
        return {
            'certificate': {
                'order': {
                    'status': {
                        'status': (
                            'FINISHED' if cert_id != 'cert2' else 'IN_PROGRESS'
                        ),
                    },
                },
                'spec': {
                    'certificator': {
                        'caName': 'InternalCA',
                        'approval': {'startrek': {'issueId': 'SECTASK-1'}},
                    },
                },
            },
        }

    @mockserver.json_handler('/client-awacs/api/OrderCertificate/')
    def _order_certificate_handler(request):
        assert request.json == {
            'meta': {
                'id': 'cert1',
                'namespaceId': 'ns1',
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
                'commonName': 'fqdn.net',
                'abcServiceId': 123,
            },
        }
        return {'certificate': {}}

    response = await call_cube(cube_name, input_data)
    result = {'status': 'success'}
    if payload is not None:
        result['payload'] = payload
    result.update(extras or {})
    assert response == result
