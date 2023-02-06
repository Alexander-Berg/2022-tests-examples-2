import argparse
import time
import datetime
import logging

import requests

from taxi.core import db
from taxi.internal import park_manager
from taxi.util import dates


SLEEP_TIMEOUT = 10
OPERATOR_UID = 0


def main(argv=None):
    args = parse_args(argv)
    partner = db.partners._collection.find_one(args.partner_id)
    url = 'http://partner-contracts.taxi.tst.yandex.net/v1/register_partner/{}/'.format(
        partner.get('country_code', '__default__')
    )
    res = requests.post(
        url=url,
        json={
            'params': partner['registration_form_new']['__default__'],
            'flow': partner['flow']
        }
    ).json()
    print 'Create inquiry', res
    inquiry_id = res['inquiry_id']
    time.sleep(SLEEP_TIMEOUT)

    partner = db.partners._collection.find_one(inquiry_id)
    data = {
        key: value
        for sample_data in partner['sample_data'].itervalues()
        for key, value in sample_data.iteritems()
    }
    print data
    if 'offer_confirmed' not in data or 'billing_client_id' not in data:
        raise ValueError('Smth wrong with {} inquiry'.format(inquiry_id))

    cities = db.cities._collection.find({'country': args.country_code}, [])
    query = {'city': {'$in': [city['_id'] for city in cities]}}
    if args.park_ids:
        query['_id'] = {'$in': args.park_ids}
    parks = list(db.parks._collection.find(query))
    new_bc_id_start = (
        dates.localized_midnight(datetime.datetime.utcnow()) -
        datetime.timedelta(days=1)
    )
    print data['billing_client_id'], new_bc_id_start
    if args.force_add_bci_to_park:
        res = db.parks._collection.update(
            {'_id': {'$in': [park['_id'] for park in parks]}},
            {
                '$set': {
                    'billing_client_ids': [
                        [datetime.datetime(2010, 1, 1), None, data['billing_client_id']]
                    ]
                }
            },
            multi=True
        )
        print res
    else:
        for index, park in enumerate(parks):
            park['billing_client_ids'] = []
            res = park_manager.add_billing_client_id_to_park(
                park, data['billing_client_id'], new_bc_id_start, OPERATOR_UID,
                log_extra=None
            )
            print(
                '{}/{}'.format(index, len(parks)),
                'Add billing_clinet_id to park',
                park['_id'],
                res
            )


def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('--partner-id', required=True)
    parser.add_argument('--country-code', required=True)
    parser.add_argument('--park-ids', nargs='*', default=None)
    parser.add_argument('--force-add-bci-to-park', action='store_true')
    return parser.parse_args(args)


if __name__ == '__main__':
    main()
