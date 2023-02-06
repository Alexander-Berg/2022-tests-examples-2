import pytest

from taxi_tests.utils import ordered_object


TAXIMETER_LOCALIZATION = {
    'CarHelper_Color_Белый': {
        'en': 'White',
        'ru': 'Белый',
        'az': 'Ağ',
        'fr': 'Blanc',
    },
    'CarHelper_Color_Желтый': {'en': 'Yellow', 'ru': 'Желтый', 'az': 'Sarı'},
    'CarHelper_Color_Оранжевый': {
        'en': 'Orange',
        'ru': 'Оранжевый',
        'az': 'Narıncı',
    },
}
TAXIMETER_LOCALIZATION_AZ = {
    'CarHelper_Color_Белый': {
        'en': 'White_az',
        'ru': 'Белый_az',
        'az': 'Ağ_az',
    },
    'CarHelper_Color_Желтый': {
        'en': 'Yellow_az',
        'ru': 'Желтый_az',
        'az': 'Sarı_az',
    },
}


@pytest.mark.translations(
    taximeter_backend_driver_messages=TAXIMETER_LOCALIZATION,
)
def test_ok(taxi_parks, load_json):
    response = taxi_parks.get('/car-colors')

    assert response.status_code == 200
    ordered_object.assert_eq(
        response.json(),
        load_json('expected_response.json'),
        [
            'colors',
            'colors.basic',
            'colors.local_overrides',
            'colors.local_overrides.translations',
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
    response = taxi_parks.get('/car-colors')

    assert response.status_code == 200
    ordered_object.assert_eq(
        response.json(),
        load_json('expected_response_az.json'),
        [
            'colors',
            'colors.basic',
            'colors.local_overrides',
            'colors.local_overrides.translations',
        ],
    )
