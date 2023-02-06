import pytest


@pytest.mark.pgsql('strongbox', files=['test_secrets.sql'])
@pytest.mark.parametrize(
    'tmv_service, tvm_ticket, expected_status, expected_response',
    [
        ('replication-testing', 'good-ticket', 200, {'secrets': []}),
        ('replication', 'bad-ticket', 401, None),
        (
            'replication',
            'good-ticket',
            200,
            {
                'secrets': [
                    {
                        'secret_key': 'TVM_ACCESS_SECRET',
                        'yav_value': [{'key': 'top', 'value': 'secret'}],
                    },
                ],
            },
        ),
    ],
)
@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[
        {'src': 'replication-testing', 'dst': 'taxi-strongbox'},
        {'src': 'replication', 'dst': 'taxi-strongbox'},
    ],
    STRONGBOX_TVM_ACCESS={
        'services': {
            'replication': {
                'production': ['replication'],
                'testing': ['replication-testing'],
            },
        },
    },
)
async def test_secrets_yav_list(
        web_app_client,
        _tvm_mock,
        _vault_mock,
        tmv_service,
        tvm_ticket,
        expected_status,
        expected_response,
):
    _tvm_mock(tmv_service)
    _vault_mock('YAV_UUID_3')
    response = await web_app_client.post(
        '/v1/secrets/yav/list',
        headers={'X-Ya-Service-Ticket': tvm_ticket},
        json={},
    )
    data = await response.json()
    assert response.status == expected_status, data
    if expected_status == 200:
        assert data == expected_response


@pytest.fixture
def _tvm_mock(patch):
    def mock(tmv_service):
        @patch('taxi.clients.tvm.TVMClient.get_allowed_service_name')
        async def _get_allowed_service_name(ticket_body, *args, **kwargs):
            if ticket_body == b'good-ticket':
                return tmv_service
            return None

    return mock


@pytest.fixture
def _vault_mock(mockserver):
    def _make_mock(version_uuid):
        @mockserver.json_handler('/vault-api/', prefix=True)
        def _request(request):
            return mockserver.make_response(
                json={
                    'status': 'ok',
                    'version': {'value': [{'key': 'top', 'value': 'secret'}]},
                },
            )

        return _request

    return _make_mock
