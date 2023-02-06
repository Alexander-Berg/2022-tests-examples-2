import pytest
from pprint import pformat

from nile.api.v1 import MockCluster
from nile.api.v1.local import StreamSource, ListSink
from nile.api.v1 import Record

from eda_etl.layer.yt.cdm.user_product.eda_user_appsession.impl import build_surge_record


@pytest.mark.parametrize(
    'input_surge, expected_surge',
    [
        pytest.param(
            [
                Record(
                    request_id=123,
                    surge_val=123,
                    name='Яндекс.Лавка',
                    place_request_seq=1,
                    place_id=123,
                    order_destination_lat=77.77,
                    order_destination_lon=33.33,
                ),
                Record(
                    request_id=123,
                    surge_val=1234,
                    name='Яндекс.Лавка',
                    place_request_seq=2,
                    place_id=1234,
                    order_destination_lat=77.33,
                    order_destination_lon=33.77,
                )
            ],
            [
                Record(
                    request_id=123,
                    eda_place_id_list=[],
                    eda_surge_val_list=[],
                    order_destination_lat=77.77,
                    order_destination_lon=33.33,
                )
            ],
            id='Lavka surge'),
        pytest.param(
            [
                Record(
                    request_id=123,
                    surge_val=123,
                    name='не Яндекс.Лавка',
                    place_request_seq=1,
                    place_id=123,
                    order_destination_lat=None,
                    order_destination_lon=33.37,
                ),
                Record(
                    request_id=123,
                    surge_val=1234,
                    name='не Яндекс.Лавка',
                    place_request_seq=2,
                    place_id=1234,
                    order_destination_lat=77.73,
                    order_destination_lon=None,
                )
            ],
            [
                Record(
                    request_id=123,
                    eda_place_id_list=[123, 1234],
                    eda_surge_val_list=[123, 1234],
                    order_destination_lat=None,
                    order_destination_lon=None,
                )
            ],
            id='Eda surge'),
        ]
    )
def test_build_surge_record(input_surge, expected_surge):

    cluster = MockCluster()
    job = cluster.job('test_build_surge_record')
    actual_surge = []
    job.table('stub') \
        .label('input_surge') \
        .groupby('request_id') \
        .sort('place_request_seq') \
        .reduce(build_surge_record) \
        .label('actual_surge')
    job.local_run(
        sources={'input_surge': StreamSource(input_surge)},
        sinks={'actual_surge': ListSink(actual_surge)}
    )

    actual_surge = sorted(actual_surge, key=lambda rec: (rec.get('request_id')))

    assert expected_surge == actual_surge, \
        'Expected surge is different from actual:\nexpected\n{},\nactual\n{}' \
            .format(pformat(expected_surge), pformat(actual_surge))
