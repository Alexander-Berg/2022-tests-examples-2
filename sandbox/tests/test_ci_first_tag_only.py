from sandbox.projects.release_machine.components.config_core.jg.lib.conditions import ci_conditions


def test_ci_first_tag_only():

    condition_body = "(not_null(context.version_info.minor, `0`)) == `0`"

    assert str(ci_conditions.CI_FIRST_TAG_ONLY) == "({})".format(condition_body)
    assert (
        ci_conditions.CI_FIRST_TAG_ONLY.to_dict()[ci_conditions.CICondition.IF] == "${{{}}}".format(condition_body)
    )
