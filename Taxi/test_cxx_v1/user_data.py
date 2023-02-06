import datetime
import json

from nile.api.v1 import Job, Record
from nile.api.v1 import aggregators as na, filters as nf, extractors as ne

from projects.eats.places_ranking.rec_sys.data_context import (
    umlaas_eats_ml_request_logs,
)
from projects.eats.data_context.v1 import OrdersCubeContext

_EPS = 1e-4


def _add_counts(features, counts, universe):
    if counts:
        d = {x: y for x, y in counts}
    else:
        d = dict()
    norm = sum(d.values())
    features.append(norm)
    for value in universe:
        features.append(d.get(value, 0))
        features.append(d.get(value, 0) / (norm + _EPS))


def _user_features_mapper(records):
    for record in records:
        features = []
        _add_counts(
            features=features,
            counts=record.get('application_platform'),
            universe=[b'iphone', b'android', b'web', b'superapp'],
        )
        _add_counts(
            features=features,
            counts=record.get('asap_flg'),
            universe=[False, True],
        )
        _add_counts(
            features=features,
            counts=record.get('delivery_type'),
            universe=[b'native', b'marketplace'],
        )
        _add_counts(
            features=features,
            counts=record.get('payment_service'),
            universe=[b'Apple Pay Yandex Eda', b'Payture RU', b'Taxi.Payment'],
        )
        _add_counts(
            features=features, counts=record.get('status'), universe=[4, 5],
        )
        features.append(record.get('delivered_actual_amount_mean'))
        features.append(record.get('delivered_actual_amount_sum'))
        features.append(record.get('delivered_amount_charged_mean'))
        features.append(record.get('delivered_amount_charged_sum'))

        features.append(record.get('first_order_timestamp'))
        features.append(record.get('first_delivered_order_timestamp'))

        yield Record(
            user_uid=str(record.user_id),
            user_embedding=[
                float(x) if x is not None else -1.0 for x in features
            ],
        )


def _update_request(request, user_embedding):
    request = json.loads(request)
    request['user_embedding'] = user_embedding
    return json.dumps(request)


class DataContext:
    def __init__(
            self,
            job: Job,
            begin_user_data_date: str,
            begin_date: str,
            end_date: str,
            seconds_till_order: int = 3600,
    ):
        begin_user_data_dttm = datetime.datetime.strptime(
            begin_user_data_date, '%Y-%m-%d',
        )
        begin_dttm = datetime.datetime.strptime(begin_date, '%Y-%m-%d')

        self._job = job
        self._data_context = umlaas_eats_ml_request_logs.DataContext(
            job=job,
            begin_date=begin_date,
            end_date=end_date,
            seconds_till_order=seconds_till_order,
        )
        self._user_orders_context = OrdersCubeContext(
            job=job,
            begin_dttm=begin_user_data_dttm,
            end_dttm=begin_dttm,
            dwh_layer='ods',
        )

    def get_user_embeddings(self):
        return (
            self._user_orders_context.get_orders_cube(
                order_fields=[
                    'user_id',
                    'status',
                    'flow_type',
                    'delivery_type',
                    'asap_flg',
                    'application_platform',
                    'payment_service',
                    'order_timestamp',
                    'actual_amount',
                    'amount_charged',
                    'place_id',
                ],
                places=True,
                place_fields=['is_fast_food_flg', 'brand_id', 'place_id'],
            )
            .groupby('user_id')
            .aggregate(
                status=na.histogram('status'),
                flow_type=na.histogram('flow_type'),
                delivery_type=na.histogram('delivery_type'),
                asap_flg=na.histogram('asap_flg'),
                application_platform=na.histogram('application_platform'),
                payment_service=na.histogram('payment_service'),
                delivered_actual_amount_mean=na.mean(
                    'actual_amount', predicate=nf.equals('status', 4),
                ),
                delivered_actual_amount_sum=na.sum(
                    'actual_amount', predicate=nf.equals('status', 4),
                ),
                delivered_amount_charged_mean=na.mean(
                    'amount_charged', predicate=nf.equals('status', 4),
                ),
                delivered_amount_charged_sum=na.sum(
                    'amount_charged', predicate=nf.equals('status', 4),
                ),
                first_order_timestamp=na.min('order_timestamp'),
                first_delivered_order_timestamp=na.min(
                    'order_timestamp', predicate=nf.equals('status', 4),
                ),
            )
            .map(_user_features_mapper)
        )

    def get(self):
        return (
            self._data_context.get()
            .join(
                self.get_user_embeddings(),
                by='user_uid',
                type='left',
                assume_unique_right=True,
            )
            .project(
                ne.all(['request', 'user_embedding']),
                request=ne.custom(
                    _update_request, 'request', 'user_embedding',
                ),
            )
        )
