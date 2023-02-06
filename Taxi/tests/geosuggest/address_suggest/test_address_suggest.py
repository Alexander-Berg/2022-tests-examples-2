import json

from nile.api.v1 import Record

from ctaxi_pyml.geosuggest.address_suggest import v1 as cxx
from projects.geosuggest.address_suggest.rec_sys.targets_extractors import v1
from projects.geosuggest.address_suggest.objects import (
    GeoPoint,
    OrderPoint,
    TargetOrder,
)
from projects.geosuggest.address_suggest.common.nile_blocks.data import (
    _target_order_from_record,
)


def test_order_targets_extractor(load_json):
    record = Record.from_dict(load_json('request.json'))
    cxx_request = cxx.Request.from_json(record.data)
    candidates = []
    for item in load_json('candidates.json'):
        candidates.append(cxx.Candidate.from_json(json.dumps(item)))
    assert len(candidates) == 33
    target_extractor = v1.OrderSourceTargetsExtractor(
        max_distance=3000, use_text=False,
    )
    targets = target_extractor(
        request=cxx_request, candidates=candidates, record=record,
    )
    assert sum(targets) == 3
    target_extractor = v1.OrderDestinationTargetsExtractor(
        max_distance=3000, use_text=False, use_completion_point=True,
    )
    targets = target_extractor(
        request=cxx_request, candidates=candidates, record=record,
    )
    assert sum(targets) == 22


def test_target_order_from_record():
    dest_address = (
        b'\xd0\xa0\xd0\xbe\xd1\x81\xd1\x81\xd0\xb8\xd1\x8f,'
        b' \xd0\x9f\xd0\xb5\xd0\xbd\xd0\xb7\xd0\xb0, '
        b'\xd1\x83\xd0\xbb\xd0\xb8\xd1\x86\xd0\xb0 '
        b'\xd0\x9a\xd0\xb8\xd0\xb6\xd0\xb5\xd0\xb2\xd0'
        b'\xb0\xd1\x82\xd0\xbe\xd0\xb2\xd0\xb0, 4'
    )
    source_address = (
        b'\xd0\xa0\xd0\xbe\xd1\x81\xd1\x81\xd0\xb8\xd1\x8f, '
        b'\xd0\x9f\xd0\xb5\xd0\xbd\xd0\xb7\xd0\xb0, '
        b'\xd1\x83\xd0\xbb\xd0\xb8\xd1\x86\xd0\xb0 '
        b'\xd0\x9a\xd0\xb8\xd1\x80\xd0\xbe\xd0\xb2\xd0\xb0, 73'
    )
    record = Record.from_dict(
        {
            'fact_destination_lon': 44.976254,
            'source_lon': 45.02101,
            'plan_destination_lon': 44.97693,
            'fact_destination_lat': 53.165729999999996,
            'source_lat': 53.198419,
            'plan_destination_lat': 53.165862,
            'plan_destination_address': dest_address,
            'source_address': source_address,
            'order_id': b'558834eeeea22f179ce688adb72b8491',
            'utc_order_dttm': b'2019-12-08 11:02:26',
            'timestamp': 1575802946,
        },
    )
    order = _target_order_from_record(record)
    truth_order = TargetOrder(
        id='558834eeeea22f179ce688adb72b8491',
        source_point=OrderPoint(
            geopoint=GeoPoint(lon=45.02101, lat=53.198419),
            text='Россия, Пенза, улица Кирова, 73',
        ),
        created=1575802946,
        destination_point=OrderPoint(
            geopoint=GeoPoint(lon=44.97693, lat=53.165862),
            text='Россия, Пенза, улица Кижеватова, 4',
        ),
        completion_point=GeoPoint(lon=44.976254, lat=53.165729999999996),
    )
    assert order == truth_order
    order_json = truth_order.to_json()
    assert TargetOrder.from_json(order_json) == truth_order
