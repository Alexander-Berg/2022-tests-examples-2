import datetime as dt

from taxi import billing

from taxi_billing_subventions import eye
from taxi_billing_subventions.common import models


def make_journal_entry(attrs):
    entity = models.Entity('unique_driver_id/1', 'driver')
    agreement_id = 'some_agreement_id'
    default_kwargs = {
        'entity': entity,
        'agreement_id': agreement_id,
        'delta': billing.Money.zero('XXX'),
        'sub_account': 'num_orders',
        'all_reasons': [],
        'details': None,
        'event_at': dt.datetime(2019, 1, 2),
        'account_id': None,
        'entry_id': None,
    }
    default_kwargs.update(attrs)
    return models.doc.JournalEntry(**default_kwargs)


def make_support_info(attrs):
    default_kwargs = {
        'kind': 'taxi/v1/order/analytical/subvention',
        'unfit_rules': [make_unfit_rule({})],
    }
    default_kwargs.update(attrs)
    return eye.analytical.SupportInfo(**default_kwargs)


def make_unfit_rule(attrs):
    default_kwargs = {
        'agreement_ref': 'some_agreement_id',
        'sub_account': 'unfit/num_orders',
        'reasons': [
            models.rule.Matcher.match_eq(
                code='mqc', value=True, expected=False,
            ),
        ],
    }
    default_kwargs.update(attrs)
    return eye.common.UnfitRule(**default_kwargs)


def make_info_journal(attrs):
    default_kwargs = {
        'journal': models.doc.SubventionJournal([]),
        'support_info': make_support_info({}),
        'payment_support_info': None,
    }
    default_kwargs.update(attrs)
    return models.doc.InfoJournal(**default_kwargs)
