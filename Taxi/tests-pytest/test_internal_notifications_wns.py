import pytest

from taxi.internal.notifications import _wns

SAMPLE_URL = (
    'https://hk2.notify.windows.com/?token=AwYAAAAq6nUxPLi1cKnO1ehtMZF1tcHprwy'
    '9%2fgc8VBSc7WPdrjdjTyOjLY06t%2fI6dSWeFXg3ZcYv%2f6Y6SNTQvo1n%2fEnKGUGFguBE'
    '7LU9DhB9lurpJbj7JZT4I9DdNl8%2b%2fLF9Yz4%3d'
)


@pytest.skip
@pytest.mark.filldb(_fill=False)
@pytest.inline_callbacks
def test_notifications():
    # We cannot actually make reliable positive test here
    # because url can get outdated breaking the test
    # We can, however, test whether we trigger only client error and not
    # some `bad` errors as invalid request or creds
    with pytest.raises(_wns.ClientError):
        data = {'order_id': '1', 'updated': 'now'}
        yield _wns.send(SAMPLE_URL, 'hello', 'world', data, 'good', 'bye')
