import json
from dmp_suite.file_utils import from_same_directory
from taxi_etl.layer.yt.ods.zendesk_hiring.tickets.impl import mapper, rename_to_pd_id
from taxi_etl.layer.yt.ods.zendesk_hiring.tickets.table import OdsTickets, OdsZendeskHiringTicketsWoPD


def test_transformation():
    with open(from_same_directory(__file__, 'data/raw_tickets.json')) as raw_json, \
         open(from_same_directory(__file__, 'data/ods_tickets.json')) as ods_json:

        ods_records = json.load(ods_json)

        for raw in json.load(raw_json):
            for ods in ods_records:
                if int(raw['id']) == ods['id']:
                    assert mapper(raw['doc'], OdsTickets, wo_pd=False) == ods
                    rename_to_pd_id(ods)
                    ods.pop('driver_license_normalized')
                    assert mapper(raw['doc'], OdsZendeskHiringTicketsWoPD, wo_pd=True) == ods
                    break
