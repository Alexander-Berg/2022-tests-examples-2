import json

import flatbuffers
import pytest

from fbs.Yandex.Taxi.Reposition.Index import Driver
from fbs.Yandex.Taxi.Reposition.Index import Response


class RepositionContext:
    def __init__(self):
        self.suitable = {}
        self.states = {}

    def reset(self):
        self.suitable = {}
        self.states = {}

    def set_mode(
            self,
            dbid,
            uuid,
            can_take_orders,
            can_take_orders_when_busy,
            reposition_check_required,
    ):
        self.states[dbid + '_' + uuid] = {
            'dbid': dbid,
            'uuid': uuid,
            'can_take_orders': can_take_orders,
            'can_take_orders_when_busy': can_take_orders_when_busy,
            'reposition_check_required': reposition_check_required,
        }

    def get_index(self):
        builder = flatbuffers.Builder(0)

        states_fbs = []

        for s in self.states.values():
            state = s.copy()
            state['driver_id'] = builder.CreateString(s['uuid'])
            state['park_db_id'] = builder.CreateString(s['dbid'])
            states_fbs.append(state)

        drivers_fbs = []

        for s in states_fbs:
            Driver.DriverStart(builder)
            Driver.DriverAddDriverId(builder, s['driver_id'])
            Driver.DriverAddParkDbId(builder, s['park_db_id'])
            Driver.DriverAddCanTakeOrders(builder, s['can_take_orders'])
            Driver.DriverAddCanTakeOrdersWhenBusy(
                builder, s['can_take_orders_when_busy'],
            )
            Driver.DriverAddRepositionCheckRequired(
                builder, s['reposition_check_required'],
            )
            drivers_fbs.append(Driver.DriverEnd(builder))

        Response.ResponseStartDriversVector(builder, len(drivers_fbs))

        for driver_fbs in drivers_fbs:
            builder.PrependUOffsetTRelative(driver_fbs)

        drivers = builder.EndVector(len(drivers_fbs))

        Response.ResponseStart(builder)
        Response.ResponseAddRevision(builder, 0)
        Response.ResponseAddDrivers(builder, drivers)
        response = Response.ResponseEnd(builder)
        builder.Finish(response)
        return builder.Output()

    def set_suitable(self, dbid, uuid, order_id, suitable=True, mode=None):
        idx = dbid + '_' + uuid + '_' + order_id
        self.suitable[idx] = {'suitable': suitable}
        if mode is not None:
            self.suitable[idx]['mode'] = mode

    def check(self, order, driver):
        check_result = self.suitable.get(
            driver['park_db_id']
            + '_'
            + driver['driver_id']
            + '_'
            + order['order_id'],
            {
                'suitable': not (
                    driver['park_db_id'] + '_' + driver['driver_id']
                    in self.states
                ),
            },
        )
        result = {
            'driver_id': driver['driver_id'],
            'park_db_id': driver['park_db_id'],
            'is_suitable': check_result['suitable'],
        }
        mode = check_result.get('mode', None)
        if mode is not None:
            result['mode'] = mode
        return result


@pytest.fixture(autouse=True)
def reposition(request, mockserver):
    reposition_context = RepositionContext()

    @mockserver.json_handler('/reposition/drivers/bulk_match_orders_drivers')
    def mock_bulk_match_orders_drivers(request):
        return [
            {
                'order_id': o['order']['order_id'],
                'drivers': [
                    reposition_context.check(o['order'], d)
                    for d in o['drivers']
                ],
            }
            for o in json.loads(request.get_data())
        ]

    @mockserver.handler('/reposition/v2/drivers/index')
    def mock_v2_drivers_index(request):
        return mockserver.make_response(
            reposition_context.get_index(),
            content_type='application/x-flatbuffers',
        )

    @mockserver.json_handler('/reposition/v1/service/events')
    def add_event(request):
        return {}

    reposition_context.reset()
    if request.node.get_marker('reposition_index'):
        for req in request.node.get_marker('reposition_index'):
            reposition_context.set_mode(**req.kwargs)

    if request.node.get_marker('reposition_suitable'):
        for req in request.node.get_marker('reposition_suitable'):
            reposition_context.set_suitable(**req.kwargs)

    yield reposition_context

    reposition_context.reset()
