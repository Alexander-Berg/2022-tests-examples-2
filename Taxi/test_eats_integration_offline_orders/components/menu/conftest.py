# pylint: disable=redefined-outer-name,invalid-name,comparison-with-callable
import pytest


@pytest.fixture()
def iiko_cloud_api_login():
    return '77c54078bb024d39ad5cb8193fe62035'


@pytest.fixture()
def iiko_cloud_organization_id():
    return '00000000-0000-0000-orga-00000000001'


@pytest.fixture()
def iiko_transport_mocks(
        mock_iiko_cloud,
        iiko_cloud_api_login,
        iiko_cloud_organization_id,
        load_json,
):
    class Mock:
        @mock_iiko_cloud('/api/1/access_token')
        @staticmethod
        async def iiko_cloud_access_token(request):
            api_login = request.json['apiLogin']
            assert api_login == iiko_cloud_api_login
            return getattr(
                Mock.iiko_cloud_access_token,
                'result',
                {
                    'correlationId': 'd7ca58cd-ff9a-4748-8f7e-deb19a9b14dd',
                    'token': '4e6f81a8-891b-4e35-b4ed-f4c10f9a4987',
                },
            )

        @mock_iiko_cloud('/api/1/nomenclature')
        @staticmethod
        async def iiko_cloud_nomenclature(request):
            assert request.json['organizationId'] == iiko_cloud_organization_id
            return getattr(
                Mock.iiko_cloud_nomenclature,
                'result',
                load_json('nomenclature.json'),
            )

    return Mock()
