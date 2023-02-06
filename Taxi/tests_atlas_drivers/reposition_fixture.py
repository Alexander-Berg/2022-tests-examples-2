from typing import Any
from typing import Dict

import flatbuffers
import pytest
# pylint: disable=import-error
from reposition.fbs.v1.service.bulk_state import DriverBonus
from reposition.fbs.v1.service.bulk_state import DriverResponse
from reposition.fbs.v1.service.bulk_state import GeoPoint
from reposition.fbs.v1.service.bulk_state import Request
from reposition.fbs.v1.service.bulk_state import Response


_SERVICE = '/reposition-api'
_BULK_STATE_URL = '/v1/service/bulk_state'


@pytest.fixture(name='reposition')
def _reposition(mockserver):
    class Context:
        def __init__(self):
            self.reposition: Dict[str, Any] = {}
            self.error: bool = False
            self.times_called = 0

        def set_reposition(self, reposition: Dict[str, Any]):
            self.reposition = reposition

        def set_error(self, error: bool = True):
            self.error = error

        def unpack_bulk_state_request(self, data):
            root = Request.Request.GetRootAsRequest(data, 0)
            drivers = []
            for i in range(root.DriversLength()):
                driver = root.Drivers(i)
                park_db_id = driver.ParkDbId().decode('utf-8')
                driver_profile_id = driver.DriverProfileId().decode('utf-8')
                drivers.append(
                    {
                        'park_db_id': park_db_id,
                        'driver_profile_id': driver_profile_id,
                    },
                )

            return {'drivers': drivers}

        def pack_bulk_state_response(self, data):
            builder = flatbuffers.Builder(0)

            states = []
            for state in data['states']:
                has_session = state['has_session']

                mode = state.get('mode')
                if mode:
                    mode = builder.CreateString(mode)
                submode = state.get('submode')
                if submode:
                    submode = builder.CreateString(submode)
                active = state.get('active')
                bonus = state.get('bonus')
                if bonus:
                    DriverBonus.DriverBonusStart(builder)
                    DriverBonus.DriverBonusAddUntil(builder, bonus['until'])
                    bonus = DriverBonus.DriverBonusEnd(builder)

                area_radius = state.get('area_radius')
                session_id = state.get('session_id')

                DriverResponse.DriverResponseStart(builder)
                DriverResponse.DriverResponseAddHasSession(
                    builder, has_session,
                )
                if mode:
                    DriverResponse.DriverResponseAddMode(builder, mode)
                if submode:
                    DriverResponse.DriverResponseAddSubmode(builder, submode)
                if active:
                    DriverResponse.DriverResponseAddActive(builder, active)
                if bonus:
                    DriverResponse.DriverResponseAddBonus(builder, bonus)
                if 'point' in state:
                    DriverResponse.DriverResponseAddPoint(
                        builder,
                        GeoPoint.CreateGeoPoint(
                            builder,
                            state['point']['latitude'],
                            state['point']['longitude'],
                        ),
                    )
                if session_id:
                    DriverResponse.DriverResponseAddSessionId(
                        builder, session_id,
                    )
                if 'start_point' in state:
                    DriverResponse.DriverResponseAddStartPoint(
                        builder,
                        GeoPoint.CreateGeoPoint(
                            builder,
                            state['start_point']['latitude'],
                            state['start_point']['longitude'],
                        ),
                    )
                if area_radius:
                    DriverResponse.DriverResponseAddAreaRadius(
                        builder, area_radius,
                    )

                states.append(DriverResponse.DriverResponseEnd(builder))

            Response.ResponseStartStatesVector(builder, len(states))

            for state in reversed(states):
                builder.PrependUOffsetTRelative(state)
            states = builder.EndVector(len(states))

            Response.ResponseStart(builder)
            Response.ResponseAddStates(builder, states)
            response = Response.ResponseEnd(builder)

            builder.Finish(response)

            return builder.Output()

    ctx = Context()

    @mockserver.json_handler(_SERVICE + _BULK_STATE_URL)
    def _bulk_state(request):
        ctx.times_called = ctx.times_called + 1
        if ctx.error:
            return mockserver.make_response(json='Server error', status=500)

        request_json = ctx.unpack_bulk_state_request(request.get_data())
        states = []
        for driver in request_json['drivers']:
            profile = driver['park_db_id'] + '_' + driver['driver_profile_id']
            state = (
                ctx.reposition[profile]
                if profile in ctx.reposition
                else {'has_session': False}
            )
            states.append(state)

        return mockserver.make_response(
            status=200,
            content_type='application/x-flatbuffers',
            response=ctx.pack_bulk_state_response({'states': states}),
        )

    return ctx
