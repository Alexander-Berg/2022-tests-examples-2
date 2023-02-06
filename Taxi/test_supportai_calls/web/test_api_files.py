import pytest

from supportai_calls import models as db_models

CALL_SERVICE_TO_EXTENSION = {
    db_models.CallService.IVR_FRAMEWORK: 'wav',
    db_models.CallService.VOXIMPLANT: 'mp3',
    db_models.CallService.YA_TELEPHONY: 'wav',
}

# Generated via `tvmknife unittest service -s 222 -d 111`
TEST_SERVICE_TICKET = (
    '3:serv:CBAQ__________9_IgUI3gEQbw:Tc0fid-P9vc-dPS_UEQcQoDtM25vXU'
    '-seEZpTLaLla8WDsG5swfFS46FQilr41TH9XHBgIVoaNC-aNFuuLqdqGB8zifyjig'
    'XReodgtA-Qy5hkJ4qv6dCpmez6bmeMl_wQxVqds35ZxfT1EWyjfHHoalP2EzS-dAem'
    '3V5k_EwBsE'
)

pytestmark = [  # pylint: disable=invalid-name
    pytest.mark.pgsql('supportai_calls', files=['db.sql']),
]


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'sample_client', 'dst': 'supportai-calls'}],
    TVM_SERVICES={'supportai-calls': 111, 'sample_client': 222},
    TVM_API_URL='$mockserver/tvm',
)
@pytest.mark.usefixtures('mocked_tvm')
@pytest.mark.parametrize(
    'call_service',
    [
        db_models.CallService.VOXIMPLANT,
        db_models.CallService.IVR_FRAMEWORK,
        db_models.CallService.YA_TELEPHONY,
    ],
)
@pytest.mark.parametrize('with_secret', [True, False])
async def test_get_link(web_app_client, call_service, with_secret):
    bucket_name = 'supportai-calls'
    expected_extension = CALL_SERVICE_TO_EXTENSION[call_service]
    file_basename = 'filename'
    audio_files_secret = '1234567890'
    project_slug = f'project_{call_service.value}'
    if with_secret:
        project_slug += '_with_secret'
    else:
        project_slug += '_no_secret'

    response = await web_app_client.get(
        f'/supportai-calls/v1/files/audio/{file_basename}/link'
        f'?project_slug={project_slug}',
        headers={'X-Ya-Service-Ticket': TEST_SERVICE_TICKET},
    )

    if call_service == db_models.CallService.IVR_FRAMEWORK:
        assert response.status == 204
        return

    if not with_secret:
        assert response.status == 500
        return

    expected_key = (
        f'{call_service.value}'
        f'/{project_slug}/{file_basename}{audio_files_secret}'
        f'.{expected_extension}'
    )

    expected_link = f'https://{bucket_name}.s3.yandex.net/{expected_key}'

    if call_service == db_models.CallService.VOXIMPLANT:
        assert (await response.text()) == expected_link
    else:
        assert (await response.text()) == expected_key
