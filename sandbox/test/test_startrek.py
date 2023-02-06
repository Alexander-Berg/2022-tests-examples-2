import textwrap

from sandbox.projects.yabs.qa.tasks.YabsCollectTestenvData.startrek import issue_description
from sandbox.projects.yabs.qa.tasks.YabsCollectTestenvData.resources import ResourceInfo


def test_issue_description_check():
    expected_text = textwrap.dedent(u'''
        Resource check [6642n](https://testenv.yandex-team.ru/?screen=timeline&database=6642n) has failed due to failure of the following tasks:
        https://sandbox.yandex-team.ru/task/1366363193/view
        https://sandbox.yandex-team.ru/task/1366363194/view

        Resources:
        [YABS_CS_INPUT_SPEC #3287279779](https://sandbox.yandex-team.ru/resource/3287279779/view)
        [YABS_CS_SETTINGS_ARCHIVE #3287271209](https://sandbox.yandex-team.ru/resource/3287271209/view)
    ''').lstrip('\n')
    assert issue_description(
        '6642n',
        [1366363193, 1366363194],
        [
            ResourceInfo('YABS_CS_INPUT_SPEC', 3287279779),
            ResourceInfo('YABS_CS_SETTINGS_ARCHIVE', 3287271209),
        ],
    ) == expected_text


def test_issue_description_switching():
    expected_text = textwrap.dedent(u'''
        Resource switching has failed, please, check [bste](https://bste.in.yandex-team.ru/) for new failures in switching.

        Resources:
        [YABS_CS_INPUT_SPEC #3287279779](https://sandbox.yandex-team.ru/resource/3287279779/view)
        [YABS_CS_SETTINGS_ARCHIVE #3287271209](https://sandbox.yandex-team.ru/resource/3287271209/view)
    ''').lstrip('\n')
    assert issue_description(
        '6642n',
        [],
        [
            ResourceInfo('YABS_CS_INPUT_SPEC', 3287279779),
            ResourceInfo('YABS_CS_SETTINGS_ARCHIVE', 3287271209),
        ],
    ) == expected_text
