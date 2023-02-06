import mock

import sandbox.common.types.notification as ctn
from sandbox.services.modules import messengerq_bot

from sandbox.yasandbox.database import mapping as mp


class TestTaskStatusNotifier(object):
    def test__track_q(self, task_manager, server, notification_trigger_controller):
        messengerq_bot.MessengerQBot.messengerq_client = mock.MagicMock()
        bot = messengerq_bot.MessengerQBot()
        bot._model = mock.MagicMock()
        bot._model.context = {}

        task = task_manager.create("TEST_TASK", owner="user", author="user")
        statuses = ["success", "exception"]
        chat_id = "3a407ebd-1bc6-4331-811e-1b95161e2d39_a4562902-cf3b-492c-9991-a74ba6cc6d9e"
        uid = 1120000000012257

        test_messages = [{
            "message": {
                "reply_to_message": {
                    "date": 15493589947,
                    "text": "hi",
                    "from": {
                        "id": "a4562902cf3b492c9991a74ba6cc6d9e"
                    },
                    "message_id": 1549358994729003,
                    "chat": {
                        "id": chat_id
                    }
                },
                "author": {
                    "is_bot": False,
                    "id": "3a407ebd1bc64331811e1b95161e2d39",
                    "uid": uid
                },
                "text": "/track {task_id} {statuses}".format(task_id=task.id, statuses=" ".join(statuses)),
                "chat": {
                    "id": chat_id
                },
                "date": 1549361723,
                "from": {
                    "is_bot": False,
                    "id": "3a407ebd1bc64331811e1b95161e2d39",
                    "uid": uid
                },
                "message_id": 1549361723428003
            },
            "update_id": 27794
        }]

        def fake_get_updates(*args, **kwargs):
            return test_messages
        bot.send_message = mock.MagicMock()

        bot.messengerq_client.getUpdates = mock.MagicMock()
        bot.messengerq_client.getUpdates.read = fake_get_updates
        bot.tick()

        triggers = list(notification_trigger_controller.Model.objects())
        assert len(triggers) == 1
        trigger = triggers[0]
        assert trigger.source == task.id
        assert trigger.transport == ctn.Transport.Q
        assert sorted(trigger.statuses) == sorted(map(str.upper, statuses))
        assert sorted(trigger.recipients) == [chat_id]
        assert bot.messengerq_client.sendMessage.create.call_count == 1
        assert bot.messengerq_client.sendMessage.create.call_args

        task_mapping = mp.Task.objects.with_id(task.id)
        assert task_mapping.notifications[0].transport == ctn.Transport.Q
        assert sorted(task_mapping.notifications[0].statuses) == sorted(map(str.upper, statuses))
        assert sorted(task_mapping.notifications[0].recipients) == [chat_id]

        bot.tick()
        triggers = list(notification_trigger_controller.Model.objects())
        assert len(triggers) == 1
        task_mapping = mp.Task.objects.with_id(task.id)
        assert len(task_mapping.notifications) == 1
