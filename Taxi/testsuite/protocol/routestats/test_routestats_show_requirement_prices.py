import pytest


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='route_additional_information_step',
    consumers=['protocol/routestats'],
    clauses=[
        {
            'title': 'route_additional_information_step',
            'value': {
                'enabled': True,
                'new_delivery_flow': True,
                'send_requirement_price_to_client': [
                    {'requirement': 'door_to_door', 'tariff': 'econom'},
                ],
            },
            'predicate': {'type': 'true'},
        },
    ],
)
def test_requirement_in_tariff_details(
        local_services_base, taxi_protocol, pricing_data_preparer, load_json,
):
    request = load_json('request.json')
    response = taxi_protocol.post('3.0/routestats', request)

    assert response.status_code == 200

    json = response.json()

    service_level_econom = [
        service_level
        for service_level in json['service_levels']
        if service_level['class'] == 'econom'
    ]
    assert len(service_level_econom) == 1

    assert 'details_tariff' in service_level_econom[0]
    details_tariff = service_level_econom[0]['details_tariff']

    requirement_item = [
        item for item in details_tariff if item['type'] == 'requirement'
    ]
    assert len(requirement_item) == 1
    assert 'value' in requirement_item[0]
    assert requirement_item[0]['type_details'] == 'door_to_door'

    service_levels_not_econom = [
        service_level
        for service_level in json['service_levels']
        if service_level['class'] != 'econom'
    ]
    assert service_levels_not_econom

    for service_level in service_levels_not_econom:
        if 'details_tariff' in service_level:
            for item in service_level['details_tariff']:
                assert item['type'] != 'requirement'


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='route_additional_information_step',
    consumers=['protocol/routestats'],
    clauses=[
        {
            'title': 'route_additional_information_step',
            'value': {'enabled': True, 'new_delivery_flow': False},
            'predicate': {'type': 'true'},
        },
    ],
)
def test_new_flow_off_no_requirement(
        local_services_base, taxi_protocol, pricing_data_preparer, load_json,
):
    request = load_json('request.json')
    response = taxi_protocol.post('3.0/routestats', request)

    assert response.status_code == 200

    json = response.json()

    for service_level in json['service_levels']:
        if 'details_tariff' in service_level:
            details_tariff = service_level['details_tariff']
            for item in details_tariff:
                assert item['type'] != 'requirement'
                assert 'type_details' not in item
