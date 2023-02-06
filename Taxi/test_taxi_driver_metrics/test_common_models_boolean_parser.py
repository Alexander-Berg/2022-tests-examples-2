import pytest

from metrics_processing.utils import boolean_parser as BooleanParser


@pytest.mark.parametrize(
    'rule, tree',
    [
        ("""""", ''),
        (""" 'TAG' """, 'TAG'),
        (""" 'плохой\\\'тег\' """, 'плохой\'тег'),
        (
            """ NOT 'tag_1' AND('tag_2' OR 'tag_3') """,
            '(AND (NOT  tag_1) (OR tag_2 tag_3))',
        ),
        (
            """ ('sd' OR 'yd') OR('fd') OR ('xd') """,
            '(OR (OR (OR sd yd) fd) xd)',
        ),
        (
            """ ((((NOT (('4'))) AND ((('3' OR '2')))) OR ('5'))) """,
            '(OR (AND (NOT  4) (OR 3 2)) 5)',
        ),
        (
            """ NOT NOT NOT NOT NOT 'NOT NOT NOT TAG' """,
            '(NOT  (NOT  (NOT  (NOT  (NOT  NOT NOT NOT TAG)))))',
        ),
        (
            """ 'DO NOT ST'AND 'F'OR NOT'HING' """,
            '(OR (AND DO NOT ST F) (NOT  HING))',
        ),
        (
            """ 'Don\\'t touch my tag!' AND 'quadruple slashes \\\\' """,
            """(AND Don't touch my tag! quadruple slashes \\)""",
        ),
    ],
)
def test_build_tree(rule, tree):
    parser = BooleanParser.Parser(rule)
    assert str(parser.tree) == tree


@pytest.mark.parametrize(
    'rule, data',
    [
        (""" '' """, [([], False, set()), ([''], True, {''})]),
        ("""((())())(()())""", [([], True, set())]),
        (""" 'TAG' """, [(['TAG'], True, {'TAG'}), ([], False, set())]),
        (
            """ NOT 'tag_1' AND('tag_2' OR 'tag_3') """,
            [
                (['tag_1', 'tag_2'], False, set()),
                (['tag_2'], True, {'tag_2'}),
                ([], False, set()),
            ],
        ),
        (
            """ ('sd' OR 'yd') OR('fd') OR ('xd') """,
            [
                (['ghost', 'in', 'the', 'shell', 'fd'], True, {'fd'}),
                ([' ', '', '69', 'fdxdyd', 'sd OR yd'], False, set()),
            ],
        ),
        (
            """ 'A' AND 'B' AND NOT 'C' """,
            [(['A', 'B'], True, {'A', 'B'}), (['A', 'B', 'C'], False, set())],
        ),
        (
            """ 'A' AND NOT 'A' """,
            [(['B'], False, set()), (['A'], False, set())],
        ),
        (
            """ 'Don\\'t touch my tag!' AND 'quadruple slashes \\\\' """,
            [
                (
                    ["""Don't touch my tag!""", """quadruple slashes \\"""],
                    True,
                    {"""Don't touch my tag!""", """quadruple slashes \\"""},
                ),
                ([], False, set()),
            ],
        ),
        (
            """ 'DO NOT ST'AND 'F'OR NOT'HING' """,
            [
                (['HING'], False, set()),
                (['F', 'HING', 'DO NOT ST'], True, {'DO NOT ST', 'F'}),
            ],
        ),
        (
            """ NOT NOT NOT NOT NOT 'NOT NOT NOT TAG' """,
            [([], True, set()), (['NOT NOT NOT TAG'], False, set())],
        ),
        (
            """ NOT (NOT 'A' AND 'B' OR NOT 'C') AND ('A' OR 'C')
                OR NOT (('A' OR NOT 'B') AND 'C') """,
            [
                ([], True, set()),
                (['A'], True, set()),
                (['B'], True, set()),
                (['C'], True, {'C'}),
                (['A', 'B'], True, set()),
                (['A', 'C'], True, {'A'}),
                (['B', 'C'], True, set()),
                (['A', 'B', 'C'], True, {'A'}),
            ],
        ),
    ],
)
def test_evaluate(rule, data):
    for test in data:
        parser = BooleanParser.Parser(rule)
        assert parser.evaluate(test[0]) == test[1]
        assert parser.triggered_tags == test[2]


@pytest.mark.parametrize(
    'rule',
    [
        """ (('Don't') OR 'feed' OR 'animals') """,
        """ NOT \\'TAG\\' AND \\'TAG\\' """,
        """ (())) """,
    ],
)
def test_parsing_exception(rule):
    with pytest.raises(BooleanParser.ParsingException):
        parser = BooleanParser.Parser(rule)
        parser.evaluate([])


@pytest.mark.parametrize(
    'rule',
    [
        """ NOT NOT NOT """,
        """ 'TAG' OR """,
        """ () AND 'TAG' """,
        """ OR OR """,
        """ (((( """,
        """ 'TAG''TAG' """,
        """ 'tag' NOT 'tag' """,
    ],
)
def test_validation_exception(rule):
    with pytest.raises(BooleanParser.ValidationException):
        parser = BooleanParser.Parser(rule)
        parser.evaluate([])
