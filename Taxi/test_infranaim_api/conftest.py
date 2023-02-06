from infranaim_app import app
from infranaim.conftest import *


@pytest.fixture
@pytest.mark.fill_db
def infranaim_client_factory():
    def _run(db_mongo, **kwargs):
        app.config['SECRET_KEY'] = 'i9i9ii'
        for key, value in kwargs.get('configs', {}).items():
            app.config[key] = value
        app.db = db_mongo
        return app.test_client()
    return _run
