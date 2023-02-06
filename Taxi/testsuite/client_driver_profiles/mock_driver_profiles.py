import pytest

TEST_LOCK = 0


@pytest.fixture
def mock_driver_profiles(mockserver, load_json):
    class Context:
        def __init__(self, load_json):
            self.driver_profiles = load_json('driver_profiles.json')
            self.mock_retrieve_by_phone = None
            self.mock_retrieve_by_license = None
            self.mock_retrieve_by_id = None
            self._run_tests()

        @staticmethod
        def _long_id(profile):
            return f'{profile["park_id"]}_{profile["uuid"]}'

        @staticmethod
        def _filtered(dictionary, fields):
            if not fields:
                return dictionary

            result = dict(dictionary)  # deepcopy
            fields_to_retain = {}
            for field in fields:
                parts = field.split('.')[1:]  # the first part is "data"
                val = fields_to_retain
                for part in parts:
                    if part not in val:
                        val[part] = {}

                    val = val[part]

            def _del(subdict, submap):
                if not isinstance(subdict, dict):
                    return
                for key in list(subdict.keys()):
                    if not submap:
                        continue
                    elif key not in submap:
                        del subdict[key]
                    else:
                        _del(subdict[key], submap[key])

            _del(result, fields_to_retain)

            return result

        @classmethod
        def _run_tests(cls):
            global TEST_LOCK  # pylint: disable=global-statement
            if TEST_LOCK:
                return

            test_data = [
                (
                    {'key1': 'value1', 'key2': 2},
                    ['data.key1'],
                    {'key1': 'value1'},
                ),
                (
                    {'key1': 'value1', 'key2': 2},
                    ['data.key1', 'data.key10'],
                    {'key1': 'value1'},
                ),
                ({'key1': 'value1', 'key2': 2}, ['data.key10'], {}),
                (
                    {'key1': {'key2': 'value2'}},
                    ['data.key1'],
                    {'key1': {'key2': 'value2'}},
                ),
                (
                    {'key1': {'key2': 'value2', 'key3': 'value3'}},
                    ['data.key1'],
                    {'key1': {'key2': 'value2', 'key3': 'value3'}},
                ),
                (
                    {'key1': {'key2': 'value2'}},
                    ['data.key1.key2'],
                    {'key1': {'key2': 'value2'}},
                ),
                (
                    {'key1': {'key2': 'value2', 'key3': 'value3'}},
                    ['data.key1.key2'],
                    {'key1': {'key2': 'value2'}},
                ),
            ]

            for datum in test_data:
                assert cls._filtered(datum[0], datum[1]) == datum[2]
            TEST_LOCK = 1

        def get_profiles_by_ids(self, park_driver_profile_ids, fields):
            result = []
            for park_driver_profile_id in park_driver_profile_ids:
                profile = next(
                    profil
                    for profil in self.driver_profiles
                    if self._long_id(profil) == park_driver_profile_id
                )

                if profile:
                    result.append(
                        {
                            'park_driver_profile_id': self._long_id(profile),
                            'data': self._filtered(profile, fields),
                        },
                    )
            return result

        def get_profiles_by_phone(self, pd_id, fields):
            def _matches(profile, pd_id):
                return bool(
                    filter(
                        lambda x: x['pd_id'] == pd_id, profile['phone_pd_ids'],
                    ),
                )

            return [
                {
                    'park_driver_profile_id': self._long_id(profile),
                    'data': self._filtered(profile, fields),
                }
                for profile in self.driver_profiles
                if _matches(profile, pd_id)
            ]

        def get_profiles_by_license(self, pd_id, fields):
            def _matches(profile, pd_id):
                return profile.get('license', {}).get('pd_id', '') == pd_id

            return [
                {
                    'park_driver_profile_id': self._long_id(profile),
                    'data': self._filtered(profile, fields),
                }
                for profile in self.driver_profiles
                if _matches(profile, pd_id)
            ]

    context = Context(load_json)

    @mockserver.json_handler(
        '/driver-profiles/v1/driver/profiles/retrieve_by_phone',
    )
    def _retrieve_by_phone(request):
        phone_pd_ids = request.json['driver_phone_in_set']
        fields = request.json.get('projection')
        return {
            'profiles_by_phone': [
                {
                    'driver_phone': phone_pd_id,
                    'profiles': context.get_profiles_by_phone(
                        phone_pd_id, fields,
                    ),
                }
                for phone_pd_id in phone_pd_ids
            ],
        }

    @mockserver.json_handler(
        '/driver-profiles/v1/driver/profiles/retrieve_by_license',
    )
    def _retrieve_by_license(request):
        license_pd_ids = request.json['driver_license_in_set']
        fields = request.json.get('projection')
        return {
            'profiles_by_license': [
                {
                    'driver_license': license_pd_id,
                    'profiles': context.get_profiles_by_license(
                        license_pd_id, fields,
                    ),
                }
                for license_pd_id in license_pd_ids
            ],
        }

    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _retrieve_by_id(request):
        park_driver_profile_ids = request.json['id_in_set']
        fields = request.json.get('projection')
        return {
            'profiles': context.get_profiles_by_ids(
                park_driver_profile_ids, fields,
            ),
        }

    context.mock_retrieve_by_phone = _retrieve_by_phone
    context.mock_retrieve_by_license = _retrieve_by_license
    context.mock_retrieve_by_id = _retrieve_by_id

    return context
