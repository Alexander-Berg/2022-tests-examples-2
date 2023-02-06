import sandbox.common.types.task as ctt
import sandbox.common.types.notification as ctn

import yasandbox.database.mapping
import yasandbox.manager.tests as manager_tests


class TestTaskStatusNotifierTrigger(object):
    def test__triggers_for_robots(self, task_manager, tasks_dir, notification_trigger_controller, user_controller):
        statuses = [ctt.Status.SUCCESS]
        transport = ctn.Transport.EMAIL
        user_controller.validated("real_user")
        real_user = user_controller.valid("real_user")
        user_controller.validated("robot_user", True)
        robot_user = user_controller.valid("robot_user")

        task = manager_tests._create_task(task_manager, "UNIT_TEST")
        yasandbox.database.mapping.Task.objects(id=task.id).update_one(
            set__notifications=[
                yasandbox.database.mapping.Task.Notification(
                    statuses=statuses,
                    transport=transport,
                    recipients=[real_user.login, robot_user.login, "user@host"]
                )
            ]
        )
        notification_trigger_controller.create_from_task(task.id)
        triggers = list(notification_trigger_controller.Model.objects(source=task.id))
        assert len(triggers) == 1
        assert triggers[0].statuses == statuses
        assert triggers[0].transport == transport
        assert triggers[0].recipients == [real_user.login, "user"]

        task = manager_tests._create_task(task_manager, "UNIT_TEST")
        yasandbox.database.mapping.Task.objects(id=task.id).update_one(
            set__notifications=[
                yasandbox.database.mapping.Task.Notification(
                    statuses=statuses,
                    transport=transport,
                    recipients=[robot_user.login]
                )
            ]
        )
        notification_trigger_controller.create_from_task(task.id)
        triggers = list(notification_trigger_controller.Model.objects(source=task.id))
        assert len(triggers) == 0

    def test__group_expansion_with_empty_email(
        self, task_manager, tasks_dir, notification_trigger_controller, user_controller, group_controller
    ):
        users = ["white", "whitewhite"]
        for user in users:
            user_controller.validated(user)
        group = group_controller.create(group_controller.Model(name="GROUP_WITH_EMPTY_EMAIL", users=users))

        task = manager_tests._create_task(task_manager, "UNIT_TEST")
        yasandbox.database.mapping.Task.objects(id=task.id).update_one(
            set__notifications=[
                yasandbox.database.mapping.Task.Notification(
                    statuses=[ctt.Status.SUCCESS],
                    transport=ctn.Transport.EMAIL,
                    recipients=[group.name]
                )
            ]
        )
        notification_trigger_controller.create_from_task(task.id)
        trigger = next(iter(notification_trigger_controller.Model.objects(source=task.id)), None)
        assert trigger and trigger.recipients == [group.name]

    def _create_telegram_login(self, login):
        return login + "_telegram_login"

    def _create_user_with_telegram_login(self, login, user_controller):
        user_controller.validated(login)
        user = user_controller.get(login)
        user.telegram_login = self._create_telegram_login(login)
        user.save()

    def test__notification_trigger(
        self, notification_controller, task_manager,
        notification_trigger_controller, user_controller, group_controller
    ):
        user_logins = ["group_user1", "group_user_2", "user3", "user_4"]
        for login in user_logins:
            self._create_user_with_telegram_login(login, user_controller)
        group = group_controller.create(group_controller.Model(name="TEST_GROUP", users=user_logins[:2]))
        telegram_logins = ["user5", "user_6"]
        task = manager_tests._create_task(task_manager, "UNIT_TEST")
        notification_trigger_controller.append(
            task.id, notification_controller.notification(
                ctn.Transport.TELEGRAM,
                ["SUCCESS"],
                [group.name] + user_logins[2:] + list(map(self._create_telegram_login, telegram_logins))
            )
        )
        trigers = list(notification_trigger_controller.Model.objects())
        assert len(trigers) == 1
        trigger = trigers[0]
        assert trigger.transport == ctn.Transport.TELEGRAM
        assert trigger.source == task.id
        assert sorted(trigger.recipients) == sorted(map(self._create_telegram_login, user_logins + telegram_logins))

    def test__notification_trigger_with_juggler(
        self, notification_controller, task_manager,
        notification_trigger_controller, user_controller, group_controller
    ):
        user_logins = ["group_user1", "group_user_2"]
        for login in user_logins:
            self._create_user_with_telegram_login(login, user_controller)
        group = group_controller.create(
            group_controller.Model(
                name="TEST_GROUP", users=user_logins,
                juggler_settings=group_controller.Model.JugglerSettings(
                    default_host="test.host", default_service="test_service"
                )
            )
        )

        juggler_recipient = "host=test2.host&service=test2_service"

        group2 = group_controller.create(group_controller.Model(name="TEST_GROUP_2", users=user_logins))
        task = manager_tests._create_task(task_manager, "UNIT_TEST")
        test_tag = "test_tag"
        notification_trigger_controller.append(
            task.id, notification_controller.notification(
                ctn.Transport.JUGGLER,
                ["SUCCESS"],
                [group.name, group2.name] + [juggler_recipient],
                check_status=ctn.JugglerStatus.OK,
                juggler_tags=[test_tag]
            )
        )
        trigers = list(notification_trigger_controller.Model.objects())
        assert len(trigers) == 1
        trigger = trigers[0]

        assert trigger.transport == ctn.Transport.JUGGLER
        assert trigger.check_status == ctn.JugglerStatus.OK
        assert trigger.juggler_tags == [test_tag]
        assert trigger.source == task.id
        assert sorted(trigger.recipients) == sorted([group.name] + [juggler_recipient])

        juggler_group_recipient = "host=test.host&service=test_service"

        assert (
            sorted(notification_controller.juggler_expanded_recipients(
                trigger.recipients, ctn.JugglerCheck.TASK_STATUS_CHANGED)
            ) == sorted([juggler_group_recipient, juggler_recipient])
        )
