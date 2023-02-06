"""Static generator for claims `/v1/segment*` handlers.
"""

import copy
import itertools

import pytest

SEG_TPL_FILENAME = 'plugins/claims_segment_static_gen/claims_segment_tpl.json'
MAX_POINTS_IN_SEGMENT = 10

CLAIMS_POINT_TYPE_MAP = {
    'pickup': 'source',
    'dropoff': 'destination',
    'return': 'return',
}


class Segment:
    def __init__(self, claims_segment_tpl, segment_number, segment_id, points):
        self._claim_point_seq = itertools.count(1)
        self._segment_number = (
            segment_number  # claim_point_ids => 11, 12, 21, 22, 23, ...
        )
        self._point_index = {}  # point_id => index in _data['points'] array
        self._json = copy.deepcopy(claims_segment_tpl)  # segment as dict

        self._prepare_data(claims_segment_tpl, segment_id, points)

    @property
    def json(self):
        return self._json

    def set_client_info(self, client_info: dict):
        self._json['client_info'] = client_info

    def set_modified_classes(self, modified_classes):
        self._json['modified_classes'] = modified_classes
        self._json['claim_revision'] += 1

    def set_tariffs_substitution(self, tariffs_substitution):
        self._json['tariffs_substitution'] = tariffs_substitution
        self._json['claim_revision'] += 1

    def set_delayed_tariffs(self, delayed_tariffs: list):
        self._json['delayed_tariffs'] = delayed_tariffs

    def set_yandex_uid(self, yandex_uid):
        self._json['yandex_uid'] = yandex_uid

    def set_calc_id(self, calc_id):
        self._json['pricing'] = {'offer_id': calc_id}

    def set_cargo_c2c_order_id(self, cargo_c2c_order_id):
        self._json['cargo_c2c_order_id'] = cargo_c2c_order_id

    def get_point(self, point_id):
        index = self._point_index.get(point_id)
        if index is None:
            assert False, 'Missing index %s: %s' % (
                point_id,
                self._point_index.keys(),
            )
        return self._json['points'][index]

    def get_location(self, location_id):
        result = None
        for location in self._json['locations']:
            if location['location_id'] == location_id:
                result = location
        if result is None:
            assert False, f'No location with id: {location_id}'
        return result

    def set_point_visit_status(
            self, point_id, new_status, is_caused_by_user=False,
    ):
        point = self.get_point(point_id)
        point['visit_status'] = new_status
        point['revision'] += 1

        if new_status in ('visited', 'skipped'):
            point['is_resolved'] = True
            point['is_return_required'] = new_status == 'skipped'
            point['resolution'] = {
                'is_skipped': new_status == 'skipped',
                'is_visited': new_status == 'visited',
            }

        if is_caused_by_user:
            self._json['points_user_version'] += 1
            self._json['claim_revision'] += 1

        if self._is_all_points_resolved():
            self._set_resolution()

    def set_claim_features(self, claim_features: list):
        self._json['claim_features'] = claim_features

    def set_point_post_payment(self, point_id):
        point = self.get_point(point_id)
        point['post_payment'] = {
            'id': '757849ca-2e29-45a6-84f7-d576603618bb',
            'method': 'card',
        }

    def set_point_coordinates(self, point_id, coordinates: list):
        point = self.get_point(point_id)
        location = self.get_location(point['location_id'])
        location['coordinates'] = coordinates

    def cancel_by_user(self):
        for point in self._json['points']:
            if point['visit_status'] == 'visited':
                if point['type'] != 'pickup':
                    raise ValueError(
                        'cannot cancel segment %s because point %s is visited'
                        % (self._json['_id'], point['point_id']),
                    )
            elif point['visit_status'] != 'skipped':
                self.set_point_visit_status(
                    self.get_point_id(point),
                    'skipped',
                    is_caused_by_user=True,
                )

        self._json['points_user_version'] += 1
        self._set_resolution(resolution='cancelled_by_user')

    def _is_all_points_resolved(self):
        for point in self._json['points']:
            if point['visit_status'] not in ('skipped', 'visited'):
                return False
        return True

    def _set_resolution(self, resolution=None):
        self._json['resolution'] = resolution
        self._json['claim_revision'] += 1

    def _prepare_data(self, claims_segment_tpl, segment_id, input_points):
        items = {}
        locations = {}
        points = []
        for (
                point_id,
                location_id,
                instructions,
                time_intervals,
        ) in input_points:
            unique_location_id = '%s_%s' % (segment_id, location_id)
            self._upsert_location(
                locations, claims_segment_tpl, unique_location_id,
            )

            unique_point_id = '%s_%s' % (unique_location_id, point_id)
            point_type, input_items = instructions
            for item_id in input_items:
                unique_item_id = '%s_%s' % (segment_id, item_id)
                self._upsert_item(
                    items,
                    claims_segment_tpl,
                    point_type,
                    unique_item_id,
                    unique_point_id,
                )

            if point_id in self._point_index:
                raise ValueError('point %s met twice' % unique_point_id)
            self._point_index[point_id] = len(points)
            points.append(
                self._new_point(
                    claims_segment_tpl,
                    unique_point_id,
                    unique_location_id,
                    len(points) + 1,
                    point_type,
                    time_intervals,
                ),
            )

        self._json['id'] = segment_id
        self._json['locations'] = list(locations.values())
        self._json['points'] = points
        self._json['items'] = list(items.values())
        self._json.pop('resolution', None)  # set it with `set_resolution()`
        self._json['diagnostics']['claim_id'] = 'claim_%s' % segment_id
        self._update_with_claims_points()

        self._check_items_filled()

    def _upsert_location(
            self, locations, claims_segment_tpl, unique_location_id,
    ):
        if unique_location_id not in locations:
            loc = copy.deepcopy(claims_segment_tpl['locations'][0])
            loc['location_id'] = unique_location_id
            loc['comment'] = loc['comment'].format(
                location_id=unique_location_id,
            )
            locations[unique_location_id] = loc

    @staticmethod
    def _upsert_item(
            items,
            claims_segment_tpl,
            point_type,
            unique_item_id,
            unique_point_id,
    ):
        if unique_item_id not in items:
            items[unique_item_id] = Segment._new_item(
                claims_segment_tpl, unique_item_id,
            )
        key = '%s_point' % point_type
        if items[unique_item_id][key] is not None:
            raise ValueError(
                '%s of item %s already set to %s, cannot set new value %s'
                % (
                    key,
                    unique_item_id,
                    items[unique_item_id][key],
                    unique_point_id,
                ),
            )
        items[unique_item_id][key] = unique_point_id

    @staticmethod
    def _new_item(claims_segment_tpl, unique_item_id):
        item = copy.deepcopy(claims_segment_tpl['items'][0])
        item['item_id'] = unique_item_id
        item['pickup_point'] = None
        item['dropoff_point'] = None
        item['return_point'] = None
        return item

    def _new_point(
            self,
            claims_segment_tpl,
            unique_point_id,
            unique_location_id,
            visit_order,
            point_type,
            time_intervals,
    ):
        point = copy.deepcopy(claims_segment_tpl['points'][0])
        point['point_id'] = unique_point_id
        point['location_id'] = unique_location_id
        point['visit_order'] = visit_order
        point['claim_point_id'] = (
            self._segment_number * MAX_POINTS_IN_SEGMENT
            + next(self._claim_point_seq)
        )
        point['visit_status'] = 'pending'
        point['type'] = point_type
        point['segment_point_type'] = CLAIMS_POINT_TYPE_MAP[point_type]
        point['time_intervals'] = time_intervals

        if visit_order % 2:
            point['external_order_id'] = point['external_order_id'].format(
                location_id=unique_location_id,
            )
        else:
            del point['external_order_id']

        del point['resolution']
        return point

    @staticmethod
    def get_point_id(point):
        return point['point_id'].split('_')[-1]

    def _check_items_filled(self):
        for item in self._json['items']:
            for key_part in ('pickup', 'dropoff', 'return'):
                key = '%s_point' % key_part
                if item.get(key) is None:
                    raise ValueError(
                        'item %s must containt all points, %s is missing'
                        % (item['item_id'], key),
                    )

    def _update_with_claims_points(self):
        points2claimpoints = {}
        for point in self._json['points']:
            claim_point_id = point['claim_point_id']
            points2claimpoints[point['point_id']] = claim_point_id

        for item in self._json['items']:
            for key in ('pickup', 'dropoff', 'return'):
                point_id = item['%s_point' % key]
                item['claim_%s_point' % key] = points2claimpoints[point_id]


class Db:
    def __init__(self, claims_segment_tpl):
        self._claims_segment_tpl = claims_segment_tpl
        self._segments = {}
        self._claims_journal = []
        self._points_journal = []

    def read_claims_journal(self, cursor=None):
        if cursor is None:
            cursor = '0'
        start = int(cursor)
        new_cursor = str(len(self._claims_journal))
        return {'cursor': new_cursor, 'entries': self._claims_journal[start:]}

    def get_segment(self, segment_id):
        return self._segments.get(segment_id)

    def add_segment(self, segment_number, points):
        segment_id = 'seg' + str(segment_number)
        if segment_id in self._segments:
            raise ValueError('cannot insert segment %s twice' % segment_id)
        self._segments[segment_id] = Segment(
            self._claims_segment_tpl, segment_number, segment_id, points,
        )
        self._add_claims_entry(segment_id)

    def cancel_segment_by_user(self, segment_id):
        self._segments[segment_id].cancel_by_user()
        self._add_claims_entry(segment_id)

    def set_segment_modified_classes(self, segment_id, modified_classes):
        self._segments[segment_id].set_modified_classes(modified_classes)
        self._add_claims_entry(segment_id)

    def set_seg_tariffs_substitution(self, segment_id, tariffs_substitution):
        self._segments[segment_id].set_tariffs_substitution(
            tariffs_substitution,
        )
        self._add_claims_entry(segment_id)

    def set_segment_point_visit_status(
            self, segment_id, point_id, new_status, is_caused_by_user=False,
    ):
        self._segments[segment_id].set_point_visit_status(
            point_id, new_status, is_caused_by_user,
        )
        self._add_points_journal_entry(segment_id, point_id)
        if (
                is_caused_by_user
                or 'resolution' in self._segments[segment_id].json
        ):
            self._add_claims_entry(segment_id)

    def set_yandex_uid(self, segment_id, yandex_uid):
        self._segments[segment_id].set_yandex_uid(yandex_uid)

    def set_calc_id(self, segment_id, calc_id):
        self._segments[segment_id].set_calc_id(calc_id)

    def set_cargo_c2c_order_id(self, segment_id, cargo_c2c_order_id):
        self._segments[segment_id].set_cargo_c2c_order_id(cargo_c2c_order_id)

    def _add_claims_entry(self, segment_id):
        segment = self._segments[segment_id].json

        entry = {
            'segment_id': segment_id,
            'revision': segment['claim_revision'],
            'created_ts': segment['diagnostics']['segment_updated_ts'],
            'current': {
                'claim_id': segment['diagnostics']['claim_id'],
                'points_user_version': segment['points_user_version'],
            },
        }
        if 'resolution' in segment:
            entry['current']['resolution'] = segment['resolution']

        self._claims_journal.append(entry)

    def _add_points_journal_entry(self, segment_id, point_id):
        point = self._segments[segment_id].get_point(point_id)

        entry = {
            'segment_id': segment_id,
            'point_id': point_id,
            'revision': point['revision'],
            'created_ts': point['last_status_change_ts'],
            'current': {},
        }

        self._points_journal.append(entry)


@pytest.fixture(name='build_claims_segment_db')
def _build_claims_segment_db(load_json):
    def _wrapper():
        return Db(load_json(SEG_TPL_FILENAME))

    return _wrapper
