from security.secret_search import Searcher
from hashlib import sha1
import tempfile
import six


def test_simple_blob():
    real_secret = 'AQAD-qJSJpcjAAADwHcUZ2Serk5EmBjzGpemfJQ'
    searcher = Searcher(validate=False)
    result = [x for x in searcher.check_blob(b'aaaa')]
    assert not result
    result = [x for x in searcher.check_blob(real_secret)]
    assert len(result) == 1
    secret = result.pop()

    assert secret.type == "YandexOAuth"
    assert secret.secret == real_secret
    assert secret.line_no == 1
    assert secret.validated is False
    assert secret.additional.get('sha1') == sha1(six.ensure_binary(real_secret)).hexdigest()


def test_simple_file():
    searcher = Searcher(validate=False)
    real_secret = 'AQAD-qJSJpcjAAADwHcUZ2Serk5EmBjzGpemfJQ'
    with tempfile.NamedTemporaryFile() as f:
        f.write(six.ensure_binary(('''
oauth_token = "%s"
not_a_oauth_token = "aaa
        ''' % real_secret).strip()))
        f.flush()
        result = [(path, secrets) for path, secrets in searcher.check_path(f.name)]
        assert len(result) == 1
        path, secrets = result.pop()
        assert path == f.name

        assert len(secrets) == 1
        secret = secrets.pop()

        assert secret.secret == real_secret
        assert secret.line_no == 1
        assert secret.validated is False
        assert secret.additional.get('sha1') == sha1(six.ensure_binary(real_secret)).hexdigest()


def test_simple_json():
    real_secret = 'AQAD-qJSJpcjAAADwHcUZ2Serk5EmBjzGpemfJQ'
    searcher = Searcher(validate=False)
    result = [(path, secrets) for path, secrets in searcher.check_json(b'{"lol":"kek"}')]
    assert not result
    result = [(path, secrets) for path, secrets in searcher.check_json('[{"lol":"kek"}, {"secret":"%s"}]' % real_secret)]
    assert len(result) == 1

    path, secrets = result.pop()
    assert path == "$.[1].secret"

    assert len(secrets) == 1
    secret = secrets.pop()

    assert secret.type == "YandexOAuth"
    assert secret.secret == real_secret
    assert secret.line_no == 1
    assert secret.validated is False
    assert secret.additional.get('sha1') == sha1(six.ensure_binary(real_secret)).hexdigest()
