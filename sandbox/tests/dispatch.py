import mock
import pytest

import common.rest
import common.config


class TestDispatch(object):
    @staticmethod
    @pytest.mark.xfail(run=False)
    @pytest.mark.usefixtures("service_user")
    def test__rest_client_dispatch(test_task_2, monkeypatch, service_login):
        import sdk2
        import yasandbox.controller.dispatch
        with common.rest.DispatchedClient as dispatch:
            dispatch(yasandbox.controller.dispatch.RestClient(None, service_login))
            monkeypatch.setattr(common.rest.Client, "_request", mock.MagicMock())
            t1 = test_task_2(None).save()
            dispatch(yasandbox.controller.dispatch.RestClient(t1.id, service_login))
            t1.current = t1
            t2 = test_task_2(t1).save()
            t1_id = t1.id
            t2_id = t2.id

            t2 = sdk2.Task[t2_id]
            assert t2.id == t2_id
            assert t2.parent.id == t1_id

            # noinspection PyUnresolvedReferences
            assert not common.rest.Client._request.called
