# -*- coding: utf-8 -*-


def assert_form_errors(rv, errors=None, status='error'):
    assert rv.status_code == 400
    assert rv.json.get('status') == status, '{} != {}'.format(repr(rv.json.get('status')), repr(status))
    assert 'error' in rv.json
    if errors:
        actual_errors = {error.split(': ', 1)[0] for error in rv.json['error'].split('; ')}
        assert actual_errors == set(errors)
