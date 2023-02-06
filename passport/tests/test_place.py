# -*- coding: utf-8 -*-
from nose.tools import (
    eq_,
    raises,
)
from passport.backend.core.validators import (
    Invalid,
    Place,
)


def test_place():
    p = Place()
    valid_values = ['fragment', 'query']
    for val in valid_values:
        eq_(p.to_python(val), val)


@raises(Invalid)
def test_place_invalid():
    Place().to_python('some_invalid_place')
