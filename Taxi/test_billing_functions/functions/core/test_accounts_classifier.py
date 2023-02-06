from billing_functions.functions.core import accounts_classifier


def test_is_park_only_sub_account():
    assert accounts_classifier.is_park_only_sub_account('/park_only')
    assert accounts_classifier.is_park_only_sub_account('/park_only/vat')
    assert not accounts_classifier.is_park_only_sub_account('/park_only/vat/1')
    assert not accounts_classifier.is_park_only_sub_account('')
