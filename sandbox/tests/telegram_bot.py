import mock
import pytest
import datetime as dt

import sandbox.common.types.notification as ctn
from sandbox.services.modules import telegram_bot as tb

from sandbox.yasandbox.database import mapping as mp


class TestTaskStatusNotifier(object):
    def test__track(self, task_manager, server, notification_trigger_controller):
        with mock.patch(
            "sandbox.services.modules.TelegramBot.sandbox_team", new_callable=mock.PropertyMock
        ) as mock_sandbox_team:
            tb.TelegramBot.telegram = mock.MagicMock()
            mock_sandbox_team.return_value = {
                "user1": "telegram_login1",
                "user2": "telegram_login2",
            }
            telegram_bot = tb.TelegramBot()
            telegram_bot._model = mock.MagicMock()
            telegram_bot._model.context = {}

            chat_id = 123456

            task = task_manager.create("TEST_TASK", owner="user", author="user")
            statuses = ["success", "exception"]

            test_message = [{
                "update_id": 42,
                "message": {
                    "from": {
                        "username": "test_user",
                        "id": chat_id
                    },
                    "chat": {
                        "id": chat_id
                    },
                    "text": "/track {task_id} {statuses}".format(task_id=task.id, statuses=" ".join(statuses))
                }
            }]

            def fake_get_updates(**kwargs):
                return {"result": test_message}
            telegram_bot.send_message = mock.MagicMock()
            telegram_bot.send_message.return_value = {"result": "ok"}

            telegram_bot.telegram.get_updates = fake_get_updates
            telegram_bot.process_updates(-1)

            triggers = list(notification_trigger_controller.Model.objects())
            assert len(triggers) == 1
            trigger = triggers[0]
            assert trigger.source == task.id
            assert trigger.transport == ctn.Transport.TELEGRAM
            assert sorted(trigger.statuses) == sorted(map(str.upper, statuses))
            assert sorted(trigger.recipients) == sorted(["test_user"])
            assert telegram_bot.send_message.call_count == 1
            assert telegram_bot.send_message.call_args

            task_mapping = mp.Task.objects.with_id(task.id)
            assert task_mapping.notifications[0].transport == ctn.Transport.TELEGRAM
            assert sorted(task_mapping.notifications[0].statuses) == sorted(map(str.upper, statuses))
            assert sorted(task_mapping.notifications[0].recipients) == sorted(["test_user"])

            telegram_bot.process_updates(-1)
            triggers = list(notification_trigger_controller.Model.objects())
            assert len(triggers) == 1
            task_mapping = mp.Task.objects.with_id(task.id)
            assert len(task_mapping.notifications) == 1

    class TestTelegramNotificationsOnWalleAutomationStatuses(object):
        @pytest.mark.parametrize("dns_enabled, healing_enabled", [
            ([False, True], [True, True]),
            ([True, True], [False, False]),
            ([True, True], [True, True]),
        ])
        def test__automation_notifies(self, dns_enabled, healing_enabled):
            database_object = mock.MagicMock()
            database_object.context = {
                "automation": {
                    "1": {
                        "dns_automation_enabled": dns_enabled[0],
                        "healing_automation_enabled": healing_enabled[0],
                        "update_ts": dt.datetime.now(),
                    },
                    "2": {
                        "dns_automation_enabled": dns_enabled[1],
                        "healing_automation_enabled": healing_enabled[1],
                        "update_ts": dt.datetime.now(),
                    },
                },
            }
            with mock.patch("sandbox.yasandbox.database.mapping.Service") as service_mock:
                service_mock.objects.with_id.return_value = database_object
                telegram_bot = tb.TelegramBot()
                telegram_bot.notify = mock.MagicMock()
                telegram_bot._model = mock.MagicMock()
                telegram_bot._model.context = {}
                telegram_bot.check_automation_statuses()

                expected_calls = (
                    (1 if any(not e for e in dns_enabled) else 0) + (1 if any(not e for e in healing_enabled) else 0)
                )
                assert len(telegram_bot.notify.call_args_list) == expected_calls
