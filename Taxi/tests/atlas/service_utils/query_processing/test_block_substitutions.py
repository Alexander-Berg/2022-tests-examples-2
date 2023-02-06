import pytest
import atlas.service_utils.query_processing.block_substitutions as bs
from atlas.service_utils.query_processing.exceptions import (
    AtlasQueryBlockParsingError,
    AtlasBlockSubstitutionError
)


@pytest.fixture
def blocked_raw_text():
    return '''
--DEFINE_ATLAS_BLOCK block_1 START
Contents of first block
--DEFINE_ATLAS_BLOCK block_1 END


--DEFINE_ATLAS_BLOCK block_2 START
Contents of second block
Still second block
Link to first block: $ATLAS_BLOCK(block_1)
--DEFINE_ATLAS_BLOCK block_2 END
'''


@pytest.fixture
def blocks(blocked_raw_text):
    return bs.split_in_query_blocks(blocked_raw_text)


def test_multisub():
    substitution_pairs = [
        ('this', 'that'),
        ('that', 'this'),
        ('better', 'worse'),
        ('1', '2'),
        ('2', '3')
    ]
    text = 'this 1 is better than that 2'
    assert bs.multisub(substitution_pairs, text) == 'that 2 is worse than this 3'


class TestSplitInQueryBlocks(object):

    def test_valid_text(self, blocked_raw_text):
        blocks = bs.split_in_query_blocks(blocked_raw_text)
        assert blocks == {
            'block_1': 'Contents of first block',
            'block_2': 'Contents of second block\nStill second block\nLink to first block: $ATLAS_BLOCK(block_1)'
        }

    def test_nested_block(self):
        text = '''
        --DEFINE_ATLAS_BLOCK block_1 START
        --DEFINE_ATLAS_BLOCK block_2 START
        --DEFINE_ATLAS_BLOCK block_2 END
        --DEFINE_ATLAS_BLOCK block_1 END
        '''
        with pytest.raises(AtlasQueryBlockParsingError):
            bs.split_in_query_blocks(text)

    def test_block_is_redefined(self):
        text = '''
        --DEFINE_ATLAS_BLOCK block_1 START
        --DEFINE_ATLAS_BLOCK block_1 END
        --DEFINE_ATLAS_BLOCK block_1 START
        --DEFINE_ATLAS_BLOCK block_1 END
        '''
        with pytest.raises(AtlasQueryBlockParsingError):
            bs.split_in_query_blocks(text)

    def test_block_without_end(self):
        text = '''
        --DEFINE_ATLAS_BLOCK block_1 START
        '''
        with pytest.raises(AtlasQueryBlockParsingError):
            bs.split_in_query_blocks(text)

    def test_unexpected_end(self):
        text = '''
        --DEFINE_ATLAS_BLOCK block_1 END
        '''
        with pytest.raises(AtlasQueryBlockParsingError):
            bs.split_in_query_blocks(text)

    def test_unmatched_end(self):
        text = '''
        --DEFINE_ATLAS_BLOCK block_1 START
        --DEFINE_ATLAS_BLOCK block_2 END
        '''
        with pytest.raises(AtlasQueryBlockParsingError):
            bs.split_in_query_blocks(text)

    def test_unrecognized_action_on_block(self):
        text = '--DEFINE_ATLAS_BLOCK block_1 ACTION'
        with pytest.raises(AtlasQueryBlockParsingError):
            bs.split_in_query_blocks(text)


class TestExtractSubstitutionsNames(object):
    def test_valid_block(self):
        block_text = ''' Title $ATLAS_BLOCK(title) was given 
            some arbitrary text

                $ATLAS_BLOCK(footer).'''
        assert bs._get_atlas_block_substitutions(block_text) == ['title', 'footer']

    def test_unexpected_token_instead_left_bracket(self):
        block_text = '$ATLAS_BLOCK title'
        with pytest.raises(AtlasBlockSubstitutionError):
            bs._get_atlas_block_substitutions(block_text)

    def test_unexpected_token_instead_right_bracket(self):
        block_text = '$ATLAS_BLOCK(title  dfdsa'
        with pytest.raises(AtlasBlockSubstitutionError):
            bs._get_atlas_block_substitutions(block_text)


def test_block_repr():
    assert repr(bs.AtlasSubqueryBlock('block_1', 10, 15)) == "AtlasSubqueryBlock('block_1', 10, 15)"


class TestGraphIsAcyclicChecker(object):
    def test_acyclic_simple(self):
        graph = {
            1: [2, 3],
            2: [3],
            3: []
        }
        assert bs._graph_has_cycle(graph) is False

    def test_cycled_simple(self):
        graph = {
            1: [2],
            2: [1]
        }
        assert bs._graph_has_cycle(graph) is True

    def test_cycled_complex(self):
        graph = {
            1: [2, 3],
            2: [3],
            3: [4, 5],
            4: [],
            5: [2]
        }
        assert bs._graph_has_cycle(graph) is True


class TestBlockGraphBuilder(object):
    def test_build_query_block_dependency_graph(self, blocks):
        graph = bs._build_query_block_dependency_graph(blocks)
        assert graph == {'block_1': [], 'block_2': ['block_1']}

    def test_link_on_undefined_block_raises(self):
        blocks = {
            'block_1': '$ATLAS_BLOCK(block_2)'
        }
        with pytest.raises(AtlasBlockSubstitutionError):
            bs._build_query_block_dependency_graph(blocks)

    def test_cycled_block_graph_raises(self):
        blocks = {
            'block_1': '$ATLAS_BLOCK(block_2)',
            'block_2': '$ATLAS_BLOCK(block_1)'
        }
        with pytest.raises(AtlasBlockSubstitutionError):
            bs._build_query_block_dependency_graph(blocks)


class TestMakeSubstitutions(object):
    def test_block_1(self, blocks):
        assert bs.make_substitutions('block_1', blocks) == 'Contents of first block'

    def test_block_2(self, blocks):
        assert bs.make_substitutions('block_2', blocks) == '''Contents of second block
Still second block
Link to first block: Contents of first block'''

    def test_build_from_diamond_graph(self):
        blocks = {
            'top': '(left: $ATLAS_BLOCK(left), right: $ATLAS_BLOCK(right))',
            'left': '--$ATLAS_BLOCK(bottom)--',
            'right': '~~$ATLAS_BLOCK(bottom)~~',
            'bottom': r'(\/)(O_O)(\/)'
        }
        assert bs.make_substitutions('top', blocks) == r'(left: --(\/)(O_O)(\/)--, right: ~~(\/)(O_O)(\/)~~)'
