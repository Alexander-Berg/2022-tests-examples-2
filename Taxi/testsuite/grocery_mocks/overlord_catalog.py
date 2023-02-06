import pytest

from . import keys

DEPOT_ID = '0'
OVERLORD_DEPOT_KEY = 'depots'
DEFAULT_OVERLORD_DEPOTS: dict = {'depots': [], 'errors': []}
WALLET_ID = 'w/28c44321-16a3-5221-a0b1-3f823998bdff'
DEFAULT_VAT = keys.DEFAULT_VAT


# pylint: disable=unused-variable,invalid-name
@pytest.fixture(name='overlord_catalog', autouse=True)
def mock_overlord_catalog(mockserver):
    payload = {}
    depot_by_location = {}
    depot_zones_by_location = {}
    products_v2 = {}
    depot_info = {'depot_status': 'available', 'not_found': False}
    products_data = {}
    category_trees = {}
    eats_mapping = {}
    categories_data = []
    products_links = []
    products_stocks = {}
    available_category_ids = set()

    @mockserver.json_handler(
        '/overlord-catalog/internal/v1/catalog/v1/depot-resolve',
    )
    def _mock_internal_depot_resolve(request):
        if depot_info['not_found']:
            return mockserver.make_response(
                json={'code': 'DEPOT_NOT_FOUND', 'message': 'Depot not found'},
                status=404,
            )
        location = request.json['position']['location']
        if tuple(location) in depot_by_location:
            depot = depot_by_location[tuple(location)]

            if depot_info['depot_status'] == 'available':
                depot['state'] = 'open'
            else:
                depot['state'] = depot_info['depot_status']
            depot_data = next(
                (
                    depot
                    for depot in payload[OVERLORD_DEPOT_KEY]['depots']
                    if 'position' in depot
                    and depot['position']['location'] == location
                ),
                None,
            )

            if depot_data:
                if 'working_hours' in depot_data:
                    depot['working_hours'] = depot_data['working_hours']

            if request.json.get('get_availability_time', False) is True and (
                    depot['state'] == 'open' or depot['state'] == 'closed'
            ):
                # нужно для тестов g-api/service-info; подойдут любые значения
                depot['availability_time'] = {
                    'from': depot['switch_time'],
                    'to': depot['switch_time'],
                }

            return depot
        return mockserver.make_response(
            json={'code': 'DEPOT_NOT_FOUND', 'message': 'Depot not found'},
            status=404,
        )

    @mockserver.json_handler(
        '/overlord-catalog/internal/v1/catalog/v2/depot-resolve',
    )
    def _mock_internal_v2_depot_resolve(request):
        if depot_info['not_found']:
            return mockserver.make_response(
                json={'code': 'DEPOT_NOT_FOUND', 'message': 'Depot not found'},
                status=404,
            )
        location = request.json['position']['location']
        if tuple(location) in depot_zones_by_location:
            depot = depot_zones_by_location[tuple(location)]
            return depot
        return mockserver.make_response(
            json={'code': 'DEPOT_NOT_FOUND', 'message': 'Depot not found'},
            status=404,
        )

    @mockserver.json_handler('/overlord-catalog/internal/v1/catalog/v1/depots')
    def mock_internal_catalog_depots(request):
        return payload.get(OVERLORD_DEPOT_KEY, DEFAULT_OVERLORD_DEPOTS)

    @mockserver.json_handler(
        '/overlord-catalog/internal/v1/catalog/v2/products',
    )
    def mock_internal_catalog_products2(request):
        return {
            'products': [
                products_v2[product_id]
                for product_id in request.json['product_ids']
                if product_id in products_v2
            ],
        }

    @mockserver.json_handler(
        '/overlord-catalog/internal/v1/catalog/v1/categories-data',
    )
    def mock_internal_categories_data(request):
        if 'cursor' in request.json:
            cursor = request.json['cursor']
        else:
            cursor = 0
        limit = request.json['limit']

        response_categories = []
        response_cursor = min(cursor + limit, len(categories_data))
        for category in categories_data[cursor:response_cursor]:
            response_categories.append(category)
        return {'cursor': response_cursor, 'categories': response_categories}

    @mockserver.json_handler(
        '/overlord-catalog/internal/v1/catalog/v1/products-links',
    )
    def mock_internal_products_links(request):
        if 'cursor' in request.json:
            cursor = request.json['cursor']
        else:
            cursor = 0
        limit = request.json['limit']

        response_products = []
        response_cursor = min(cursor + limit, len(products_links))
        for product in products_links[cursor:response_cursor]:
            response_products.append(product)
        return {'cursor': response_cursor, 'products': response_products}

    @mockserver.json_handler(
        '/overlord-catalog/internal/v1/catalog/v1/products-data',
    )
    def mock_internal_products_data(request):
        if 'cursor' in request.json:
            cursor = request.json['cursor']
        else:
            cursor = 0
        limit = request.json['limit']

        response_products = []
        response_cursor = min(cursor + limit, len(products_data))
        product_ids_ordered = sorted(products_data.keys())
        for product_id in product_ids_ordered[cursor:response_cursor]:
            response_products.append(products_data[product_id])
        return {'cursor': response_cursor, 'products': response_products}

    @mockserver.json_handler(
        '/overlord-catalog/internal/v1/catalog/v2/category-tree',
    )
    def _mock_category_tree_list(request):
        if 'cursor' in request.json:
            cursor = int(request.json['cursor'])
        else:
            cursor = 0
        limit = int(request.json['limit'])

        category_trees_list = list(category_trees.items())
        category_trees_list.sort(key=lambda i: i[0])

        response_trees = []
        response_cursor = min(cursor + limit, len(category_trees_list))
        for category_tree_values in category_trees_list[
                cursor:response_cursor
        ]:
            category_tree = category_tree_values[1]
            category_tree['depot_ids'] = list(category_tree_values[0])
            response_trees.append(category_tree)
        return {'cursor': response_cursor, 'category_trees': response_trees}

    @mockserver.json_handler('/overlord-catalog/internal/v1/catalog/v1/stocks')
    def mock_internal_stocks(request):
        depot_id = request.json['depot_id']
        if depot_id not in products_stocks:
            return mockserver.make_response(
                json={'code': 'DEPOT_NOT_FOUND', 'message': 'Depot not found'},
                status=404,
            )
        stocks = []
        for product_id in request.json['product_ids']:
            if product_id in products_stocks[depot_id]:
                stocks.append(products_stocks[depot_id][product_id])
        return {'stocks': stocks}

    @mockserver.json_handler(
        '/overlord-catalog/internal/v1/catalog/v1/eats-mapping',
    )
    def mock_internal_eats_mapping(request):
        if 'cursor' in request.json:
            cursor = int(request.json['cursor'])
        else:
            cursor = 0
        limit = int(request.json['limit'])

        eats_mapping_list = list(eats_mapping.items())
        eats_mapping_list.sort(key=lambda i: i[0])
        response_mapping = []
        response_cursor = min(cursor + limit, len(eats_mapping_list))
        for eats_mapping_values in eats_mapping_list[cursor:response_cursor]:
            mapping = eats_mapping_values[1]
            mapping['depot_id'] = eats_mapping_values[0]
            response_mapping.append(mapping)
        return {'depot_mapping': response_mapping, 'cursor': response_cursor}

    @mockserver.json_handler(
        '/overlord-catalog/internal/v1/catalog/v1/categories-availability',
    )
    def mock_internal_categories_availability(request):
        category_ids = request.json['category_ids']

        result = []
        for category_id in category_ids:
            result.append(
                {
                    'category_id': category_id,
                    'available': category_id in available_category_ids,
                },
            )

        return {'categories': result}

    @mockserver.json_handler(
        '/overlord-catalog/internal/v1/catalog/v1/pull-event-queue',
    )
    def _mock_internal_pull_event_queue(request):
        requested_events_type = request.json['event']
        available_events = context.products_events.get(
            requested_events_type, list(),
        )
        return mockserver.make_response(
            status=200, json={'events': available_events},
        )

    class Context:
        def __init__(self):
            self.products_events = {}

        def add_location(
                self,
                *,
                legacy_depot_id,
                depot_id='original_depot_id',
                location,
                zone_type='pedestrian',
                state='open',
                switch_time=keys.TS_DEFAULT_DEPOT_SWITCH_TIME,
                working_hours=keys.DEFAULT_DEPOT_ZONE_WORKING_HOURS,
                all_day=False,
                with_rover=True,
        ):
            if state != 'open':
                all_day = False
                working_hours = None

            depot_by_location[tuple(location)] = {
                'depot_id': depot_id,
                'depot_external_id': legacy_depot_id,
                'zone_type': zone_type,
                'state': state,
                'switch_time': switch_time,
                'working_hours': working_hours,
                'all_day': all_day,
            }
            depot_zones_by_location[tuple(location)] = {
                'depot_id': depot_id,
                'depot_external_id': legacy_depot_id,
                'best_zone': {
                    'zone_type': zone_type,
                    'state': state,
                    'switch_time': switch_time,
                },
                'optional_zones': (
                    [
                        {
                            'zone_type': 'rover',
                            'state': state,
                            'switch_time': switch_time,
                        },
                    ]
                    if with_rover
                    else None
                ),
            }

        def add_next_location(
                self,
                *,
                location,
                legacy_depot_id=None,
                depot_id=None,
                zone_type='yandex_taxi',
                state='closed',
                switch_time,
                next_depot_time=None,
        ):
            depot = depot_by_location.get(tuple(location))
            if depot is None:
                return

            if legacy_depot_id is None:
                legacy_depot_id = depot['depot_external_id']
            if depot_id is None:
                depot_id = depot['depot_id']

            if next_depot_time is None:
                next_depot_time = depot['switch_time']

            depot['next_depot_time'] = next_depot_time

            depot['next_depot'] = {
                'depot_id': depot_id,
                'depot_external_id': legacy_depot_id,
                'zone': {
                    'state': state,
                    'zone_type': zone_type,
                    'switch_time': switch_time,
                    'working_hours': keys.DEFAULT_DEPOT_ZONE_WORKING_HOURS,
                },
            }

        def set_location_zone_type(self, *, location, zone_type='pedestrian'):
            depot = depot_by_location[tuple(location)]
            depot['zone_type'] = zone_type
            zone_depot = depot_zones_by_location[tuple(location)]
            zone_depot['best_zone']['zone_type'] = zone_type

        def clear(self):
            nonlocal payload, depot_by_location, depot_zones_by_location
            nonlocal products_v2, depot_info, products_data, category_trees

            payload = {}
            depot_by_location = {}
            depot_zones_by_location = {}
            products_v2 = {}
            depot_info = {'depot_status': 'available', 'not_found': False}
            products_data = {}
            category_trees = dict()

        def add_depot(
                self,
                *,
                legacy_depot_id,
                depot_id=keys.DEFAULT_WMS_DEPOT_ID,
                country_iso3='RUS',
                country_iso2='RU',
                region_id=213,
                timezone='Europe/Moscow',
                location=None,
                address=None,
                tin=None,
                personal_tin_id=keys.DEFAULT_DEPOT_PERSONAL_TIN_ID,
                phone_number='+78007700460',
                company_type='yandex',
                currency='RUB',
                directions=None,
                short_address=None,
                name=None,
                working_hours=None,
                email=None,
                detailed_zones=None,
                zones_mode=None,
                polygons=None,
                position=None,
                oebs_depot_id=None,
        ):
            if location is None:
                location = keys.DEFAULT_DEPOT_LOCATION
            if OVERLORD_DEPOT_KEY not in payload:
                payload[OVERLORD_DEPOT_KEY] = {'depots': [], 'errors': []}

            self.add_location(
                legacy_depot_id=legacy_depot_id,
                depot_id=depot_id,
                location=location,
            )

            if position is None:
                position = {'location': location}

            depot = {
                'depot_id': depot_id,
                'legacy_depot_id': legacy_depot_id,
                'country_iso3': country_iso3,
                'country_iso2': country_iso2,
                'region_id': region_id,
                'timezone': timezone,
                'position': position,
                'personal_tin_id': personal_tin_id,
                'phone_number': phone_number,
                'currency': currency,
                'company_type': company_type,
                'oebs_depot_id': oebs_depot_id,
            }

            if detailed_zones is None:
                depot['detailed_zones'] = []
            else:
                depot['detailed_zones'] = detailed_zones

            if polygons is None:
                polygons = [
                    [
                        {'lat': 20.0, 'lon': 20.0},
                        {'lat': 30.0, 'lon': 20.0},
                        {'lat': 30.0, 'lon': 30.0},
                        {'lat': 20.0, 'lon': 30.0},
                        {'lat': 20.0, 'lon': 20.0},
                    ],
                ]

            if zones_mode in ('with_geozones', 'without_geozones'):
                depot['detailed_zones'] = [
                    {
                        'status': 'active',
                        'timetable': [
                            {
                                'day_type': 'Everyday',
                                'working_hours': {
                                    'from': {'hour': 0, 'minute': 0},
                                    'to': {'hour': 0, 'minute': 0},
                                },
                            },
                        ],
                        'zoneType': 'pedestrian',
                    }
                    for _ in polygons
                ]

                if zones_mode == 'with_geozones':
                    for idx, polygon in enumerate(polygons):
                        detailed_zone = depot['detailed_zones'][idx]
                        detailed_zone['geozone'] = {'type': 'MultiPolygon'}
                        detailed_zone['geozone']['coordinates'] = [[polygon]]
            elif zones_mode == 'nothing':
                del depot['detailed_zones']

            if address is not None:
                depot['address'] = address
            if tin is not None:
                depot['tin'] = tin

            if directions is not None:
                depot['directions'] = directions
            if short_address is not None:
                depot['short_address'] = short_address
            if name is not None:
                depot['name'] = name
            if working_hours is not None:
                depot['working_hours'] = working_hours
            if email is not None:
                depot['email'] = email

            payload[OVERLORD_DEPOT_KEY]['depots'].append(depot)
            return depot

        def times_called_depots(self):
            return mock_internal_catalog_depots.times_called

        def times_called(self):
            return mock_internal_catalog_products2.times_called

        def flush(self):
            mock_internal_catalog_depots.flush()
            mock_internal_catalog_products2.flush()
            mock_internal_products_data.flush()

        def add_product(
                self,
                *,
                product_id,
                external_id=None,
                price=keys.DEFAULT_PRICE,
                in_stock='100',
                vat=DEFAULT_VAT,
                measurements=None,
                options2=None,
                category_ids=None,
                legal_restrictions=None,
                parent_id=None,
                logistic_tags=None,
                master_categories=None,
                amount_pack=1,
                private_label=None,
                supplier_tin=None,
        ):
            if category_ids is None:
                category_ids = [f'{product_id}_category']

            categories = []
            for category_id in category_ids:
                categories.append(
                    {
                        'id': category_id,
                        'title': f'title for {category_id}',
                        'parent_ids': [],
                    },
                )

            default_options2 = {}
            if options2 is not None:
                default_options2 = {**options2}

            if logistic_tags is not None:
                default_options2 = {
                    **default_options2,
                    'logistic_tags': logistic_tags,
                }

            products_v2[product_id] = {
                'product_id': product_id,
                'external_id': external_id,
                'title': f'title for {product_id}',
                'catalog_price': str(price),
                'quantity_limit': in_stock,
                'category_ids': category_ids,
                'categories': categories,
                'vat': vat,
                'subtitle': f'subtitle for {product_id}',
                'image_url_templates': [f'url for {product_id}'],
                'options': default_options2,
                'legal_restrictions': legal_restrictions,
                'parent_id': parent_id,
                'master_categories': master_categories,
                'private_label': private_label,
                'supplier_tin': supplier_tin,
            }

            products_data[product_id] = {
                'product_id': product_id,
                'title': f'title for {product_id}',
                'long_title': f'long title for {product_id}',
                'description': f'description for {product_id}',
                'image_url_templates': [f'url for {product_id}'],
                # TODO: https://st.yandex-team.ru/LAVKABACKEND-4145
                'image_url_template': f'url for {product_id}',
                **({'external_id': external_id} if external_id else {}),
            }

            default_options = {
                'shelf_life_measure_unit': f'shelf life for {product_id}',
                'amount': f'amount for {product_id}',
                'amount_units': f'amount units for {product_id}',
                'pfc': [],
                'storage': [],
                'ingredients': [],
                'country_codes': [],
                'amount_pack': amount_pack,
            }

            if measurements:
                products_data[product_id]['options'] = {
                    **default_options,
                    'measurements': measurements,
                }

        def add_category_tree(self, *, depot_id, category_tree):
            if isinstance(depot_id, str):
                depot_id = (depot_id,)
            elif isinstance(depot_id, list):
                depot_id = tuple(depot_id)
            else:
                assert False
            category_trees[depot_id] = category_tree

        def remove_product(self, product_id):
            products_v2.pop(product_id)

        def set_depot_status(self, depot_status):
            depot_info['depot_status'] = depot_status

        def set_depot_not_found(self):
            depot_info['not_found'] = True

        def add_categories_data(self, *, new_categories_data):
            for category in new_categories_data:
                assert 'category_id' in category
                available_category_ids.add(category['category_id'])
            categories_data.extend(new_categories_data)

        def add_category_data(
                self,
                *,
                category_id,
                title,
                external_id=None,
                image_url_template=None,
                description=None,
        ):
            if image_url_template is None:
                image_url_template = f'{category_id}-url-template'
            if description is None:
                description = f'{category_id}-description'
            categories_data.append(
                {
                    'category_id': category_id,
                    'description': description,
                    'image_url_template': image_url_template,
                    'title': title,
                    **(
                        {'external_id': external_id}
                        if external_id is not None
                        else {}
                    ),
                },
            )

        def add_products_links(self, *, new_products_links):
            products_links.extend(new_products_links)

        def add_products_data(self, *, new_products_data):
            for product in new_products_data:
                products_data[product['product_id']] = product

        def add_product_data(
                self,
                *,
                product_id,
                title,
                long_title=None,
                image_url_template=None,
                description=None,
        ):
            if long_title is None:
                long_title = title
            if image_url_template is None:
                image_url_template = f'{product_id}-url-template'
            if description is None:
                description = f'{product_id}-description'
            products_data[product_id] = {
                'product_id': product_id,
                'description': description,
                'image_url_template': image_url_template,
                'title': title,
                'long_title': long_title,
            }

        def add_products_stocks(self, *, depot_id, new_products_stocks):
            if depot_id not in products_stocks:
                products_stocks[depot_id] = {}
            for stock in new_products_stocks:
                product_id = stock['product_id']
                products_stocks[depot_id][product_id] = stock

        def add_eats_mapping(self, *, depot_id, new_eats_mapping):
            eats_mapping[depot_id] = new_eats_mapping

        def set_category_availability(self, *, category_id, available):
            if available:
                available_category_ids.add(category_id)
            elif category_id in available_category_ids:
                available_category_ids.remove(category_id)

        def add_depots(self, *, depot_ids):
            for depot_id in depot_ids:
                self.add_depot(legacy_depot_id=depot_id)

        def set_products_events(self, products_events):
            self.products_events.update(products_events)

        @property
        def internal_stocks_times_called(self):
            return mock_internal_stocks.times_called

        @property
        def internal_categories_availability_times_called(self):
            return mock_internal_categories_availability.times_called

        @property
        def internal_depot_resolve_times_called(self):
            return _mock_internal_depot_resolve.times_called

    context = Context()
    context.add_depot(legacy_depot_id=DEPOT_ID)

    return context
