import os
from typing import Dict
from typing import NamedTuple
from typing import Optional

import pytest

import python_version


@pytest.mark.parametrize('cli_options', [[], ['--bump']])
def test_missed_file(tmpdir, teamcity_report_problems, cli_options):
    filename = os.path.join(tmpdir, 'non_existent_version.py')
    with pytest.raises(SystemExit) as wrapped_exc:
        python_version.main(cli_options + [filename])
    assert wrapped_exc.value.code == 2
    assert teamcity_report_problems.calls == [
        {
            'description': 'python version file not found: ' + filename,
            'identity': None,
        },
    ]


@pytest.mark.parametrize(
    'contents',
    [
        'version = 1',
        '__version__ = \'10.2hotfix3\'',
        '  __version = \'1.5\'',
        '__version__    = \'1.5\'',
        '__version__    =     \'1.5\'',
        '__version__ =     \'1.5\'',
        '__version__ = \'1.5.\'',
        '__version__ = \'.1.5\'',
    ],
)
def test_print_no_version(capsys, tmpdir, contents):
    filename = os.path.join(tmpdir, 'version.py')
    with open(filename, 'w') as fp:
        fp.write(contents)
    python_version.main([filename])
    captured = capsys.readouterr()
    assert captured.out == '_no_version\n'


@pytest.mark.parametrize(
    'contents',
    [
        'version = 1',
        '__version__ = \'10.2hotfix3\'',
        '  __version = \'1.5\'',
        '__version__    = \'1.5\'',
        '__version__    =     \'1.5\'',
        '__version__ =     \'1.5\'',
        '__version__ = \'1.5.\'',
        '__version__ = \'.1.5\'',
    ],
)
def test_bump_no_version(tmpdir, teamcity_report_problems, contents):
    filename = os.path.join(tmpdir, 'version.py')
    with open(filename, 'w') as fp:
        fp.write(contents)
    with pytest.raises(SystemExit) as wrapped_exc:
        python_version.main(['--bump', filename])
    assert wrapped_exc.value.code == 2
    assert teamcity_report_problems.calls == [
        {
            'description': 'no __version__ found in ' + filename,
            'identity': None,
        },
    ]


class BumpParams(NamedTuple):
    source_contents: str
    expected_contents: str
    teamcity_messages: Optional[Dict[str, str]] = None


@pytest.mark.parametrize(
    'params',
    [
        pytest.param(
            BumpParams(
                source_contents='\n\n__version__ = \'0\'\n',
                expected_contents='\n\n__version__ = \'1\'\n',
                teamcity_messages={'buildNumber': '\'1\''},
            ),
            id='bump group1',
        ),
        pytest.param(
            BumpParams(
                source_contents='\n\n__version__ = \'1.7\'\n',
                expected_contents='\n\n__version__ = \'1.8\'\n',
                teamcity_messages={'buildNumber': '\'1.8\''},
            ),
            id='bump group2',
        ),
        pytest.param(
            BumpParams(
                source_contents='\n\n__version__ = \'1.7.100\'\n',
                expected_contents='\n\n__version__ = \'1.7.101\'\n',
                teamcity_messages={'buildNumber': '\'1.7.101\''},
            ),
            id='bump group3',
        ),
        pytest.param(
            BumpParams(
                source_contents='__version__ = \'1.7.100\'',
                expected_contents='__version__ = \'1.7.101\'',
                teamcity_messages={'buildNumber': '\'1.7.101\''},
            ),
            id='save end of lines',
        ),
        pytest.param(
            BumpParams(
                source_contents='__version__ = \'1.7.100\'\n',
                expected_contents='__version__ = \'1.7.101\'\n',
                teamcity_messages={'buildNumber': '\'1.7.101\''},
            ),
            id='bump save-eol',
        ),
        pytest.param(
            BumpParams(
                source_contents='__version__ = \'1.7.100\'\n\n',
                expected_contents='__version__ = \'1.7.101\'\n\n',
                teamcity_messages={'buildNumber': '\'1.7.101\''},
            ),
            id='bump save-eol',
        ),
        pytest.param(
            BumpParams(
                source_contents='\n\n__version__ = \'1.0\'\n'
                '__version__ = \'2.0\'\n',
                expected_contents='\n\n__version__ = \'1.1\'\n'
                '__version__ = \'2.0\'\n',
                teamcity_messages={'buildNumber': '\'1.1\''},
            ),
            id='bump first',
        ),
    ],
)
def test_bump_version(tmpdir, teamcity_messages, params):
    filename = os.path.join(tmpdir, 'version.py')
    with open(filename, 'w') as fp:
        fp.write(params.source_contents)
    python_version.main(['--bump', filename])

    with open(filename) as fp:
        new_contents = fp.read()

    assert params.expected_contents == new_contents

    tc_messages = params.teamcity_messages or {}
    assert tc_messages == {
        call['message_name']: call['value'] for call in teamcity_messages.calls
    }


class PrintParams(NamedTuple):
    source_contents: str
    expected_version: str


@pytest.mark.parametrize(
    'params',
    [
        pytest.param(
            PrintParams(
                source_contents='\n\n__version__ = \'0\'\n',
                expected_version='0',
            ),
            id='print group1',
        ),
        pytest.param(
            PrintParams(
                source_contents='\n\n__version__ = \'1.7\'\n',
                expected_version='1.7',
            ),
            id='print group2',
        ),
        pytest.param(
            PrintParams(
                source_contents='\n\n__version__ = \'1.7.100\'\n',
                expected_version='1.7.100',
            ),
            id='print group3',
        ),
        pytest.param(
            PrintParams(
                source_contents='\n\n__version__ = \'1.0\'\n'
                '__version__ = \'2.0\'\n',
                expected_version='1.0',
            ),
            id='print first',
        ),
    ],
)
def test_print_version(tmpdir, capsys, params):
    filename = os.path.join(tmpdir, 'version.py')
    with open(filename, 'w') as fp:
        fp.write(params.source_contents)
    python_version.main([filename])
    captured = capsys.readouterr()
    assert captured.out == params.expected_version + '\n'
