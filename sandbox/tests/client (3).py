from __future__ import unicode_literals

import six
from six.moves import cPickle
import pytest

from sandbox.common.types import client as ctc


class TestTag(object):
    @staticmethod
    def __to_str(values):
        return list(six.moves.map(lambda _: tuple(set(map(str, _)) for _ in _), values))

    def test__tag_query(self):
        assert not ctc.Tag.Query(())
        assert ctc.Tag.Query("GENERIC")
        assert ctc.Tag.Query("GENERIC & OSX") == ctc.Tag.GENERIC & ctc.Tag.Group.OSX
        assert ctc.Tag.Query("GENERIC & OSX") != ctc.Tag.Query(ctc.Tag.GENERIC)

    def test__tag_query_pickle(self):
        query = ctc.Tag.Query("GENERIC & OSX")
        assert cPickle.loads(cPickle.dumps(query)) == query
        new_query = ctc.Tag.Query(())
        new_query.__setstate__(query.__getstate__())
        assert new_query == query

    def test__custom_group(self):
        # __len__ is called implicitly
        assert ctc.Tag.Group.CUSTOM
        assert ctc.Tag.Group.USER

    def test__tag_query_check(self):
        with pytest.raises(ValueError):
            ctc.Tag.Query(()).check()

        with pytest.raises(ValueError):
            ctc.Query((ctc.Tag.GENERIC, ctc.Tag.OSX_SIERRA, ~ctc.Tag.GENERIC, ~ctc.Tag.OSX_SIERRA)).check()

        ctc.Tag.Query("GENERIC & OSX").check()

    def test__tag_query_predicate(self):
        pred = self.__to_str([
            (
                {ctc.Tag.GENERIC},
                {
                    ctc.Tag.MULTISLOT, ctc.Tag.PORTOD, ctc.Tag.WINDOWS,
                    ctc.Tag.Group.SERVICE, ctc.Tag.Group.MULTISLOTS, ctc.Tag.Group.OSX,
                    ctc.Tag.M1
                }
            )
        ])
        assert ctc.Tag.Query.predicates("") == pred
        assert ctc.Tag.Query.predicates("") == pred  # hits the cache

        assert ctc.Tag.Query.predicates("BROWSER") == self.__to_str([
            (
                {ctc.Tag.BROWSER},
                {
                    ctc.Tag.MULTISLOT, ctc.Tag.PORTOD, ctc.Tag.WINDOWS,
                    ctc.Tag.Group.SERVICE, ctc.Tag.Group.MULTISLOTS, ctc.Tag.Group.OSX,
                    ctc.Tag.M1
                }
            )
        ])
        assert ctc.Tag.Query.predicates("MULTISLOT") == self.__to_str([
            (
                {ctc.Tag.GENERIC, ctc.Tag.MULTISLOT},
                {ctc.Tag.PORTOD, ctc.Tag.Group.SERVICE, ctc.Tag.Group.OSX, ctc.Tag.WINDOWS, ctc.Tag.M1}
            )
        ])
        assert ctc.Tag.Query.predicates("BROWSER & MULTISLOT") == self.__to_str([
            (
                {ctc.Tag.BROWSER, ctc.Tag.MULTISLOT},
                {ctc.Tag.PORTOD, ctc.Tag.Group.SERVICE, ctc.Tag.Group.OSX, ctc.Tag.WINDOWS, ctc.Tag.M1}
            )
        ])
        assert ctc.Tag.Query.predicates("BROWSER & ~MULTISLOT") == self.__to_str([
            (
                {ctc.Tag.BROWSER},
                {
                    ctc.Tag.MULTISLOT, ctc.Tag.PORTOD, ctc.Tag.WINDOWS,
                    ctc.Tag.Group.SERVICE, ctc.Tag.Group.MULTISLOTS, ctc.Tag.Group.OSX, ctc.Tag.M1
                }
            )
        ])
        assert ctc.Tag.Query.predicates("CUSTOM_TAG") == self.__to_str([
            ({ctc.Tag.CUSTOM_TAG}, {ctc.Tag.Group.SERVICE})
        ])
        assert ctc.Tag.Query.predicates("MULTISLOTS") == self.__to_str([
            (
                {ctc.Tag.GENERIC, ctc.Tag.Group.MULTISLOTS},
                {ctc.Tag.PORTOD, ctc.Tag.Group.SERVICE, ctc.Tag.Group.OSX, ctc.Tag.WINDOWS, ctc.Tag.M1}
            )
        ])
        assert ctc.Tag.Query.predicates("LINUX") == self.__to_str([
            (
                {ctc.Tag.GENERIC, ctc.Tag.Group.LINUX},
                {
                    ctc.Tag.PORTOD, ctc.Tag.Group.SERVICE,
                    ctc.Tag.MULTISLOT, ctc.Tag.Group.MULTISLOTS, ctc.Tag.M1
                }
            )
        ])
        assert ctc.Tag.Query.predicates("LINUX_XENIAL") == self.__to_str([
            (
                {ctc.Tag.GENERIC, ctc.Tag.LINUX_XENIAL},
                {
                    ctc.Tag.PORTOD, ctc.Tag.Group.SERVICE,
                    ctc.Tag.MULTISLOT, ctc.Tag.Group.MULTISLOTS, ctc.Tag.M1
                }
            )
        ])
        assert ctc.Tag.Query.predicates("OSX") == self.__to_str([
            (
                {ctc.Tag.GENERIC, ctc.Tag.Group.OSX},
                {
                    ctc.Tag.PORTOD, ctc.Tag.Group.SERVICE,
                    ctc.Tag.MULTISLOT, ctc.Tag.Group.MULTISLOTS, ctc.Tag.M1
                }
            )
        ])
        assert ctc.Tag.Query.predicates("OSX_SIERRA") == self.__to_str([
            (
                {ctc.Tag.GENERIC, ctc.Tag.OSX_SIERRA},
                {
                    ctc.Tag.PORTOD, ctc.Tag.Group.SERVICE,
                    ctc.Tag.MULTISLOT, ctc.Tag.Group.MULTISLOTS, ctc.Tag.M1
                }
            )
        ])
        # empty set
        assert ctc.Tag.Query.predicates("MULTISLOT & ~GENERIC") == self.__to_str([
            (
                {ctc.Tag.GENERIC, ctc.Tag.MULTISLOT},
                {
                    ctc.Tag.GENERIC, ctc.Tag.PORTOD, ctc.Tag.Group.SERVICE,
                    ctc.Tag.Group.OSX, ctc.Tag.WINDOWS, ctc.Tag.M1
                }
            )
        ])
        # all generic multi slots
        assert ctc.Tag.Query.predicates("~BROWSER & MULTISLOT") == self.__to_str([
            (
                {ctc.Tag.GENERIC, ctc.Tag.MULTISLOT},
                {
                    ctc.Tag.BROWSER, ctc.Tag.PORTOD, ctc.Tag.Group.SERVICE,
                    ctc.Tag.Group.OSX, ctc.Tag.WINDOWS, ctc.Tag.M1
                }
            )
        ])
        # all generic multi slots (1 core)
        assert ctc.Tag.Query.predicates("~BROWSER & CORES1") == self.__to_str([
            (
                {ctc.Tag.GENERIC, ctc.Tag.CORES1},
                {
                    ctc.Tag.BROWSER, ctc.Tag.PORTOD, ctc.Tag.Group.SERVICE,
                    ctc.Tag.Group.OSX, ctc.Tag.WINDOWS, ctc.Tag.M1
                }
            )
        ])
        # all generic fat multi slots (4 cores)
        assert ctc.Tag.Query.predicates("~BROWSER & CORES4") == self.__to_str([
            (
                {ctc.Tag.GENERIC, ctc.Tag.CORES4},
                {
                    ctc.Tag.BROWSER, ctc.Tag.PORTOD, ctc.Tag.Group.SERVICE,
                    ctc.Tag.Group.OSX, ctc.Tag.WINDOWS, ctc.Tag.M1
                }
            )
        ])
        # all generic fat multi slots (8 cores)
        assert ctc.Tag.Query.predicates("~BROWSER & CORES8") == self.__to_str([
            (
                {ctc.Tag.GENERIC, ctc.Tag.CORES8},
                {
                    ctc.Tag.BROWSER, ctc.Tag.PORTOD, ctc.Tag.Group.SERVICE,
                    ctc.Tag.Group.OSX, ctc.Tag.WINDOWS, ctc.Tag.M1
                }
            )
        ])
        # negative default outside the groups
        assert ctc.Tag.Query.predicates("DYNAMIC_SLOTS") == self.__to_str([
            (
                {ctc.Tag.DYNAMIC_SLOTS, ctc.Tag.GENERIC},
                {
                    ctc.Tag.MULTISLOT, ctc.Tag.PORTOD,
                    ctc.Tag.Group.SERVICE, ctc.Tag.Group.MULTISLOTS, ctc.Tag.Group.OSX, ctc.Tag.WINDOWS, ctc.Tag.M1
                }
            )
        ])

    def test__query_representation(self):
        samples = [
            (ctc.Tag.GENERIC, "GENERIC"),
            (ctc.Tag.Group.LINUX, "LINUX"),
            (~ctc.Tag.Group.LINUX, "~LINUX"),
            (ctc.Tag.Group.LINUX & ctc.Tag.GENERIC, "LINUX & GENERIC"),
            (ctc.Tag.GENERIC & ctc.Tag.Group.LINUX, "GENERIC & LINUX"),
            (ctc.Tag.Group.LINUX & (ctc.Tag.GENERIC | ctc.Tag.PORTO), "LINUX & (GENERIC | PORTO)"),
            (ctc.Tag.Group.LINUX & (ctc.Tag.PORTO | ctc.Tag.GENERIC), "LINUX & (PORTO | GENERIC)"),
            ((ctc.Tag.PORTO | ctc.Tag.GENERIC) & ctc.Tag.Group.LINUX, "(PORTO | GENERIC) & LINUX"),
            (~(ctc.Tag.PORTO | ctc.Tag.GENERIC) & ctc.Tag.Group.LINUX, "~(PORTO | GENERIC) & LINUX"),
            ((ctc.Tag.PORTO | ctc.Tag.GENERIC) & ~ctc.Tag.Group.LINUX, "(PORTO | GENERIC) & ~LINUX"),
            ((ctc.Tag.PORTO | ctc.Tag.GENERIC) | ctc.Tag.SERVER, "PORTO | GENERIC | SERVER"),
            (ctc.Tag.GENERIC & (ctc.Tag.MULTISLOT & ctc.Tag.Group.LINUX), "GENERIC & MULTISLOT & LINUX"),
            (ctc.Tag.GENERIC | (ctc.Tag.MULTISLOT & ctc.Tag.Group.LINUX), "GENERIC | MULTISLOT & LINUX"),
            (
                (ctc.Tag.GENERIC & ctc.Tag.SSD) | (ctc.Tag.MULTISLOT & ctc.Tag.Group.LINUX),
                "GENERIC & SSD | MULTISLOT & LINUX"
            ),
            ((ctc.Tag.GENERIC | ctc.Tag.PORTO) & (ctc.Tag.SSD | ctc.Tag.HDD), "(GENERIC | PORTO) & (SSD | HDD)"),
            (~(ctc.Tag.GENERIC | ctc.Tag.PORTO), "~(GENERIC | PORTO)"),
            (~(ctc.Tag.GENERIC & ctc.Tag.PORTO), "~(GENERIC & PORTO)")
        ]

        for query, query_repr_ref in samples:
            assert str(query) == query_repr_ref
            assert str(ctc.Tag.Query(query_repr_ref)) == query_repr_ref
            assert str(ctc.Tag.Query.cast(query_repr_ref)) == query_repr_ref
            assert str(ctc.Tag.Query.__decode__(query_repr_ref)) == query_repr_ref

        assert str(ctc.Tag.Query("(~(GENERIC) & ((LINUX | (OSX))))")) == "~GENERIC & (LINUX | OSX)"

        query = ctc.Tag.Query(ctc.Tag.PORTO | ctc.Tag.GENERIC)
        assert str(query & ctc.Tag.Group.LINUX) == "(PORTO | GENERIC) & LINUX"

    @pytest.mark.parametrize("sample", (
        "2 + 2",  # forbidden expression
        "2 + +",  # syntax error
        "FOOBAR",  # unknown identifier
    ))
    def test__invalid_query(self, sample):
        with pytest.raises(ValueError):
            ctc.Tag.Query.__decode__(sample, raise_errors=True)

        assert ctc.Tag.Query.__decode__(sample) is None

        with pytest.raises(ValueError):
            ctc.Tag.Query(sample)

    @pytest.mark.parametrize("src", (
        ctc.Tag.GENERIC & (ctc.Tag.MULTISLOT & ctc.Tag.Group.LINUX),
        "(~(GENERIC) & ((LINUX | (OSX))))",
        2.345,
        None
    ))
    def test__decode_idempotency(self, src):
        output = ctc.Tag.Query.__decode__(src)
        v2 = ctc.Tag.Query.__decode__(output)
        assert v2 == output

    def test__filter(self):
        tags = ("FOO", "BAR", "NON_TAG", "CUSTOM_FOO", "GENERIC", "OSX_MOJAVE")

        assert ctc.Tag.filter(tags, include_groups=False) == {"CUSTOM_FOO", "GENERIC", "OSX_MOJAVE"}
        assert ctc.Tag.filter(tags, include_groups=True) == {
            "CUSTOM", "CUSTOM_FOO", "GENERIC", "PURPOSE", "OS", "OSX", "OSX_MOJAVE"
        }

    def test__simplify_representation(self):
        assert repr(ctc.Tag.GENERIC & ctc.Tag.GENERIC) == repr(ctc.Tag.GENERIC)
        assert repr(ctc.Tag.GENERIC & ctc.Tag.SSD) == repr(ctc.Tag.GENERIC & ctc.Tag.SSD)
        assert repr(ctc.Tag.GENERIC & ctc.Tag.SSD & ctc.Tag.SSD) == repr(ctc.Tag.GENERIC & ctc.Tag.SSD)
        assert repr(ctc.Tag.GENERIC & ctc.Tag.SSD & ctc.Tag.GENERIC) == repr(ctc.Tag.GENERIC & ctc.Tag.SSD)

        assert repr(ctc.Tag.GENERIC | ctc.Tag.GENERIC) == repr(ctc.Tag.GENERIC)
        assert repr(ctc.Tag.GENERIC | ctc.Tag.SSD) == repr(ctc.Tag.GENERIC | ctc.Tag.SSD)
        assert repr(ctc.Tag.GENERIC | ctc.Tag.SSD | ctc.Tag.SSD) == repr(ctc.Tag.GENERIC | ctc.Tag.SSD)
        assert repr(ctc.Tag.GENERIC | ctc.Tag.SSD | ctc.Tag.GENERIC) == repr(ctc.Tag.GENERIC | ctc.Tag.SSD)

        assert repr(
            ctc.Tag.GENERIC & ctc.Tag.LINUX_BIONIC | ctc.Tag.LINUX_BIONIC & ctc.Tag.GENERIC
        ) == repr(
            ctc.Tag.GENERIC & ctc.Tag.LINUX_BIONIC
        )
        query1 = ctc.Query(
            "(GENERIC | OSX | PORTO) & "
            "(~LINUX | LINUX_PRECISE | LINUX_TRUSTY | LINUX_XENIAL | LINUX_BIONIC | LINUX_FOCAL)"
        )
        query2 = ctc.Query("LINUX & GENERIC & ~OSX")
        assert repr(query1 & query2) == "{} & {}".format(repr(query1), repr(query2))
        assert repr(query1 & query2 & query2) == "{} & {}".format(repr(query1), repr(query2))
