import datetime as dt
import enum
import json
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from tests_driver_mode_subscription import common
from tests_driver_mode_subscription import driver


_DEFAULT_WORK_MODE = 'orders'
_UNIQUE_DRIVER_ID = 'unique-driver-id'


MOSCOW_POSITION = common.Position(55.737636, 37.601434)
PERM_POSITION = common.Position(58, 56.22)
SAMARA_POSITION = common.Position(53.18, 50.11)
LONDON_POSITION = common.Position(51.5, 0)
OMSK_POSITION = common.Position(54.96, 73.38)
SPB_POSITION = common.Position(59.91, 30.30)


class ServiceError(enum.Enum):
    NoError = 1
    TimeoutError = 2
    ServerError = 3


class Scene:
    def __init__(
            self,
            profiles: Dict[driver.Profile, driver.Mode],
            udid: Optional[str] = None,
    ):
        assert profiles
        self.profiles: Dict[driver.Profile, driver.Mode] = profiles.copy()
        self.udid: str = udid or _UNIQUE_DRIVER_ID
        self.driver_mode_index_mode_set_mock: Any = None
        self.driver_trackstory_mock: Any = None
        self.yagr_raw_mock: Any = None

    def setup(
            self,
            mockserver,
            mocked_time,
            driver_authorizer=None,
            mock_dmi_set: bool = True,
            mock_dmi_history: bool = True,
            mock_driver_trackstory: bool = True,
            mock_driver_ui_profile: bool = True,
            mock_yagr_raw: bool = True,
            mock_driver_profiles: bool = True,
    ):
        if mock_dmi_set:
            self.driver_mode_index_mode_set_mock = (
                self._mock_driver_mode_index_mode_set(mockserver)
            )

        if mock_dmi_history:
            self.mock_driver_mode_index_history(mockserver, mocked_time)

        if mock_driver_trackstory:
            self.driver_trackstory_mock = self.mock_driver_trackstory(
                mockserver, MOSCOW_POSITION,
            )

        if mock_yagr_raw:
            self.yagr_raw_mock = self.mock_yagr_raw(mockserver)

        self.mock_retrieve_profiles(mockserver)
        self.mock_retrieve_uniques(mockserver)
        self.mock_driver_fix_prepare(mockserver)

        if driver_authorizer:
            for profile, _ in self.profiles.items():
                driver_authorizer.set_session(
                    db=profile.park_id(),
                    session=profile.session(),
                    driver_id=profile.profile_id(),
                )

        if mock_driver_ui_profile:
            self.mock_driver_ui_profile(mockserver)

        if mock_driver_profiles:
            self.mock_driver_profiles(mockserver)

    def mock_driver_tags(
            self,
            mockserver,
            tags: List[str],
            service_error: ServiceError = ServiceError.NoError,
    ):
        @mockserver.json_handler('/driver-tags/v1/drivers/match/profile')
        def _match_profile(request):
            request_data = json.loads(request.get_data())
            profile = driver.Profile.create(
                park_id=request_data['dbid'], profile_id=request_data['uuid'],
            )
            assert profile in self.profiles
            if service_error == ServiceError.TimeoutError:
                raise mockserver.TimeoutError()
            if service_error == ServiceError.ServerError:
                return mockserver.make_response(status=500)
            return {'tags': tags}

        return _match_profile

    def _mock_driver_mode_index_mode_set(self, mockserver):
        @mockserver.json_handler('/driver-mode-index/v1/mode/subscribe')
        def _driver_mode_index_mode_set(request):
            request_data = json.loads(request.get_data())
            # {
            #   'event_at': '2019-05-01T05:00:00+00:00',
            #   'external_ref': 'idempotency_key',
            #   'data': {
            #       'driver': {
            #           'park_id': 'dbid0',
            #           'driver_profile_id': 'uuid0'
            #       },
            #       'mode': 'orders'
            #   }
            # }
            request_driver = request_data['data']['driver']
            profile = driver.Profile.create(
                park_id=request_driver['park_id'],
                profile_id=request_driver['driver_profile_id'],
            )
            assert profile in self.profiles

            self.profiles[profile] = driver.Mode(
                work_mode=request_data['data']['work_mode'],
                started_at_iso=request_data['event_at'],
            )

            return {
                'external_ref': request_data['external_ref'],
                'data': request_data['data'],
                'event_at': self.profiles[profile].started_at_iso(),
            }

        return _driver_mode_index_mode_set

    def mock_driver_mode_index_history(self, mockserver, mocked_time):
        @mockserver.json_handler('/driver-mode-index/v1/mode/history')
        def _driver_mode_index_mode_history(request):
            request_data = json.loads(request.get_data())
            driver_data = request_data['driver']
            profile = driver.Profile.create(
                park_id=driver_data['park_id'],
                profile_id=driver_data['driver_profile_id'],
            )

            mode = self.profiles[profile]
            return common.mode_history_response(
                request=request,
                work_mode=mode.work_mode,
                mocked_time=mocked_time,
                started_at=mode.started_at_iso(),
                mode_settings=mode.mode_settings,
            )

        return _driver_mode_index_mode_history

    def mock_retrieve_uniques(self, mockserver):
        @mockserver.json_handler(
            '/unique-drivers/v1/driver/uniques/retrieve_by_profiles',
        )
        def _v1_uniques(request):
            data = json.loads(request.get_data())
            profiles = data['profile_id_in_set']
            assert len(profiles) == 1
            dbid_uuid = profiles[0]

            assert dbid_uuid in self.profiles
            return {
                'uniques': [
                    {
                        'park_driver_profile_id': dbid_uuid,
                        'data': {'unique_driver_id': self.udid},
                    },
                ],
            }

        return _v1_uniques

    def mock_retrieve_profiles(self, mockserver):
        @mockserver.json_handler(
            '/unique-drivers/v1/driver/profiles/retrieve_by_uniques',
        )
        def _v1_profiles(request):
            data = json.loads(request.get_data())
            uniques = data['id_in_set']
            assert len(uniques) == 1
            unique_driver_id = uniques[0]
            assert unique_driver_id == self.udid

            response_profiles = {
                'unique_driver_id': self.udid,
                'data': [
                    {
                        'park_id': profile.park_id(),
                        'driver_profile_id': profile.profile_id(),
                        'park_driver_profile_id': profile.dbid_uuid(),
                    }
                    for profile, _ in self.profiles.items()
                ],
            }
            return {'profiles': [response_profiles]}

    @staticmethod
    def mock_driver_fix_prepare(mockserver):
        @mockserver.json_handler('/driver-fix/v1/mode/prepare/')
        def _v1_driver_fix_mode_prepare(request):
            data = json.loads(request.get_data())
            if 'mode_settings' in data:
                return {}
            return None

        return _v1_driver_fix_mode_prepare

    async def verify_profile_modes(
            self, profiles: Dict[driver.Profile, driver.Mode],
    ):
        assert self.profiles == profiles

    @staticmethod
    def mock_yagr_raw(mockserver):
        @mockserver.json_handler('/yagr-raw/service/v2/position/store')
        def _position_store(request):
            return mockserver.make_response(
                status=200,
                headers={'X-Polling-Power-Policy': 'policy'},
                content_type='application/json',
            )

        return _position_store

    @staticmethod
    def mock_driver_trackstory(
            mockserver,
            driver_position: Optional[common.Position] = None,
            service_error: ServiceError = ServiceError.NoError,
            driver_position_time: Optional[dt.datetime] = None,
    ):
        @mockserver.json_handler('/driver-trackstory/query/positions')
        def _query_position(request):
            if service_error == ServiceError.TimeoutError:
                raise mockserver.TimeoutError()
            if service_error == ServiceError.ServerError:
                return mockserver.make_response(
                    status=500, json={'message': 'internal error'},
                )
            if driver_position:
                driver_position_timestamp = 0
                if driver_position_time:
                    driver_position_timestamp = driver_position_time.replace(
                        tzinfo=dt.timezone.utc,
                    ).timestamp()
                return {
                    'results': [
                        [
                            {
                                'position': {
                                    'lat': driver_position.lat,
                                    'lon': driver_position.lon,
                                    'timestamp': driver_position_timestamp,
                                },
                                'source': 'Adjusted',
                            },
                        ],
                    ],
                }
            return {'results': [[]]}

        return _query_position

    @staticmethod
    def mock_driver_ui_profile(mockserver):
        @mockserver.json_handler('/driver-ui-profile/v1/mode')
        def _driver_ui_profile(request):
            return mockserver.make_response('{"status": "ok"}', status=200)

    def mock_driver_profiles(self, mockserver):
        @mockserver.json_handler(
            '/driver-profiles/v1/driver/app/profiles/retrieve',
        )
        def _handler(request):
            return {
                'profiles': [
                    {
                        'park_driver_profile_id': profile.dbid_uuid(),
                        'data': {
                            'taximeter_version': '8.80 (562)',
                            'locale': profile.locale(),
                        },
                    }
                    for profile in self.profiles
                ],
            }
