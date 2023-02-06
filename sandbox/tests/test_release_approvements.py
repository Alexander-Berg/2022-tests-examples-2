import pytest
import mock
import json

from six import string_types

from sandbox.projects.release_machine.components.config_core import release_approvements
from sandbox.projects.release_machine.components.config_core import responsibility
from sandbox.projects.release_machine import release_approvements_formatter


@pytest.fixture
def simple_approvement_settings():
    return release_approvements.ReleaseApprovementsSettings(
        description="Simple release approvement settings",
        stages=[
            release_approvements.ReleaseApprovementStage("approver_1"),
            release_approvements.ReleaseApprovementStage("approver_2"),
            release_approvements.ReleaseApprovementStage("approver_3"),
        ],
    )


@pytest.fixture
def simple_approvement_with_responsible():
    return release_approvements.ReleaseApprovementsSettings(
        description="Simple release approvement settings that use Responsible object",
        stages=[
            release_approvements.ReleaseApprovementStage(responsibility.Responsible(
                abc=responsibility.Abc(schedule_slug="test_duty", service_name="test_service"),
                login="default_approver",
            ))
        ],
    )


@pytest.mark.parametrize('arg', [
    'simple_approvement_settings',
    'simple_approvement_with_responsible',
])
@mock.patch('sandbox.projects.release_machine.helpers.responsibility_helper.get_responsible_user_login')
def test_approvement_settings_common_characteristics(get_responsible_user_login_mock, arg, request):

    settings = request.getfixturevalue(arg)
    get_responsible_user_login_mock.return_value = "mocked_approver"

    ticket_key = "TEST"
    author = "test"
    groups = ["test"]

    settings_dict = release_approvements_formatter.release_approvements_settings_to_dict(
        settings=settings,
        ticket_key=ticket_key,
        author=author,
        groups=groups,
    )

    assert isinstance(settings_dict, dict)

    # Test OK API required params
    # https://wiki.yandex-team.ru/Intranet/OK/private-api/#sozdanieizapusksoglasovanija

    assert "type" in settings_dict
    assert "object_id" in settings_dict
    assert "text" in settings_dict
    assert "stages" in settings_dict
    assert "author" in settings_dict
    assert "groups" in settings_dict
    assert "is_parallel" in settings_dict

    assert isinstance(settings_dict["type"], string_types)
    assert isinstance(settings_dict["object_id"], string_types)
    assert isinstance(settings_dict["text"], string_types)
    assert isinstance(settings_dict["stages"], list)
    assert isinstance(settings_dict["author"], string_types)
    assert isinstance(settings_dict["groups"], list)
    assert isinstance(settings_dict["is_parallel"], bool)

    for stage_dict in settings_dict["stages"]:

        assert isinstance(stage_dict, dict)

        if "approver" in stage_dict:
            assert isinstance(stage_dict["approver"], string_types)
            continue

        assert "need_all" in stage_dict
        assert "stages" in stage_dict

        assert isinstance(stage_dict["need_all"], bool)
        assert isinstance(stage_dict["stages"], list)

    settings_json = release_approvements_formatter.release_approvements_settings_to_json(
        settings=settings,
        ticket_key=ticket_key,
        author=author,
        groups=groups,
    )

    assert isinstance(settings_json, string_types)
    json.loads(settings_json)
