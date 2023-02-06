import importlib

import pytest

try:
    importlib.import_module('flask')
except ModuleNotFoundError:
    noflask = True
else:
    noflask = False

app = None


@pytest.mark.skipif(noflask, reason='flask is not installed')
def test_flask_ping():
    from easytap import Tap

    tap = Tap(7)

    tap.import_ok('easytaphttp.flask', 'import easytaphttp.flask')

    import easytaphttp.flask
    import flask

    global app
    app = flask.Flask(__name__)

    @app.route('/ping')
    def ping():
        return 'PONG'

    t = easytaphttp.flask.FlaskTest(tap, __name__, 'app')
    tap.ok(t, 'instance created')
    tap.eq_ok(t.url_for('.ping'), '/ping', 'url_for')

    t.get_ok('.ping')
    t.status_is(200)
    t.content_type_like(r'^text/html')
    t.content_is('PONG')
    assert tap.done_testing()


@pytest.mark.skipif(noflask, reason='flask is not installed')
def test_flask_json():
    from easytap import Tap

    tap = Tap(8)

    tap.import_ok('easytaphttp.flask', 'import easytaphttp.flask')

    import easytaphttp.flask
    import flask
    from flask import make_response
    import json

    global app
    app = flask.Flask(__name__)

    @app.route('/form/<variant>')
    def json_response(variant):
        resp = make_response(json.dumps({
            'variant': variant,
            'hello': 'world'
        }), 200)
        resp.headers['content-type'] = 'application/json'
        return resp

    t = easytaphttp.flask.FlaskTest(tap, __name__, 'app')

    tap.eq_ok(t.url_for(('.json_response', {'variant': 'help'})),
              '/form/help', 'url_for placeholder')

    t.get_ok(('.json_response', {'variant': '123'}))
    t.content_type_like(r'application/json')
    t.json_has('variant')
    t.json_has('hello')

    t.json_is('variant', '123')
    t.json_is('hello', 'world')
    assert tap.done_testing()


@pytest.mark.skipif(noflask, reason='flask is not installed')
def test_flask_form():
    from easytap import Tap

    tap = Tap(8)

    tap.import_ok('easytaphttp.flask', 'import easytaphttp.flask')

    import easytaphttp.flask
    import flask
    from flask import make_response, request
    import json

    global app
    app = flask.Flask(__name__)

    @app.route('/form', methods=['GET', 'POST'])
    def form():
        resp = make_response(json.dumps({
            'hello': 'world',
            'form': request.form
        }), 200)
        resp.headers['content-type'] = 'application/json'
        return resp

    t = easytaphttp.flask.FlaskTest(tap, __name__, 'app')
    t.post_ok('.form', form={'a': 'b'})
    t.status_is(200)
    t.content_type_like(r'application/json')
    t.json_has('hello')

    t.json_has('form')
    t.json_has('form.a')
    t.json_is('form.a', 'b')
    assert tap.done_testing()


@pytest.mark.skipif(noflask, reason='flask is not installed')
def test_flask_json_request():
    from easytap import Tap

    tap = Tap(8)

    tap.import_ok('easytaphttp.flask', 'import easytaphttp.flask')

    import easytaphttp.flask
    import flask
    from flask import make_response, request
    import json

    global app
    app = flask.Flask(__name__)

    @app.route('/json-request', methods=['GET', 'POST'])
    def jrequest():
        resp = make_response(json.dumps({
            'hello': 'world',
            'json': request.get_json()
        }), 200)
        resp.headers['content-type'] = 'application/json'
        return resp

    t = easytaphttp.flask.FlaskTest(tap, __name__, 'app')

    t.post_ok('.jrequest', json={'a': 'b'})
    t.status_is(200)
    t.content_type_like(r'application/json')
    t.json_has('hello')

    t.json_has('json')
    t.json_has('json.a')
    t.json_is('json.a', 'b')
    assert tap.done_testing()


@pytest.mark.skipif(noflask, reason='flask is not installed')
def test_flask_html_response():
    from easytap import Tap

    tap = Tap(13)

    tap.import_ok('easytaphttp.flask', 'import easytaphttp.flask')

    import easytaphttp.flask
    import flask

    global app
    app = flask.Flask(__name__)

    @app.route('/html-response', methods=['GET', 'POST'])
    def hresponse():
        return """
            <html>
                <head>
                    <title>Тестовая страница</title>
                </head>
                <body>
                    <p align="justify" id="test1">Абзац</p>
                    <p align="left" id="test2">Еще абзац</p>
                </body>
            </html>
        """

    t = easytaphttp.flask.FlaskTest(tap, __name__, 'app')

    t.post_ok('.hresponse', json={'a': 'b'})
    t.status_is(200)
    t.content_type_like(r'text/html')

    t.html_has('body/p')
    t.html_has('body/p[@align="left"]')

    t.html_is('body/p[@align="left"]', 'Еще абзац')
    t.html_is('body/p[@align="justify"]', 'Абзац')

    t.html_isnt('body/p[@align="justify"]', 'Еще абзац')
    t.html_isnt('foo/bar', 'baz')

    t.html_like('body/p[@align="left"]', '.*абзац')

    t.html_unlike('body/p[@align="justify"]', '9[Аа]бзац')
    t.html_unlike('foo/bar', 'baz')
    assert tap.done_testing()


@pytest.mark.skipif(noflask, reason='flask is not installed')
def test_flask_cookie():
    from easytap import Tap

    tap = Tap(11)

    tap.import_ok('easytaphttp.flask', 'import easytaphttp.flask')

    import easytaphttp.flask
    import flask
    from flask import make_response, request

    global app
    app = flask.Flask(__name__)

    @app.route('/cookie', methods=['GET', 'POST'])
    def cresponse():
        resp = make_response(f"""
            <html>
                <head>
                    <title>Тестовая страница</title>
                </head>
                <body>
                    <p>{ request.cookies.get('hello', 'No') }</p>
                </body>
            </html>
        """)
        resp.set_cookie('hello', 'world')
        return resp

    t = easytaphttp.flask.FlaskTest(tap, __name__, 'app')

    t.post_ok('.cresponse', json={'a': 'b'})
    t.status_is(200)
    t.content_type_like(r'text/html')

    t.html_has('body/p')
    t.html_is('body/p', 'No')

    t.post_ok('.cresponse', json={'a': 'b'})
    t.status_is(200)
    t.content_type_like(r'text/html')
    t.html_has('body/p')
    t.html_is('body/p', 'world')

    assert tap.done_testing()
