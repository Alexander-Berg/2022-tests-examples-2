# coding: utf-8

import datetime
import pytz
from collections import namedtuple

import pytest
import torch
import numpy as np

from taxi_pyml.common import (
    time_utils,
    preprocessing,
    text_preprocessor,
    decorators,
    experiments,
    counters,
    hashes,
)


class TestTimeUtils:
    def test_timestamp(self):
        assert (
            time_utils.timestamp(datetime.datetime(2018, 1, 1)) == 1514775600
        )

    def test_localize(self):
        expected = pytz.timezone('Europe/Moscow').localize(
            datetime.datetime(2019, 1, 1, 3, 0),
        )
        assert (
            time_utils.localize(
                datetime.datetime(2019, 1, 1), timezone='Europe/Moscow',
            )
            == expected
        )

    def test_timestring(self):
        assert (
            time_utils.timestring(
                datetime.datetime(2018, 1, 1), timezone='UTC',
            )
            == '2018-01-01T00:00:00+0000'
        )

    def test_parse_timestring_2_aware_dt(self):
        result = time_utils.parse_timestring_2_aware_dt(
            '2018-01-01T00:00:00+0000',
        )
        assert result == datetime.datetime(2018, 1, 1, tzinfo=pytz.utc)

    def test_parse_timestring(self):
        assert time_utils.parse_timestring(
            '2018-01-01T03:00:00+0300',
        ) == datetime.datetime(2018, 1, 1)

    def test_datetime_2_timestamp(self):
        assert (
            time_utils.datetime_2_timestamp(datetime.datetime(2018, 1, 1))
            == 1514764800
        )

    def test_datetime_2_epoch_minutes(self):
        assert (
            time_utils.datetime_2_epoch_minutes(datetime.datetime(2018, 1, 1))
            == 25246080
        )

    def test_parse_datetime(self):
        value = time_utils.parse_datetime('2019-09-01 12:00:34')
        assert value == datetime.datetime(2019, 9, 1, 12, 0, 34)

    def test_parse_epoch_minutes(self):
        value = time_utils.parse_epoch_minutes('2019-09-01 12:00:00')
        assert value == 26122320.0

    def test_str_time_diff(self):
        value = time_utils.str_time_diff(
            '2019-09-01 12:00:00', '2019-12-02 15:00:00',
        )
        assert value == 7959600.0


class TestPreprocessing:
    def test_pytorch_one_hot(self):
        assert torch.equal(
            preprocessing.pytorch_one_hot([1], num_classes=3),
            torch.tensor([0, 1, 0]),
        )
        assert torch.equal(
            preprocessing.pytorch_one_hot([0, 2], num_classes=3),
            torch.tensor([1, 0, 1]),
        )


class TestTextPreprocessor:
    def test_preprocess_text(self):
        assert (
            text_preprocessor.preprocess_text('Привет :) Меня зовут Алиса!')
            == 'привет я звать алиса'
        )

    def test_tokenize_text(self):
        # FIXME pkostikov: tokenizer from package required
        pass


class TestDecorators:
    def test_cached_property(self):
        counter = [0]

        class Example:
            def __init__(self):
                self._cache = dict()

            @decorators.cached_property
            def value(self):
                counter[0] += 1
                return 4 + 7

        example = Example()
        assert counter[0] == 0
        assert example.value == 11
        assert counter[0] == 1
        assert example.value == 11
        assert counter[0] == 1

    def test_cached_method(self):
        counter = [0]

        class Example:
            def __init__(self):
                self._cache = dict()

            @decorators.cached_method
            def value(self, x):
                counter[0] += 1
                return x + 1

        example = Example()
        assert counter[0] == 0
        assert example.value(1) == 2
        assert counter[0] == 1
        assert example.value(2) == 3
        assert counter[0] == 2
        assert example.value(1) == 2
        assert counter[0] == 2
        assert example.value(x=1) == 2
        assert counter[0] == 3
        assert example.value(x=1) == 2
        assert counter[0] == 3

    def test_required_fields(self):
        class Example:
            def __init__(self, x=None, y=None):
                self.x = x
                self.y = y

            @decorators.required_fields('x')
            def get_x(self):
                return self.x

            @decorators.required_fields('y')
            def get_y(self):
                return self.y

        with pytest.raises(ValueError):
            Example().get_x()

        with pytest.raises(ValueError):
            Example(x=1).get_y()

        example = Example(x=1, y=2)
        assert example.get_x() == 1
        assert example.get_y() == 2


class TestExperiments:
    def test_config_types(self):
        config = experiments.Config(
            experiments_description=[
                ('first', [0, 20]),
                ('second', {'type': 'range', 'value': [20, 40]}),
                ('third', {'type': 'exact', 'value': [40, 50]}),
                ('fourth', {'type': 'range', 'value': [41, 50]}),
                ('first', {'type': 'range', 'value': [50, 100]}),
                ('fifth', {'type': 'range', 'value': [50, 100]}),
            ],
        )
        assert config.get_experiments(0) == ['first']
        assert config.get_experiments(20) == ['second']
        assert config.get_experiments(40) == ['third']
        assert config.get_experiments(50) == ['third', 'first', 'fifth']
        assert config.get_experiments(41) == ['fourth']
        assert config.get_experiments(49) == ['fourth']
        assert config.get_experiments(51) == ['first', 'fifth']

    def test_experiment_modes_1(self):
        with pytest.raises(ValueError):
            experiments.Experiment(
                config=experiments.Config(
                    experiments_description=[('first', [0, 20])],
                ),
                field_name='user_id',
                allow_empty=False,
                allow_multiple=False,
            )

    def test_experiment_modes_2(self):
        with pytest.raises(ValueError):
            experiments.Experiment(
                config=experiments.Config(
                    experiments_description=[('first', [0, 20])],
                ),
                field_name='user_id',
                allow_empty=False,
                allow_multiple=True,
            )

    def test_experiment_modes_3(self):
        with pytest.raises(ValueError):
            experiments.Experiment(
                config=experiments.Config(
                    experiments_description=[
                        ('first', [0, 20]),
                        ('second', [19, 21]),
                    ],
                ),
                field_name='user_id',
                allow_empty=True,
                allow_multiple=False,
            )

    def test_experiment_modes_4(self):
        with pytest.raises(ValueError):
            experiments.Experiment(
                config=experiments.Config(
                    experiments_description=[
                        ('first', [0, 100]),
                        ('second', [19, 21]),
                    ],
                ),
                field_name='user_id',
                allow_empty=False,
                allow_multiple=False,
            )

    def test_experiment_modes_5(self):
        exp = experiments.Experiment(
            config=experiments.Config(
                experiments_description=[
                    ('first', [0, 20]),
                    ('second', [20, 60]),
                    ('third', [60, 100]),
                ],
            ),
            field_name='user_id',
            allow_empty=False,
            allow_multiple=False,
            use_attribute=False,
        )

        assert exp({'user_id': 0}) == ['first']
        assert exp({'user_id': 1}) == ['first']
        assert exp({'user_id': 2}) == ['third']
        assert exp({'user_id': 3}) == ['third']
        assert exp({'user_id': 4}) == ['second']
        assert exp({'user_id': 5}) == ['second']

    def test_experiment_modes_6(self):
        exp = experiments.Experiment(
            config=experiments.Config(
                experiments_description=[
                    ('first', [0, 20]),
                    ('second', [20, 60]),
                    ('third', [60, 100]),
                ],
            ),
            field_name='user_id',
            allow_empty=False,
            allow_multiple=False,
            use_attribute=True,
        )
        Struct = namedtuple('Struct', 'user_id')

        assert exp(Struct(user_id=0)) == ['first']
        assert exp(Struct(user_id=1)) == ['first']
        assert exp(Struct(user_id=2)) == ['third']
        assert exp(Struct(user_id=3)) == ['third']
        assert exp(Struct(user_id=4)) == ['second']
        assert exp(Struct(user_id=5)) == ['second']


class TestCounters:
    def test_parse_datetime(self):
        counter = counters.PairwiseCounter.create_from_pair_counts(
            pair_counts=[
                ('123', '123', 100),
                ('1', '1', 80),
                ('2', '2', 60),
                ('1', '2', 30),
                ('2', '1', 30),
            ],
            total_key='123',
        )
        eps = 1e-3
        assert counter.calculate_pmi('1', '2') == pytest.approx(
            np.log(0.625), abs=eps,
        )
        assert counter.calculate_pmi('2', '1') == pytest.approx(
            np.log(0.625), abs=eps,
        )
        assert counter.calculate_npmi('1', '2') == pytest.approx(
            0.3 * np.log(0.625), abs=eps,
        )
        assert counter.calculate_npmi('2', '1') == pytest.approx(
            0.3 * np.log(0.625), abs=eps,
        )


class TestHashes:
    def test_hash_split_predicate(self):
        hash_wrapper = hashes.HashWrapper(
            percent_from=0, percent_to=50, mod=100, salt='salt',
        )
        assert hash_wrapper.get_percent(0) == 16
        assert hash_wrapper.predicate(0)
        assert hash_wrapper.get_percent('abcdef') == 52
        assert hash_wrapper.get_percent(b'abcdef') == 52
        assert not hash_wrapper.predicate('abcdef')

    def test_hash_sha1_predicate(self):
        hash_wrapper = hashes.HashWrapper(
            hash_function=hashes.calculate_sha1,
            percent_from=0,
            percent_to=50,
            mod=100,
            salt='salt',
        )
        assert hash_wrapper.get_percent(0) == 19
        assert hash_wrapper.predicate(0)
        assert hash_wrapper.get_percent('abcdef') == 6
        assert hash_wrapper.get_percent(b'abcdef') == 6
        assert hash_wrapper.predicate('abcdef')
