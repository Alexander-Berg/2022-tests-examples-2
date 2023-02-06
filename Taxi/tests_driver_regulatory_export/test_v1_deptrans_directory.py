import json

import pytest


@pytest.mark.config(
    DEPTRANS_DIR_RETURN_DRIVER_LICENSES=True,
    DEPTRANS_BULK_REQUESTS_CHUNK_SIZE=2,
    DEPTRANS_CLASSES_WITHOUT_PERMISSION={'business': ['elite', 'vip']},
)
async def test_v1_deptrans_directory(
        taxi_driver_regulatory_export, mockserver, load_json,
):
    @mockserver.json_handler('/candidates/deptrans')
    def _mock_candidates(request):
        assert request.method == 'POST'
        data = json.loads(request.get_data())
        assert data == {
            'format': 'extended',
            'deptrans': {'classes_without_permission': ['elite', 'vip']},
        }
        return load_json('answer_extend_plus_business.json')

    @mockserver.json_handler('/personal/v1/driver_licenses/bulk_retrieve')
    def _mock_driver_license(request):
        body = json.loads(request.get_data())
        profiles = []
        for driver_id in body['items']:
            tmp = driver_id['id']
            profiles.append({'value': 'license_' + tmp, 'id': tmp})
        body = {'items': profiles}
        return mockserver.make_response(json.dumps(body), 200)

    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _mock_driver_profiles(request):
        body = json.loads(request.get_data())
        profiles = []
        for driver_id in body['id_in_set']:
            profiles.append(
                {
                    'park_driver_profile_id': driver_id,
                    'revision': '0',
                    'data': {
                        'park_id': '111',
                        'uuid': driver_id,
                        'hiring_details': {
                            'hiring_type': 'commercial',
                            'hiring_date': '1970-01-15T06:56:07.000',
                        },
                        'full_name': {
                            'first_name': 'Иван',
                            'middle_name': 'Иванович',
                            'last_name': 'Иванов',
                        },
                        'license': {'pd_id': 'number1', 'country': ''},
                        'phone_pd_ids': [{'pd_id': 'phone_pd_id_4'}],
                        'email_pd_ids': [],
                    },
                },
            )
        body = {'profiles': profiles}
        return mockserver.make_response(json.dumps(body), 200)

    response = await taxi_driver_regulatory_export.get(
        '/v1/deptrans/directory',
    )
    assert response.status_code == 200
    data = response.json()
    assert data['success']
    data = data['data']
    assert len(data) == 3
    assert data[0]['attid'] == 2823537196
    assert data[0]['reg_number'] == 'Х237УТ777'
    assert data[0]['licenseNumber'] == '159749'
    assert data[0]['hasOrder'] == 'free'
    assert (
        data[0]['driver_license']
        == 'dfe10ceb8a402ea518d8e89126044a1e8a30c1d4db37d5941fcdb7dd3c2dd166'
    )
    assert data[0]['tariff'] == 'usual'

    assert 'licenseNumber' not in data[1]
    assert data[1]['tariff'] == 'business'

    assert data[2]['licenseNumber'] == '160747'
    assert data[1]['tariff'] == 'business'
