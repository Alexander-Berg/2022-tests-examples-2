from pahtest import lexemes as l
from pahtest.fields import Fields
from pahtest.grammar import Grammar
from pahtest.results import Note


MISSED_ONE = 'Missed required field'
MISSED_ONE_OF = 'Only one of'
# TODO - rewrite it to tap test
kwargs = {'xpath': '/html/body', 'description': 'Just body'}


def test_args_validation():
    """Test every validation except of validate required."""
    defaults = dict(
        name='ok', description='Ok test',
        code=['/html/body', 'Just body'],
        grammar=Grammar(list=[l.locator, l.desc], dict=[l.locator, l.desc])
    )

    options = Fields(
        name='ok', description='Ok test',
        code=[], grammar=Grammar(list=[], dict=[])
    ).dict
    assert {'description': 'Ok test', 'desc': 'Ok test'} == options, options

    # correct code for grammar should not lead to error
    options = Fields(**defaults).dict
    assert ['xpath', 'css', 'description', 'desc'] == list(options.keys())
    assert ['/html/body', '', 'Just body', 'Just body'] == list(options.values())

    # default description
    options = Fields(**{**defaults, 'code': ['/html/body']}).dict
    assert ['xpath', 'css', 'description', 'desc'] == list(options.keys())
    assert ['/html/body', '', 'Ok test', 'Ok test'] == list(options.values())

    error = Fields(**{**defaults, 'code': ['one', 'two', 'three']}).dict
    assert isinstance(error, Note), error
    assert 'is allowed max' in error.message, error.message


def test_kwargs_validation():
    """Test every validation except of validate required."""
    defaults = dict(
        name='ok', description='Ok test',
        code=kwargs,
        grammar=Grammar(list=[l.locator, l.desc], dict=[l.locator, l.desc])
    )
    options = Fields(
        name='ok', description='Ok test',
        code={}, grammar=Grammar(list=[], dict=[])
    ).dict
    assert {'description': 'Ok test', 'desc': 'Ok test'} == options, options

    # correct code for grammar should not lead to error
    options = Fields(**defaults).dict
    assert ['xpath', 'css', 'description', 'desc'] == list(options.keys())
    assert ['/html/body', '', 'Just body', 'Just body'] == list(options.values())

    options = Fields(**{**defaults, 'code': {'xpath': '/html/body'}}).dict
    assert ['xpath', 'css', 'description', 'desc'] == list(options.keys())
    assert ['/html/body', '', 'Ok test', 'Ok test'] == list(options.values())

    error = Fields(**{**defaults, 'code': {
        'xpath': '/html/body', 'description': 'Just body', 'unknown': 10}
    }).dict
    assert isinstance(error, Note), error
    assert 'unwanted args' in error.message, error.message


def test_normalization():
    defaults = dict(
        name='ok', description='Ok test',
        code=kwargs,
        grammar=Grammar(list=[l.locator, l.desc], dict=[l.locator, l.desc])
    )

    # full args normalization
    options = Fields(**defaults).dict
    assert ['xpath', 'css', 'description', 'desc'] == list(options.keys())
    assert ['/html/body', '', 'Just body', 'Just body'] == list(options.values())

    # partial args normalization
    options = Fields(**{**defaults, 'code': ['/html/body']}).dict
    assert ['xpath', 'css', 'description', 'desc'] == list(options.keys())
    assert ['/html/body', '', 'Ok test', 'Ok test'] == list(options.values())


def test_xpath_css_normalization():
    defaults = dict(
        name='ok', description='Ok test',
        grammar=Grammar(list=[l.locator, l.desc], dict=[l.locator, l.desc])
    )
    # xpath normalization
    options = Fields(**defaults, code=['xpath:/html/body']).dict
    assert options['xpath'] == '/html/body'
    # no xpath normalization
    options = Fields(**defaults, code=['/html:/body']).dict
    assert options['xpath'] == '/html:/body'
    # css normalization
    options = Fields(**defaults, code=['css:html > body']).dict
    assert options['css'] == 'html > body'


def test_validate_required():
    defaults = dict(name='ok', description='Ok test')
    code = {'xpath': '/html/body', 'css': 'html > body'}
    # one required field missed
    error = Fields(
        **defaults,
        code={'css': 'html > body'},
        grammar=Grammar(list=[], dict=[l.L('xpath', required=True)])
    ).dict
    assert isinstance(error, Note), error
    assert 'unwanted args' in error.message
    # - tuple case: [('xpath', 'css')] with one arg filled
    options = Fields(
        **defaults, code={'xpath': '/html/body'},
        grammar=Grammar(list=[], dict=[l.locator])
    ).dict
    assert isinstance(options, dict), options
    # - tuple case: [('xpath', 'css')] with zero args filled
    error = Fields(
        **defaults,
        code={'description': 'Just ok'},
        grammar=Grammar(list=[], dict=[l.locator])
    ).dict
    assert isinstance(error, Note), error
    assert 'unwanted args' in error.message

    # - tuple case: [('xpath', 'css')] with every arg filled
    error = Fields(
        **defaults, code=code,
        grammar=Grammar(list=[], dict=[l.locator])
    ).dict
    assert isinstance(error, Note), error
    assert 'unwanted args' in error.message


def test_validate_types():
    # wrong type will be autocasted
    options = Fields(
        name='ok', description='Ok test',
        code={'xpath': '/html/body', 'description': 0},
        grammar=Grammar(list=[], dict=[l.locator, l.desc])
    ).dict
    assert isinstance(options, dict), options
