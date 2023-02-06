from taxi_buildagent.tools.vcs import git_repo


def test_group_output_by_submodules():
    # pylint: disable=protected-access
    result = git_repo.SubmodulesGroup._group_output_by_submodules(
        'Entering \'submodule\'\n'
        'aaa\n'
        'bbb\n'
        'Entering \'empty\'\n'
        'Entering \'another-submodule\'\n'
        'ccc\n',
    )
    assert result == {
        'submodule': ['aaa', 'bbb'],
        'empty': [''],
        'another-submodule': ['ccc'],
    }
