from pahtest.action import Action
from pahtest.browser import Browser
from pahtest.options import PlainOptions
from pahtest.results import ActionResult


def test_plain_form():
    """
    Plain form looks like this:

    ```
    tests:
      # plain form ...
      - test: get_ok
        url: /
      # ... is just like this
      - get_ok:
          url: /
    ```
    """
    kwargs = dict(
        index=1,
        browser=Browser(hub_url='', name='chrome'),
        options=PlainOptions(name='', code={}),
    )
    action = Action(code={'test': 'get_ok', 'url': '/'}, **kwargs)
    assert not list(action.validate())  # no errors
    assert 'get_ok' == action.func_name
    assert {'url': '/'} == action.func_args

    action = Action(code={'get_ok': '/', 'has': '/html'}, **kwargs)
    errors = list(action.validate())
    assert 1 == len(errors), [str(e) for e in errors]
    assert isinstance(errors[0], ActionResult)
    assert 'Test must contain single key.' == errors[0].message
