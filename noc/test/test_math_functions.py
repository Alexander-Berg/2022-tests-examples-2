# coding=utf-8
import logging
import os
import types
from unittest.mock import patch

import pytest

if os.environ.get("USE_PYMATH", False):
    import noc.grad.grad.lib.math_functions as math_functions
    from noc.grad.grad.lib.math_functions import (
        delta_count,
        delta,
        resampler_linear,
        resampler_repeat,
        delta_float,
        speed,
    )
else:
    import noc.grad.grad.lib.cmath_functions as math_functions
    from noc.grad.grad.lib.cmath_functions import (
        delta_count,
        delta,
        resampler_linear,
        resampler_repeat,
        delta_float,
        speed,
    )

from noc.grad.grad.lib.pipeline import pipeline, gen_iface_to_fn
from noc.grad.grad.lib.fns import FNS
from noc.grad.grad.lib.test_functions import MIBS, make_job
from noc.grad.grad.lib import snmp_helper

patches = []


def setup_module(module):
    patches.append(patch.dict(snmp_helper.MIBS, MIBS, clear=True))
    for p in patches:
        p.start()


def teardown_module(module):
    for p in patches:
        p.stop()


MAX_UINT64 = 2**64 - 1
TS = 0
TEST_KEY = (("ifname", "eth0"), ("sensor", "rx"))
TEST_KEY_V2 = (("ifname", "eth0"), ("sensor", "tx"))
TEST_KEY2 = (("ifname", "eth1"), ("sensor", "rx"))
PERIOD = 4
TS_PERIOD_0 = TS + PERIOD * 1
TS_PERIOD_1 = TS + PERIOD * 2
TS_PERIOD_2 = TS + PERIOD * 3
TS_PERIOD_3 = TS + PERIOD * 4
TS_PERIOD_4 = TS + PERIOD * 5
NO_LOG = None
TS_PERIOD_5 = TS + PERIOD * 6
DEBUG = True

IFNAME = "100GE3/0/21"
HOST = "localhost"

if DEBUG:
    math_functions.DEBUG = True
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(filename)s:%(lineno)d - %(funcName)s() - %(levelname)s - %(message)s",
    )


def _partial_cmp(p1, p2):
    if p1.func == p2.func and p1.args == p2.args and p1.keywords == p2.keywords:
        return True
    return False


RESAMPLE_CASES = [
    [
        "проверяем что в пропущенный период вычислилось значение",
        [[TS_PERIOD_0, 0], [TS_PERIOD_2, 10]],
        [[TS_PERIOD_1, 5], [TS_PERIOD_2, 10]],
    ],
    [
        "округление",
        [[TS_PERIOD_0, 0], [TS_PERIOD_3, 1]],
        [[TS_PERIOD_1, 1], [TS_PERIOD_2, 1], [TS_PERIOD_3, 1]],
    ],
    [
        "отрицательные числа",
        [[TS_PERIOD_0, 0], [TS_PERIOD_3, -24]],
        [[TS_PERIOD_1, -8], [TS_PERIOD_2, -16], [TS_PERIOD_3, -24]],
    ],
]

FLAP_PIPELINE_CASES = [
    [
        "тест флапов 1",
        [[TS_PERIOD_0, 100], [TS_PERIOD_0 + 1, 100], [TS_PERIOD_3, 200]],
        [[TS_PERIOD_1, 0], [TS_PERIOD_2, 0], [TS_PERIOD_3, 1]],
    ],
    [
        "тест флапов 2",
        [[TS_PERIOD_0, 1], [TS_PERIOD_0 + 1, 1], [TS_PERIOD_4, 1]],
        [[TS_PERIOD_1, 0], [TS_PERIOD_2, 0], [TS_PERIOD_3, 0], [TS_PERIOD_4, 0]],
    ],
    [
        "тест флапов с дыркой",
        [[TS_PERIOD_0, 0], [TS_PERIOD_1, 0], [TS_PERIOD_2 + 2, 0], [TS_PERIOD_3, 0], [TS_PERIOD_5, 0]],
        [[TS_PERIOD_2, 0], [TS_PERIOD_3, 0], [TS_PERIOD_4, 0], [TS_PERIOD_5, 0]],
    ],
]

DELTA_COUNT_CASES = [
    [
        "было изменение числа в TS_PERIOD_1",
        [[TS_PERIOD_0, 1], [TS_PERIOD_1, 999]],
        [[TS_PERIOD_1, 1]],
    ],
    [
        "не было изменение числа",
        [[TS_PERIOD_0, 1], [TS_PERIOD_1, 1]],
        [[TS_PERIOD_1, 0]],
    ],
    [
        "было 1 изменение числа",
        [[TS_PERIOD_0, 100], [TS_PERIOD_1, 100], [TS_PERIOD_2, 200], [TS_PERIOD_3, 200]],
        [[TS_PERIOD_1, 0], [TS_PERIOD_2, 1], [TS_PERIOD_3, 0]],
    ],
    [
        "было 1 изменение числа с пропуском периода",
        [[TS_PERIOD_0, 100], [TS_PERIOD_1, 100], [TS_PERIOD_3, 200]],
        [[TS_PERIOD_1, 0], [TS_PERIOD_3, 1]],
    ],
    [
        "отрицательный ts",
        [[TS_PERIOD_1, 10], [TS_PERIOD_0, 1], [TS_PERIOD_2, 1]],
        [[TS_PERIOD_2, 0]],
    ],
    [
        "одинаковый ts",
        [[TS_PERIOD_1, 100], [TS_PERIOD_1, 100], [TS_PERIOD_1, 100], [TS_PERIOD_2, 100]],
        [[TS_PERIOD_2, 0]],
    ],
]

DELTA_CASES_SIMPLE = [
    [
        "проверка того что нет OverflowError Python int too large to convert to C long",
        (
            (1000, MAX_UINT64 - 300, None),
            (1010, MAX_UINT64 - 200, 10.0),
            (1020, MAX_UINT64 - 100, 10.0),
            (1030, MAX_UINT64, 10.0),
            (1035, MAX_UINT64, 0.0),
            (1040, 0, None),
        ),
    ],
    ["регулярное получение данных", ((1000, 100, None), (1010, 200, 10.0), (1020, 300, 10.0), (1030, 400, 10.0))],
    [
        "переполенение счетчика",
        ((1000, 100, None), (1010, 200, 10.0), (1020, 0, None), (1030, 100, 10.0), (1040, 200, 10.0)),
    ],
]

DELTA_CASES_SIMPLE_FLOAT = [
    [
        "проверка того что нет OverflowError Python int too large to convert to C long",
        (
            (1000, float(MAX_UINT64), None),
            (1010, float(MAX_UINT64) + 10000, 819.2),
            (1020, float(MAX_UINT64) + 20000, 1228.8),
            (1030, 0, None),
        ),
    ],
]

DELTA_CASES = [
    [
        "простая разница",
        [[[TEST_KEY, 0, TS_PERIOD_0]], [[TEST_KEY, PERIOD * 10, TS_PERIOD_1]]],
        [[TEST_KEY, 10, TS_PERIOD_1]],
    ],
    [
        "дробное значение",
        [[[TEST_KEY, 0, TS_PERIOD_0]], [[TEST_KEY, PERIOD * 10 + 2, TS_PERIOD_1]]],
        [[TEST_KEY, 10.5, TS_PERIOD_1]],
    ],
    # ["удаление всех key, ts если value уменьшилось",
    #  ([[TEST_KEY, PERIOD, TS_PERIOD_0], [TEST_KEY_V2, PERIOD, TS_PERIOD_0]],
    #   [[TEST_KEY, 0, TS_PERIOD_1], [TEST_KEY_V2, PERIOD * 2, TS_PERIOD_1]],  # TEST_KEY обнулился
    #   [[TEST_KEY, PERIOD, TS_PERIOD_2], [TEST_KEY_V2, PERIOD * 3, TS_PERIOD_2]],
    #   [[TEST_KEY, PERIOD * 2, TS_PERIOD_3], [TEST_KEY_V2, PERIOD * 4, TS_PERIOD_3]]),
    #  [[TEST_KEY, 1, TS_PERIOD_2], [TEST_KEY_V2, 1, TS_PERIOD_2],
    #   [TEST_KEY, 1, TS_PERIOD_3], [TEST_KEY_V2, 1, TS_PERIOD_3]],
    #  ],
]


@pytest.mark.parametrize("comment, test_input, expected", DELTA_COUNT_CASES)
def test_count_delta(comment, test_input, expected):
    res = []
    prev_data = {}
    for data in test_input:
        input_ts, input_value = data
        kvts_list = [(TEST_KEY, input_value, input_ts)]
        tmp_res = delta_count(prev_data, kvts_list)
        for k, v, ts in tmp_res:
            res.append([ts, v])
    assert res == expected, comment


@pytest.mark.parametrize("comment, test_input, expected", DELTA_CASES)
def test_delta(comment, test_input, expected):
    res = []
    prev_data = {}
    for kvts_list in test_input:
        tmp_res = delta(prev_data, kvts_list)
        for k, v, ts in tmp_res:
            res.append([k, v, ts])
    assert res == expected, comment


@pytest.mark.parametrize("comment, test_input, expected", RESAMPLE_CASES)
def test_resample(comment, test_input, expected):
    res = []
    prev_data = {}
    for data in test_input:
        input_ts, input_value = data
        kvts_list = [(TEST_KEY, input_value, input_ts)]
        tmp_res = resampler_linear(prev_data, kvts_list, period=PERIOD, cast=True)
        for k, v, ts in tmp_res:
            res.append([ts, v])
    assert res == expected, comment


def test_resampler_repeat():
    period = 5
    test_data = [
        [
            # [key, value, ts, res]
            ["left", TEST_KEY, 0, 0, []],
            ["left", TEST_KEY, 10, 10, [[TEST_KEY, 10, 5], [TEST_KEY, 10, 10]]],  # без выравнивания
            ["left", TEST_KEY, 10, 16, [[TEST_KEY, 10, 15]]],  # надо выравнить тк ts=16 а не 15
            ["left", TEST_KEY, 0, 17, []],  # ничего нет. следующие ts 20 должен быть
            ["left", TEST_KEY, 0, 21, [[TEST_KEY, 0, 20]]],
            ["left", TEST_KEY, 0, 25, [[TEST_KEY, 0, 25]]],
            ["left", TEST_KEY, 0, 21, []],  # ts назад
            ["left", TEST_KEY, 10000, 24, []],
            ["left", TEST_KEY, 10000, 26, [[TEST_KEY, 10000, 25]]],
            ["left", TEST_KEY, 10000, 30, [[TEST_KEY, 10000, 30]]],
        ],
        [
            ["right", TEST_KEY, 0, 0, []],
            ["right", TEST_KEY, 10, 10, [[TEST_KEY, 0, 5], [TEST_KEY, 10, 10]]],  # без выравнивания
            ["right", TEST_KEY, 10, 16, [[TEST_KEY, 10, 15]]],  # надо выравнить тк ts=16 а не 15
            ["right", TEST_KEY, 10, 17, []],  # ничего нет. следующие ts 20 должен быть
            ["right", TEST_KEY, 0, 21, [[TEST_KEY, 10, 20]]],
        ],
    ]
    for test in test_data:
        prev_data = {}
        for element in test:
            res = resampler_repeat(prev_data, [tuple(element[1:4])], period=period, direction=element[0], cast=True)
            assert res == element[4]
            # проверка совпадения типов
            for l_index in range(len(res)):
                for k_index in range(len(res)):
                    assert res[l_index][k_index] == element[4][l_index][k_index]
                    assert isinstance(res[l_index][k_index], type(element[4][l_index][k_index]))


@pytest.mark.parametrize("comment, test_input, expected", FLAP_PIPELINE_CASES)
def test_flap_pipeline(comment, test_input, expected):
    TEST_KEY = (("ifname", "eth0"), ("sensor", "flap"))
    all_keys = ["flap"]
    fns = FNS(all_keys)
    fns.add("flap", "delta_count")
    fns.add("flap", "resampler_repeat_%s" % PERIOD)
    pl = pipeline(make_job(), fns)
    res = []
    for data in test_input:
        input_ts, input_value = data
        kvts_list = [(TEST_KEY, input_value, input_ts)]
        tmp_res = pl.send(kvts_list)
        for ts, k, v in tmp_res:
            res.append([ts, v["flap"]])
    assert res == expected, comment


def _resample_test(test_data, period):
    prev_data = {}
    for element, exp in test_data:
        res = resampler_linear(prev_data, [tuple(x) for x in element], period=period)
        exp = [tuple(x) for x in exp]
        assert res == exp
        # for l in range(len(res)):
        #     for k in range(len(res)):
        #         .assertEqual(res[l][k], exp[l][k])
        #         .assertEqual(type(res[l][k]), type(exp[l][k]))


def test_resampler1():
    test_data = [
        [[[TEST_KEY, 0, 0]], []],
        [[[TEST_KEY, 10, 10]], [(TEST_KEY, 5, 5), (TEST_KEY, 10, 10)]],
    ]
    _resample_test(test_data, 5)


def test_resampler_multikey():
    test_data = [
        [[[TEST_KEY, 0, 0], [TEST_KEY2, 0, 0]], []],
        [
            [[TEST_KEY, 10, 10], [TEST_KEY2, 10, 10]],
            [[TEST_KEY, 5, 5], [TEST_KEY, 10, 10], [TEST_KEY2, 5, 5], [TEST_KEY2, 10, 10]],
        ],
    ]
    _resample_test(test_data, 5)


def test_no_resample_in_future():
    key = ("key",)
    prev_data = {}
    resampler_linear(prev_data, [(key, 0.566, 822)], period=60, cast=True)
    f = resampler_linear(prev_data, [(key, 0.183, 882)], period=60, cast=True)
    assert f == [(('key',), 1, 840)]


def test_no_resample_in_future2():
    key = ("key",)
    prev_data = {}
    resampler_linear(prev_data, [(key, 0.75, 1473691034)], period=60, cast=True)
    res = resampler_linear(prev_data, [(key, 0, 1473691162)], period=60, cast=True)
    assert res == [(key, 1, 1473691080), (key, 1, 1473691140)]


def test_resample_small_interval():
    # в интервал семплирования ничего не попадает
    key = ("key",)
    prev_data = {}
    resampler_linear(prev_data, [(key, 1, 1)], period=60)
    res = resampler_linear(prev_data, [(key, 2, 2)], period=60)
    assert res == []


def test_resample_long_interval():
    # в интервал семплирования попадает больше 1-го измерения
    resampler = gen_iface_to_fn(resampler_linear, period=20)()
    res = []
    for i in [1, 5, 10, 12, 18, 21, 30, 65]:
        tmp = resampler.send([(TEST_KEY, i, i)])
        res.extend(tmp)
    assert [(TEST_KEY, 20.0, 20), (TEST_KEY, 40.0, 40), (TEST_KEY, 60.0, 60)] == res


def test_resample_align_in_interval():
    # в интервал семплирования попадает выравненные данные
    prev_data = {}
    resampler_linear(prev_data, [(TEST_KEY, 1, 1)], period=60)
    resampler_linear(prev_data, [(TEST_KEY, 55, 55)], period=60)
    res = resampler_linear(prev_data, [(TEST_KEY, 65, 65)], period=60)
    assert res == [(TEST_KEY, 60, 60)]


def test_resample_rounding_issue():
    """
    из-за округлений могут возникать не те числа что ожидаются
    """
    prev_data = {}
    # тут 120.1111111111111 - 120.1111111111111/120*120 != 0
    # может и отрицательное число получится

    resampler_linear(prev_data, [(TEST_KEY, 120.1111111111111, 0)], period=60, cast=False)
    f = resampler_linear(prev_data, [(TEST_KEY, 0, 120)], period=60, cast=False)
    assert f == [(TEST_KEY, 60.05555555555556, 60), (TEST_KEY, 0.0, 120)]


def test_resample_key_blink():
    """иногда ключи могут пропадат. мы должны какое-то время хранить старые данные"""
    prev_data = {}
    resampler_linear(prev_data, [(TEST_KEY, 1, 1), (TEST_KEY2, 101, 1)], period=60, cast=None)

    res = resampler_linear(prev_data, [(TEST_KEY, 61, 61)], period=60, cast=None)
    assert res == [(TEST_KEY, 60.0, 60)]
    res = resampler_linear(prev_data, [(TEST_KEY, 121, 121), (TEST_KEY2, 221, 121)], period=60, cast=None)
    assert res == [(TEST_KEY, 120.0, 120), (TEST_KEY2, 160.0, 60), (TEST_KEY2, 220.0, 120)]
    res = resampler_linear(prev_data, [(TEST_KEY, 181, 181), (TEST_KEY2, 281, 181)], period=60, cast=None)
    assert res == [(TEST_KEY, 180.0, 180), (TEST_KEY2, 280.0, 180)]


def _delta_wrapper(test_data, fn=delta):
    counter_name = "counter"
    key = ("key", counter_name)
    prev_data = {}
    for ts, counter_value, expect_delta in test_data:
        res = fn(prev_data, [[key, counter_value, ts]])
        if expect_delta is not None:
            if not res:
                raise Exception("received empty data from delta calculator. expected %s at ts=%s" % (expect_delta, ts))
            r = res[0][1]
            assert r == expect_delta, "%s != %s at %s" % (r, expect_delta, ts)
        else:
            assert res == []


@pytest.mark.parametrize("comment, test_input", DELTA_CASES_SIMPLE)
def test_delta_simple(comment, test_input):
    _delta_wrapper(test_data=test_input)


@pytest.mark.parametrize("comment, test_input", DELTA_CASES_SIMPLE_FLOAT)
def test_delta_simple_float(comment, test_input):
    _delta_wrapper(test_data=test_input, fn=delta_float)


def _run_fn_or_gen(fn, in_data):
    fn_prev_data = {}
    if isinstance(fn, types.GeneratorType):
        data = fn.send(in_data)
    else:
        data = fn(fn_prev_data, in_data)
    return data


SPEED_CASES = [
    [
        "простые ровные данные",
        [[TS_PERIOD_0, 0], [TS_PERIOD_1, 1 * PERIOD], [TS_PERIOD_2, 2 * PERIOD]],
        [[TS_PERIOD_1, 1], [TS_PERIOD_2, 1]],
    ],
    [
        "в один период(TS_PERIOD_0) много данных",
        [
            [TS_PERIOD_0, 0],
            [TS_PERIOD_0 + 1, 0],
            [TS_PERIOD_0 + 2, 0],
            [TS_PERIOD_1, 1 * PERIOD],
            [TS_PERIOD_2, 2 * PERIOD],
        ],
        [[TS_PERIOD_1, 1], [TS_PERIOD_2, 1]],
    ],
    [
        "слишком большой интервал между данными",
        [
            [TS_PERIOD_0, 0],  # промежуток
            [1000 + TS_PERIOD_0, 0],
            [1000 + TS_PERIOD_1, 1 * PERIOD],
            [1000 + TS_PERIOD_2, 2 * PERIOD],
        ],
        [[1000 + TS_PERIOD_1, 1], [1000 + TS_PERIOD_2, 1]],
    ],
    [
        "обнуление счетчика",
        [[TS_PERIOD_0 + 1, 1], [TS_PERIOD_1, 1 * PERIOD], [TS_PERIOD_2, 0], [TS_PERIOD_3, 1 * PERIOD]],
        [[TS_PERIOD_3, 1]],
    ],
    [
        "уменьшается ts",
        [
            [TS_PERIOD_2, 2 * PERIOD],
            [TS_PERIOD_3, 3 * PERIOD],
            [TS_PERIOD_0, 0],
            [TS_PERIOD_4, 4 * PERIOD],
            [TS_PERIOD_5, 5 * PERIOD],
        ],
        [
            [TS_PERIOD_3, 1],
            # [TS_PERIOD_4, 1] должен сброс кеша данных
            [TS_PERIOD_5, 1],
        ],
    ],
    [
        "между вторым и третьим измерением нет целого интервала ",
        [[TS_PERIOD_0, 0], [TS_PERIOD_1 + 1, PERIOD + 1], [TS_PERIOD_2, PERIOD * 2]],
        [[TS_PERIOD_1, 1], [TS_PERIOD_2, 1]],
    ],
    [
        "new_ts в align отрицательный",  # потому что второй TS_PERIOD_0 + 1 будет выравнен до TS_PERIOD_0
        [[TS_PERIOD_0 + 1, 0], [TS_PERIOD_0 + 1, 0]],
        [],
    ],
    [
        "дробные числа",
        [[TS_PERIOD_0, 0], [TS_PERIOD_1, 1]],
        [[TS_PERIOD_1, 0.25]],
    ],
    [
        "несколько интервалов между замерами без выравнивания",
        [[TS_PERIOD_0, 0], [TS_PERIOD_3, PERIOD * 3]],
        [[TS_PERIOD_1, 1], [TS_PERIOD_2, 1], [TS_PERIOD_3, 1]],
    ],
    [
        "несколько интервалов между замерами",
        [[TS_PERIOD_0 + 1, 1], [TS_PERIOD_3, PERIOD * 3]],
        [[TS_PERIOD_2, 1], [TS_PERIOD_3, 1]],
    ],
    [
        "с разными смещением",
        [
            [TS_PERIOD_0 + PERIOD - 1, TS_PERIOD_0 + PERIOD - 1],
            [TS_PERIOD_1 + PERIOD - 2, TS_PERIOD_1 + PERIOD - 2],
            [TS_PERIOD_2 + PERIOD - 3, TS_PERIOD_2 + PERIOD - 3],
            [TS_PERIOD_4, TS_PERIOD_4],
            [TS_PERIOD_5, TS_PERIOD_5],
        ],
        [[TS_PERIOD_2, 1.0], [TS_PERIOD_3, 1.0], [TS_PERIOD_4, 1.0], [TS_PERIOD_5, 1.0]],
    ],
    [
        "большие значения",
        [[TS_PERIOD_0, 0], [TS_PERIOD_1, 2**63 + PERIOD], [TS_PERIOD_2, 2**63 + PERIOD * 2]],
        [[TS_PERIOD_1, 2**63 / PERIOD], [TS_PERIOD_2, 1]],
    ],
]


@pytest.mark.parametrize("comment, test_input, expected", SPEED_CASES)
def test_speed(comment, test_input, expected):
    res = []
    prev_data = {}
    for data in test_input:
        input_ts, input_value = data
        kvts_list = [(TEST_KEY, input_value, input_ts)]
        tmp_res = speed(prev_data, kvts_list, resample=PERIOD)
        for k, v, ts in tmp_res:
            assert k == TEST_KEY
            res.append([ts, v])
    assert res == expected, comment


def test_speed_max_time_delta():  # NOCDEV-4156
    prev_data = {}
    resample = 30
    max_time_delta = 60
    test_input = [
        [TEST_KEY, 0, resample - 2, (0, 28, 0, 0), []],
        [TEST_KEY, 0, resample * 2 - 1 + max_time_delta, (0, 119, 0.0, 1), [(0.0, 60), (0.0, 90)]],
    ]
    for k, input_value, input_ts, prev_data_exp, res in test_input:
        kvts_list = [(k, input_value, input_ts)]
        tmp_res = speed(prev_data, kvts_list, resample=resample, max_time_delta=max_time_delta)
        compres = [(TEST_KEY, i[0], i[1]) for i in res]
        assert compres == tmp_res
        assert {TEST_KEY: prev_data_exp} == prev_data


def test_speed2():
    # NOCDEV-3203
    prev_data = {}
    test_input = [
        [0, 1, (0, 1, 0, 0), []],
        [0, 61, (0, 1, 0, 0), []],
        [0, 121, (0, 121, 0, 1), [(0.0, 120)]],
        [500000000181, 181, (500000000181, 181, 138888888.93916667, 1), [(8194444447.410833, 180)]],
        [500000000241, 241, (500000000241, 241, 0.016666666666666666, 1), [(138888889.92249998, 240)]],
        [500000000301, 301, (500000000301, 301, 0.016666666666666666, 1), [(1.0, 300)]],
        [500000000361, 361, (500000000361, 361, 0.016666666666666666, 1), [(1.0, 360)]],
    ]
    for input_value, input_ts, prev_data_exp, res in test_input:
        kvts_list = [(TEST_KEY, input_value, input_ts)]
        tmp_res = speed(prev_data, kvts_list, resample=60)
        compres = [(TEST_KEY, i[0], i[1]) for i in res]
        assert tmp_res == compres
        assert prev_data == {TEST_KEY: prev_data_exp}
        for k, v, ts in tmp_res:
            assert k == TEST_KEY


def test_speed3():
    prev_data = {}
    test_input = [
        [1, 1612547590, []],
        [1, 1612547650, []],
        [1, 1612547710, [(0.0, 1612547700)]],
        [1, 1612547767, [(0.0, 1612547760)]],
        [
            1,
            1612548071,
            [(0.0, 1612547820), (0.0, 1612547880), (0.0, 1612547940), (0.0, 1612548000), (0.0, 1612548060)],
        ],
    ]

    for input_value, input_ts, res in test_input:
        kvts_list = [(TEST_KEY, input_value, input_ts)]
        tmp_res = speed(prev_data, kvts_list, resample=60, max_time_delta=720)
        compres = [(TEST_KEY, i[0], i[1]) for i in res]
        assert tmp_res == compres
        for k, v, ts in tmp_res:
            assert k == TEST_KEY


def test_speed4():
    # TODO: https://st.yandex-team.ru/NOCDEV-5587#612cf5b197363144fa5375cf
    prev_data = {}
    test_input1 = [
        [4220136, 20],
        [4220154, 30],
        [4220175, 41],
        [4220217, 50],
        # [4220272, 70],
        [4220288, 81],
        # [4220334, 90],
        [4220367, 111],
    ]
    # 90
    test_input2 = [
        [4408698, 21],
        [4408727, 31],
        [4408739, 41],
        [4408775, 51],
        # [4408813, 70],
        [4408827, 81],
        # [44408855, 91],
        [4408879, 111],
    ]
    print("---")
    for input_value, input_ts in test_input1:
        kvts_list = [(TEST_KEY, input_value, input_ts)]
        tmp_res = speed(prev_data, kvts_list, resample=10, max_time_delta=20)
        print(input_value, input_ts, "res", [x[-1] for x in tmp_res])
    print("---")
    for input_value, input_ts in test_input2:
        kvts_list = [(TEST_KEY, input_value, input_ts)]
        tmp_res = speed(prev_data, kvts_list, resample=10, max_time_delta=20)
        print(input_value, input_ts, "res", [x[-1] for x in tmp_res])
        # compres = [(TEST_KEY, i[0], i[1]) for i in res]
