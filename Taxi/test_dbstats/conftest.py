from dbstats_app import app
from infranaim.conftest import *


@pytest.fixture
@pytest.mark.filldb
def flask_client(mongodb):
    app.config['SECRET_KEY'] = 'i9i9ii'
    app.db = mongodb
    return app.test_client()
