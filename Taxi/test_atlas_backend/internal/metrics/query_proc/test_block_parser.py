# pylint: disable=W0621,W0212
import pytest

import atlas_backend.internal.metrics.query_proc.block_parser as bp


@pytest.fixture
def blocked_raw_text():
    return """
--DEFINE_ATLAS_BLOCK block_1 START
Contents of first block
--DEFINE_ATLAS_BLOCK block_1 END


--DEFINE_ATLAS_BLOCK block_2 START
Contents of second block
Still second block
Link to first block: $ATLAS_BLOCK(block_1)
--DEFINE_ATLAS_BLOCK block_2 END
"""


@pytest.fixture
def blocks_fixture(blocked_raw_text):
    return bp.split_in_query_blocks(blocked_raw_text)


def test_multisub():
    substitution_pairs = [
        ('this', 'that'),
        ('that', 'this'),
        ('better', 'worse'),
        ('1', '2'),
        ('2', '3'),
    ]
    text = 'this 1 is better than that 2'
    assert (
        bp.multisub(substitution_pairs, text) == 'that 2 is worse than this 3'
    )


class TestSplitInQueryBlocks:
    def test_valid_text(self, blocked_raw_text):
        blocks = bp.split_in_query_blocks(blocked_raw_text)
        assert blocks == {
            'block_1': 'Contents of first block',
            'block_2': (
                'Contents of second block\n'
                'Still second block\n'
                'Link to first block: $ATLAS_BLOCK(block_1)'
            ),
        }

    def test_nested_block(self):
        text = """
        --DEFINE_ATLAS_BLOCK block_1 START
        --DEFINE_ATLAS_BLOCK block_2 START
        --DEFINE_ATLAS_BLOCK block_2 END
        --DEFINE_ATLAS_BLOCK block_1 END
        """
        with pytest.raises(bp.AtlasQueryBlockParsingError):
            bp.split_in_query_blocks(text)

    def test_block_is_redefined(self):
        text = """
        --DEFINE_ATLAS_BLOCK block_1 START
        --DEFINE_ATLAS_BLOCK block_1 END
        --DEFINE_ATLAS_BLOCK block_1 START
        --DEFINE_ATLAS_BLOCK block_1 END
        """
        with pytest.raises(bp.AtlasQueryBlockParsingError):
            bp.split_in_query_blocks(text)

    def test_block_without_end(self):
        text = """
        --DEFINE_ATLAS_BLOCK block_1 START
        """
        with pytest.raises(bp.AtlasQueryBlockParsingError):
            bp.split_in_query_blocks(text)

    def test_unexpected_end(self):
        text = """
        --DEFINE_ATLAS_BLOCK block_1 END
        """
        with pytest.raises(bp.AtlasQueryBlockParsingError):
            bp.split_in_query_blocks(text)

    def test_unmatched_end(self):
        text = """
        --DEFINE_ATLAS_BLOCK block_1 START
        --DEFINE_ATLAS_BLOCK block_2 END
        """
        with pytest.raises(bp.AtlasQueryBlockParsingError):
            bp.split_in_query_blocks(text)

    def test_unrecognized_block_action(self):
        text = '--DEFINE_ATLAS_BLOCK block_1 ACTION'
        with pytest.raises(bp.AtlasQueryBlockParsingError):
            bp.split_in_query_blocks(text)


def test_valid_block():
    block_text = (
        ' Title $ATLAS_BLOCK(title) was given '
        '   some arbitrary text '
        '               '
        ' $ATLAS_BLOCK(footer).'
    )
    assert bp._extract_block_substitutions(block_text) == ['title', 'footer']


def test_unexpected_token_instead_left_bracket():
    block_text = '$ATLAS_BLOCK title'
    with pytest.raises(bp.AtlasBlockSubstitutionError):
        bp._extract_block_substitutions(block_text)


def test_unexpected_token_instead_right_bracket():
    block_text = '$ATLAS_BLOCK(title  dfdsa'
    with pytest.raises(bp.AtlasBlockSubstitutionError):
        bp._extract_block_substitutions(block_text)


def test_block_repr():
    assert (
        repr(bp.AtlasSubqueryBlock('block_1', 10, 15))
        == 'AtlasSubqueryBlock("block_1", 10, 15)'
    )


def test_acyclic_simple():
    graph = {'1': ['2', '3'], '2': ['3'], '3': []}
    assert bp._graph_has_cycle(graph) is False


def test_cycled_simple():
    graph = {'1': ['2'], '2': ['1']}
    assert bp._graph_has_cycle(graph) is True


def test_cycled_complex():
    graph = {'1': ['2', '3'], '2': ['3'], '3': ['4', '5'], '4': [], '5': ['2']}
    assert bp._graph_has_cycle(graph) is True


def test_build_query_block_dependency_graph(blocks_fixture):
    graph = bp._build_query_block_dependency_graph(blocks_fixture)
    assert graph == {'block_1': [], 'block_2': ['block_1']}


def test_link_on_undefined_block_raises():
    blocks = {'block_1': '$ATLAS_BLOCK(block_2)'}
    with pytest.raises(bp.AtlasBlockSubstitutionError):
        bp._build_query_block_dependency_graph(blocks)


def test_cycled_block_graph_raises():
    blocks = {
        'block_1': '$ATLAS_BLOCK(block_2)',
        'block_2': '$ATLAS_BLOCK(block_1)',
    }
    with pytest.raises(bp.AtlasBlockSubstitutionError):
        bp._build_query_block_dependency_graph(blocks)


def test_block_1(blocks_fixture):
    assert (
        bp.make_substitutions('block_1', blocks_fixture)
        == 'Contents of first block'
    )


def test_block_2(blocks_fixture):
    assert (
        bp.make_substitutions('block_2', blocks_fixture)
        == """Contents of second block
Still second block
Link to first block: Contents of first block"""
    )


def test_build_from_diamond_graph():
    blocks = {
        'top': '(left: $ATLAS_BLOCK(left), right: $ATLAS_BLOCK(right))',
        'left': '--$ATLAS_BLOCK(bottom)--',
        'right': '~~$ATLAS_BLOCK(bottom)~~',
        'bottom': r'(\/)(O_O)(\/)',
    }
    assert (
        bp.make_substitutions('top', blocks)
        == r'(left: --(\/)(O_O)(\/)--, right: ~~(\/)(O_O)(\/)~~)'
    )
