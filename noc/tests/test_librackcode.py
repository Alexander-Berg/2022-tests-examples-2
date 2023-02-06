import pytest

from noc.library.python.racktables.rackcode import (And, LexerError,
                                                    NoParseError, Not, Or,
                                                    Predicate, Tag, parse)


def test_parser_misc():
    assert Tag(name="{магистральный свитч}") == Tag(name="{магистральный свитч}")
    assert parse("{L3-ToR}") == Tag(name="{L3-ToR}"), parse("{L3-ToR}")
    assert parse("{L3-ToR}") != Tag(name="{L8-ToR}"), parse("{L3-ToR}")
    assert parse("[работает netmap]") == Predicate("[работает netmap]")
    assert parse("[не работает netmap]") != Predicate("[работает netmap]")


@pytest.mark.parametrize(
    "datum, exspectandum",
    [
        ("{$cn_lab-vla-1s1}", Tag("{$cn_lab-vla-1s1}")),
        ("not {L3-ToR}", Not(Tag("{L3-ToR}"))),
        ("(not {L3-ToR})", Not(Tag("{L3-ToR}"))),
        ("((((not {L3-ToR}))))", Not(Tag("{L3-ToR}"))),
        ("((((not {L3-ToR}))))", Not(Tag("{L3-ToR}"))),
        (
            "((((not {L3-ToR}) and not ([yolo] or {lol}))))",
            And(Not(Tag("{L3-ToR}")), Not(Or(Predicate("[yolo]"), Tag("{lol}")))),
        ),
        (
            "{a} and {b} or {c} and {d} and {e} or {f}",
            Or(
                And(Tag("{a}"), Tag("{b}")),
                Or(And(Tag("{c}"), And(Tag("{d}"), Tag("{e}"))), Tag("{f}")),
            ),
        ),
        ("{a} and {b} or {c}", Or(And(Tag("{a}"), Tag("{b}")), Tag("{c}"))),
        (
            "not (({в оффлайне} and not {ещё не работает}) or {infiniband} or {interconnect})"
            " and ({route reflector} or {серверный свитч} or {spine1} or {spine2}"
            " or {юзерский свитч} or {свитч для IPMI} or {пиринговый свитч}"
            " or {свитч агрегации} or {магистральный свитч} or {border router}"
            " or {datacenter core} or {YANET} or ({Autonomous WiFi точка} and ({Cisco}"
            " or ({iap master} and {Aruba}))))",
            And(
                Not(
                    Or(
                        And(Tag("{в оффлайне}"), Not(Tag("{ещё не работает}"))),
                        Or(Tag("{infiniband}"), Tag(name="{interconnect}")),
                    )
                ),
                Or(
                    Tag("{route reflector}"),
                    Or(
                        Tag(name="{серверный свитч}"),
                        Or(
                            Tag("{spine1}"),
                            Or(
                                Tag("{spine2}"),
                                Or(
                                    Tag("{юзерский свитч}"),
                                    Or(
                                        Tag("{свитч для IPMI}"),
                                        Or(
                                            Tag("{пиринговый свитч}"),
                                            Or(
                                                Tag("{свитч агрегации}"),
                                                Or(
                                                    Tag("{магистральный свитч}"),
                                                    Or(
                                                        Tag("{border router}"),
                                                        Or(
                                                            Tag("{datacenter core}"),
                                                            Or(
                                                                Tag("{YANET}"),
                                                                And(
                                                                    Tag(
                                                                        "{Autonomous WiFi точка}"
                                                                    ),
                                                                    Or(
                                                                        Tag("{Cisco}"),
                                                                        And(
                                                                            Tag(
                                                                                "{iap master}"
                                                                            ),
                                                                            Tag(
                                                                                "{Aruba}"
                                                                            ),
                                                                        ),
                                                                    ),
                                                                ),
                                                            ),
                                                        ),
                                                    ),
                                                ),
                                            ),
                                        ),
                                    ),
                                ),
                            ),
                        ),
                    ),
                ),
            ),
        ),
        (
            "{конюшня NOC} and not (({Cloud} and not {свитч для IPMI}) or {CloudNetbox} or {$nameless})",
            And(
                Tag("{конюшня NOC}"),
                Not(
                    Or(
                        And(Tag("{Cloud}"), Not(Tag("{свитч для IPMI}"))),
                        Or(Tag("{CloudNetbox}"), Tag("{$nameless}")),
                    )
                ),
            ),
        ),
        ("and {tor}", NoParseError),
        ("{", NoParseError),  # Was LexerError
        ("{L3-ToR", LexerError),
        ("L3-ToR}", NoParseError),  # Was LexerError
        ("{$$$dollars}", LexerError),
        ("{L3-ToR} AND {L100-ToR}", LexerError),
        ("{L3-ToR} and", NoParseError),
        ("((({tor} and {not tor}))", NoParseError),
    ],
)
def test_parser(datum, exspectandum):
    if isinstance(exspectandum, type) and issubclass(exspectandum, Exception):
        with pytest.raises(exspectandum):
            parse(datum, raise_on_error=True)
    else:
        assert parse(datum) == exspectandum
