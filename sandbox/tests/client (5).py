import pytest

import yasandbox.api.xmlrpc.tests


class TestClient(yasandbox.api.xmlrpc.tests.TestXmlrpcBase):
    @pytest.mark.usefixtures("server")
    def test__list_clients(self, api_session, client_manager):
        client = client_manager.create('test_client')
        ret = api_session.list_clients()
        assert isinstance(ret, list)
        assert isinstance(ret[0], dict)
        assert ret[0]['hostname'] == client.hostname
