# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pytest

from taxi import config


@pytest.mark.parametrize('city_config', [
    {},
    {'Москва': {'valid_scores': [3, 4, 5]}},
    {
        'Москва': {'valid_scores': [3, 4, 5]},
        'Екатеринбург': {'valid_scores': [2, 3, 4, 5]},
    },
    {
        'Москва': {
            'valid_scores': [3, 4, 5],
            'misc_scores_required': True
        }
    },
    {
        'Москва': {
            'valid_scores': [3, 4, 5],
            'misc_scores_required': False
        }
    }
])
@pytest.inline_callbacks
def test_correct_exam_cities_config(city_config):
    yield config.EXAM_CITIES.save(city_config)


@pytest.mark.parametrize('city_config', [
    [],
    {'Москва': {}},
    {'Москва': {'valid_scores': ['3', '4', '5']}},  # Strings rather than ints
    {
        'Москва': {
            'misc_scores_required': False
        }
    }
])
@pytest.inline_callbacks
def test_incorrect_exam_cities_config(city_config):
    with pytest.raises(config.exceptions.ValidationError):
        yield config.EXAM_CITIES.save(city_config)
