import uuid
import pytest
import httplib

from sandbox import common
from sandbox.common.types import user as ctu

from sandbox.yasandbox.database import mapping


class TestAuthenticate(object):
    def test__create_external_session(
        self, rest_session, rest_session_login, rest_session_maker_session, session_maker_login
    ):
        with pytest.raises(common.rest.Client.HTTPError) as ex:
            rest_session.authenticate.external.session.create(
                login=session_maker_login, ttl=600, service="tasklet_stable", job_id="tasklet_1"
            )
        assert ex.value.status == httplib.FORBIDDEN

        with pytest.raises(common.rest.Client.HTTPError) as ex:
            rest_session_maker_session.authenticate.external.session.create(
                login="test_kek", ttl=600, service="tasklet_stable", job_id="tasklet_1"
            )
        assert ex.value.status == httplib.BAD_REQUEST

        session = rest_session_maker_session.authenticate.external.session.create(
            login=rest_session_login, ttl=600, service="tasklet_stable", job_id="tasklet_1"
        )

        token = session["token"]
        oauth_model = mapping.OAuthCache.objects.with_id(token)
        assert oauth_model.login == rest_session_login == session["login"]
        assert oauth_model.properties.service == "tasklet_stable" == session["service"]
        assert oauth_model.source == ctu.TokenSource.EXTERNAL_SESSION
        assert oauth_model.app_id == "tasklet_1" == session["job_id"]
        assert oauth_model.ttl == 600 == session["ttl"]
        assert oauth_model.properties.session_maker == session_maker_login

        session2 = rest_session_maker_session.authenticate.external.session.create(
            login=rest_session_login, ttl=300, service="tasklet_stable", job_id="tasklet_2",
            sandbox_task_id=1
        )
        token2 = session2["token"]
        assert token != token2

        oauth_model = mapping.OAuthCache.objects.with_id(token2)
        assert oauth_model.login == rest_session_login == session2["login"]
        assert oauth_model.properties.service == "tasklet_stable" == session2["service"]
        assert oauth_model.source == ctu.TokenSource.EXTERNAL_SESSION
        assert oauth_model.app_id == "tasklet_2" == session2["job_id"]
        assert oauth_model.ttl == 300 == session2["ttl"]
        assert oauth_model.properties.session_maker == session_maker_login
        assert oauth_model.properties.sandbox_task_id == 1 == session2["sandbox_task_id"]

        assert mapping.OAuthCache.objects(token=token).count() == 1

    def test__get_external_session(
        self, rest_session, rest_session_login, rest_session_maker_session, session_maker_login,
        rest_session_maker2_session
    ):
        session1 = rest_session_maker_session.authenticate.external.session.create(
            login=rest_session_login, ttl=600, service="tasklet_stable", job_id="tasklet_1",
            sandbox_task_1=1
        )
        rest_session_maker_session.authenticate.external.session.create(
            login=rest_session_login, ttl=300, service="tasklet_prestable", job_id="tasklet_2",
            sandbox_task_id=2
        )

        with pytest.raises(common.rest.Client.HTTPError) as ex:
            rest_session.authenticate.external.session.search.create(
                service="tasklet_stable", job_id="tasklet_1"
            )
        assert ex.value.status == httplib.FORBIDDEN
        with pytest.raises(common.rest.Client.HTTPError) as ex:
            rest_session_maker_session.authenticate.external.session.search.create(
                service="tasklet_stable", job_id="tasklet_3"
            )
        assert ex.value.status == httplib.NOT_FOUND
        with pytest.raises(common.rest.Client.HTTPError) as ex:
            rest_session_maker_session.authenticate.external.session.search.create(
                service="tasklet_stable",
            )
        assert ex.value.status == httplib.BAD_REQUEST
        with pytest.raises(common.rest.Client.HTTPError) as ex:
            rest_session_maker_session.authenticate.external.session.search.create(
                service="tasklet_prestable", job_id="tasklet_1"
            )
        assert ex.value.status == httplib.FORBIDDEN
        with pytest.raises(common.rest.Client.HTTPError) as ex:
            rest_session_maker_session.authenticate.external.session.search.create(
                service="tasklet_stable", job_id="tasklet_3", token=session1["token"]
            )
        assert ex.value.status == httplib.NOT_FOUND
        with pytest.raises(common.rest.Client.HTTPError) as ex:
            rest_session_maker2_session.authenticate.external.session.search.create(
                service="tasklet_stable", job_id="tasklet_1"
            )
        assert ex.value.status == httplib.FORBIDDEN
        get_session1 = rest_session_maker_session.authenticate.external.session.search.create(
            service="tasklet_stable", job_id="tasklet_1"
        )
        assert get_session1 == session1
        get_session1 = rest_session_maker_session.authenticate.external.session.search.create(
            service="tasklet_stable", token=session1["token"]
        )
        assert get_session1 == session1
        get_session1 = rest_session_maker_session.authenticate.external.session.search.create(
            service="tasklet_stable", job_id="tasklet_1", token=session1["token"]
        )
        assert get_session1 == session1

    def test__delete_external_session(
        self, rest_session, rest_session_login, rest_session_maker_session, session_maker_login,
        rest_session_maker2_session
    ):
        with pytest.raises(common.rest.Client.HTTPError) as ex:
            rest_session_maker_session.authenticate.external.session.delete(
                token="test_kek", service="tasklet_stable"
            )
        assert ex.value.status == httplib.NOT_FOUND

        session = rest_session_maker_session.authenticate.external.session.create(
            login=rest_session_login, ttl=600, service="tasklet_stable", job_id="tasklet_1"
        )
        token = session["token"]
        assert mapping.OAuthCache.objects(token=token).count()

        with pytest.raises(common.rest.Client.HTTPError) as ex:
            rest_session.authenticate.external.session.delete(
                token=token, service="tasklet_stable"
            )
        assert ex.value.status == httplib.FORBIDDEN

        with pytest.raises(common.rest.Client.HTTPError) as ex:
            rest_session_maker2_session.authenticate.external.session.delete(
                token=token, service="tasklet_stable"
            )
        assert ex.value.status == httplib.FORBIDDEN

        with pytest.raises(common.rest.Client.HTTPError) as ex:
            rest_session_maker_session.authenticate.external.session.delete(
                token=token, service="tasklet_testing"
            )
        assert ex.value.status == httplib.FORBIDDEN

        rest_session_maker_session.authenticate.external.session.delete(
            token=token, service="tasklet_stable"
        )
        assert not mapping.OAuthCache.objects(token=token).count()

    def test__use_external_session(
        self, rest_session, rest_session_login, rest_session_maker_session, serviceq
    ):
        session = rest_session_maker_session.authenticate.external.session.create(
            login=rest_session_login, ttl=600, service="tasklet_stable", job_id="tasklet_1"
        )
        token = session["token"]
        client = common.rest.Client(auth=token)
        response = client.user.current.read()
        assert response["login"] == rest_session_login

    def test__task_session(self, rest_session, rest_session_login, rest_session_maker_session, serviceq):
        oauth = mapping.OAuthCache(
            token=uuid.uuid4().hex,
            login=rest_session_login,
            ttl=60,
            source=":".join([ctu.TokenSource.CLIENT, "test_client"]),
            task_id=1,
            vault="test",
        )
        oauth.save()

        with pytest.raises(common.rest.Client.HTTPError) as ex:
            rest_session.authenticate.task.session.search.create(token=oauth.token)
        assert ex.value.status == httplib.FORBIDDEN
        with pytest.raises(common.rest.Client.HTTPError) as ex:
            rest_session_maker_session.authenticate.task.session.search.create(token="fail")
        assert ex.value.status == httplib.NOT_FOUND
        session = rest_session_maker_session.authenticate.task.session.search.create(token=oauth.token)
        assert session["token"] == oauth.token
        assert session["task_id"] == oauth.task_id
        assert session["login"] == oauth.login
        assert session["ttl"] == oauth.ttl
