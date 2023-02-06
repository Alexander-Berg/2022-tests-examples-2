import datetime

import pytest

from taxi_maintenance.stuff import graphite_billing


@pytest.inline_callbacks
@pytest.mark.filldb()
def test_maintenance_graphite_billing():
    interval = graphite_billing.eval_measurement_interval(datetime.datetime(2017, 5, 19, 0, 2))
    refinterval = (datetime.datetime(2017, 5, 19, 0, 0),
                   datetime.datetime(2017, 5, 19, 0, 5))
    assert interval == refinterval

    nextinterval = graphite_billing.eval_measurement_interval(datetime.datetime(2017, 5, 19, 0, 7))
    nextinterval_shtrih = graphite_billing.eval_measurement_interval(datetime.datetime(2017, 5, 19, 0, 5))
    refnextinterval = (datetime.datetime(2017, 5, 19, 0, 5), datetime.datetime(2017, 5, 19, 0, 10))
    assert nextinterval == refnextinterval
    assert nextinterval == nextinterval_shtrih

    docs = yield graphite_billing.fetch_docs(interval)
    assert len(docs) == 8

    codes = graphite_billing.collect_status_codes(docs)
    refcodes = {
        u'status_codes.technical_error._'
            u'7___Failed_to_connect_to_pay_alfabank_ua_port_443__No_route_to_host__': {1495152000: 1},
        u'status_codes.technical_error.Unknown_errorRC_34__reason_Fraud_card__pick_up': {1495152000: 1},
        u'status_codes.payment_timeout.timeout_while_waiting_for_success': {1495152000: 1},
        u'failure_groups.___billing_failure___': {1495152000: 1},
        u'status_codes.technical_error.http_500_Processing_error': {1495152000: 1},
        u'failure_groups.YM': {1495152000: 2},
        u'status_codes.unknown_error.'
            u'AttributeError___module__object_has_no_attribute__card_type_by_number_': {1495152000: 1},
        u'status_codes.not_enough_funds.___empty_status_desc___': {1495152000: 3},
        u'status_codes.technical_error.http_400_Bad_Request': {1495152000: 1},
        u'status_codes.technical_error.Unknown_error__RC__103__reason_Third_party_system_error': {1495152000: 1},
        u'failure_groups.___other___': {1495152000: 9},
        u'status_codes.technical_error.Cant_connect_to_paysys_connection_refused_': {1495152000: 1},
        u'status_codes.authorization_reject.'
            u'Declined_Transaction_not_permitted_to_card__RC_57__reason_'
            u'Transaction_not_permitted_to_card': {1495152000: 1},
        u'failure_groups.Alpha': {1495152000: 1}
    }
    assert codes == refcodes

    metrics = []
    for metric in graphite_billing.build_metric(codes):
        metrics.append(metric)
    refmetrics = [
        (u'billing.status_codes.technical_error._'
                u'7___Failed_to_connect_to_pay_alfabank_ua_port_443__No_route_to_host__', 1, 1495152000),
        (u'billing.status_codes.technical_error.Unknown_errorRC_34__reason_Fraud_card__pick_up', 1, 1495152000),
        (u'billing.status_codes.payment_timeout.timeout_while_waiting_for_success', 1, 1495152000),
        (u'billing.failure_groups.___billing_failure___', 1, 1495152000),
        (u'billing.failure_groups.YM', 2, 1495152000),
        (u'billing.status_codes.unknown_error.'
            u'AttributeError___module__object_has_no_attribute__card_type_by_number_', 1, 1495152000),
        (u'billing.status_codes.not_enough_funds.___empty_status_desc___', 3, 1495152000),
        (u'billing.status_codes.technical_error.http_400_Bad_Request', 1, 1495152000),
        (u'billing.status_codes.technical_error.'
            u'Unknown_error__RC__103__reason_Third_party_system_error', 1, 1495152000),
        (u'billing.status_codes.technical_error.http_500_Processing_error', 1, 1495152000),
        (u'billing.failure_groups.___other___', 9, 1495152000),
        (u'billing.status_codes.technical_error.Cant_connect_to_paysys_connection_refused_', 1, 1495152000),
        (u'billing.status_codes.authorization_reject.'
            u'Declined_Transaction_not_permitted_to_card__RC_57__reason_'
            u'Transaction_not_permitted_to_card', 1, 1495152000),
        (u'billing.failure_groups.Alpha', 1, 1495152000)
    ]
    assert metrics == refmetrics
