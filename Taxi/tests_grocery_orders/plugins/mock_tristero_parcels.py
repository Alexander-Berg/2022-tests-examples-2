import pytest


@pytest.fixture(name='tristero_parcels')
def mock_tristero_parcels(mockserver):
    class Context:
        def __init__(self):
            self.last_state_request_body = None
            self.payload = {}
            self.parcels = []

        def set_delivered_times_called(self):
            return mock_set_delivered.times_called

        def set_state_times_called(self):
            return mock_set_state.times_called

        def get_parcels_info_times_called(self):
            return mock_parcels_info.times_called

        def last_set_state_request_body(self):
            return self.last_state_request_body

        def check_set_state(self, state, state_meta):
            self.payload['state'] = state
            self.payload['state_meta'] = state_meta

        def set_parcels(self, parcels):
            self.parcels = parcels

    context = Context()

    @mockserver.json_handler(
        '/tristero-parcels/internal/v1/parcels/v1/set-delivered',
    )
    def mock_set_delivered(request):
        assert all(':st-pa' in parcel for parcel in request.json['parcel_ids'])
        return {}

    @mockserver.json_handler(
        '/tristero-parcels/internal/v1/parcels/v1/set-state',
    )
    def mock_set_state(request):
        assert all(
            parcel.endswith(':st-pa')
            for parcel in request.json['parcel_wms_ids']
        )
        if 'state' in context.payload:
            assert request.json['state'] == context.payload['state']
        if 'state_meta' in context.payload:
            assert request.json['state_meta'] == context.payload['state_meta']
        context.last_state_request_body = request.json
        return {'parcel_wms_ids': request.json['parcel_wms_ids']}

    @mockserver.json_handler(
        '/tristero-parcels/internal/v1/parcels/v1/parcels-info',
    )
    def mock_parcels_info(request):
        parcel_ids = request.json['parcel_ids']
        assert all(parcel.endswith(':st-pa') for parcel in parcel_ids)
        return {'parcels': context.parcels}

    return context
