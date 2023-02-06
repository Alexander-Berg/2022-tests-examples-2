import os

import ymlcfg


def test_ref(tap, test_cfg_dir):
    tap.plan(9)

    cfg = ymlcfg.loader(test_cfg_dir("ref"))
    tap.ok(cfg, "tests/cfg/ref")

    tap.eq(cfg("hello"), "some", "value from another config file")
    tap.eq(cfg("full"), {"hello": "some"}, "full another config file")

    tap.eq(cfg("json_key"), "bar", "json config file")

    tap.eq(cfg("deep"), {"more": {"hello": "some"}},
           "deep recursion ref resolve")
    tap.eq(cfg("deep_inside.obj1.value3"), "some",
           "deep inside dict")
    tap.eq(cfg("deep_inside.list1.2"), "some",
           "deep inside list")
    tap.eq(cfg("foo.some_array.0.unknown_format1"), "Abrakadabra Abrakadabra",
           "Unknown extension")
    tap.eq(cfg("foo.some_array.0.unknown_format2"), "Abrakadabra Abrakadabra",
           "Unknown format, no extension")
    tap.done_testing()


def test_broken_ref(tap, test_cfg_dir):
    with tap.plan(2):
        os.environ['CONFIGNAME'] = 'broken'
        cfg = ymlcfg.loader(test_cfg_dir("ref"))
        tap.ok(cfg, "tests/cfg/ref")
        with tap.raises(ValueError, "Broken reference"):
            cfg("foo")
