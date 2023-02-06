import allure
from flask.testing import FlaskClient


def attach_flask_response(response):
    allure.attach(response.status, response.data)


class AllureFlaskTestClient(FlaskClient):
    def __init__(self, *args, **kwargs):
        super(AllureFlaskTestClient, self).__init__(*args, **kwargs)

    def open(self, *args, **kwargs):
        as_tuple = kwargs.get("as_tuple", False)
        method = kwargs.get("method", "-")
        path = kwargs.get("path", args[0] if len(args) > 0 else "-")
        with allure.step(f"Request {method} {path}"):
            if as_tuple:
                environ, response = super(AllureFlaskTestClient, self).open(*args, **kwargs)
                attach_flask_response(response)
                return environ, response
            else:
                response = super(AllureFlaskTestClient, self).open(*args, **kwargs)
                attach_flask_response(response)
                return response
