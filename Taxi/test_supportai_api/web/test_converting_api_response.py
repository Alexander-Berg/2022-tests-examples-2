import pytest

from generated.clients_libs.supportai import supportai_lib as supportai_models

from supportai_api.generated.service.swagger.models import api as api_models

TEST_SERVICE_TICKET = (
    '3:serv:CBAQ__________9_IgUI3gEQbw:Tc0fid-P9vc-dPS_UEQcQoDtM25vXU'
    '-seEZpTLaLla8WDsG5swfFS46FQilr41TH9XHBgIVoaNC-aNFuuLqdqGB8zifyjig'
    'XReodgtA-Qy5hkJ4qv6dCpmez6bmeMl_wQxVqds35ZxfT1EWyjfHHoalP2EzS-dAem'
    '3V5k_EwBsE'
)

KEEP_LIST_FEATURES = [True, False]
KEEP_NULL_FEATURES = [True, False]
PROJECT_TO_CONVERTING_SETTINGS = {
    f'project{"_list" if keep_list else ""}{"_null" if keep_null else ""}': {
        'keep_list_features': keep_list,
        'keep_null_features': keep_null,
    }
    for keep_list in KEEP_LIST_FEATURES
    for keep_null in KEEP_NULL_FEATURES
}
PROJECT_IDS = list(PROJECT_TO_CONVERTING_SETTINGS.keys())

pytestmark = [  # pylint: disable=invalid-name
    pytest.mark.config(
        SUPPORTAI_API_INTERNAL_USERS={
            'users': [
                {
                    'tvm_service_name': 'sample_client',
                    'project_ids': PROJECT_IDS,
                },
            ],
        },
        SUPPORTAI_API_RESPONSE_CONVERTING_SETTINGS=(
            PROJECT_TO_CONVERTING_SETTINGS
        ),
        TVM_ENABLED=True,
        TVM_RULES=[{'src': 'sample_client', 'dst': 'supportai-api'}],
        TVM_SERVICES={'supportai-api': 111, 'sample_client': 222},
        TVM_API_URL='$mockserver/tvm',
    ),
    pytest.mark.usefixtures('mocked_tvm'),
    pytest.mark.pgsql(dbname='supportai_api_tokens', files=['tokens.sql']),
]


async def test_api_response_converting(
        web_app_client, mockserver, stq3_context,
):
    common_feature = supportai_models.Feature(key='common', value='some_value')
    list_feature = supportai_models.Feature(
        key='list', value=['value1', 'value2'],
    )
    null_feature = supportai_models.Feature(key='null', value=None)
    features = [common_feature, list_feature, null_feature]

    @mockserver.json_handler('supportai/supportai/v1/support')
    async def _(_):
        return supportai_models.SupportResponse(
            features=supportai_models.ResponseFeatures(
                probabilities=[], features=features,
            ),
        ).serialize()

    for project_id in PROJECT_IDS:
        converting_config = (
            stq3_context.config.SUPPORTAI_API_RESPONSE_CONVERTING_SETTINGS
        )
        keep_list = converting_config[project_id]['keep_list_features']
        keep_null = converting_config[project_id]['keep_null_features']

        api_response = await web_app_client.post(
            f'supportai-api/v1/support?project_id={project_id}',
            headers={
                'X-Ya-Service-Ticket': TEST_SERVICE_TICKET,
                'X-Real-IP': '0.0.0.0',
            },
            json=api_models.SupportRequest(
                dialog=api_models.Dialog(messages=[]), features=[],
            ).serialize(),
        )
        assert api_response.status == 200

        api_response_body = await api_response.json()
        response_features = api_response_body['features']['features']
        response_features_dict = {
            response_feature['key']: response_feature['value']
            for response_feature in response_features
        }

        if keep_list:
            assert list_feature.key in response_features_dict
            assert (
                response_features_dict[list_feature.key] == list_feature.value
            )
        else:
            assert list_feature.key not in response_features_dict

        if keep_null:
            assert null_feature.key in response_features_dict
            assert response_features_dict[null_feature.key] is None
        else:
            assert null_feature.key not in response_features_dict

        assert common_feature.key in response_features_dict
        assert (
            response_features_dict[common_feature.key] == common_feature.value
        )
