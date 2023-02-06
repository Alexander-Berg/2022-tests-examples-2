import pytest


@pytest.fixture(name='vehicles')
def _mock_vehicles(mockserver):
    class DriverProfilesContext:
        def __init__(self):
            self.brandings_by_carid = {}
            self.retrieve_by_driver_id = None
            self.vehicles_cache_retrieve = None

        @staticmethod
        def build_mock_car_id(dbid_uuid):
            return dbid_uuid.replace('_', '') + 'vehicle'

        def set_branding(self, dbid_uuid, branding):
            self.brandings_by_carid[
                self.build_mock_car_id(dbid_uuid)
            ] = branding

    context = DriverProfilesContext()

    @mockserver.json_handler(
        '/driver-profiles/v1/vehicle_bindings/cars/retrieve_by_driver_id',
    )
    def _retrieve_by_driver_id(request):
        assert request.query['consumer'] == 'subvention-order-context'
        profiles = [
            {
                'park_driver_profile_id': dbid_uuid,
                'data': {'car_id': context.build_mock_car_id(dbid_uuid)},
            }
            for dbid_uuid in request.json['id_in_set']
        ]
        return {'profiles': profiles}

    @mockserver.json_handler('/fleet-vehicles/v1/vehicles/cache-retrieve')
    def _vehicles_cache_retrieve(request):
        vehicles = []
        for park_id_car_id in request.json['id_in_set']:
            car_id = park_id_car_id.split('_')[-1]
            item = {'park_id_car_id': park_id_car_id}
            branding = context.brandings_by_carid.get(car_id)
            if branding is None:
                item['data'] = {}
            else:
                item['data'] = {'amenities': branding}
                if 'lightbox' in branding:
                    item['data']['lightbox_confirmed'] = True
                if 'sticker' in branding:
                    item['data']['sticker_confirmed'] = True
            vehicles.append(item)
        return {'vehicles': vehicles}

    context.retrieve_by_driver_id = _retrieve_by_driver_id
    context.vehicles_cache_retrieve = _vehicles_cache_retrieve

    return context
