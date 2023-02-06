import enum
import json
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from dateutil import parser

from testsuite import utils

from tests_driver_mode_subscription import driver


# generated by tvmknife: tvmknife unittest service -s 111 -d 2345
MOCK_TICKET = (
    '3:serv:CBAQ__________9_IgUIbxCpEg:IbtpYNKAUzWVDN1G5xxIq8vsGLU3avd7T0ed3gd'
    '2Y8tpEvlybiHHNkt4ObUCrKWVu863GCwcnGuv8pv316BBdjLuUni2LXVEZxB5zvpW45e18cFD'
    'Hp0oz8Gj1ucPS5rr81UaCnvHpk36ooMv-mEkGtx8TxTVBaarde_8mUljT04'
)

DRIVER_FIX_FEATURE = 'driver_fix'
TAGS_FEATURE = 'tags'
REPOSITION_FEATURE = 'reposition'
ACTIVE_TRANSPORT_FEATURE = 'active_transport'
GEOBOOKING_FEATURE = 'geobooking'
FEATURES_WITH_MODE_SETTINGS = {DRIVER_FIX_FEATURE, GEOBOOKING_FEATURE}


DEFAULT_INDEX_EXTERNAL_REF = 'default-idempotency-token'

MODE_HISTORY_CURSOR = 'cursor'
MODE_SETTINGS = {'rule_id': 'some_id', 'shift_close_time': '23:59:59+0300'}


class Position:
    def __init__(self, lat: float, lon: float):
        self.lat = lat
        self.lon = lon


def get_api_v1_headers(
        profile: driver.Profile,
        platform: str = 'android',
        version: str = '8.80 (562)',
):
    result = {
        'User-Agent': 'Taximeter 8.80 (562)',
        'X-YaTaxi-Park-Id': profile.park_id(),
        'X-YaTaxi-Driver-Profile-Id': profile.profile_id(),
        'X-Request-Application-Version': version,
        'X-Request-Application': 'taximeter',
        'X-Request-Version-Type': '',
        'X-Request-Platform': platform,
        'X-Ya-Service-Ticket': MOCK_TICKET,
    }

    return result


def mode_set_testpoint_data(
        profile: driver.Profile,
        accept_language: Optional[str],
        external_ref: str,
        active_since: str,
        mode: str,
        mode_settings: Optional[Dict] = None,
        source: Optional[str] = None,
        change_reason: Optional[str] = None,
        compensation_policy: Optional[str] = None,
):
    _compensation_policy = compensation_policy or 'forbid'
    return {
        'accept_language': accept_language,
        'external_ref': external_ref,
        'park_id_driver_profile_id': profile.dbid_uuid(),
        'mode': mode,
        'active_since': active_since,
        'mode_settings': mode_settings,
        'source': source,
        'change_reason': change_reason,
        'compensation_policy': _compensation_policy,
    }


def get_mode_history_request(request_data) -> driver.Profile:
    data = request_data['driver']
    return driver.Profile.create(data['park_id'], data['driver_profile_id'])


def mode_history_response(
        request,
        work_mode: str,
        mocked_time,
        started_at: Optional[str] = None,
        mode_settings: Optional[Dict[str, Any]] = None,
):
    request_data = json.loads(request.get_data())
    driver_profile = get_mode_history_request(request_data)
    assert request_data['begin_at'] == '1970-01-01T00:00:00+00:00'
    assert (
        utils.to_utc(parser.isoparse(request_data['end_at']))
        == mocked_time.now()
    )
    assert request_data['sort'] == 'desc'

    if not started_at:
        started_at = '2019-05-01T08:00:00+0300'

    data = {
        'driver': {
            'driver_profile_id': driver_profile.profile_id(),
            'park_id': driver_profile.park_id(),
        },
        'mode': work_mode,
    }

    if mode_settings:
        data['settings'] = mode_settings

    return {
        'docs': [
            {
                'kind': 'driver_mode_subscription',
                'external_event_ref': DEFAULT_INDEX_EXTERNAL_REF,
                'event_at': started_at,
                'data': data,
            },
        ],
        'cursor': MODE_HISTORY_CURSOR,
    }


async def get_mode(
        taxi_driver_mode_subscription, park_id: str, driver_profile_id: str,
):
    return await taxi_driver_mode_subscription.get(
        'v1/mode/get',
        params={
            'park_id': park_id,
            'driver_profile_id': driver_profile_id,
            'tz': 'Europe/Moscow',
        },
        headers={
            'User-Agent': 'Taximeter 8.90 (228)',
            'X-Ya-Service-Ticket': MOCK_TICKET,
        },
    )


async def get_available_offers(
        taxi_driver_mode_subscription,
        profile: driver.Profile,
        client_position: Optional[Position] = None,
        timezone: str = 'Europe/Moscow',
        platform: str = 'android',
        version: str = '8.80 (562)',
):
    params: Dict[str, Any] = {}
    if client_position:
        params['lat'] = client_position.lat
        params['lon'] = client_position.lon
    params['tz'] = timezone

    response = await taxi_driver_mode_subscription.get(
        'v1/view/available_offers',
        params=params,
        headers={
            **get_api_v1_headers(profile, platform, version),
            'Accept-Language': 'ru',
        },
    )
    return response


async def available_offers_diagnostics(
        taxi_driver_mode_subscription,
        park_id: str,
        driver_profile_id: str,
        position: Optional[Position] = None,
):
    position_str = ''
    if position:
        position_str += f'&lat={position.lat}&lon={position.lon}'

    response = await taxi_driver_mode_subscription.get(
        f'v1/available_offers/diagnostics?park_id={park_id}'
        f'&driver_profile_id={driver_profile_id}{position_str}',
        headers={'Accept-Language': 'ru', 'X-Ya-Service-Ticket': MOCK_TICKET},
    )
    assert response.status_code == 200

    response_json = response.json()

    driver_modes = response_json['driver_modes']
    for item in driver_modes:
        item['availability']['reasons'].sort()
        item['display']['reasons'].sort()

    return response_json


async def verify_mode(
        taxi_driver_mode_subscription,
        park_id: str,
        driver_profile_id: str,
        expected_work_mode: str,
        expected_started_at_iso: Optional[str] = None,
):
    mode_get_response = await get_mode(
        taxi_driver_mode_subscription, park_id, driver_profile_id,
    )
    assert mode_get_response.status_code == 200
    response_json = mode_get_response.json()
    assert response_json['active_mode'] == expected_work_mode
    if expected_started_at_iso is not None:
        assert response_json['active_since'] == expected_started_at_iso


async def set_mode(
        taxi_driver_mode_subscription,
        profile: driver.Profile,
        work_mode: str,
        mode_settings: Optional[Dict[str, Any]],
        set_by_session: bool,
        external_ref: Optional[str] = None,
        location_data: Optional[Dict[str, Any]] = None,
        fallback_position: Optional[Position] = None,
):
    request: Dict[str, Any] = {
        'external_ref': external_ref or 'idempotency_key',
        'mode_id': work_mode,
    }

    if mode_settings is not None:
        request['mode_settings'] = mode_settings

    if set_by_session:
        params = {'park_id': profile.park_id(), 'tz': 'Europe/Moscow'}
        headers = {**get_api_v1_headers(profile), 'Accept-Language': 'ru'}

        if location_data is not None:
            request['location_data'] = location_data

        return await taxi_driver_mode_subscription.post(
            'v1/mode/set_by_session',
            json=request,
            params=params,
            headers=headers,
        )

    # inter-service mode set
    headers = {
        'User-Agent': 'Taximeter 8.80 (562)',
        'X-Ya-Service-Ticket': MOCK_TICKET,
    }

    request['park_id'] = profile.park_id()
    request['driver_profile_id'] = profile.profile_id()

    if fallback_position:
        request['fallback_position'] = [
            fallback_position.lon,
            fallback_position.lat,
        ]

    return await taxi_driver_mode_subscription.post(
        'v1/mode/set', json=request, headers=headers,
    )


async def set_mode_by_rule_id(
        taxi_driver_mode_subscription,
        profile: driver.Profile,
        mode_rule_id: str,
        mode_settings: Optional[Dict[str, Any]],
        external_ref: Optional[str] = None,
        location_data: Optional[Dict[str, Any]] = None,
):
    request: Dict[str, Any] = {
        'external_ref': external_ref or 'idempotency_key',
        'mode_rule_id': mode_rule_id,
    }
    if mode_settings is not None:
        request['mode_settings'] = mode_settings
    if location_data is not None:
        request['location_data'] = location_data

    params = {'park_id': profile.park_id(), 'tz': 'Europe/Moscow'}
    headers = {**get_api_v1_headers(profile), 'Accept-Language': 'ru'}

    return await taxi_driver_mode_subscription.post(
        'v1/mode/set_by_session', json=request, params=params, headers=headers,
    )


async def logistic_workshifts_start(
        taxi_driver_mode_subscription,
        profile: driver.Profile,
        mode_rule_id: str,
        mode_rule_settings: Dict[str, Any],
        idempotency_token: Optional[str] = None,
):

    request: Dict[str, Any] = {
        'mode_rule_id': mode_rule_id,
        'mode_rule_settings': mode_rule_settings,
    }

    headers = {
        **get_api_v1_headers(profile),
        'Accept-Language': 'ru',
        'Timezone': 'Europe/Moscow',
    }

    if idempotency_token is not None:
        headers['X-Idempotency-Token'] = idempotency_token

    return await taxi_driver_mode_subscription.post(
        'driver/v1/logistic-workshifts/start', json=request, headers=headers,
    )


class ResetModeRequest:
    def __init__(
            self,
            supported_display_modes: Optional[List[str]] = None,
            orders_provider: Optional[str] = None,
            supported_transport_types: Optional[List[str]] = None,
            reason: str = 'low_taximeter_version',
            language: Optional[str] = 'ru',
    ):
        self._display_modes = supported_display_modes
        self._orders_provider = orders_provider
        self._transport_types = supported_transport_types
        self._reason = reason
        self._language = language

    async def post(
            self,
            taxi_driver_mode_subscription,
            driver_profile: driver.Profile,
    ):
        request: Dict[str, Any] = {'external_ref': 'idempotency_key'}

        headers = {
            'User-Agent': 'Taximeter 8.80 (562)',
            'X-Ya-Service-Ticket': MOCK_TICKET,
        }

        if self._language:
            headers['Accept-Language'] = self._language

        request['park_id'] = driver_profile.park_id()
        request['driver_profile_id'] = driver_profile.profile_id()
        if self._display_modes is not None:
            request['supported_display_modes'] = self._display_modes
        if self._orders_provider is not None:
            request['orders_provider'] = self._orders_provider
        if self._transport_types is not None:
            request['supported_transport_types'] = self._transport_types
        request['reason'] = self._reason

        return await taxi_driver_mode_subscription.post(
            'v1/mode/reset', json=request, headers=headers,
        )


async def get_mode_change_history(
        taxi_driver_mode_subscription,
        driver_profile: driver.Profile,
        cursor: Optional[str] = None,
        limit: Optional[int] = None,
        newer_than: Optional[str] = None,
        older_than: Optional[str] = None,
):
    params = {
        'park_id': driver_profile.park_id(),
        'driver_profile_id': driver_profile.profile_id(),
    }
    if cursor is not None:
        params['cursor'] = cursor
    if limit is not None:
        params['limit'] = limit
    if newer_than is not None:
        params['newer_than'] = newer_than
    if older_than is not None:
        params['older_than'] = older_than

    return await taxi_driver_mode_subscription.get(
        'v1/admin/mode/change/history',
        params=params,
        headers={'Accept-Language': 'ru', 'X-Ya-Service-Ticket': MOCK_TICKET},
    )


def build_set_mode_result(
        set_by_session: bool,
        active_mode: str,
        active_mode_type: str,
        active_since: str,
        feature_toggles: Optional[Dict[str, Any]] = None,
        taximeter_polling_policy: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    expected_response: Dict[str, Any] = {
        'active_mode': active_mode,
        'active_mode_type': active_mode_type,
        'active_since': active_since,
    }
    if set_by_session:
        expected_response['feature_toggles'] = (
            {} if feature_toggles is None else feature_toggles
        )
        expected_response['taximeter_polling_policy'] = (
            {}
            if taximeter_polling_policy is None
            else taximeter_polling_policy
        )
    return expected_response


def build_reset_mode_response(
        active_mode: str, active_mode_type: str, active_since: str,
) -> Dict[str, str]:
    return {
        'active_mode': active_mode,
        'active_mode_type': active_mode_type,
        'active_since': active_since,
    }


class ServiceError(enum.Enum):
    NoError = 1
    TimeoutError = 2
    ServerError = 3


def make_driver_tags_mock(
        mockserver,
        tags: List[str],
        expected_dbid: str,
        expected_uuid: str,
        service_error: ServiceError = ServiceError.NoError,
):
    @mockserver.json_handler('/driver-tags/v1/drivers/match/profile')
    def _match_profile(request):
        request_data = json.loads(request.get_data())
        assert request_data['dbid'] == expected_dbid
        assert request_data['uuid'] == expected_uuid
        if service_error == ServiceError.TimeoutError:
            raise mockserver.TimeoutError()
        if service_error == ServiceError.ServerError:
            return mockserver.make_response(status=500)
        return {'tags': tags}

    return _match_profile