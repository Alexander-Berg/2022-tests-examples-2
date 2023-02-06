from sandbox.projects.common.build import BuildArcadiaProjectsForAll as bapfa


def test_arcadia_project_base_target_params():
    input = {
        'ya-bin': 12,
        'ymake': 13,
    }
    assert bapfa.BuildArcadiaProjectsForAll._gen_helpful_links(input) == [
        "<b>ya-bin</b>: <a href='https://sandbox.yandex-team.ru/task/12/view' target='_blank'>https://sandbox.yandex-team.ru/task/12/view</a>",
        "<b>ymake</b>: <a href='https://sandbox.yandex-team.ru/task/13/view' target='_blank'>https://sandbox.yandex-team.ru/task/13/view</a>",
    ]
