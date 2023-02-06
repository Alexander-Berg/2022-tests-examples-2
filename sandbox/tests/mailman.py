import mock
import email
import pytest
import smtplib
import collections

import common.types.task as ctt
import common.types.notification as ctn

import services.modules.mailman as mailman
import yasandbox.database.mapping as mapping
import yasandbox.manager.tests as manager_tests

import sandboxsdk.tests.sandboxapi

Mail = collections.namedtuple("Mail", ("from_addr", "to_addrs", "msg"))


class TestMailman(object):

    @staticmethod
    def latest_mail():
        assert isinstance(smtplib.SMTP, mock.Mock), "Please mock smtplib.SMTP first"
        return Mail(*smtplib.SMTP("localhost").sendmail.call_args[0])

    @pytest.mark.usefixtures("notification_controller", "sdk2_dispatched_rest_session")
    def test__reply_to_header(self, task_manager, notification_trigger_controller, task_status_notifier):
        def to_address(user_login):
            return user_login + mailman.Mailman.DOMAIN

        code_authors = ["black", "yellow"]
        smtplib.SMTP = mock.Mock()

        task = manager_tests._create_task(task_manager, "TEST_TASK", owner="user", host="host")
        notification_trigger_controller.Model(
            source=task.id,
            statuses=[ctt.Status.ENQUEUING],
            transport=ctn.Transport.EMAIL,
            recipients=["white", "orange"]
        ).save()

        task.set_status(ctt.Status.ENQUEUING)
        task_status_notifier.tick()

        send_list = mapping.Notification.objects(task_id=task.id, transport=ctn.Transport.EMAIL, sent=False)
        mm = mailman.Mailman()
        mm._tasks_owners = {
            "TEST_TASK": code_authors
        }
        mm.send_email_notification(send_list[0])

        raw_message = self.latest_mail().msg
        mail = email.message_from_string(raw_message)
        assert "Reply-To" in mail

        subscribers = [address.strip() for address in mail["Reply-To"].split(",")]
        assert all([to_address(login) in subscribers for login in ["sandbox"] + code_authors]), subscribers

    @pytest.mark.usefixtures("sdk2_dispatched_rest_session")
    def test__warn_on_message_size_exceedance(self, notification_controller):
        body = "A" * mailman.Mailman.MESSAGE_SIZE_LIMIT
        notification_controller.save(
            notification_controller.Transport.EMAIL,
            ["test_recipient"], "test_user", "Test", body
        )

        smtplib.SMTP = mock.Mock()
        send_list = mapping.Notification.objects(transport=ctn.Transport.EMAIL, sent=False)
        mailman.Mailman().send_email_notification(send_list[0])

        raw_message = self.latest_mail().msg
        mail = email.message_from_string(raw_message)
        assert mail.get_payload().startswith(mailman.Mailman.WARNING_TEMPLATE.split("{}")[0])

    @pytest.mark.usefixtures("notification_controller", "sdk2_dispatched_rest_session")
    def test__strip_html_tags_in_text_version(
            self, task_manager, notification_trigger_controller, task_status_notifier
    ):
        task = manager_tests._create_task(task_manager, "TEST_TASK", owner="user", host="host")
        notification_trigger_controller.Model(
            source=task.id,
            statuses=[ctt.Status.ENQUEUING],
            transport=ctn.Transport.EMAIL,
            recipients=["werat"]
        ).save()

        task.set_status(ctt.Status.ENQUEUING)
        task_status_notifier.tick()

        html = "<b><i><div>Hello</div>, <a href='http://example.com'>Your Boldness!</a></b></i></body>"
        text = "Hello, Your Boldness!"

        smtplib.SMTP = mock.Mock()
        notification = mapping.Notification.objects(task_id=task.id, transport=ctn.Transport.EMAIL, sent=False).first()
        notification.body = html
        mailman.Mailman().send_email_notification(notification)

        raw_message = self.latest_mail().msg
        mail = email.message_from_string(raw_message)
        text_message = mail.get_payload()[0].get_payload()[0].get_payload(decode=True)
        assert text_message == text

    @pytest.mark.usefixtures("notification_controller", "sdk2_dispatched_rest_session")
    def test__send_urgent_email(
        self, task_manager, server, notification_trigger_controller, api_session, rest_session, task_session_context
    ):
        def multiple_notify(task, urgent):
            with task_session_context(api_session, task.id):
                channel = sandboxsdk.tests.sandboxapi.sandboxapi_instance(server, api_session)
                channel.send_email("white", [], "testing xmlrpc", "{!r}".format(urgent), urgent=urgent)

            with task_session_context(rest_session, task.id):
                rest_session.notification(
                    recipients=["black", "white"],
                    subject="testing api", body="{!r}".format(urgent),
                    transport=ctn.Transport.EMAIL,
                    urgent=urgent
                )

        task = manager_tests._create_task(task_manager, "TEST_TASK", owner="user", host="host")
        smtplib.SMTP = mock.Mock()
        expected_address = {
            True: "sandbox-urgent <sandbox-urgent@yandex-team.ru>",
            False: "sandbox-noreply <sandbox-noreply@yandex-team.ru>"
        }

        for really_urgent in (True, False):
            multiple_notify(task, really_urgent)
            notifications = list(mapping.Notification.objects(sent=False))
            assert len(notifications) == 2  # XMLRPC and REST
            for notification in notifications:
                mailman.Mailman().send_email_notification(notification)
                from_address = self.latest_mail().from_addr
                assert notification.urgent == really_urgent, notification.to_json()
                assert from_address == expected_address[really_urgent], notification.to_json()

    def test__send_telegram_notification_about_task(
        self, task_manager, server, notification_trigger_controller, task_status_notifier, notification_controller
    ):
        task = manager_tests._create_task(task_manager, "TEST_TASK", owner="user", host="host")
        notification_trigger_controller.Model(
            source=task.id,
            statuses=[ctt.Status.ENQUEUING],
            transport=ctn.Transport.TELEGRAM,
            recipients=["telegram_login_1", "telegram_login_2"]
        ).save()

        task.set_status(ctt.Status.ENQUEUING)
        task_status_notifier.tick()
        mailman.Mailman.telegram_client = mock.MagicMock()
        notification = mapping.Notification.objects(
            task_id=task.id, transport=ctn.Transport.TELEGRAM, sent=False
        ).first()
        telegram_bot_model = mapping.Service(
            name="telegram_bot",
            context={
                "usernames": {
                    "telegram_login_1": "chat_id1"
                }
            }
        )
        mm = mailman.Mailman()
        mm._telegram_bot_model = telegram_bot_model
        mm.send_telegram_notification(notification)

        assert mm.telegram_client.send_message.call_count == 1
        assert mm.telegram_client.send_message.call_args[0][0] == "chat_id1"

        notifications = mapping.Notification.objects()
        assert len(notifications) == 1

        notification = notifications[0]
        assert notification.sent
        assert notification.transport == ctn.Transport.TELEGRAM

    def test__send_telegram_notification_from_task(
        self, rest_session, rest_session_login, task_session,
        task_manager, server, notification_controller, group_controller, user_controller
    ):
        task_id = 1
        task_session(rest_session, task_id, login=rest_session_login)

        notification1 = {
            "recipients": ["telegram_login_1"],
            "transport": ctn.Transport.TELEGRAM,
            "body": "Test text 1",
            "task_id": task_id
        }
        notification2 = {
            "recipients": ["telegram_login_1", "telegram_login_2"],
            "transport": ctn.Transport.TELEGRAM,
            "body": "Test text 2",
            "task_id": task_id
        }
        telegram_chat_id = "-823782424"
        user = user_controller.create(mapping.User(
            login="telegram_login_3"
        ))
        user_controller.validated(user.login)
        group_controller.create(
            mapping.Group(name='TGROUP', users=["telegram_login_3"], telegram_chat_id=telegram_chat_id)
        )

        notification3 = {
            "recipients": ["TGROUP"],
            "transport": ctn.Transport.TELEGRAM,
            "body": "Test text 3",
            "task_id": task_id
        }

        mailman.Mailman.telegram_client = mock.MagicMock()
        mm = mailman.Mailman()
        telegram_bot_model = mapping.Service(
            name="telegram_bot",
            context={
                "usernames": {
                    "telegram_login_1": "chat_id1",
                    "telegram_login_2": "chat_id2",
                }
            }
        )
        mm._telegram_bot_model = telegram_bot_model

        rest_session.notification(**notification1)
        notification = mapping.Notification.objects(sent=False).first()
        assert notification.body == notification1["body"]
        mm.send_telegram_notification(notification)

        assert mm.telegram_client.send_message.call_count == 1
        assert mm.telegram_client.send_message.call_args[0][0] == "chat_id1"
        assert mm.telegram_client.send_message.call_args[0][1] == notification1["body"]
        mm.telegram_client.send_message.reset_mock()

        rest_session.notification(**notification2)
        notification = mapping.Notification.objects(sent=False).first()
        assert notification.body == notification2["body"]
        mm.send_telegram_notification(notification)
        assert mm.telegram_client.send_message.call_count == 2
        call_chats = sorted((
            mm.telegram_client.send_message.call_args_list[0][0][0],
            mm.telegram_client.send_message.call_args_list[1][0][0]
        ))
        assert call_chats == sorted(("chat_id1", "chat_id2"))
        text1 = mm.telegram_client.send_message.call_args_list[0][0][1]
        text2 = mm.telegram_client.send_message.call_args_list[1][0][1]
        assert text1 == text2 == notification2["body"]
        mm.telegram_client.send_message.reset_mock()

        with mock.patch(
            "sandbox.yasandbox.controller.user.User.check_telegram_username"
        ) as mock_check_telegram_username:
            mock_check_telegram_username.return_value = False

            mm.telegram_client.get_chat_member = mock.MagicMock()
            mm.telegram_client.get_chat_member.return_value = {
                "ok": False
            }

            mm.telegram_client.get_chat_administrators = mock.MagicMock()
            mm.telegram_client.get_chat_administrators.return_value = {
                "ok": True,
                "result": [{"user": {"username": "TashaToolsBot"}}]
            }
            rest_session.notification(**notification3)
            notification = mapping.Notification.objects(sent=False).first()
            assert notification.body == notification3["body"]
            mm.send_telegram_notification(notification)

            assert mm.telegram_client.send_message.call_count == 1
            assert mm.telegram_client.send_message.call_args[0][0] == telegram_chat_id
            assert mm.telegram_client.send_message.call_args[0][1] == notification3["body"]
            mm.telegram_client.send_message.reset_mock()

            mapping.Group.objects(name='TGROUP').update(set__telegram_chat_id="-38738578345")
            mm.telegram_client.get_chat_administrators.return_value = {
                "ok": True,
                "result": [{"user": {"username": "Kek"}}]
            }
            rest_session.notification(**notification3)
            notification = mapping.Notification.objects(sent=False).first()
            assert notification.body == notification3["body"]
            mm.send_telegram_notification(notification)

            assert mm.telegram_client.send_message.call_count == 0

            mapping.Group.objects(name='TGROUP').update(set__telegram_chat_id="-38738578356")
            mm.telegram_client.send_message.reset_mock()
            mm.telegram_client.get_chat_member.return_value = {
                "ok": True,
                "result": {
                    "status": "administrator"
                }
            }
            rest_session.notification(**notification3)
            notification = mapping.Notification.objects(sent=False).first()
            assert notification.body == notification3["body"]
            mm.send_telegram_notification(notification)
            assert mm.telegram_client.send_message.call_count == 1

    def test__send_q_notification_about_task(
        self, task_manager, server, notification_trigger_controller, task_status_notifier, notification_controller
    ):
        task = manager_tests._create_task(task_manager, "TEST_TASK", owner="user", host="host")
        notification_trigger_controller.Model(
            source=task.id,
            statuses=[ctt.Status.ENQUEUING],
            transport=ctn.Transport.Q,
            recipients=["q_chat_1"]
        ).save()

        task.set_status(ctt.Status.ENQUEUING)
        task_status_notifier.tick()
        mailman.Mailman.messengerq_client = mock.MagicMock()
        notification = mapping.Notification.objects(
            task_id=task.id, transport=ctn.Transport.Q, sent=False
        ).first()

        mm = mailman.Mailman()
        mm.send_messengerq_notification(notification)

        assert mm.messengerq_client.sendMessage.create.call_count == 1

        notifications = mapping.Notification.objects()
        assert len(notifications) == 1

        notification = notifications[0]
        assert notification.sent
        assert notification.transport == ctn.Transport.Q

    def test__send_q_notification_from_task(
        self, rest_session, rest_session_login, task_session,
        task_manager, server, notification_controller, user_controller
    ):
        user1 = user_controller.Model(login="test_user1", messenger_chat_id="q_chat_1").save()
        user2 = user_controller.Model(login="test_user2", messenger_chat_id="q_chat_2").save()
        task_id = 1
        task_session(rest_session, task_id, login=rest_session_login)

        notification1 = {
            "recipients": [user1.login],
            "transport": ctn.Transport.Q,
            "body": "Test text 1",
            "task_id": task_id
        }
        notification2 = {
            "recipients": [user1.login, user2.login],
            "transport": ctn.Transport.Q,
            "body": "Test text 2",
            "task_id": task_id
        }

        mailman.Mailman.messengerq_client = mock.MagicMock()
        mm = mailman.Mailman()

        rest_session.notification(**notification1)
        notification = mapping.Notification.objects(sent=False).first()
        assert notification.body == notification1["body"]
        mm.send_messengerq_notification(notification)

        assert mm.messengerq_client.sendMessage.create.call_count == 1
        mm.messengerq_client.sendMessage.reset_mock()

        rest_session.notification(**notification2)
        notification = mapping.Notification.objects(sent=False).first()
        assert notification.body == notification2["body"]
        mm.send_messengerq_notification(notification)
        assert mm.messengerq_client.sendMessage.create.call_count == 2

    def test__send_juggler_notification_about_task(
        self, task_manager, server, notification_trigger_controller, task_status_notifier, notification_controller,
        group_controller, user_controller
    ):
        user_controller.validated("user1")
        task = manager_tests._create_task(task_manager, "TEST_TASK", owner="user", host="host")
        group = group_controller.create(group_controller.Model(
            name="TEST_GROUP", users=["user1"],
            juggler_settings=group_controller.Model.JugglerSettings(
                default_host="test.host", default_service="test_service",
                checks={
                    ctn.JugglerCheck.TASK_STATUS_CHANGED: group_controller.Model.JugglerSettings.JugglerCheck(
                        service="test2_service"
                    )
                }
            )
        ))
        juggler_recipient = "host=test2.host&service=test2_service"

        test_tag = 'test_tag'
        notification_trigger_controller.Model(
            source=task.id,
            statuses=[ctt.Status.ENQUEUING],
            transport=ctn.Transport.JUGGLER,
            recipients=[group.name, juggler_recipient],
            check_status=ctn.JugglerStatus.OK,
            juggler_tags=[test_tag]
        ).save()

        task.set_status(ctt.Status.ENQUEUING)
        task_status_notifier.tick()
        mailman.Mailman.juggler_client = mock.MagicMock()
        notification = mapping.Notification.objects(
            task_id=task.id, transport=ctn.Transport.JUGGLER, sent=False
        ).first()

        assert notification.transport == ctn.Transport.JUGGLER
        juggler_group_recipient = "host={}&service={}".format(
            group.juggler_settings.default_host, group.juggler_settings.checks[
                ctn.JugglerCheck.TASK_STATUS_CHANGED
            ].service
        )
        assert sorted(notification.send_to) == sorted([juggler_group_recipient, juggler_recipient])

        mm = mailman.Mailman()
        mm.send_juggler_notification([notification])

        assert mm.juggler_client.events.call_count == 1
        assert mm.juggler_client.events.call_args[1]['events'][0]['tags'] == [test_tag]

        notifications = mapping.Notification.objects()
        assert len(notifications) == 1

        notification = notifications[0]
        assert notification.sent
        assert notification.transport == ctn.Transport.JUGGLER
