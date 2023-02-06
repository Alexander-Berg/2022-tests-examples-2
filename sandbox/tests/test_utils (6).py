from sandbox.projects.yabs.SysConstLifetime.sys_const.utils import (
    camel_to_snake, build_arc_search_link
)


def test_camel_to_snake():
    const = 'SomeConstantName'
    result = camel_to_snake(const)
    expected = 'some-constant-name'
    assert result == expected


def test_build_arc_search_link():
    const = 'SomeConstantName'
    result = build_arc_search_link(const)
    expected = 'https://a.yandex-team.ru/search?search=(SomeConstantName%7Csome-constant-name),%5Eyabs%2F.*,jC,arcadia,%5Eyabs%2Fqa%2Foneshots%2F.*,200&repo=arc'
    assert result == expected
