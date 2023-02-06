from swaggen import tracing


FILEPATH = 'some.yaml'
BASE_TRACE = ('some', 'trace')

SAMPLE_DICT = tracing.Dict(
    {
        'str': 'Ave, Caesar',
        'int': 666,
        'None': None,
        'float': 2.28,
        'dict': {'a': 'b'},
        'list': [0, '1', 2.28, None, {'': 1}, []],
    },
    filepath=FILEPATH,
    trace=BASE_TRACE,
)


def test_happy_path():
    assert SAMPLE_DICT['str'] == 'Ave, Caesar'
    assert SAMPLE_DICT['int'] == 666
    assert SAMPLE_DICT['float'] == 2.28
    assert SAMPLE_DICT['None'] is None
    assert isinstance(SAMPLE_DICT['dict'], tracing.Dict)
    assert SAMPLE_DICT['dict']['a'] == 'b'
    assert SAMPLE_DICT['dict'].filepath == FILEPATH
    assert SAMPLE_DICT['dict'].trace == BASE_TRACE + ('dict',)
    assert isinstance(SAMPLE_DICT['list'], tracing.List)
    assert SAMPLE_DICT['list'].filepath == FILEPATH
    assert SAMPLE_DICT['list'].trace == BASE_TRACE + ('list',)
    assert SAMPLE_DICT['list'][0] == 0
    assert SAMPLE_DICT['list'][1] == '1'
    assert SAMPLE_DICT['list'][2] == 2.28
    assert SAMPLE_DICT['list'][3] is None
    assert isinstance(SAMPLE_DICT['list'][4], tracing.Dict)
    assert SAMPLE_DICT['list'][4].filepath == FILEPATH
    assert SAMPLE_DICT['list'][4].trace == BASE_TRACE + ('list', '4')

    assert isinstance(SAMPLE_DICT['list'][5], tracing.List)
    assert SAMPLE_DICT['list'][5].filepath == FILEPATH
    assert SAMPLE_DICT['list'][5].trace == BASE_TRACE + ('list', '5')

    for key, value in SAMPLE_DICT.items():  # pylint: disable=no-member
        if key == 'dict':
            assert isinstance(value, tracing.Dict)
            assert value.filepath == FILEPATH
            assert value.trace == BASE_TRACE + ('dict',)
        if key == 'list':
            assert isinstance(value, tracing.List)
            assert value.filepath == FILEPATH
            assert value.trace == BASE_TRACE + ('list',)

    for i, item in enumerate(SAMPLE_DICT['list']):
        if i == 4:
            assert isinstance(item, tracing.Dict)
            assert item.filepath == FILEPATH
            assert item.trace == BASE_TRACE + ('list', '4')
        if i == 5:
            assert isinstance(item, tracing.List)
            assert item.filepath == FILEPATH
            assert item.trace == BASE_TRACE + ('list', '5')
