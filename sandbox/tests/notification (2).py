import time
import pytest
import httplib

import sandbox.common.types.notification as ctn


class TestRESTAPINotification(object):
    @pytest.mark.usefixtures("notification_controller")
    def test__create_get_notification(self, rest_session, rest_session_login, test_task, task_session):
        task = test_task()
        task_session(rest_session, task.id + 1, login=rest_session_login)

        test_tag = "test_tag"
        noti = {
            "recipients": ["qwer", "asdf"],
            "subject": "some notification",
            "body": "notification body",
            "transport": ctn.Transport.EMAIL,
            "type": ctn.Type.HTML,
            "headers": ["header1", "header2"],
            "charset": ctn.Charset.ASCI,
            "view": ctn.View.EXECUTION_REPORT,
            "task_id": 12345,
            "host": "my_host",
            "check_status": ctn.JugglerStatus.OK,
            "juggler_tags": [test_tag]
        }

        created_noti = rest_session.notification(**noti)
        assert created_noti and isinstance(created_noti, dict)
        created_noti_id = created_noti.get("id")
        assert created_noti_id
        requested_noti = rest_session.notification[created_noti_id][:]
        assert requested_noti == created_noti

        requested_noti.pop("id")
        assert requested_noti.pop("author") == rest_session_login
        assert requested_noti.pop("inconsistent") is False
        assert requested_noti.pop("sent") is False
        assert requested_noti.pop("created")
        assert requested_noti.pop("urgent") is False
        assert requested_noti == noti

        for _ in ("subject", "body", "type", "headers", "charset", "view", "task_id", "host", "check_status"):
            noti.pop(_)

        created_noti = rest_session.notification(**noti)
        assert created_noti and isinstance(created_noti, dict)
        created_noti_id = created_noti.get("id")
        assert created_noti_id
        requested_noti = rest_session.notification[created_noti_id][:]
        assert requested_noti == created_noti

        for _ in ("id", "urgent"):
            requested_noti.pop(_)
        assert requested_noti.pop("author") == rest_session_login
        assert requested_noti.pop("inconsistent") is False
        assert requested_noti.pop("sent") is False
        assert requested_noti.pop("body") == ""
        assert requested_noti.pop("charset") == ctn.Charset.UTF
        assert requested_noti.pop("headers") == []
        assert requested_noti.pop("subject") == "Default subject"
        assert requested_noti.pop("task_id") == task.id + 1
        assert requested_noti.pop("type") == ctn.Type.TEXT
        assert requested_noti.pop("view") == ctn.View.DEFAULT
        assert requested_noti.pop("host") == ""
        assert requested_noti.pop("check_status") is None
        assert requested_noti.pop("created")
        assert requested_noti == noti

        noti.pop("recipients")
        with pytest.raises(rest_session.HTTPError) as ex:
            rest_session.notification(**noti)
        assert ex.value.status == httplib.BAD_REQUEST

    @pytest.mark.usefixtures("notification_controller")
    def test__list_notifications(self, rest_session, rest_session_login, test_task, task_session):
        task = test_task()
        task_session(rest_session, task.id, login=rest_session_login)

        ret = rest_session.notification[:1]
        assert ret["total"] == 0
        assert ret["limit"] == 1
        assert ret["offset"] == 0
        assert len(ret["items"]) == 0

        noti1 = {
            "recipients": ["qwer", "asdf"],
            "transport": ctn.Transport.EMAIL,
            "task_id": 12345
        }
        noti2 = {
            "recipients": ["rewq", "fdsa"],
            "transport": ctn.Transport.TELEGRAM,
            "task_id": 54321
        }
        noti1 = rest_session.notification(**noti1)
        time.sleep(1)
        noti2 = rest_session.notification(**noti2)

        import yasandbox.database.mapping
        yasandbox.database.mapping.Notification.objects(id=noti1["id"]).update_one(set__sent=True)
        noti1["sent"] = True

        for extra_field in (
            "author", "charset", "headers", "host", "inconsistent", "view", "body", "check_status", "juggler_tags"
        ):
            noti1.pop(extra_field)
            noti2.pop(extra_field)

        ret = rest_session.notification[:10]
        assert ret["total"] == 2
        assert ret["limit"] == 10
        assert ret["offset"] == 0
        assert len(ret["items"]) == 2
        for noti in (noti2, noti1):
            item = ret["items"].pop(0)
            assert item.pop("url")
            assert item == noti

        ret = rest_session.notification[1:10]
        assert ret["total"] == 2
        assert ret["limit"] == 10
        assert ret["offset"] == 1
        assert len(ret["items"]) == 1
        assert ret["items"][0].pop("url")
        assert ret["items"][0] == noti1

        ret = rest_session.notification[:10:"+date"]
        assert ret["total"] == 2
        assert ret["limit"] == 10
        assert ret["offset"] == 0
        assert len(ret["items"]) == 2
        for noti in (noti1, noti2):
            item = ret["items"].pop(0)
            assert item.pop("url")
            assert item == noti

        for noti in (noti1, noti2):
            for field in ("transport", "sent", "task_id"):
                ret = rest_session.notification[{field: noti[field]}, :10]
                assert ret["total"] == 1
                assert ret["limit"] == 10
                assert ret["offset"] == 0
                assert len(ret["items"]) == 1
                item = ret["items"].pop(0)
                assert item.pop("url")
                assert item == noti

        ret = rest_session.notification[{"recipient": "qwer"}, : 10]
        assert ret["total"] == 1
        assert ret["limit"] == 10
        assert ret["offset"] == 0
        assert len(ret["items"]) == 1
        item = ret["items"].pop(0)
        assert item.pop("url")
        assert item == noti1

    def test__notification_list_empty(self, rest_session):
        resp = rest_session.notification.read(limit=0)
        assert not resp["items"]
