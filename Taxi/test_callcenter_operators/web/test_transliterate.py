import pytest

from callcenter_operators import utils


@pytest.mark.parametrize(
    ['string', 'expected'],
    [
        pytest.param('abcd', 'abcd', id='ascii symbols'),
        pytest.param('бвg', 'bvg', id='mixed cyrillic and ascii'),
        pytest.param('лБл', 'lBl', id='single capital'),
        pytest.param('ш', 'sh', id='complex letter'),
        pytest.param('лЩл', 'lSchl', id='complex capital'),
        pytest.param('лß', None, id='non cyrillic letter'),
        pytest.param('Ä', None, id='upper non cyrillic letter'),
    ],
)
async def test_transliteration(string, expected):
    result = utils.transliterate(string)
    assert result == expected, result
