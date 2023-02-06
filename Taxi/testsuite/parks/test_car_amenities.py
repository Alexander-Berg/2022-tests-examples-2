import pytest

from taxi_tests.utils import ordered_object


TAXIMETER_LOCALIZATION = {
    'CarHelper_ServiceType_Animals': {
        'en': 'Animals',
        'ru': 'Животные',
        'az': 'Heyvanlar',
        'fr': 'Animaux',
    },
    'CarHelper_ServiceType_Bicycle': {
        'en': 'Bike',
        'ru': 'Велосипед',
        'az': 'Velosiped',
    },
    'CarHelper_ServiceType_Conditioner': {
        'en': 'Air conditioning',
        'ru': 'Кондиционер',
        'az': 'Kondisioner',
    },
}
TAXIMETER_LOCALIZATION_AZ = {
    'CarHelper_ServiceType_Animals': {
        'en': 'Animals_az',
        'ru': 'Животные_az',
        'az': 'Heyvanlar_az',
        'fr': 'Animaux_az',
    },
    'CarHelper_ServiceType_Bicycle': {
        'en': 'Bike_az',
        'ru': 'Велосипед_az',
        'az': 'Velosiped_az',
    },
}


@pytest.mark.translations(
    taximeter_backend_driver_messages=TAXIMETER_LOCALIZATION,
)
def test_ok(taxi_parks, load_json):
    response = taxi_parks.get('/car-amenities')

    assert response.status_code == 200
    ordered_object.assert_eq(
        response.json(),
        load_json('expected_response.json'),
        [
            'amenities',
            'amenities.local_overrides',
            'amenities.basic',
            'amenities.local_overrides.translations',
        ],
    )


@pytest.mark.config(
    LOCALES_APPLICATION_TYPE_OVERRIDES={
        'aze': {
            'override_keysets': {
                'taximeter_backend_driver_messages': 'override_az',
            },
        },
    },
)
@pytest.mark.translations(
    taximeter_backend_driver_messages=TAXIMETER_LOCALIZATION,
    override_az=TAXIMETER_LOCALIZATION_AZ,
)
def test_ok_az(taxi_parks, load_json):
    response = taxi_parks.get('/car-amenities')

    assert response.status_code == 200
    ordered_object.assert_eq(
        response.json(),
        load_json('expected_response_az.json'),
        [
            'amenities',
            'amenities.local_overrides',
            'amenities.basic',
            'amenities.local_overrides.translations',
        ],
    )
