# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import pytest

from contractor_mentorship_plugins import *  # noqa: F403 F401


@pytest.fixture(name='unique_drivers')
def _uniques(mockserver):
    @mockserver.json_handler(
        '/unique-drivers/v1/driver/uniques/retrieve_by_profiles',
    )
    def _retrieve_by_profiles(request):
        return context.retrieve_by_profiles_response

    @mockserver.json_handler(
        '/unique-drivers/v1/driver/profiles/retrieve_by_uniques',
    )
    def _retrieve_by_uniques(request):
        return context.retrieve_by_uniques_response

    class FixtureContext:
        def __init__(self):
            self.retrieve_by_profiles = _retrieve_by_profiles
            self.retrieve_by_profiles_response = {'uniques': []}
            self.retrieve_by_uniques = _retrieve_by_uniques
            self.retrieve_by_uniques_response = {'profiles': []}

        def set_retrieve_by_uniques(
                self, unique_driver_id, driver_profile_id, park_id,
        ):
            self.retrieve_by_uniques_response = {
                'profiles': [
                    {
                        'unique_driver_id': (
                            unique_driver_id if unique_driver_id else 'udid'
                        ),
                        'data': [
                            {
                                'park_id': park_id if park_id else 'park_id',
                                'driver_profile_id': (
                                    driver_profile_id
                                    if driver_profile_id
                                    else 'driver_profile_id'
                                ),
                                'park_driver_profile_id': (
                                    'f{park_id}_{driver_profile_id}'
                                ),
                            },
                        ],
                    },
                ],
            }

        def set_retrieve_by_profiles(
                self, unique_driver_id, driver_profile_id, park_id,
        ):
            self.retrieve_by_profiles_response = {
                'uniques': [
                    {
                        'park_driver_profile_id': (
                            park_id + '_' + driver_profile_id
                        ),
                        'data': {'unique_driver_id': unique_driver_id},
                    },
                ],
            }

    context = FixtureContext()

    return context


@pytest.fixture(autouse=True)
def driver_profiles(mockserver):
    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _retrieve(request):
        profiles = []
        for profile_id in request.json['id_in_set']:
            profiles.append(
                {
                    'park_driver_profile_id': profile_id,
                    'data': {
                        'full_name': {
                            'first_name': 'Иван',
                            'middle_name': 'Иванович',
                            'last_name': 'Иванов',
                        },
                        'phone_pd_ids': [{'pd_id': 'phone_pd_id'}],
                    },
                },
            )
        response_body = {'profiles': profiles}
        return mockserver.make_response(status=200, json=response_body)


@pytest.fixture(autouse=True)
def mock_personal_phones(mockserver):
    @mockserver.json_handler('/personal/v1/phones/bulk_retrieve')
    def _handler2(request):
        return mockserver.make_response(
            status=200,
            json={'items': [{'id': 'phone_pd_id', 'value': '+79002222220'}]},
        )


@pytest.fixture(autouse=True)
def mock_client_events_push(request, mockserver):
    @mockserver.json_handler('/client-events/push')
    def _handler2(request_):
        if 'no_client_events_version' in request.keywords:
            return mockserver.make_response(status=200, json={})
        return mockserver.make_response(status=200, json={'version': '777'})


@pytest.fixture(autouse=True)
def mock_personal_phone_store(mockserver):
    @mockserver.json_handler('/personal/v1/phones/store')
    def _phones_store(request):
        return {
            'id': request.json['value'] + '_id',
            'value': request.json['value'],
        }


@pytest.fixture(autouse=True)
def _mock_udriver_photos(mockserver):
    @mockserver.json_handler('/udriver-photos/driver-photos/v1/fleet/photos')
    def _driver_photos_v1_fleet_photos(request):
        actual_photos = []
        for driver_udid in request.json['unique_driver_ids']:
            actual_photos.append(
                {
                    'actual_photo': {
                        'avatar_url': 'very_good_looking_person.jpg',
                        'portrait_url': (
                            'very_good_looking_person_portrait_mode.jpg'
                        ),
                    },
                    'unique_driver_id': driver_udid,
                },
            )
        response_body = {'actual_photos': actual_photos}
        return mockserver.make_response(status=200, json=response_body)


class ParksContext:
    def __init__(self):
        self.country_id = 'rus'
        self.requests = []
        self.has_error = False

    def set_response(self, country_id):
        self.country_id = country_id

    def set_error(self, value):
        self.has_error = value

    def get_requests(self):
        return self.requests


@pytest.fixture(name='fleet_parks', autouse=True)
def mock_fleet_parks(mockserver):
    context = ParksContext()

    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _list(request):
        context.requests.append(request)

        if context.has_error:
            return mockserver.make_response(
                status=500, json={'code': '500', 'message': 'lalala'},
            )

        parks = []
        for x in request.json['query']['park']['ids']:
            country_id = context.country_id
            park = {
                'id': x,
                'login': f'{x}_login',
                'name': f'{x}_name',
                'is_active': True,
                'city_id': f'{x} town',
                'locale': 'ru',
                'is_billing_enabled': True,
                'is_franchising_enabled': True,
                'country_id': country_id,
                'demo_mode': False,
                'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
            }

            parks.append(park)

        response = {'parks': parks}
        return mockserver.make_response(status=200, json=response)

    return context


@pytest.fixture(name='driver_orders', autouse=True)
def mock_driver_orders(mockserver):
    @mockserver.json_handler('/driver-orders/v1/driver/orders/has-finished')
    def _has_finished(request):
        return mockserver.make_response(
            status=200, json={'has_finished': context.has_finished_response},
        )

    class DriverOrdersContext:
        def __init__(self):
            self.has_finished = _has_finished
            self.has_finished_response = False

        def set_response(self, has_finished):
            self.has_finished_response = has_finished

    context = DriverOrdersContext()

    return context
