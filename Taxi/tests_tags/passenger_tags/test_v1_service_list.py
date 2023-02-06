import pytest

from tests_tags.passenger_tags import constants


@pytest.mark.config(
    TVM_SERVICES={
        constants.TAGS_TVM_NAME: constants.TAGS_TVM_ID,
        'reposition': 2,
        'brand_new_service': 3,
        'driver-protocol': 4,
        'antifraud': 5,
        'tags-topics': 200,
        'statistics': 300,
        'sticker': 333,
        'testsuite': 18,
        'yql': 334,
    },
    TVM_RULES=[
        {'src': 'reposition', 'dst': constants.TAGS_TVM_NAME},
        {'src': 'brand_new_service', 'dst': constants.TAGS_TVM_NAME},
        # typo in config
        {'src': 'driver-protokol', 'dst': constants.TAGS_TVM_NAME},
        {'src': constants.TAGS_TVM_NAME, 'dst': 'antifraud'},
        {'src': 'testsuite', 'dst': constants.TAGS_TVM_NAME},
    ],
    TVM_ENABLED=True,
)
@pytest.mark.nofilldb()
async def test_services_list(taxi_passenger_tags, load):
    header_data = {
        'X-Ya-Service-Ticket': load(f'tvm2_ticket_18_{constants.TAGS_TVM_ID}'),
    }
    response = await taxi_passenger_tags.get(
        'v1/admin/services/list', headers=header_data,
    )
    assert response.status_code == 200
    should_be_names = ['brand_new_service', 'reposition', 'testsuite']
    response = response.json()
    assert 'names' in response
    response['names'] = sorted(response['names'])
    assert response == {'names': should_be_names}
