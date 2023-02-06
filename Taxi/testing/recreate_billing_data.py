"""Tool for recreating parks' client_ids, products and contracts.

ATTENTION!!! This is for testing only! You can't and shouldn't do it in prod.

Run on %taxi_test_import machines, they have necessary grants.

After calling this you'll need to wait until balances appear in Balance
(that is done 10-minutely). Then you can perform manually
    parks_balances.update_parks_balances_single_city (see script's output)
or wait for our task (performed hourly).

Usage:

To recreate data for all parks (see PREPAID_PARK_IDS for prepaid ones):

    PYTHONPATH=/usr/lib/yandex/taxi-tasks:$PYTHONPATH python \
        tools/testing/recreate_billing_data.py ""

To recreate data for specific parks:

    PYTHONPATH=/usr/lib/yandex/taxi-tasks:$PYTHONPATH python \
        tools/testing/recreate_billing_data.py "999030 999080 999010"

To recreate data for specific parks with explicit contract types:

    PYTHONPATH=/usr/lib/yandex/taxi-tasks:$PYTHONPATH python \
        tools/testing/recreate_billing_data.py "999030_pre 999080_post 999010"

This will create 999030 prepaid, 999090 postpaid,
and 999010 - depending on whether it is present in PREPAID_PARK_IDS

"""
import argparse
import collections
import datetime
import time
import urlparse

from taxi.core import async
from taxi.core import db
from taxi.external import billing
from taxi.internal import park_manager
from taxi.internal.city_kit import country_manager
from taxi.util import dates
from taxi_maintenance.stuff import import_drivers
from taxi_maintenance.stuff import update_parks_balances

TODAY = dates.localize()
PASSPORT_UID = '4001808845'

PREPAID_PARK_IDS = [
    '999030',
    '999010',
    # all the reset will be postpaid
]
FIRM_IDS = {
    'rus': 13,
    '__default__': 22,
}
PERSON_TYPES = {
    'rus': 'ur',
    '__default__': 'eu_yt',
}
CURRENCY_IDS = {
    'kaz': 840,
}


@async.inline_callbacks
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--parks', default=[])
    args = parser.parse_args()
    park_ids = {}
    if args.parks:
        for park_and_type in args.parks.split():
            # handle "999030_pre 999080_post" form
            park_and_type = park_and_type.split('_', 1)
            if len(park_and_type) == 1:
                park_id = park_and_type[0]
                contract_type = (
                    'pre' if park_id in PREPAID_PARK_IDS else 'post'
                )
            else:
                park_id, contract_type = park_and_type
                assert contract_type in {'pre', 'post'}, \
                    'contract type for %s is not one of pre|post' % park_id
            park_ids[park_id] = contract_type
        parks_cursor = db.parks.find({'_id': {'$in': park_ids.keys()}})
    else:
        parks_cursor = db.parks.find()
    park_docs = yield parks_cursor.sort('city').run()
    cities_to_update_balances = collections.defaultdict(list)
    for park_doc in park_docs:
        park_id = park_doc['_id']
        park_name = park_doc['name']
        park_phone = park_doc['phone'] or '123456789'
        park_email = park_doc['email'] or 't@t.t'
        park_city = park_doc['city']
        park_country_doc = yield country_manager.get_doc_by_city_id(park_city)
        park_country = park_country_doc['_id']
        firm_id = FIRM_IDS.get(park_country, FIRM_IDS['__default__'])
        country_id = park_country_doc['region_id']
        currency_id = CURRENCY_IDS.get(park_country)
        person_type = PERSON_TYPES.get(park_country, PERSON_TYPES['__default__'])

        print park_city, park_id
        try:
            billing_client_id = None
            billing_client_id_start = dates.localize()
            for billing_service in billing.settings.BILLINGS:
                billing_client_id = yield park_manager.create_billing_products(
                    billing_service,
                    park_doc,
                    billing_client_id,
                    billing_client_id_start,
                    PASSPORT_UID
                )
            print '\tnew client_id:', billing_client_id

            print '\tcreating person_id'
            person_id = yield create_person_id(
                PASSPORT_UID, billing_client_id,
                park_name, park_email, park_phone, person_type
            )

            contract_type = park_ids.get(
                park_id,  # if provided in script args
                'pre' if park_id in PREPAID_PARK_IDS else 'post'
            )
            print '\tcreating %spaid contract' % contract_type
            contract_info = yield create_contract(
                PASSPORT_UID, billing_client_id, person_id, contract_type,
                firm_id, country_id, currency_id
            )
            print '\tcreated %spaid contract: %s' % (contract_type, contract_info)

            cities_to_update_balances[park_doc['city']].append(park_id)
        except Exception as exc:
            print 'for park', park_id, ':', exc.__class__.__name__, exc

    for city_id, clids in cities_to_update_balances.iteritems():
        print u'NOT updated balances in %s, to perform it manually, issue:' % city_id
        print u"\tparks_balances.update_parks_balances_single_city(u'%s', %s)" % (city_id, clids)

    print 'waiting until balances are created in Balance (10-minutely)'
    now = datetime.datetime.utcnow()
    after_10_mins = now + datetime.timedelta(minutes=10)
    rounded = datetime.datetime(
        after_10_mins.year,
        after_10_mins.month,
        after_10_mins.day,
        after_10_mins.hour,
        int(after_10_mins.minute / 10) * 10
    ) + datetime.timedelta(minutes=1)
    left_to_wait = (rounded - now).seconds
    print 'waiting till {}, left {} seconds to wait'.format(rounded, left_to_wait)
    time.sleep(left_to_wait)
    print 'update parks balances'
    yield update_parks_balances.do_stuff()
    print 'import drivers'
    yield import_drivers.do_stuff()


@async.inline_callbacks
def create_person_id(operator_id, client_id, name, email, phone, person_type,
                     log_extra=None):
    """Create invoice in billing to prepay commissions.

    :param operator_id: Yandex uid of user who creates the invoice.
    :param client_id: Park's client_id.
    :param name: Park's name.
    :param email: Park's email.
    :param phone: Park's phone.
    :param log_extra: Extra log data.
    :return: Billing's response which is int with person_id.
    """
    person_params = {
        # not sure if we can change everything here, so leave it be
        'client_id': client_id,
        'email': email,
        'fname': name,
        'inn': '7719246912',
        'kpp': '234567890',
        'legaladdress': 'Street',
        'lname': 'Park',
        'longname': 'Organization',
        'mname': 'Test',
        'name': 'Test',
        'person_id': 0,
        'phone': phone,
        'postaddress': 'Street',
        'postcode': '123456',
        'type': person_type,
    }
    response = yield billing.create_client_person(
        operator_id, person_params, log_extra=log_extra
    )
    async.return_value(response)


@async.inline_callbacks
def create_contract(operator_id, client_id, person_id, contract_type, firm_id, country_id, currency_id,
                    log_extra=None):
    """Create invoice in billing to prepay commissions.

    :param operator_id: Yandex uid of user who creates the invoice.
    :param client_id: Park's client_id.
    :param person_id: Some balance person_id to create contract.
    :param contract_type: String of contract type ('pre' or 'post').
    :param log_extra: Extra log data.
    :return: Billing's response which is dict:
        {
            'EXTERNAL_ID': '71272/15',
            'ID': 262180,
        }
    """
    assert contract_type in {'pre', 'post'}, 'contract_type should be pre|post'
    if contract_type == 'pre':
        query_string = get_prepay_query_string(client_id, person_id, firm_id, country_id)
    else:
        query_string = get_postpay_query_string(client_id, person_id, firm_id, country_id)

    post = urlparse.parse_qsl(query_string, True)
    contract_params = {k: v.decode('utf-8') for k, v in post}
    if currency_id is not None:
        contract_params['currency'] = str(currency_id)
    if country_id == 225:
        contract_params['region'] = '77000000000'
    args = (operator_id, contract_params)
    response = yield billing._call_balance(
        'CreateContract', args, log_extra=log_extra
    )
    async.return_value(response)


def get_postpay_query_string(client_id, person_id, firm_id, country_id):
    # this string will be sometimes changed by information from balance
    return (
        'external-id=&num=&fake-id=0&commission=0&print-form-type=0&brand-type=70'
        '&client-id=' + str(client_id) + '&person-id=' + str(person_id) +
        '&account-type=0&firm=' + str(firm_id) + '&country=' + str(country_id) + '&manager-code=20453&manager-bo-code=&dt=2016-09-01T00%3A00%3A00&finish-dt=&payment-type=3&unilateral=1&services=1&services-111=111&services-124=124&services-128=128&memo=&atypical-conditions-checkpassed=1&calc-termination=&attorney-agency-id=&force-direct-migration-checkpassed=1&commission-charge-type=1&minimal-payment-commission=&commission-payback-type=2&commission-payback-pct=&commission-type=&partner-commission-type=1&supercommission-bonus=1&partner-commission-pct=&partner-commission-pct2=0.5+%25&supercommission=0&named-client-declared-sum=&commission-declared-sum=&partner-commission-sum=&linked-contracts=1&limitlinked-contracts=&partner-min-commission-sum=&partner-max-commission-sum=&advance-payment-sum=&region=None&discard-nds=0&discount-policy-type=3&discount-fixed=0&declared-sum=&fixed-discount-pct=&rit-limit=&federal-budget=&federal-declared-budget=&federal-annual-program-budget=&belarus-budget=&belarus-budget-price=&ukr-budget=&kzt-budget=&kzt-agency-budget=&kz-budget=&budget-discount-pct=&rit-discount=&year-planning-discount=&year-planning-discount-custom=&year-product-discount=&wholesale-agent-premium-awards-scale-type=1&use-ua-cons-discount-checkpassed=1&consolidated-discount=&use-consolidated-discount-checkpassed=1&regional-budget=&use-regional-cons-discount-checkpassed=1&pda-budget=&autoru-budget=&retro-discount=&contract-discount=&discount-pct=&discount-findt=&credit-type=2&payment-term=100&payment-term-max=&calc-defermant=0&personal-account=&personal-account-checkpassed=1&auto-credit-checkpassed=1&personal-account-fictive-checkpassed=1&repayment-on-consume-checkpassed=1&credit-limit=17&limitcredit-limit=&credit-currency-limit=810&limitcredit-currency-limit=&credit-limit-single=&credit-limit-in-contract-currency-checkpassed=1&turnover-forecast=17&limitturnover-forecast=&partner-credit=&partner-credit-checkpassed=1&discount-commission=&pp-1137-checkpassed=1&non-resident-clients-checkpassed=1&new-commissioner-report-checkpassed=1&link-contract-id=&service-min-cost=40000&test-period-duration=&adfox-products=%5B%7B%22id%22%3A%221%22%2C%22num%22%3A505178%2C%22name%22%3A%22ADFOX.Adv+%28agency%29%22%2C%22scale%22%3A%22%22%2C%22account%22%3A%22%22%7D%2C%7B%22id%22%3A%222%22%2C%22num%22%3A504642%2C%22name%22%3A%22ADFOX.Adv+%28agency%29+default%22%2C%22scale%22%3A%22%22%2C%22account%22%3A%22%22%7D%2C%7B%22id%22%3A%223%22%2C%22num%22%3A505175%2C%22name%22%3A%22ADFOX.Adv+%28standart%29%22%2C%22scale%22%3A%22%22%2C%22account%22%3A%22%22%7D%2C%7B%22id%22%3A%224%22%2C%22num%22%3A504404%2C%22name%22%3A%22ADFOX.Adv+%28standart%29+default%22%2C%22scale%22%3A%22%22%2C%22account%22%3A%22%22%7D%2C%7B%22id%22%3A%225%22%2C%22num%22%3A505174%2C%22name%22%3A%22ADFOX.Exchange%22%2C%22scale%22%3A%22%22%2C%22account%22%3A%22%22%7D%2C%7B%22id%22%3A%226%22%2C%22num%22%3A504403%2C%22name%22%3A%22ADFOX.Exchange+default%22%2C%22scale%22%3A%22%22%2C%22account%22%3A%22%22%7D%2C%7B%22id%22%3A%227%22%2C%22num%22%3A505173%2C%22name%22%3A%22ADFOX.Mobile%22%2C%22scale%22%3A%22%22%2C%22account%22%3A%22%22%7D%2C%7B%22id%22%3A%228%22%2C%22num%22%3A504402%2C%22name%22%3A%22ADFOX.Mobile+default%22%2C%22scale%22%3A%22%22%2C%22account%22%3A%22%22%7D%2C%7B%22id%22%3A%229%22%2C%22num%22%3A505172%2C%22name%22%3A%22ADFOX.Nets%22%2C%22scale%22%3A%22%22%2C%22account%22%3A%22%22%7D%2C%7B%22id%22%3A%2210%22%2C%22num%22%3A504401%2C%22name%22%3A%22ADFOX.Nets+default%22%2C%22scale%22%3A%22%22%2C%22account%22%3A%22%22%7D%2C%7B%22id%22%3A%2211%22%2C%22num%22%3A504441%2C%22name%22%3A%22ADFOX.Sites%2Bmobile+default%22%2C%22scale%22%3A%22%22%2C%22account%22%3A%22%22%7D%2C%7B%22id%22%3A%2212%22%2C%22num%22%3A505171%2C%22name%22%3A%22ADFOX.Sites%2Bmobile+%28shows%29%22%2C%22scale%22%3A%22%22%2C%22account%22%3A%22%22%7D%2C%7B%22id%22%3A%2213%22%2C%22num%22%3A504400%2C%22name%22%3A%22ADFOX.Sites1+default%22%2C%22scale%22%3A%22%22%2C%22account%22%3A%22%22%7D%2C%7B%22id%22%3A%2214%22%2C%22num%22%3A505170%2C%22name%22%3A%22ADFOX.Sites1+%28shows%29%22%2C%22scale%22%3A%22%22%2C%22account%22%3A%22%22%7D%2C%7B%22id%22%3A%2215%22%2C%22num%22%3A505176%2C%22name%22%3A%22ADFOX.Sites2+%28requests%29%22%2C%22scale%22%3A%22%22%2C%22account%22%3A%22%22%7D%2C%7B%22id%22%3A%2216%22%2C%22num%22%3A505177%2C%22name%22%3A%22%D0%92%D1%8B%D0%B3%D1%80%D1%83%D0%B7%D0%BA%D0%B0+%D0%BB%D0%BE%D0%B3%D0%BE%D0%B2+%D0%B8%D0%B7+%D0%9F%D1%80%D0%BE%D0%B3%D1%80%D0%B0%D0%BC%D0%BC%D1%8B%22%2C%22scale%22%3A%22%22%2C%22account%22%3A%22%22%7D%2C%7B%22id%22%3A%2217%22%2C%22num%22%3A504420%2C%22name%22%3A%22%D0%97%D0%B0%D0%B2%D0%B5%D0%B4%D0%B5%D0%BD%D0%B8%D0%B5+%D1%80%D0%B5%D0%BA%D0%BB%D0%B0%D0%BC%D0%BD%D0%BE%D0%B9+%D0%BA%D0%B0%D0%BC%D0%BF%D0%B0%D0%BD%D0%B8%D0%B8%22%2C%22scale%22%3A%22%22%2C%22account%22%3A%22%22%7D%2C%7B%22id%22%3A%2218%22%2C%22num%22%3A504421%2C%22name%22%3A%22%D0%97%D0%B0%D0%B2%D0%B5%D0%B4%D0%B5%D0%BD%D0%B8%D0%B5+%D1%80%D0%B5%D0%BA%D0%BB%D0%B0%D0%BC%D0%BD%D0%BE%D0%B9+%D0%BA%D0%B0%D0%BC%D0%BF%D0%B0%D0%BD%D0%B8%D0%B8+Adv%22%2C%22scale%22%3A%22%22%2C%22account%22%3A%22%22%7D%2C%7B%22id%22%3A%2219%22%2C%22num%22%3A504412%2C%22name%22%3A%22%D0%97%D0%B0%D0%BF%D1%80%D0%BE%D1%81%D1%8B+ADFox%22%2C%22scale%22%3A%22%22%2C%22account%22%3A%22%22%7D%2C%7B%22id%22%3A%2220%22%2C%22num%22%3A504423%2C%22name%22%3A%22%D0%98%D1%81%D0%BF%D0%BE%D0%BB%D1%8C%D0%B7%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5+%D0%BC%D0%BE%D0%B4%D1%83%D0%BB%D1%8F+%C2%AB%D0%A2%D0%B0%D1%80%D0%B3%D0%B5%D1%82%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5+%D0%BF%D0%BE+%D0%BF%D0%BE%D0%B2%D0%B5%D0%B4%D0%B5%D0%BD%D0%B8%D1%8E%C2%BB+%D0%B4%D0%BB%D1%8F+ADFOX.Sites%2BMobile%22%2C%22scale%22%3A%22%22%2C%22account%22%3A%22%22%7D%2C%7B%22id%22%3A%2221%22%2C%22num%22%3A504422%2C%22name%22%3A%22%D0%98%D1%81%D0%BF%D0%BE%D0%BB%D1%8C%D0%B7%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5+%D0%BC%D0%BE%D0%B4%D1%83%D0%BB%D1%8F+%5C%22%D0%A2%D0%B0%D1%80%D0%B3%D0%B5%D1%82%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5+%D0%BF%D0%BE+%D0%BF%D0%BE%D0%B2%D0%B5%D0%B4%D0%B5%D0%BD%D0%B8%D1%8E%5C%22+%D0%B4%D0%BB%D1%8F+ADFOX.Sites1+%28shows%29%22%2C%22scale%22%3A%22%22%2C%22account%22%3A%22%22%7D%2C%7B%22id%22%3A%2222%22%2C%22num%22%3A504644%2C%22name%22%3A%22%D0%98%D1%81%D0%BF%D0%BE%D0%BB%D1%8C%D0%B7%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5+%D0%BC%D0%BE%D0%B4%D1%83%D0%BB%D1%8F+%5C%22%D0%A2%D0%B0%D1%80%D0%B3%D0%B5%D1%82%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5+%D0%BF%D0%BE+%D0%BF%D0%BE%D0%B2%D0%B5%D0%B4%D0%B5%D0%BD%D0%B8%D1%8E%5C%22+%D0%B4%D0%BB%D1%8F+ADFOX.Sites2+%28requests%29%22%2C%22scale%22%3A%22%22%2C%22account%22%3A%22%22%7D%2C%7B%22id%22%3A%2223%22%2C%22num%22%3A504424%2C%22name%22%3A%22%D0%9A%D0%B0%D1%81%D1%82%D0%BE%D0%BC%D0%B8%D0%B7%D0%B0%D1%86%D0%B8%D1%8F+%D0%B0%D0%BA%D0%BA%D0%B0%D1%83%D0%BD%D1%82%D0%B0%22%2C%22scale%22%3A%22%22%2C%22account%22%3A%22%22%7D%2C%7B%22id%22%3A%2224%22%2C%22num%22%3A504419%2C%22name%22%3A%22%D0%9D%D0%B5%D1%81%D1%82%D0%B0%D0%BD%D0%B4%D0%B0%D1%80%D1%82%D0%BD%D0%B0%D1%8F+%D1%81%D1%82%D0%B0%D1%82%D0%B8%D1%81%D1%82%D0%B8%D1%87%D0%B5%D1%81%D0%BA%D0%B0%D1%8F+%D0%BE%D1%82%D1%87%D0%B5%D1%82%D0%BD%D0%BE%D1%81%D1%82%D1%8C+%28%D0%BF%D0%BE%D0%B4%D0%B4%D0%B5%D1%80%D0%B6%D0%BA%D0%B0%29%22%2C%22scale%22%3A%22%22%2C%22account%22%3A%22%22%7D%2C%7B%22id%22%3A%2225%22%2C%22num%22%3A507216%2C%22name%22%3A%22%D0%9D%D0%B5%D1%81%D1%82%D0%B0%D0%BD%D0%B4%D0%B0%D1%80%D1%82%D0%BD%D1%8B%D0%B5+%D1%84%D0%BE%D1%80%D0%BC%D0%B0%D1%82%D1%8B+%D0%BE%D1%82%D1%87%D0%B5%D1%82%D0%BD%D0%BE%D1%81%D1%82%D0%B8+-+%D0%B3%D1%80%D1%83%D0%BF%D0%BF%D0%B0%22%2C%22scale%22%3A%22%22%2C%22account%22%3A%22%22%7D%2C%7B%22id%22%3A%2226%22%2C%22num%22%3A507217%2C%22name%22%3A%22%D0%9D%D0%B5%D1%81%D1%82%D0%B0%D0%BD%D0%B4%D0%B0%D1%80%D1%82%D0%BD%D1%8B%D0%B9+%D1%84%D0%BE%D1%80%D0%BC%D0%B0%D1%82+%D0%BC%D0%B0%D1%82%D0%B5%D1%80%D0%B8%D0%B0%D0%BB%D0%BE%D0%B2+In-page+video+A-NF%22%2C%22scale%22%3A%22%22%2C%22account%22%3A%22%22%7D%2C%7B%22id%22%3A%2227%22%2C%22num%22%3A504418%2C%22name%22%3A%22%D0%A0%D0%B0%D0%B7%D1%80%D0%B0%D0%B1%D0%BE%D1%82%D0%BA%D0%B0+%D0%BD%D0%B5%D1%81%D1%82%D0%B0%D0%BD%D0%B4%D0%B0%D1%80%D1%82%D0%BD%D0%BE%D0%B9+%D1%81%D1%82%D0%B0%D1%82%D0%B8%D1%81%D1%82%D0%B8%D1%87%D0%B5%D1%81%D0%BA%D0%BE%D0%B9+%D0%BE%D1%82%D1%87%D0%B5%D1%82%D0%BD%D0%BE%D1%81%D1%82%D0%B8%22%2C%22scale%22%3A%22%22%2C%22account%22%3A%22%22%7D%2C%7B%22id%22%3A%2228%22%2C%22num%22%3A505422%2C%22name%22%3A%22%D0%A2%D0%B0%D1%80%D0%B3%D0%B5%D1%82%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5+%D0%9C%D0%B0%D1%82%D0%B5%D1%80%D0%B8%D0%B0%D0%BB%D0%BE%D0%B2+%D0%BF%D0%BE+%D0%BF%D0%BE%D0%BB%D1%83%2C+%D0%B2%D0%BE%D0%B7%D1%80%D0%B0%D1%81%D1%82%D1%83+%D0%B8+%D0%B4%D0%BE%D1%85%D0%BE%D0%B4%D1%83+%D0%B4%D0%BB%D1%8F+Adv+%28AA-PVD%29%22%2C%22scale%22%3A%22%22%2C%22account%22%3A%22%22%7D%2C%7B%22id%22%3A%2229%22%2C%22num%22%3A505423%2C%22name%22%3A%22%D0%A2%D0%B0%D1%80%D0%B3%D0%B5%D1%82%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5+%D0%9C%D0%B0%D1%82%D0%B5%D1%80%D0%B8%D0%B0%D0%BB%D0%BE%D0%B2+%D0%BF%D0%BE+%D0%BF%D0%BE%D0%BB%D1%83%2C+%D0%B2%D0%BE%D0%B7%D1%80%D0%B0%D1%81%D1%82%D1%83+%D0%B8+%D0%B4%D0%BE%D1%85%D0%BE%D0%B4%D1%83+%D0%B4%D0%BB%D1%8F+Adv+%28%D0%90%D0%B3%D0%B5%D0%BD%D1%82%D1%81%D1%82%D0%B2%D0%BE%29+%28AA-AG-PVD%29%22%2C%22scale%22%3A%22%22%2C%22account%22%3A%22%22%7D%2C%7B%22id%22%3A%2230%22%2C%22num%22%3A505424%2C%22name%22%3A%22%D0%A2%D0%B0%D1%80%D0%B3%D0%B5%D1%82%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5+%D0%9C%D0%B0%D1%82%D0%B5%D1%80%D0%B8%D0%B0%D0%BB%D0%BE%D0%B2+%D0%BF%D0%BE+%D0%BF%D0%BE%D0%BB%D1%83%2C+%D0%B2%D0%BE%D0%B7%D1%80%D0%B0%D1%81%D1%82%D1%83+%D0%B8+%D0%B4%D0%BE%D1%85%D0%BE%D0%B4%D1%83+%D0%B4%D0%BB%D1%8F+Mobile+%28AM-PVD%29%22%2C%22scale%22%3A%22%22%2C%22account%22%3A%22%22%7D%2C%7B%22id%22%3A%2231%22%2C%22num%22%3A505425%2C%22name%22%3A%22%D0%A2%D0%B0%D1%80%D0%B3%D0%B5%D1%82%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5+%D0%9C%D0%B0%D1%82%D0%B5%D1%80%D0%B8%D0%B0%D0%BB%D0%BE%D0%B2+%D0%BF%D0%BE+%D0%BF%D0%BE%D0%BB%D1%83%2C+%D0%B2%D0%BE%D0%B7%D1%80%D0%B0%D1%81%D1%82%D1%83+%D0%B8+%D0%B4%D0%BE%D1%85%D0%BE%D0%B4%D1%83+%D0%B4%D0%BB%D1%8F+Nets+%28AN-PVD%29%22%2C%22scale%22%3A%22%22%2C%22account%22%3A%22%22%7D%2C%7B%22id%22%3A%2232%22%2C%22num%22%3A505426%2C%22name%22%3A%22%D0%A2%D0%B0%D1%80%D0%B3%D0%B5%D1%82%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5+%D0%9C%D0%B0%D1%82%D0%B5%D1%80%D0%B8%D0%B0%D0%BB%D0%BE%D0%B2+%D0%BF%D0%BE+%D0%BF%D0%BE%D0%BB%D1%83%2C+%D0%B2%D0%BE%D0%B7%D1%80%D0%B0%D1%81%D1%82%D1%83+%D0%B8+%D0%B4%D0%BE%D1%85%D0%BE%D0%B4%D1%83+%D0%B4%D0%BB%D1%8F+Sites+%28AS-PVD%29%22%2C%22scale%22%3A%22%22%2C%22account%22%3A%22%22%7D%2C%7B%22id%22%3A%2233%22%2C%22num%22%3A505427%2C%22name%22%3A%22%D0%A2%D0%B0%D1%80%D0%B3%D0%B5%D1%82%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5+%D0%9C%D0%B0%D1%82%D0%B5%D1%80%D0%B8%D0%B0%D0%BB%D0%BE%D0%B2+%D0%BF%D0%BE+%D0%BF%D0%BE%D0%BB%D1%83%2C+%D0%B2%D0%BE%D0%B7%D1%80%D0%B0%D1%81%D1%82%D1%83+%D0%B8+%D0%B4%D0%BE%D1%85%D0%BE%D0%B4%D1%83+%D0%B4%D0%BB%D1%8F+Sites%2BMobile+%28AS%2BM-PVD%29%22%2C%22scale%22%3A%22%22%2C%22account%22%3A%22%22%7D%2C%7B%22id%22%3A%2234%22%2C%22num%22%3A505428%2C%22name%22%3A%22%D0%A2%D0%B0%D1%80%D0%B3%D0%B5%D1%82%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5+%D0%9C%D0%B0%D1%82%D0%B5%D1%80%D0%B8%D0%B0%D0%BB%D0%BE%D0%B2+%D0%BF%D0%BE+%D0%BF%D0%BE%D0%BB%D1%83%2C+%D0%B2%D0%BE%D0%B7%D1%80%D0%B0%D1%81%D1%82%D1%83+%D0%B8+%D0%B4%D0%BE%D1%85%D0%BE%D0%B4%D1%83+%D0%B4%D0%BB%D1%8F+Sites-R+%28AS-R-PVD%29%22%2C%22scale%22%3A%22%22%2C%22account%22%3A%22%22%7D%2C%7B%22id%22%3A%2235%22%2C%22num%22%3A504413%2C%22name%22%3A%22%D0%A2%D0%B0%D1%80%D0%B3%D0%B5%D1%82%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5+%D0%9C%D0%B0%D1%82%D0%B5%D1%80%D0%B8%D0%B0%D0%BB%D0%BE%D0%B2+%D0%BF%D0%BE+%D0%BF%D0%BE%D0%BB%D1%83+%D0%B8+%D0%B2%D0%BE%D0%B7%D1%80%D0%B0%D1%81%D1%82%D1%83+%D0%B4%D0%BB%D1%8F+ADFOX.Sites%22%2C%22scale%22%3A%22%22%2C%22account%22%3A%22%22%7D%2C%7B%22id%22%3A%2236%22%2C%22num%22%3A504414%2C%22name%22%3A%22%D0%A2%D0%B0%D1%80%D0%B3%D0%B5%D1%82%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5+%D0%9C%D0%B0%D1%82%D0%B5%D1%80%D0%B8%D0%B0%D0%BB%D0%BE%D0%B2+%D0%BF%D0%BE+%D0%BF%D0%BE%D0%BB%D1%83+%D0%B8+%D0%B2%D0%BE%D0%B7%D1%80%D0%B0%D1%81%D1%82%D1%83+%D0%B4%D0%BB%D1%8F+ADFOX.Sites%2BMobile%22%2C%22scale%22%3A%22%22%2C%22account%22%3A%22%22%7D%2C%7B%22id%22%3A%2237%22%2C%22num%22%3A506516%2C%22name%22%3A%22%D0%A2%D0%B0%D1%80%D0%B3%D0%B5%D1%82%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5+%D0%BC%D0%B0%D1%82%D0%B5%D1%80%D0%B8%D0%B0%D0%BB%D0%BE%D0%B2+%28%D1%80%D0%B0%D1%81%D1%88%D0%B8%D1%80%D0%B5%D0%BD%D0%BD%D1%8B%D0%B9+%D0%BF%D0%B0%D0%BA%D0%B5%D1%82%29%22%2C%22scale%22%3A%22%22%2C%22account%22%3A%22%22%7D%2C%7B%22id%22%3A%2238%22%2C%22num%22%3A506517%2C%22name%22%3A%22%D0%A2%D0%B5%D1%85%D0%BD%D0%B8%D1%87%D0%B5%D1%81%D0%BA%D0%B0%D1%8F+%D0%B8%D0%BD%D1%82%D0%B5%D0%B3%D1%80%D0%B0%D1%86%D0%B8%D1%8F+%D1%81%D0%B5%D1%80%D0%B2%D0%B8%D1%81%D0%BE%D0%B2+%C2%AB%D0%AF%D0%BD%D0%B4%D0%B5%D0%BA%D1%81.%D0%A0%D0%B0%D0%B4%D0%B8%D0%BE%C2%BB+%D0%B8+%C2%AB%D0%AF%D0%BD%D0%B4%D0%B5%D0%BA%D1%81.%D0%9C%D1%83%D0%B7%D1%8B%D0%BA%D0%B0%C2%BB%22%2C%22scale%22%3A%22%22%2C%22account%22%3A%22%22%7D%5D&apikeys-tariffs=%5B%7B%22group_id%22%3A%221%22%2C%22group_cc%22%3A%22apikeys_rasp%22%2C%22group_name%22%3A%22API+%D0%AF%D0%BD%D0%B4%D0%B5%D0%BA%D1%81.%D0%A0%D0%B0%D1%81%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9%22%2C%22member%22%3A%22%22%2C%22id%22%3A%221%22%7D%2C%7B%22group_id%22%3A%222%22%2C%22group_cc%22%3A%22apikeys_atom%22%2C%22group_name%22%3A%22API+%D0%90%D1%82%D0%BE%D0%BC%D0%B0%22%2C%22member%22%3A%22%22%2C%22id%22%3A%222%22%7D%2C%7B%22group_id%22%3A%223%22%2C%22group_cc%22%3A%22apikeys_microtest%22%2C%22group_name%22%3A%22API+%D0%B2%D0%B0%D0%BB%D0%B8%D0%B4%D0%B0%D1%82%D0%BE%D1%80%D0%B0+%D0%BC%D0%B8%D0%BA%D1%80%D0%BE%D1%80%D0%B0%D0%B7%D0%BC%D0%B5%D1%82%D0%BA%D0%B8%22%2C%22member%22%3A%22%22%2C%22id%22%3A%223%22%7D%2C%7B%22group_id%22%3A%224%22%2C%22group_cc%22%3A%22apikeys_text_rec%22%2C%22group_name%22%3A%22API+%D0%A0%D0%B0%D1%81%D0%BF%D0%BE%D0%B7%D0%BD%D0%B0%D0%B2%D0%B0%D0%BD%D0%B8%D1%8F+%D1%82%D0%B5%D0%BA%D1%81%D1%82%D0%B0%22%2C%22member%22%3A%22%22%2C%22id%22%3A%224%22%7D%2C%7B%22group_id%22%3A%225%22%2C%22group_cc%22%3A%22apikeys_aviatickets%22%2C%22group_name%22%3A%22API+%D0%AF%D0%BD%D0%B4%D0%B5%D0%BA%D1%81.%D0%90%D0%B2%D0%B8%D0%B0%D0%B1%D0%B8%D0%BB%D0%B5%D1%82%D0%BE%D0%B2%22%2C%22member%22%3A%22%22%2C%22id%22%3A%225%22%7D%2C%7B%22group_id%22%3A%226%22%2C%22group_cc%22%3A%22apikeys_raspmobile%22%2C%22group_name%22%3A%22API+%D0%AF%D0%BD%D0%B4%D0%B5%D0%BA%D1%81.%D0%A0%D0%B0%D1%81%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9+%D0%B4%D0%BB%D1%8F+%D0%BC%D0%BE%D0%B1%D0%B8%D0%BB%D1%8C%D0%BD%D1%8B%D1%85+%D0%BF%D1%80%D0%B8%D0%BB%D0%BE%D0%B6%D0%B5%D0%BD%D0%B8%D0%B9%22%2C%22member%22%3A%22%22%2C%22id%22%3A%226%22%7D%2C%7B%22group_id%22%3A%227%22%2C%22group_cc%22%3A%22apikeys_rabota%22%2C%22group_name%22%3A%22API+%D0%AF%D0%BD%D0%B4%D0%B5%D0%BA%D1%81.%D0%A0%D0%B0%D0%B1%D0%BE%D1%82%D1%8B%22%2C%22member%22%3A%22%22%2C%22id%22%3A%227%22%7D%2C%7B%22group_id%22%3A%228%22%2C%22group_cc%22%3A%22apikeys_realty%22%2C%22group_name%22%3A%22API+%D0%AF%D0%BD%D0%B4%D0%B5%D0%BA%D1%81.%D0%9D%D0%B5%D0%B4%D0%B2%D0%B8%D0%B6%D0%B8%D0%BC%D0%BE%D1%81%D1%82%D0%B8%22%2C%22member%22%3A%22%22%2C%22id%22%3A%228%22%7D%2C%7B%22group_id%22%3A%229%22%2C%22group_cc%22%3A%22apikeys_auto%22%2C%22group_name%22%3A%22API+%D0%AF%D0%BD%D0%B4%D0%B5%D0%BA%D1%81.%D0%90%D0%B2%D1%82%D0%BE%22%2C%22member%22%3A%22%22%2C%22id%22%3A%229%22%7D%2C%7B%22group_id%22%3A%2210%22%2C%22group_cc%22%3A%22apikeys_speechkit%22%2C%22group_name%22%3A%22Yandex+SpeechKit%22%2C%22member%22%3A%22%22%2C%22id%22%3A%2210%22%7D%2C%7B%22group_id%22%3A%2211%22%2C%22group_cc%22%3A%22apikeys_city%22%2C%22group_name%22%3A%22API+%D0%9F%D0%BE%D0%B8%D1%81%D0%BA%D0%B0+%D0%BF%D0%BE+%D0%BE%D1%80%D0%B3%D0%B0%D0%BD%D0%B8%D0%B7%D0%B0%D1%86%D0%B8%D1%8F%D0%BC%22%2C%22member%22%3A%22%22%2C%22id%22%3A%2211%22%7D%2C%7B%22group_id%22%3A%2212%22%2C%22group_cc%22%3A%22apikeys_apimaps%22%2C%22group_name%22%3A%22API+%D0%AF%D0%BD%D0%B4%D0%B5%D0%BA%D1%81.%D0%9A%D0%B0%D1%80%D1%82%22%2C%22member%22%3A%22%22%2C%22id%22%3A%2212%22%7D%2C%7B%22group_id%22%3A%2213%22%2C%22group_cc%22%3A%22apikeys_market%22%2C%22group_name%22%3A%22API+%D0%AF%D0%BD%D0%B4%D0%B5%D0%BA%D1%81.%D0%9C%D0%B0%D1%80%D0%BA%D0%B5%D1%82%D0%B0%22%2C%22member%22%3A%22%22%2C%22id%22%3A%2213%22%7D%2C%7B%22group_id%22%3A%2214%22%2C%22group_cc%22%3A%22apikeys_partner%22%2C%22group_name%22%3A%22API+%D0%9F%D0%B0%D1%80%D1%82%D0%BD%D0%B5%D1%80%D1%81%D0%BA%D0%BE%D0%B3%D0%BE+%D0%B8%D0%BD%D1%82%D0%B5%D1%80%D1%84%D0%B5%D0%B9%D1%81%D0%B0%22%2C%22member%22%3A%22%22%2C%22id%22%3A%2214%22%7D%2C%7B%22group_id%22%3A%2215%22%2C%22group_cc%22%3A%22apikeys_testv6%22%2C%22group_name%22%3A%22Test+IPv6%22%2C%22member%22%3A%22%22%2C%22id%22%3A%2215%22%7D%2C%7B%22group_id%22%3A%2216%22%2C%22group_cc%22%3A%22apikeys_pogoda%22%2C%22group_name%22%3A%22API+%D0%AF%D0%BD%D0%B4%D0%B5%D0%BA%D1%81.%D0%9F%D0%BE%D0%B3%D0%BE%D0%B4%D1%8B%22%2C%22member%22%3A%22%22%2C%22id%22%3A%2216%22%7D%2C%7B%22group_id%22%3A%2217%22%2C%22group_cc%22%3A%22apikeys_speechkitjsapi%22%2C%22group_name%22%3A%22SpeechKit+JavaScript+Web+API%22%2C%22member%22%3A%22%22%2C%22id%22%3A%2217%22%7D%2C%7B%22group_id%22%3A%2218%22%2C%22group_cc%22%3A%22apikeys_speechkitmobile%22%2C%22group_name%22%3A%22SpeechKit+Mobile+SDK%22%2C%22member%22%3A%22%22%2C%22id%22%3A%2218%22%7D%2C%7B%22group_id%22%3A%2219%22%2C%22group_cc%22%3A%22apikeys_speechkitcloud%22%2C%22group_name%22%3A%22SpeechKit+Cloud%22%2C%22member%22%3A%22%22%2C%22id%22%3A%2219%22%7D%2C%7B%22group_id%22%3A%2220%22%2C%22group_cc%22%3A%22apikeys_staticmaps%22%2C%22group_name%22%3A%22Static+API+%D0%AF%D0%BD%D0%B4%D0%B5%D0%BA%D1%81.%D0%9A%D0%B0%D1%80%D1%82%22%2C%22member%22%3A%22%22%2C%22id%22%3A%2220%22%7D%2C%7B%22group_id%22%3A%2221%22%2C%22group_cc%22%3A%22apikeys_ydfimoder%22%2C%22group_name%22%3A%22API+YDF.ImageModeration%22%2C%22member%22%3A%22%22%2C%22id%22%3A%2221%22%7D%5D&commission-categories=%5B%5D&autoru-q-plan=&loyal-clients=%5B%5D&client-limits=%5B%5D&brand-clients=%5B%5D&discard-media-discount-checkpassed=1&is-booked-checkpassed=1&is-booked-dt=&is-faxed-checkpassed=1&is-signed=&is-signed-checkpassed=1&is-signed-date=5+%D1%81%D0%B5%D0%BD+2016+%D0%B3.&is-signed-dt=2016-09-05T00%3A00%3A00&deal-passport-checkpassed=1&sent-dt-checkpassed=1&is-suspended-checkpassed=1&button-submit=%D0%A1%D0%BE%D1%85%D1%80%D0%B0%D0%BD%D0%B8%D1%82%D1%8C&collateral-form=&id='
    )


def get_prepay_query_string(client_id, person_id, firm_id, country_id):
    # this string will be sometimes changed by information from balance
    return (
        '&external-id=&num=&fake-id=0&commission=0&print-form-type=0&brand-type=70'
        '&client-id=' + str(client_id) + '&person-id=' + str(person_id) +
        '&firm=' + str(firm_id) + '&country=' + str(country_id) + '&account-type=0&bank-details-id=510&manager-code=20453&manager-bo-code=&dt=2016-09-01T00%3A00%3A00&finish-dt=&payment-type=2&unilateral=1&services=1&services-111=111&services-124=124&services-128=128&memo=&atypical-conditions-checkpassed=1&calc-termination=&attorney-agency-id=&force-direct-migration-checkpassed=1&commission-charge-type=1&minimal-payment-commission=&commission-payback-type=2&commission-payback-pct=&commission-type=&partner-commission-type=1&supercommission-bonus=1&partner-commission-pct=&partner-commission-pct2=&supercommission=0&named-client-declared-sum=&commission-declared-sum=&partner-commission-sum=&linked-contracts=1&limitlinked-contracts=&partner-min-commission-sum=&partner-max-commission-sum=&advance-payment-sum=10000&region=77000000000&discard-nds=0&discount-policy-type=3&discount-fixed=0&declared-sum=&fixed-discount-pct=&rit-limit=&federal-budget=&federal-declared-budget=&federal-annual-program-budget=&belarus-budget=&belarus-budget-price=&ukr-budget=&kzt-budget=&kzt-agency-budget=&kz-budget=&budget-discount-pct=&rit-discount=&year-planning-discount=&year-planning-discount-custom=&year-product-discount=&wholesale-agent-premium-awards-scale-type=1&use-ua-cons-discount-checkpassed=1&consolidated-discount=&use-consolidated-discount-checkpassed=1&regional-budget=&use-regional-cons-discount-checkpassed=1&pda-budget=&autoru-budget=&retro-discount=&contract-discount=&discount-pct=&discount-findt=&credit-type=0&payment-term=&payment-term-max=&calc-defermant=0&personal-account=&personal-account-checkpassed=1&auto-credit-checkpassed=1&lift-credit-on-payment-checkpassed=1&personal-account-fictive-checkpassed=1&repayment-on-consume-checkpassed=1&credit-limit=17&limitcredit-limit=&credit-currency-limit=810&limitcredit-currency-limit=&credit-limit-single=&credit-limit-in-contract-currency-checkpassed=1&turnover-forecast=17&limitturnover-forecast=&partner-credit-checkpassed=1&discount-commission=&pp-1137-checkpassed=1&non-resident-clients-checkpassed=1&new-commissioner-report-checkpassed=1&link-contract-id=&service-min-cost=&test-period-duration=&adfox-products=%5B%7B%22id%22%3A%221%22%2C%22num%22%3A505178%2C%22name%22%3A%22ADFOX.Adv+%28agency%29%22%2C%22scale%22%3A%22%22%2C%22account%22%3A%22%22%7D%2C%7B%22id%22%3A%222%22%2C%22num%22%3A504642%2C%22name%22%3A%22ADFOX.Adv+%28agency%29+default%22%2C%22scale%22%3A%22%22%2C%22account%22%3A%22%22%7D%2C%7B%22id%22%3A%223%22%2C%22num%22%3A505175%2C%22name%22%3A%22ADFOX.Adv+%28standart%29%22%2C%22scale%22%3A%22%22%2C%22account%22%3A%22%22%7D%2C%7B%22id%22%3A%224%22%2C%22num%22%3A504404%2C%22name%22%3A%22ADFOX.Adv+%28standart%29+default%22%2C%22scale%22%3A%22%22%2C%22account%22%3A%22%22%7D%2C%7B%22id%22%3A%225%22%2C%22num%22%3A505174%2C%22name%22%3A%22ADFOX.Exchange%22%2C%22scale%22%3A%22%22%2C%22account%22%3A%22%22%7D%2C%7B%22id%22%3A%226%22%2C%22num%22%3A504403%2C%22name%22%3A%22ADFOX.Exchange+default%22%2C%22scale%22%3A%22%22%2C%22account%22%3A%22%22%7D%2C%7B%22id%22%3A%227%22%2C%22num%22%3A505173%2C%22name%22%3A%22ADFOX.Mobile%22%2C%22scale%22%3A%22%22%2C%22account%22%3A%22%22%7D%2C%7B%22id%22%3A%228%22%2C%22num%22%3A504402%2C%22name%22%3A%22ADFOX.Mobile+default%22%2C%22scale%22%3A%22%22%2C%22account%22%3A%22%22%7D%2C%7B%22id%22%3A%229%22%2C%22num%22%3A505172%2C%22name%22%3A%22ADFOX.Nets%22%2C%22scale%22%3A%22%22%2C%22account%22%3A%22%22%7D%2C%7B%22id%22%3A%2210%22%2C%22num%22%3A504401%2C%22name%22%3A%22ADFOX.Nets+default%22%2C%22scale%22%3A%22%22%2C%22account%22%3A%22%22%7D%2C%7B%22id%22%3A%2211%22%2C%22num%22%3A504441%2C%22name%22%3A%22ADFOX.Sites%2Bmobile+default%22%2C%22scale%22%3A%22%22%2C%22account%22%3A%22%22%7D%2C%7B%22id%22%3A%2212%22%2C%22num%22%3A505171%2C%22name%22%3A%22ADFOX.Sites%2Bmobile+%28shows%29%22%2C%22scale%22%3A%22%22%2C%22account%22%3A%22%22%7D%2C%7B%22id%22%3A%2213%22%2C%22num%22%3A504400%2C%22name%22%3A%22ADFOX.Sites1+default%22%2C%22scale%22%3A%22%22%2C%22account%22%3A%22%22%7D%2C%7B%22id%22%3A%2214%22%2C%22num%22%3A505170%2C%22name%22%3A%22ADFOX.Sites1+%28shows%29%22%2C%22scale%22%3A%22%22%2C%22account%22%3A%22%22%7D%2C%7B%22id%22%3A%2215%22%2C%22num%22%3A505176%2C%22name%22%3A%22ADFOX.Sites2+%28requests%29%22%2C%22scale%22%3A%22%22%2C%22account%22%3A%22%22%7D%2C%7B%22id%22%3A%2216%22%2C%22num%22%3A505177%2C%22name%22%3A%22%D0%92%D1%8B%D0%B3%D1%80%D1%83%D0%B7%D0%BA%D0%B0+%D0%BB%D0%BE%D0%B3%D0%BE%D0%B2+%D0%B8%D0%B7+%D0%9F%D1%80%D0%BE%D0%B3%D1%80%D0%B0%D0%BC%D0%BC%D1%8B%22%2C%22scale%22%3A%22%22%2C%22account%22%3A%22%22%7D%2C%7B%22id%22%3A%2217%22%2C%22num%22%3A504420%2C%22name%22%3A%22%D0%97%D0%B0%D0%B2%D0%B5%D0%B4%D0%B5%D0%BD%D0%B8%D0%B5+%D1%80%D0%B5%D0%BA%D0%BB%D0%B0%D0%BC%D0%BD%D0%BE%D0%B9+%D0%BA%D0%B0%D0%BC%D0%BF%D0%B0%D0%BD%D0%B8%D0%B8%22%2C%22scale%22%3A%22%22%2C%22account%22%3A%22%22%7D%2C%7B%22id%22%3A%2218%22%2C%22num%22%3A504421%2C%22name%22%3A%22%D0%97%D0%B0%D0%B2%D0%B5%D0%B4%D0%B5%D0%BD%D0%B8%D0%B5+%D1%80%D0%B5%D0%BA%D0%BB%D0%B0%D0%BC%D0%BD%D0%BE%D0%B9+%D0%BA%D0%B0%D0%BC%D0%BF%D0%B0%D0%BD%D0%B8%D0%B8+Adv%22%2C%22scale%22%3A%22%22%2C%22account%22%3A%22%22%7D%2C%7B%22id%22%3A%2219%22%2C%22num%22%3A504412%2C%22name%22%3A%22%D0%97%D0%B0%D0%BF%D1%80%D0%BE%D1%81%D1%8B+ADFox%22%2C%22scale%22%3A%22%22%2C%22account%22%3A%22%22%7D%2C%7B%22id%22%3A%2220%22%2C%22num%22%3A504423%2C%22name%22%3A%22%D0%98%D1%81%D0%BF%D0%BE%D0%BB%D1%8C%D0%B7%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5+%D0%BC%D0%BE%D0%B4%D1%83%D0%BB%D1%8F+%C2%AB%D0%A2%D0%B0%D1%80%D0%B3%D0%B5%D1%82%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5+%D0%BF%D0%BE+%D0%BF%D0%BE%D0%B2%D0%B5%D0%B4%D0%B5%D0%BD%D0%B8%D1%8E%C2%BB+%D0%B4%D0%BB%D1%8F+ADFOX.Sites%2BMobile%22%2C%22scale%22%3A%22%22%2C%22account%22%3A%22%22%7D%2C%7B%22id%22%3A%2221%22%2C%22num%22%3A504422%2C%22name%22%3A%22%D0%98%D1%81%D0%BF%D0%BE%D0%BB%D1%8C%D0%B7%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5+%D0%BC%D0%BE%D0%B4%D1%83%D0%BB%D1%8F+%5C%22%D0%A2%D0%B0%D1%80%D0%B3%D0%B5%D1%82%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5+%D0%BF%D0%BE+%D0%BF%D0%BE%D0%B2%D0%B5%D0%B4%D0%B5%D0%BD%D0%B8%D1%8E%5C%22+%D0%B4%D0%BB%D1%8F+ADFOX.Sites1+%28shows%29%22%2C%22scale%22%3A%22%22%2C%22account%22%3A%22%22%7D%2C%7B%22id%22%3A%2222%22%2C%22num%22%3A504644%2C%22name%22%3A%22%D0%98%D1%81%D0%BF%D0%BE%D0%BB%D1%8C%D0%B7%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5+%D0%BC%D0%BE%D0%B4%D1%83%D0%BB%D1%8F+%5C%22%D0%A2%D0%B0%D1%80%D0%B3%D0%B5%D1%82%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5+%D0%BF%D0%BE+%D0%BF%D0%BE%D0%B2%D0%B5%D0%B4%D0%B5%D0%BD%D0%B8%D1%8E%5C%22+%D0%B4%D0%BB%D1%8F+ADFOX.Sites2+%28requests%29%22%2C%22scale%22%3A%22%22%2C%22account%22%3A%22%22%7D%2C%7B%22id%22%3A%2223%22%2C%22num%22%3A504424%2C%22name%22%3A%22%D0%9A%D0%B0%D1%81%D1%82%D0%BE%D0%BC%D0%B8%D0%B7%D0%B0%D1%86%D0%B8%D1%8F+%D0%B0%D0%BA%D0%BA%D0%B0%D1%83%D0%BD%D1%82%D0%B0%22%2C%22scale%22%3A%22%22%2C%22account%22%3A%22%22%7D%2C%7B%22id%22%3A%2224%22%2C%22num%22%3A504419%2C%22name%22%3A%22%D0%9D%D0%B5%D1%81%D1%82%D0%B0%D0%BD%D0%B4%D0%B0%D1%80%D1%82%D0%BD%D0%B0%D1%8F+%D1%81%D1%82%D0%B0%D1%82%D0%B8%D1%81%D1%82%D0%B8%D1%87%D0%B5%D1%81%D0%BA%D0%B0%D1%8F+%D0%BE%D1%82%D1%87%D0%B5%D1%82%D0%BD%D0%BE%D1%81%D1%82%D1%8C+%28%D0%BF%D0%BE%D0%B4%D0%B4%D0%B5%D1%80%D0%B6%D0%BA%D0%B0%29%22%2C%22scale%22%3A%22%22%2C%22account%22%3A%22%22%7D%2C%7B%22id%22%3A%2225%22%2C%22num%22%3A507216%2C%22name%22%3A%22%D0%9D%D0%B5%D1%81%D1%82%D0%B0%D0%BD%D0%B4%D0%B0%D1%80%D1%82%D0%BD%D1%8B%D0%B5+%D1%84%D0%BE%D1%80%D0%BC%D0%B0%D1%82%D1%8B+%D0%BE%D1%82%D1%87%D0%B5%D1%82%D0%BD%D0%BE%D1%81%D1%82%D0%B8+-+%D0%B3%D1%80%D1%83%D0%BF%D0%BF%D0%B0%22%2C%22scale%22%3A%22%22%2C%22account%22%3A%22%22%7D%2C%7B%22id%22%3A%2226%22%2C%22num%22%3A507217%2C%22name%22%3A%22%D0%9D%D0%B5%D1%81%D1%82%D0%B0%D0%BD%D0%B4%D0%B0%D1%80%D1%82%D0%BD%D1%8B%D0%B9+%D1%84%D0%BE%D1%80%D0%BC%D0%B0%D1%82+%D0%BC%D0%B0%D1%82%D0%B5%D1%80%D0%B8%D0%B0%D0%BB%D0%BE%D0%B2+In-page+video+A-NF%22%2C%22scale%22%3A%22%22%2C%22account%22%3A%22%22%7D%2C%7B%22id%22%3A%2227%22%2C%22num%22%3A504418%2C%22name%22%3A%22%D0%A0%D0%B0%D0%B7%D1%80%D0%B0%D0%B1%D0%BE%D1%82%D0%BA%D0%B0+%D0%BD%D0%B5%D1%81%D1%82%D0%B0%D0%BD%D0%B4%D0%B0%D1%80%D1%82%D0%BD%D0%BE%D0%B9+%D1%81%D1%82%D0%B0%D1%82%D0%B8%D1%81%D1%82%D0%B8%D1%87%D0%B5%D1%81%D0%BA%D0%BE%D0%B9+%D0%BE%D1%82%D1%87%D0%B5%D1%82%D0%BD%D0%BE%D1%81%D1%82%D0%B8%22%2C%22scale%22%3A%22%22%2C%22account%22%3A%22%22%7D%2C%7B%22id%22%3A%2228%22%2C%22num%22%3A505422%2C%22name%22%3A%22%D0%A2%D0%B0%D1%80%D0%B3%D0%B5%D1%82%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5+%D0%9C%D0%B0%D1%82%D0%B5%D1%80%D0%B8%D0%B0%D0%BB%D0%BE%D0%B2+%D0%BF%D0%BE+%D0%BF%D0%BE%D0%BB%D1%83%2C+%D0%B2%D0%BE%D0%B7%D1%80%D0%B0%D1%81%D1%82%D1%83+%D0%B8+%D0%B4%D0%BE%D1%85%D0%BE%D0%B4%D1%83+%D0%B4%D0%BB%D1%8F+Adv+%28AA-PVD%29%22%2C%22scale%22%3A%22%22%2C%22account%22%3A%22%22%7D%2C%7B%22id%22%3A%2229%22%2C%22num%22%3A505423%2C%22name%22%3A%22%D0%A2%D0%B0%D1%80%D0%B3%D0%B5%D1%82%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5+%D0%9C%D0%B0%D1%82%D0%B5%D1%80%D0%B8%D0%B0%D0%BB%D0%BE%D0%B2+%D0%BF%D0%BE+%D0%BF%D0%BE%D0%BB%D1%83%2C+%D0%B2%D0%BE%D0%B7%D1%80%D0%B0%D1%81%D1%82%D1%83+%D0%B8+%D0%B4%D0%BE%D1%85%D0%BE%D0%B4%D1%83+%D0%B4%D0%BB%D1%8F+Adv+%28%D0%90%D0%B3%D0%B5%D0%BD%D1%82%D1%81%D1%82%D0%B2%D0%BE%29+%28AA-AG-PVD%29%22%2C%22scale%22%3A%22%22%2C%22account%22%3A%22%22%7D%2C%7B%22id%22%3A%2230%22%2C%22num%22%3A505424%2C%22name%22%3A%22%D0%A2%D0%B0%D1%80%D0%B3%D0%B5%D1%82%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5+%D0%9C%D0%B0%D1%82%D0%B5%D1%80%D0%B8%D0%B0%D0%BB%D0%BE%D0%B2+%D0%BF%D0%BE+%D0%BF%D0%BE%D0%BB%D1%83%2C+%D0%B2%D0%BE%D0%B7%D1%80%D0%B0%D1%81%D1%82%D1%83+%D0%B8+%D0%B4%D0%BE%D1%85%D0%BE%D0%B4%D1%83+%D0%B4%D0%BB%D1%8F+Mobile+%28AM-PVD%29%22%2C%22scale%22%3A%22%22%2C%22account%22%3A%22%22%7D%2C%7B%22id%22%3A%2231%22%2C%22num%22%3A505425%2C%22name%22%3A%22%D0%A2%D0%B0%D1%80%D0%B3%D0%B5%D1%82%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5+%D0%9C%D0%B0%D1%82%D0%B5%D1%80%D0%B8%D0%B0%D0%BB%D0%BE%D0%B2+%D0%BF%D0%BE+%D0%BF%D0%BE%D0%BB%D1%83%2C+%D0%B2%D0%BE%D0%B7%D1%80%D0%B0%D1%81%D1%82%D1%83+%D0%B8+%D0%B4%D0%BE%D1%85%D0%BE%D0%B4%D1%83+%D0%B4%D0%BB%D1%8F+Nets+%28AN-PVD%29%22%2C%22scale%22%3A%22%22%2C%22account%22%3A%22%22%7D%2C%7B%22id%22%3A%2232%22%2C%22num%22%3A505426%2C%22name%22%3A%22%D0%A2%D0%B0%D1%80%D0%B3%D0%B5%D1%82%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5+%D0%9C%D0%B0%D1%82%D0%B5%D1%80%D0%B8%D0%B0%D0%BB%D0%BE%D0%B2+%D0%BF%D0%BE+%D0%BF%D0%BE%D0%BB%D1%83%2C+%D0%B2%D0%BE%D0%B7%D1%80%D0%B0%D1%81%D1%82%D1%83+%D0%B8+%D0%B4%D0%BE%D1%85%D0%BE%D0%B4%D1%83+%D0%B4%D0%BB%D1%8F+Sites+%28AS-PVD%29%22%2C%22scale%22%3A%22%22%2C%22account%22%3A%22%22%7D%2C%7B%22id%22%3A%2233%22%2C%22num%22%3A505427%2C%22name%22%3A%22%D0%A2%D0%B0%D1%80%D0%B3%D0%B5%D1%82%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5+%D0%9C%D0%B0%D1%82%D0%B5%D1%80%D0%B8%D0%B0%D0%BB%D0%BE%D0%B2+%D0%BF%D0%BE+%D0%BF%D0%BE%D0%BB%D1%83%2C+%D0%B2%D0%BE%D0%B7%D1%80%D0%B0%D1%81%D1%82%D1%83+%D0%B8+%D0%B4%D0%BE%D1%85%D0%BE%D0%B4%D1%83+%D0%B4%D0%BB%D1%8F+Sites%2BMobile+%28AS%2BM-PVD%29%22%2C%22scale%22%3A%22%22%2C%22account%22%3A%22%22%7D%2C%7B%22id%22%3A%2234%22%2C%22num%22%3A505428%2C%22name%22%3A%22%D0%A2%D0%B0%D1%80%D0%B3%D0%B5%D1%82%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5+%D0%9C%D0%B0%D1%82%D0%B5%D1%80%D0%B8%D0%B0%D0%BB%D0%BE%D0%B2+%D0%BF%D0%BE+%D0%BF%D0%BE%D0%BB%D1%83%2C+%D0%B2%D0%BE%D0%B7%D1%80%D0%B0%D1%81%D1%82%D1%83+%D0%B8+%D0%B4%D0%BE%D1%85%D0%BE%D0%B4%D1%83+%D0%B4%D0%BB%D1%8F+Sites-R+%28AS-R-PVD%29%22%2C%22scale%22%3A%22%22%2C%22account%22%3A%22%22%7D%2C%7B%22id%22%3A%2235%22%2C%22num%22%3A504413%2C%22name%22%3A%22%D0%A2%D0%B0%D1%80%D0%B3%D0%B5%D1%82%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5+%D0%9C%D0%B0%D1%82%D0%B5%D1%80%D0%B8%D0%B0%D0%BB%D0%BE%D0%B2+%D0%BF%D0%BE+%D0%BF%D0%BE%D0%BB%D1%83+%D0%B8+%D0%B2%D0%BE%D0%B7%D1%80%D0%B0%D1%81%D1%82%D1%83+%D0%B4%D0%BB%D1%8F+ADFOX.Sites%22%2C%22scale%22%3A%22%22%2C%22account%22%3A%22%22%7D%2C%7B%22id%22%3A%2236%22%2C%22num%22%3A504414%2C%22name%22%3A%22%D0%A2%D0%B0%D1%80%D0%B3%D0%B5%D1%82%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5+%D0%9C%D0%B0%D1%82%D0%B5%D1%80%D0%B8%D0%B0%D0%BB%D0%BE%D0%B2+%D0%BF%D0%BE+%D0%BF%D0%BE%D0%BB%D1%83+%D0%B8+%D0%B2%D0%BE%D0%B7%D1%80%D0%B0%D1%81%D1%82%D1%83+%D0%B4%D0%BB%D1%8F+ADFOX.Sites%2BMobile%22%2C%22scale%22%3A%22%22%2C%22account%22%3A%22%22%7D%2C%7B%22id%22%3A%2237%22%2C%22num%22%3A506516%2C%22name%22%3A%22%D0%A2%D0%B0%D1%80%D0%B3%D0%B5%D1%82%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5+%D0%BC%D0%B0%D1%82%D0%B5%D1%80%D0%B8%D0%B0%D0%BB%D0%BE%D0%B2+%28%D1%80%D0%B0%D1%81%D1%88%D0%B8%D1%80%D0%B5%D0%BD%D0%BD%D1%8B%D0%B9+%D0%BF%D0%B0%D0%BA%D0%B5%D1%82%29%22%2C%22scale%22%3A%22%22%2C%22account%22%3A%22%22%7D%2C%7B%22id%22%3A%2238%22%2C%22num%22%3A506517%2C%22name%22%3A%22%D0%A2%D0%B5%D1%85%D0%BD%D0%B8%D1%87%D0%B5%D1%81%D0%BA%D0%B0%D1%8F+%D0%B8%D0%BD%D1%82%D0%B5%D0%B3%D1%80%D0%B0%D1%86%D0%B8%D1%8F+%D1%81%D0%B5%D1%80%D0%B2%D0%B8%D1%81%D0%BE%D0%B2+%C2%AB%D0%AF%D0%BD%D0%B4%D0%B5%D0%BA%D1%81.%D0%A0%D0%B0%D0%B4%D0%B8%D0%BE%C2%BB+%D0%B8+%C2%AB%D0%AF%D0%BD%D0%B4%D0%B5%D0%BA%D1%81.%D0%9C%D1%83%D0%B7%D1%8B%D0%BA%D0%B0%C2%BB%22%2C%22scale%22%3A%22%22%2C%22account%22%3A%22%22%7D%5D&apikeys-tariffs=%5B%7B%22group_id%22%3A%221%22%2C%22group_cc%22%3A%22apikeys_rasp%22%2C%22group_name%22%3A%22API+%D0%AF%D0%BD%D0%B4%D0%B5%D0%BA%D1%81.%D0%A0%D0%B0%D1%81%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9%22%2C%22member%22%3A%22%22%2C%22id%22%3A%221%22%7D%2C%7B%22group_id%22%3A%222%22%2C%22group_cc%22%3A%22apikeys_atom%22%2C%22group_name%22%3A%22API+%D0%90%D1%82%D0%BE%D0%BC%D0%B0%22%2C%22member%22%3A%22%22%2C%22id%22%3A%222%22%7D%2C%7B%22group_id%22%3A%223%22%2C%22group_cc%22%3A%22apikeys_microtest%22%2C%22group_name%22%3A%22API+%D0%B2%D0%B0%D0%BB%D0%B8%D0%B4%D0%B0%D1%82%D0%BE%D1%80%D0%B0+%D0%BC%D0%B8%D0%BA%D1%80%D0%BE%D1%80%D0%B0%D0%B7%D0%BC%D0%B5%D1%82%D0%BA%D0%B8%22%2C%22member%22%3A%22%22%2C%22id%22%3A%223%22%7D%2C%7B%22group_id%22%3A%224%22%2C%22group_cc%22%3A%22apikeys_text_rec%22%2C%22group_name%22%3A%22API+%D0%A0%D0%B0%D1%81%D0%BF%D0%BE%D0%B7%D0%BD%D0%B0%D0%B2%D0%B0%D0%BD%D0%B8%D1%8F+%D1%82%D0%B5%D0%BA%D1%81%D1%82%D0%B0%22%2C%22member%22%3A%22%22%2C%22id%22%3A%224%22%7D%2C%7B%22group_id%22%3A%225%22%2C%22group_cc%22%3A%22apikeys_aviatickets%22%2C%22group_name%22%3A%22API+%D0%AF%D0%BD%D0%B4%D0%B5%D0%BA%D1%81.%D0%90%D0%B2%D0%B8%D0%B0%D0%B1%D0%B8%D0%BB%D0%B5%D1%82%D0%BE%D0%B2%22%2C%22member%22%3A%22%22%2C%22id%22%3A%225%22%7D%2C%7B%22group_id%22%3A%226%22%2C%22group_cc%22%3A%22apikeys_raspmobile%22%2C%22group_name%22%3A%22API+%D0%AF%D0%BD%D0%B4%D0%B5%D0%BA%D1%81.%D0%A0%D0%B0%D1%81%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B9+%D0%B4%D0%BB%D1%8F+%D0%BC%D0%BE%D0%B1%D0%B8%D0%BB%D1%8C%D0%BD%D1%8B%D1%85+%D0%BF%D1%80%D0%B8%D0%BB%D0%BE%D0%B6%D0%B5%D0%BD%D0%B8%D0%B9%22%2C%22member%22%3A%22%22%2C%22id%22%3A%226%22%7D%2C%7B%22group_id%22%3A%227%22%2C%22group_cc%22%3A%22apikeys_rabota%22%2C%22group_name%22%3A%22API+%D0%AF%D0%BD%D0%B4%D0%B5%D0%BA%D1%81.%D0%A0%D0%B0%D0%B1%D0%BE%D1%82%D1%8B%22%2C%22member%22%3A%22%22%2C%22id%22%3A%227%22%7D%2C%7B%22group_id%22%3A%228%22%2C%22group_cc%22%3A%22apikeys_realty%22%2C%22group_name%22%3A%22API+%D0%AF%D0%BD%D0%B4%D0%B5%D0%BA%D1%81.%D0%9D%D0%B5%D0%B4%D0%B2%D0%B8%D0%B6%D0%B8%D0%BC%D0%BE%D1%81%D1%82%D0%B8%22%2C%22member%22%3A%22%22%2C%22id%22%3A%228%22%7D%2C%7B%22group_id%22%3A%229%22%2C%22group_cc%22%3A%22apikeys_auto%22%2C%22group_name%22%3A%22API+%D0%AF%D0%BD%D0%B4%D0%B5%D0%BA%D1%81.%D0%90%D0%B2%D1%82%D0%BE%22%2C%22member%22%3A%22%22%2C%22id%22%3A%229%22%7D%2C%7B%22group_id%22%3A%2210%22%2C%22group_cc%22%3A%22apikeys_speechkit%22%2C%22group_name%22%3A%22Yandex+SpeechKit%22%2C%22member%22%3A%22%22%2C%22id%22%3A%2210%22%7D%2C%7B%22group_id%22%3A%2211%22%2C%22group_cc%22%3A%22apikeys_city%22%2C%22group_name%22%3A%22API+%D0%9F%D0%BE%D0%B8%D1%81%D0%BA%D0%B0+%D0%BF%D0%BE+%D0%BE%D1%80%D0%B3%D0%B0%D0%BD%D0%B8%D0%B7%D0%B0%D1%86%D0%B8%D1%8F%D0%BC%22%2C%22member%22%3A%22%22%2C%22id%22%3A%2211%22%7D%2C%7B%22group_id%22%3A%2212%22%2C%22group_cc%22%3A%22apikeys_apimaps%22%2C%22group_name%22%3A%22API+%D0%AF%D0%BD%D0%B4%D0%B5%D0%BA%D1%81.%D0%9A%D0%B0%D1%80%D1%82%22%2C%22member%22%3A%22%22%2C%22id%22%3A%2212%22%7D%2C%7B%22group_id%22%3A%2213%22%2C%22group_cc%22%3A%22apikeys_market%22%2C%22group_name%22%3A%22API+%D0%AF%D0%BD%D0%B4%D0%B5%D0%BA%D1%81.%D0%9C%D0%B0%D1%80%D0%BA%D0%B5%D1%82%D0%B0%22%2C%22member%22%3A%22%22%2C%22id%22%3A%2213%22%7D%2C%7B%22group_id%22%3A%2214%22%2C%22group_cc%22%3A%22apikeys_partner%22%2C%22group_name%22%3A%22API+%D0%9F%D0%B0%D1%80%D1%82%D0%BD%D0%B5%D1%80%D1%81%D0%BA%D0%BE%D0%B3%D0%BE+%D0%B8%D0%BD%D1%82%D0%B5%D1%80%D1%84%D0%B5%D0%B9%D1%81%D0%B0%22%2C%22member%22%3A%22%22%2C%22id%22%3A%2214%22%7D%2C%7B%22group_id%22%3A%2215%22%2C%22group_cc%22%3A%22apikeys_testv6%22%2C%22group_name%22%3A%22Test+IPv6%22%2C%22member%22%3A%22%22%2C%22id%22%3A%2215%22%7D%2C%7B%22group_id%22%3A%2216%22%2C%22group_cc%22%3A%22apikeys_pogoda%22%2C%22group_name%22%3A%22API+%D0%AF%D0%BD%D0%B4%D0%B5%D0%BA%D1%81.%D0%9F%D0%BE%D0%B3%D0%BE%D0%B4%D1%8B%22%2C%22member%22%3A%22%22%2C%22id%22%3A%2216%22%7D%2C%7B%22group_id%22%3A%2217%22%2C%22group_cc%22%3A%22apikeys_speechkitjsapi%22%2C%22group_name%22%3A%22SpeechKit+JavaScript+Web+API%22%2C%22member%22%3A%22%22%2C%22id%22%3A%2217%22%7D%2C%7B%22group_id%22%3A%2218%22%2C%22group_cc%22%3A%22apikeys_speechkitmobile%22%2C%22group_name%22%3A%22SpeechKit+Mobile+SDK%22%2C%22member%22%3A%22%22%2C%22id%22%3A%2218%22%7D%2C%7B%22group_id%22%3A%2219%22%2C%22group_cc%22%3A%22apikeys_speechkitcloud%22%2C%22group_name%22%3A%22SpeechKit+Cloud%22%2C%22member%22%3A%22%22%2C%22id%22%3A%2219%22%7D%2C%7B%22group_id%22%3A%2220%22%2C%22group_cc%22%3A%22apikeys_staticmaps%22%2C%22group_name%22%3A%22Static+API+%D0%AF%D0%BD%D0%B4%D0%B5%D0%BA%D1%81.%D0%9A%D0%B0%D1%80%D1%82%22%2C%22member%22%3A%22%22%2C%22id%22%3A%2220%22%7D%2C%7B%22group_id%22%3A%2221%22%2C%22group_cc%22%3A%22apikeys_ydfimoder%22%2C%22group_name%22%3A%22API+YDF.ImageModeration%22%2C%22member%22%3A%22%22%2C%22id%22%3A%2221%22%7D%2C%7B%22group_id%22%3A%2241%22%2C%22group_cc%22%3A%22apikeys_balance%22%2C%22group_name%22%3A%22API+%D0%AF%D0%BD%D0%B4%D0%B5%D0%BA%D1%81.%D0%91%D0%B0%D0%BB%D0%B0%D0%BD%D1%81%22%2C%22member%22%3A%22%22%2C%22id%22%3A%2222%22%7D%2C%7B%22group_id%22%3A%2242%22%2C%22group_cc%22%3A%22apikeys_ydfiduplic%22%2C%22group_name%22%3A%22API+YDF.ImageDuplicates%22%2C%22member%22%3A%22%22%2C%22id%22%3A%2223%22%7D%2C%7B%22group_id%22%3A%2243%22%2C%22group_cc%22%3A%22apikeys_sitesearch%22%2C%22group_name%22%3A%22API+%D0%9F%D0%BE%D0%B8%D1%81%D0%BA%D0%B0+%D0%B4%D0%BB%D1%8F+%D1%81%D0%B0%D0%B9%D1%82%D0%B0%22%2C%22member%22%3A%22%22%2C%22id%22%3A%2224%22%7D%2C%7B%22group_id%22%3A%2244%22%2C%22group_cc%22%3A%22apikeys_testspeechkitcloud%22%2C%22group_name%22%3A%22%5BTEST%5D+SpeechKit+Cloud%22%2C%22member%22%3A%22%22%2C%22id%22%3A%2225%22%7D%5D&commission-categories=%5B%5D&autoru-q-plan=&loyal-clients=%5B%5D&client-limits=%5B%5D&brand-clients=%5B%5D&discard-media-discount-checkpassed=1&is-booked-checkpassed=1&is-booked-dt=&is-faxed-checkpassed=1&is-signed=&is-signed-checkpassed=1&is-signed-date=14+%D1%81%D0%B5%D0%BD+2016+%D0%B3.&is-signed-dt=2016-09-14T00%3A00%3A00&deal-passport-checkpassed=1&sent-dt-checkpassed=1&is-suspended-checkpassed=1&button-submit=%D0%A1%D0%BE%D1%85%D1%80%D0%B0%D0%BD%D0%B8%D1%82%D1%8C&collateral-form=&id='
    )


if __name__ == '__main__':
    main()
