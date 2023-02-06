# pylint: disable=invalid-name
import pytest

from taxi import discovery

from test_taxi_exp.helpers import experiment

PHONES = ['BAD_PHONE', '+79998886644', '+76668886644']
PHONE_IDS = [
    '8acf3a0383de4fd9a6d8866e6c218284',
    '7dd39170d35b47169771f508f3b0fdba',
    '6134ca6ac4754dcaaa566c853e9b8bc7',
]
EXPERIMENT_NAME = 'test_convert_phones'
MATCH_PREDICATE = {
    'type': 'in_set',
    'init': {
        'set': PHONES,
        'set_elem_type': 'string',
        'arg_name': 'phone_id',
        'transform': 'replace_phone_to_personal_phone_id',
    },
}


@pytest.mark.config(
    TVM_RULES=[{'src': 'taxi_exp', 'dst': 'personal'}],
    EXP3_ADMIN_CONFIG={
        'settings': {'common': {'in_set_max_elements_count': 100}},
        'features': {'common': {'enable_convert_phone_to_phone_id': True}},
    },
)
@pytest.mark.pgsql('taxi_exp', files=['default.sql'])
async def test_bad_phones_in_replace(
        taxi_exp_client, patch_aiohttp_session, response_mock, mockserver,
):
    @patch_aiohttp_session(
        '{}v1/countries/list'.format(
            discovery.find_service('territories').url,
        ),
    )
    def _countries_from_territories(method, url, **kwargs):
        return response_mock(
            json={
                'countries': [
                    {
                        '_id': 'aaaaa',
                        'phone_code': '7',
                        'phone_min_length': 11,
                        'phone_max_length': 11,
                        'national_access_code': '7',
                    },
                ],
            },
        )

    @mockserver.json_handler('/personal/v1/phones/bulk_store')
    async def _phone_ids_from_personal(request):
        return {
            'items': [
                {'id': phone_id, 'value': phone}
                for phone_id, phone in zip(PHONE_IDS, PHONES)
                if phone is not None
            ],
        }

    # fail experiment
    response = await taxi_exp_client.post(
        '/v1/experiments/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': EXPERIMENT_NAME},
        json=experiment.generate(
            name=EXPERIMENT_NAME, match_predicate=MATCH_PREDICATE,
        ),
    )
    assert response.status == 400
    data = await response.json()
    assert data['code'] == 'UNABLE_TO_TRANSFORM'
    assert (
        data['message'] == """Unable to transform: Bad phones: ['BAD_PHONE']"""
    )
