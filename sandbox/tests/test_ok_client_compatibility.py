import typeguard
import mock

from library.python.ok_client import CreateApprovementRequest
from sandbox.projects.release_machine.components.config_core import release_approvements
from sandbox.projects.release_machine.components.config_core import responsibility
from sandbox.projects.release_machine import release_approvements_formatter


def check_type(name, value, expected_type):
    try:
        typeguard.check_type(name, value, expected_type)
    except TypeError:
        return False
    return True


@mock.patch('sandbox.projects.release_machine.helpers.responsibility_helper.get_responsible_user_login')
def test_rm_approvement_settings_compatible_with_ok_approvement_request(get_responsible_user_login_mock):

    get_responsible_user_login_mock.return_value = "responsible_approver"

    settings = release_approvements.ReleaseApprovementsSettings(
        description="Lorem ipsum",
        stages=[
            "approver_0",
            responsibility.Responsible(
                abc=responsibility.Abc(schedule_slug="test_duty", service_name="test_service"),
                login="default_approver",
            ),
            release_approvements.ReleaseApprovementStage(
                stage="approver_1",
            ),
            release_approvements.ReleaseApprovementStage(
                stage=[
                    release_approvements.ReleaseApprovementStage("approver_2"),
                    release_approvements.ReleaseApprovementStage("approver_3"),
                    release_approvements.ReleaseApprovementStage("approver_4"),
                    release_approvements.ReleaseApprovementStage(
                        responsibility.Responsible(
                            abc=responsibility.Abc(schedule_slug="test_duty_other", service_name="test_service_other"),
                            login="default_approver_2",
                        ),
                    ),
                ],
            ),
        ],
    )

    settings_dict = release_approvements_formatter.release_approvements_settings_to_dict(
        settings=settings,
        ticket_key="TICKET-1",
        author="robot-srch-releaser",
    )

    for field_name, field_type in CreateApprovementRequest.__annotations__.items():

        assert field_name in settings_dict, "{} not found in release approvement settings dict".format(field_name)

        value = settings_dict[field_name]

        assert check_type(
            field_name,
            value,
            field_type,
        ), (
            "'{field_name}' of unexpected type found in release approvement settings dict:\n  "
            "{value} (of type {value_type}) is not a valid instance of type {expected_type}".format(
                field_name=field_name,
                value=value,
                value_type=type(value),
                expected_type=field_type,
            )
        )
