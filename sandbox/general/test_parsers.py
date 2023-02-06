import pytest

from sandbox.projects.ads.infra.ads_infra_release_builder.lib import parse_svn_revision, parse_project


def test_parse_svn_revision_trunk():
    assert parse_svn_revision("r123") == "123"


def test_parse_svn_revision_release_branch():
    assert parse_svn_revision("releases/logos/r123") == "123"


@pytest.mark.parametrize("revision", [
    "abc",
    "abcr103",
    "r123a",
    "releases/logos/r123/1",
    "releases/logos/r123a",
    "trunk/releases/logos/r123/1"
])
def test_parse_svn_revision_incorrect_raises(revision):
    with pytest.raises(RuntimeError):
        parse_svn_revision(revision)


@pytest.mark.parametrize("binary,project", [
    ("logos/projects/ads/graph/bin/logos_tool", "ads"),
    ("logos/projects/statkey/graph/bin/logos_tool", "statkey")
])
def test_parse_project(binary, project):
    assert parse_project(binary) == project
