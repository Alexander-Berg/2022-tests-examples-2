import uuid
import pytest


@pytest.fixture(scope="session")
def service_login():
    return "test-service-user"


@pytest.fixture(scope="session")
def sudoer_login():
    return "test-sudoer-user"


@pytest.fixture(scope="session")
def session_maker_login():
    return "test-session-maker-user"


@pytest.fixture(scope="session")
def session_maker2_login():
    return "test-session-maker2-user"


@pytest.fixture(scope="session")
def api_session_login():
    return "test-api-user"


@pytest.fixture(scope="session")
def api_session_group():
    return "TEST-API-GROUP"


@pytest.fixture(scope="session")
def api_su_session_login():
    return "test-api-su-user"


@pytest.fixture(scope="session")
def api_su_session_group():
    return "TEST-API-SU-GROUP"


@pytest.fixture(scope="session")
def api_trusted_session_login():
    return "test-api-trusted-user"


@pytest.fixture(scope="session")
def api_trusted_session_group():
    return "TEST-API-TRUSTED-GROUP"


@pytest.fixture(scope="session")
def gui_session_login():
    return "test-gui-user"


@pytest.fixture(scope="session")
def gui_su_session_login():
    return "test-gui-su-user"


@pytest.fixture(scope="session")
def rest_session_login():
    return "test-rest-user"


@pytest.fixture(scope="session")
def rest_session_login2():
    return "test-rest-user2"


@pytest.fixture(scope="session")
def rest_session_group():
    return "TEST-REST-GROUP"


@pytest.fixture(scope="session")
def rest_su_session_login():
    return "test-rest-su-user"


@pytest.fixture(scope="session")
def rest_su_session_group():
    return "TEST-REST-SU-GROUP"


@pytest.fixture(scope="session")
def releaser():
    """We append this user to releasers for all AbstractResource (see common_initialize)"""
    return "test-releaser-user"


@pytest.fixture(scope="session")
def rest_session_token():
    return "TOK_" + uuid.uuid4().hex[4:]


@pytest.fixture(scope="session")
def rest_su_session_token():
    return "TOK_" + uuid.uuid4().hex[4:]


@pytest.fixture(scope="session")
def rest_sudoer_token():
    return "TOK_" + uuid.uuid4().hex[4:]


@pytest.fixture(scope="session")
def rest_session_maker_token():
    return "TOK_" + uuid.uuid4().hex[4:]


@pytest.fixture(scope="session")
def rest_session_maker2_token():
    return "TOK_" + uuid.uuid4().hex[4:]
