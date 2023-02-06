import urllib

import pytest

from tests_contractor_merch import util


MUTABLE = 'by-offer-id'
IMMUTABLE = 'by-immutable-id'
FETCH_BY_IDS = {
    MUTABLE: '/feeds/v1/fetch_by_id',
    IMMUTABLE: '/feeds/v1/fetch_by_package_id',
}
HANDLERS_BY_IDS = {
    MUTABLE: '/driver/v1/contractor-merch/v1/offer/feed-id-1',
    IMMUTABLE: (
        '/driver/v1/contractor-merch/v1/'
        'offer-by-immutable-id/feeds-admin-id-1'
    ),
}

TESTS_COUNT = 4


@pytest.mark.translations(
    taximeter_backend_marketplace=util.ERROR_TRANSLATIONS,
    taximeter_backend_marketplace_custom_messages=(
        util.CUSTOM_MESSAGES_TRANSLATIONS
    ),
)
@pytest.mark.experiments3()
@pytest.mark.parametrize('offer_id_type', [MUTABLE, IMMUTABLE])
@pytest.mark.parametrize('test_id', list(range(TESTS_COUNT)))
async def test_individual_link_params(
        taxi_contractor_merch,
        load_json,
        mock_billing_replication,
        mock_driver_profiles,
        mock_driver_tags,
        mock_feeds,
        mock_fleet_antifraud,
        mock_fleet_parks,
        mock_driver_trackstory,
        mock_fleet_transactions_api,
        mock_parks_activation,
        mock_parks_replica,
        mock_personal,
        offer_id_type,
        test_id,
):
    path = f'tests/test{test_id}/'

    links = load_json(path + 'links.json')
    feeds_response = load_json(
        'responses/feeds_response_with_individual_link.json',
    )
    feeds_response['feed'][0]['payload']['meta_info'][
        'individual_link_params'
    ]['individual_link'] = links['individual_link']
    mock_feeds.set_response(feeds_response)

    mock_driver_profiles.response = load_json(
        path + 'driver_profiles_response.json',
    )

    mock_personal.responses = load_json(path + 'personal_responses.json')

    mock_fleet_transactions_api.balance = '1000'

    response = await taxi_contractor_merch.get(
        HANDLERS_BY_IDS[offer_id_type],
        headers=util.get_headers('park_id', 'driver_id'),
    )

    assert response.status == 200

    response_json = response.json()
    response_json['offer']['offer_data']['actions'][-1]['individual_link'] = (
        urllib.parse.unquote_plus(
            response_json['offer']['offer_data']['actions'][-1][
                'individual_link'
            ],
        )
    )

    assert response_json['offer']['offer_data']['actions'][-1] == {
        'type': 'individual_link',
        'link_caption': 'MANGO',
        'general_link': 'https://mango.rocks/',
        'agreement_text': 'I agree to eat MANGO',
        'individual_link': links['expected_link'],
    }

    assert mock_driver_profiles.driver_profiles.times_called == 2


@pytest.mark.translations(
    taximeter_backend_marketplace=util.ERROR_TRANSLATIONS,
    taximeter_backend_marketplace_custom_messages=(
        util.CUSTOM_MESSAGES_TRANSLATIONS
    ),
)
@pytest.mark.experiments3()
@pytest.mark.parametrize('offer_id_type', [MUTABLE, IMMUTABLE])
async def test_empty_general_link(
        taxi_contractor_merch,
        load_json,
        mock_billing_replication,
        mock_driver_profiles,
        mock_driver_tags,
        mock_feeds,
        mock_fleet_antifraud,
        mock_fleet_parks,
        mock_driver_trackstory,
        mock_fleet_transactions_api,
        mock_parks_activation,
        mock_parks_replica,
        mock_personal,
        offer_id_type,
):
    feeds_response = load_json(
        'responses/feeds_response_without_general_link.json',
    )
    mock_feeds.set_response(feeds_response)

    response = await taxi_contractor_merch.get(
        HANDLERS_BY_IDS[offer_id_type],
        headers=util.get_headers('park_id', 'driver_id'),
    )

    assert response.status == 200

    response_json = response.json()
    response_json['offer']['offer_data']['actions'][-1]['individual_link'] = (
        urllib.parse.unquote_plus(
            response_json['offer']['offer_data']['actions'][-1][
                'individual_link'
            ],
        )
    )

    assert response_json['offer']['offer_data']['actions'][-1] == {
        'agreement_text': 'I agree to eat MANGO',
        'individual_link': (
            'https://client.mango.rocks/onboard-v1/ya_taxi?name=Питер&'
            'surname=Паркер&birthDate=10.08.2001&license=5124123666&'
            'email=chelovek_pavuk@yandex.ru&phone=9999999999&'
            'externalId=park_id_driver_id&parkName=super_park1'
        ),
        'link_caption': 'MANGO',
        'type': 'individual_link',
    }


@pytest.mark.experiments3()
@pytest.mark.parametrize('offer_id_type', [MUTABLE, IMMUTABLE])
async def test_individual_link_failed_draft(
        taxi_contractor_merch,
        mockserver,
        load_json,
        mock_billing_replication,
        mock_driver_profiles,
        mock_driver_tags,
        mock_feeds,
        mock_fleet_antifraud,
        mock_fleet_parks,
        mock_fleet_transactions_api,
        mock_fleet_vehicles,
        mock_driver_trackstory,
        mock_contractor_merch_payments,
        mock_parks_activation,
        mock_parks_replica,
        mock_personal,
        offer_id_type,
):
    path = 'tests/test4/'
    links = load_json(path + 'links.json')
    feeds_response = load_json(
        'responses/feeds_response_with_individual_link.json',
    )
    feeds_response['feed'][0]['payload']['meta_info'][
        'individual_link_params'
    ]['individual_link'] = links['individual_link']

    mock_driver_profiles.response = load_json(
        path + 'driver_profiles_response.json',
    )
    mock_personal.responses = load_json(path + 'personal_responses.json')
    mock_contractor_merch_payments.fail_draft()
    mock_feeds.set_response(feeds_response)
    mock_fleet_transactions_api.balance = '1000'

    response = await taxi_contractor_merch.get(
        HANDLERS_BY_IDS[offer_id_type],
        headers=util.get_headers('park_id', 'driver_id'),
    )

    assert response.status == 200

    response_json = response.json()
    assert not response_json['is_available']
    assert not response_json['is_avaliable']
    assert response_json['problem_description'] == {
        'code': 'payment_draft_failed',
        'localized_message': (
            'На вашем балансе недостаточно средств для совершения покупки'
        ),
    }

    assert mock_driver_profiles.driver_profiles.times_called == 1


@pytest.mark.experiments3()
@pytest.mark.parametrize('offer_id_type', [MUTABLE, IMMUTABLE])
async def test_individual_link_merchant_id_to_draft(
        taxi_contractor_merch,
        mockserver,
        load_json,
        mock_billing_replication,
        mock_driver_profiles,
        mock_driver_tags,
        mock_feeds,
        mock_fleet_antifraud,
        mock_fleet_parks,
        mock_fleet_transactions_api,
        mock_fleet_vehicles,
        mock_driver_trackstory,
        mock_contractor_merch_payments,
        mock_parks_activation,
        mock_parks_replica,
        mock_personal,
        offer_id_type,
):
    path = 'tests/test4/'
    links = load_json(path + 'links.json')
    feeds_response = load_json(
        'responses/feeds_response_with_individual_link.json',
    )
    feeds_response['feed'][0]['payload']['meta_info'][
        'individual_link_params'
    ]['individual_link'] = links['individual_link']
    feeds_response['feed'][0]['payload']['meta_info']['merchant_id'] = 'Farsh'

    mock_driver_profiles.response = load_json(
        path + 'driver_profiles_response.json',
    )
    mock_personal.responses = load_json(path + 'personal_responses.json')
    mock_feeds.set_response(feeds_response)
    mock_fleet_transactions_api.balance = '1000'

    response = await taxi_contractor_merch.get(
        HANDLERS_BY_IDS[offer_id_type],
        headers=util.get_headers('park_id', 'driver_id'),
    )

    assert response.status == 200
    assert (
        mock_contractor_merch_payments.draft.next_call()['request'].json[
            'merchant_id'
        ]
        == 'Farsh'
    )
