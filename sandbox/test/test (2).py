import yatest.common

from sandbox.projects.geosearch.CommitFreshGeosearchData.lib import YaMakeUtils
from yalibrary.makelists_resources import ResourceModel


def test_current_resources():
    path = yatest.common.test_source_path('data/ya_make.txt')
    res = list(YaMakeUtils.get_current_resources(path))
    assert len(res) == 2
    assert res[0].resource_id == '2222222222'
    assert res[0].line_number == 10
    assert res[1].resource_id == '3333333333'
    assert res[1].line_number == 13


def test_replace_resources():
    path = yatest.common.test_source_path('data/ya_make.txt')
    res_path = yatest.common.output_path('ya_make.txt')
    model = ResourceModel(
        source=path,
        is_autoupdated=False,
        resource_id='2222222222',
        line_number=10,
    )
    YaMakeUtils.replace_resources(path, res_path, [(model, '2222222223')])
    return yatest.common.canonical_file(res_path, local=True)
