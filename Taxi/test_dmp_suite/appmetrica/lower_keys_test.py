from dmp_suite.appmetrica.lower_keys import lower_keys


def test_lower_keys():
    for input_dict, expected in (
        ({}, {}),
        ({'': ''}, {'': ''}),
        ({b'': ''}, {b'': ''}),
        ({'UpperCaseKey': 'UpperCaseValue'}, {'uppercasekey': 'UpperCaseValue'}),
        ({'lowercasekey': 'UpperCaseValue'}, {'lowercasekey': 'UpperCaseValue'}),
        ({b'UpperCaseKey': b'UpperCaseValue'}, {b'uppercasekey': b'UpperCaseValue'}),
        ({b'lowercasekey': b'lowercasevalue'}, {b'lowercasekey': b'lowercasevalue'}),
        ({b'UpperCaseKey': b'UpperCaseValue', 'UpperCaseKey': 'UpperCaseValue'},
         {b'uppercasekey': b'UpperCaseValue', 'uppercasekey': 'UpperCaseValue'}),
        (123, 123),
        ('UpperCaseString', 'UpperCaseString'),
        (
            {
                b'CommonParams': {
                    b'account_type': b'lite',
                    b'account_uid': 12345
                },
                b'commonparams': {
                    b'account_uid': 12345,
                    b'ongoing_orderids': [],
                    b'userid': b'aaaaaaaaaaaaaaaaaaaaaaaaa'
                }
            },
            {
                b'commonparams': {
                    b'account_type': b'lite',
                    b'account_uid': 12345,
                    b'ongoing_orderids': [],
                    b'userid': b'aaaaaaaaaaaaaaaaaaaaaaaaa'
                }
            },
        )
    ):
        actual = lower_keys(input_dict)

        assert (expected == actual), \
            'Expected lower case dict is different from actual:\nexpected: {},\nactual: {}\ntest sample: {}'.format(
                expected, actual, input_dict
            )
