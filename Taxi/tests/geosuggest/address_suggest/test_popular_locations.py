import json
import six
import pytest

from nile.api.v1 import clusters, Record
from nile.api.v1.local import StreamSource, ListSink

from ctaxi_pyml.geosuggest.address_suggest import v1 as cxx
from projects.geosuggest.address_suggest.popular_locations.nile_blocks.raw_candidates import (  # noqa pylint: disable=line-too-long
    _mapper,
)
from projects.geosuggest.address_suggest.popular_locations import packers


class TestDataNileBlock:
    def test_mapper(self):
        org_destination = {
            b'geopoint': [24.096201, 56.961651],
            b'oid': b'113722835322',
            b'uris': [b'uri'],
        }
        org_record = Record(
            popular_location_geohash='qoiurgq', destinations=[org_destination],
        )
        address_destination = {
            b'geopoint': [27.536062, 53.879974],
            b'uris': [b'another_uri'],
        }
        address_record = Record(
            popular_location_geohash='lsaekgh',
            destinations=[address_destination],
        )
        ytpp_destination = {
            b'geopoint': [37.65598098125059, 55.7757404249768],
            b'uris': [
                six.ensure_binary(
                    'ytpp://Лениградский вокзал/Остановка такси #1',
                ),
            ],
        }
        ytpp_record = Record(
            popular_location_geohash='aweiuwr',
            destinations=[address_destination, ytpp_destination],
        )
        job = clusters.MockCluster().job()
        out_table = job.table('').label('input').map(_mapper)
        out_table.label('output').put('output')
        output_records = []
        job.local_run(
            sources={
                'input': StreamSource(
                    [org_record, address_record, ytpp_record],
                ),
            },
            sinks={'output': ListSink(output_records)},
        )
        truth_output_records = [
            Record(
                id='qoiurgq_113722835322',
                lon=24.096201,
                lat=56.961651,
                oid='113722835322',
                popular_location=json.dumps(
                    {
                        'id': 'qoiurgq_113722835322',
                        'lon': 24.096201,
                        'lat': 56.961651,
                        'score': None,
                        'oid': '113722835322',
                        'uri': 'uri',
                        'embedding': None,
                    },
                ),
            ),
            Record(
                id='aweiuwr',
                lon=37.65598098125059,
                lat=55.7757404249768,
                oid=None,
                popular_location=json.dumps(
                    {
                        'id': 'aweiuwr',
                        'lon': 37.65598098125059,
                        'lat': 55.7757404249768,
                        'score': None,
                        'oid': None,
                        'uri': 'ytpp://Лениградский вокзал/Остановка такси #1',
                        'embedding': None,
                    },
                ),
            ),
        ]
        assert len(output_records) == len(truth_output_records)
        # assert output_records == truth_output_records


def test_packer_from_records():
    popular_locations_packer = packers.DefaultPacker()
    popular_location_json = json.dumps(
        {
            'id': 'lsaekgh',
            'lon': 27.536062,
            'lat': 53.879974,
            'score': 1.0,
            'oid': None,
            'embedding': [1, 2, 3, 4],
        },
    )
    records = [Record(popular_location=popular_location_json)]
    storage_binary = popular_locations_packer(records)
    storage_restored = cxx.PopularLocationsStorage.from_compressed_json(
        six.ensure_str(storage_binary),
    )
    assert storage_restored.items[0].id == 'lsaekgh'
    assert storage_restored.items[0].score == pytest.approx(1.0)
    assert storage_restored.items[0].geopoint.lon == pytest.approx(27.536062)
    assert storage_restored.items[0].geopoint.lat == pytest.approx(53.879974)
    assert storage_restored.items[0].embedding == pytest.approx(
        [1.0, 2.0, 3.0, 4.0],
    )
