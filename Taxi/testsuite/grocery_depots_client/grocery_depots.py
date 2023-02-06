import pytest


DEPOT_ID_TEMPLATE = '0123456789abcdef{:028d}'
ZONE_ID_TEMPLATE = '0987654321abcdef{:06d}{:06d}'

ZONE_BASE_LON = 37.29
ZONE_BASE_LAT = 55.91
ZONE_SIZE = 0.02
ZONE_STEP = 0.01
DEPOT_DEFAULT_LOCATION = {'lon': ZONE_BASE_LON, 'lat': ZONE_BASE_LAT}


def _generate_rectange_zone(depot_id, zone_index, location=None):
    seed = depot_id * 10 + zone_index + 11
    assert seed > 10

    if location is None:
        location = DEPOT_DEFAULT_LOCATION

    left_up_angle_lon = location['lon'] - ZONE_STEP
    left_up_angle_lat = location['lat'] - ZONE_STEP

    right_up_angle_lon = left_up_angle_lon + ZONE_SIZE
    right_up_angle_lat = left_up_angle_lat

    right_down_angle_lon = right_up_angle_lon
    right_down_angle_lat = right_up_angle_lat + ZONE_SIZE

    left_down_angle_lon = left_up_angle_lon
    left_down_angle_lat = right_down_angle_lat

    return [
        {'lon': left_up_angle_lon, 'lat': left_up_angle_lat},
        {'lon': right_up_angle_lon, 'lat': right_up_angle_lat},
        {'lon': right_down_angle_lon, 'lat': right_down_angle_lat},
        {'lon': left_down_angle_lon, 'lat': left_down_angle_lat},
        {'lon': left_up_angle_lon, 'lat': left_up_angle_lat},
    ]


def _get_rectange_center(rectange):
    center_lon = round(
        (
            rectange[0]['lon']
            + rectange[1]['lon']
            + rectange[2]['lon']
            + rectange[3]['lon']
        )
        / 4,
        2,
    )

    center_lat = round(
        (
            rectange[0]['lat']
            + rectange[1]['lat']
            + rectange[2]['lat']
            + rectange[3]['lat']
        )
        / 4,
        2,
    )

    return {'lon': center_lon, 'lat': center_lat}


class DeliveryZone:
    def __init__(
            self,
            *,
            depot_test_id,
            depot_id,
            legacy_depot_id,
            zone_id=None,
            zone_index=0,
            delivery_type='pedestrian',
            status='active',
            timetable=None,
            geozone=None,
            effective_from=None,
            effective_till=None,
            zone_center=None,
    ):
        if timetable is None:
            timetable = [
                {
                    'day_type': 'Everyday',
                    'working_hours': {
                        'from': {'hour': 0, 'minute': 0},
                        'to': {'hour': 0, 'minute': 0},
                    },
                },
            ]

        if zone_id is None:
            zone_id = ZONE_ID_TEMPLATE.format(depot_test_id, zone_index)

        if geozone is None:
            assert zone_center is None
            rectange = _generate_rectange_zone(depot_test_id, zone_index)
            zone_center = _get_rectange_center(rectange)
            geozone = {'type': 'MultiPolygon', 'coordinates': [[rectange]]}

        self._zone_id = zone_id
        self._depot_id = depot_id
        self._legacy_depot_id = legacy_depot_id
        self._delivery_type = delivery_type
        self._status = status
        self._timetable = timetable
        self._geozone = geozone
        self._effective_from = effective_from
        self._effective_till = effective_till
        self._zone_center = zone_center

    def get_json(self):
        return {
            'zone_id': self._zone_id,
            'depot_id': self._depot_id,
            'legacy_depot_id': self._legacy_depot_id,
            'zone_type': self._delivery_type,
            'zone_status': self._status,
            'timetable': self._timetable,
            'geozone': self._geozone,
            'effective_till': self._effective_till,
            'effective_from': self._effective_from,
        }

    @property
    def zone_center(self):
        return self._zone_center

    @property
    def zone_center_as_array(self):
        return [self._zone_center['lon'], self._zone_center['lat']]


class GroceryDepot:
    def __init__(
            self,
            depot_test_id,
            *,
            legacy_depot_id=None,
            depot_id=None,
            country_iso3='RUS',
            country_iso2='RU',
            region_id=213,
            timezone='Europe/Moscow',
            address=None,
            tin=None,
            phone_number='+78005553535',
            email=None,
            directions=None,
            currency='RUB',
            company_id=None,
            company_type='yandex',
            allow_parcels=False,
            name=None,
            short_address=None,
            status='active',
            hidden=False,
            auto_add_zone=True,
            delivery_type='pedestrian',
            location=None,
            timetable=None,
            oebs_depot_id=None,
    ):
        zones = []
        if legacy_depot_id is None:
            legacy_depot_id = str(depot_test_id)

        if depot_id is None:
            depot_id = DEPOT_ID_TEMPLATE.format(depot_test_id)

        if auto_add_zone:
            rectange = _generate_rectange_zone(depot_test_id, 0, location)
            zone_center = _get_rectange_center(rectange)
            if location is None:
                location = zone_center
            geozone = {'type': 'MultiPolygon', 'coordinates': [[rectange]]}
            zones = [
                DeliveryZone(
                    depot_test_id=depot_test_id,
                    depot_id=depot_id,
                    legacy_depot_id=legacy_depot_id,
                    zone_index=0,
                    geozone=geozone,
                    zone_center=zone_center,
                    delivery_type=delivery_type,
                ),
            ]

        if location is None:
            location = DEPOT_DEFAULT_LOCATION

        if timetable is None:
            timetable = [
                {
                    'day_type': 'Everyday',
                    'working_hours': {
                        'from': {'hour': 7, 'minute': 0},
                        'to': {'hour': 22, 'minute': 0},
                    },
                },
            ]

        self._depot_test_id = depot_test_id
        self._depot_id = depot_id
        self._legacy_depot_id = legacy_depot_id
        self._country_iso3 = country_iso3
        self._country_iso2 = country_iso2
        self._region_id = region_id
        self._timezone = timezone
        self._location = location
        self._address = address
        self._tin = tin
        self._phone_number = phone_number
        self._email = email
        self._directions = directions
        self._currency = currency
        self._company_id = company_id
        self._company_type = company_type
        self._allow_parcels = allow_parcels
        self._name = name
        self._short_address = short_address
        self._status = status
        self._hidden = hidden
        self._zones = zones
        self._timetable = timetable
        self._oebs_depot_id = oebs_depot_id

    def get_json(self):
        return {
            'depot_id': self._depot_id,
            'legacy_depot_id': self._legacy_depot_id,
            'country_iso3': self._country_iso3,
            'country_iso2': self._country_iso2,
            'region_id': self._region_id,
            'timezone': self._timezone,
            'location': self._location,
            'address': self._address,
            'tin': self._tin,
            'phone_number': self._phone_number,
            'email': self._email,
            'directions': self._directions,
            'currency': self._currency,
            'company_id': self._company_id,
            'company_type': self._company_type,
            'allow_parcels': self._allow_parcels,
            'name': self._name,
            'short_address': self._short_address,
            'status': self._status,
            'hidden': self._hidden,
            'timetable': self._timetable,
            'oebs_depot_id': self._oebs_depot_id,
        }

    def get_zones_json(self):
        return [zone.get_json() for zone in self._zones]

    def add_zone(
            self,
            *,
            zone_id=None,
            delivery_type='pedestrian',
            status='active',
            timetable=None,
            geozone=None,
            effective_from=None,
            effective_till=None,
    ):
        self._zones.append(
            DeliveryZone(
                depot_test_id=self._depot_test_id,
                depot_id=self._depot_id,
                legacy_depot_id=self._legacy_depot_id,
                zone_id=zone_id,
                zone_index=len(self._zones),
                delivery_type=delivery_type,
                status=status,
                timetable=timetable,
                geozone=geozone,
                effective_from=effective_from,
                effective_till=effective_till,
            ),
        )
        return self._zones[-1]

    @property
    def legacy_depot_id(self):
        return self._legacy_depot_id

    @property
    def depot_id(self):
        return self._depot_id

    @property
    def location(self):
        return self._location

    @property
    def location_as_array(self):
        return [self._location['lon'], self._location['lat']]

    @property
    def phone_number(self):
        return self._phone_number


@pytest.fixture(name='grocery_depots', autouse=True)
def mock_grocery_depots(mockserver):
    depots = {}

    @mockserver.json_handler('/grocery-depots/internal/v1/depots/v1/depots')
    def mock_internal_depots(request):
        legacy_depot_ids = request.json['legacy_depot_ids']
        response_depots = []
        response_errors = []
        if legacy_depot_ids:
            for legacy_depot_id in legacy_depot_ids:
                if legacy_depot_id in depots:
                    response_depots.append(depots[legacy_depot_id].get_json())
                else:
                    response_errors.append(
                        {
                            'legacy_depot_id': legacy_depot_id,
                            'error_code': 'not_found',
                        },
                    )
        else:
            response_depots += [depot.get_json() for depot in depots.values()]
        return mockserver.make_response(
            json={'depots': response_depots, 'errors': response_errors},
            status=200,
        )

    @mockserver.json_handler('/grocery-depots/internal/v1/depots/v1/zones')
    def mock_internal_zones(request):
        legacy_depot_ids = request.json['legacy_depot_ids']
        response_zones = []
        if legacy_depot_ids:
            for legacy_depot_id in legacy_depot_ids:
                if legacy_depot_id in depots:
                    response_zones += depots[legacy_depot_id].get_zones_json()
        else:
            for _, depot in depots:
                response_zones += depot.get_zones_json()
        return mockserver.make_response(
            json={'zones': response_zones}, status=200,
        )

    class Context:
        def times_called_depots(self):
            return mock_internal_depots.times_called

        def times_called_zones(self):
            return mock_internal_zones.times_called

        def flush(self):
            mock_internal_depots.flush()
            mock_internal_zones.flush()

        def clear_depots(self):
            depots.clear()
            assert depots == {}

        def depots(self):
            return depots

        def add_depot(
                self,
                depot_test_id=1,
                *,
                legacy_depot_id=None,
                depot_id=None,
                status='active',
                auto_add_zone=True,
                allow_parcels=False,
                phone_number='+78005553535',
                delivery_type='pedestrian',
                region_id=213,
                location=None,
                address=None,
                email=None,
                directions=None,
                company_id=None,
                company_type='yandex',
                timezone='Europe/Moscow',
                timetable=None,
                country_iso3='RUS',
                country_iso2='RU',
                currency='RUB',
                short_address=None,
                tin=None,
                name=None,
                oebs_depot_id=None,
        ):
            if legacy_depot_id is not None:
                assert legacy_depot_id not in depots
            if isinstance(location, list):
                location = {
                    'lon': float(location[0]),
                    'lat': float(location[1]),
                }
            depot = GroceryDepot(
                depot_test_id=depot_test_id,
                legacy_depot_id=legacy_depot_id,
                depot_id=depot_id,
                status=status,
                auto_add_zone=auto_add_zone,
                allow_parcels=allow_parcels,
                phone_number=phone_number,
                delivery_type=delivery_type,
                region_id=region_id,
                address=address,
                email=email,
                directions=directions,
                company_id=company_id,
                company_type=company_type,
                location=location,
                timezone=timezone,
                timetable=timetable,
                country_iso3=country_iso3,
                country_iso2=country_iso2,
                currency=currency,
                short_address=short_address,
                tin=tin,
                name=name,
                oebs_depot_id=oebs_depot_id,
            )
            assert depot.legacy_depot_id not in depots
            depots[depot.legacy_depot_id] = depot
            return depot

    context = Context()
    return context
