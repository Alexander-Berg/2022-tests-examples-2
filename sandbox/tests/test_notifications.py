import pytest

from sandbox.projects.release_machine.components.config_core import notifications


@pytest.mark.parametrize("notification", [
    notifications.Notification(
        event_type="NewBranch",
        chat_name="test",
        conditions=notifications.NotificationCondition(
            conditions=[
                notifications.NotificationConditionItem(
                    field="task_data.status",
                    operator="TEXT_EXACTLY_IS",
                    value="SUCCESS",
                ),
                notifications.NotificationConditionItem(
                    field="task_data.status",
                    operator="TEXT_EXACTLY_IS",
                    value="FAILURE",
                ),
            ],
            join_strategy="OR",
        ),
    ),
    notifications.Notification(
        event_type="NewTag",
        chat_name="test",
        message_template_file="notifications/new_tag.html",
        conditions=notifications.NotificationCondition(
            conditions=[
                notifications.NotificationConditionItem(
                    field="task_data.status",
                    operator="TEXT_EXACTLY_IS",
                    value="SUCCESS",
                ),
                notifications.NotificationConditionItem(
                    field="new_tag_data.tag_number",
                    operator="EQ",
                    value="1",
                ),
            ],
            join_strategy="AND",
        ),
    ),
])
def test__notification_config_converts_to_protobuf_correctly(notification):
    try:
        notification.to_protobuf()
    except Exception as e:
        raise AssertionError("to_protobuf method failed. Original error: {}".format(e))
