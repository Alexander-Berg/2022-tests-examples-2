import os
import sys
import shutil
import itertools as it
import subprocess as sp
import collections

import pytest

import yatest.common
import yalibrary.makelists

FAIL_MESSAGE = (
    "Tasks tests have failed, open `logsdir/stderr` for details.\n"
    "Read more on Sandbox tasks tests at https://wiki.yandex-team.ru/sandbox/tasks/tests"
)

LIBRARY_NODES = ("LIBRARY", "PY2_LIBRARY", "PY23_LIBRARY", "PY3_LIBRARY")
TEST_NODES = ("PY2TEST", "PY23_TEST", "PY3TEST")
BINARY_NODES = TEST_NODES + ("PY3_LIBRARY", "PY2_PROGRAM", "PY3_PROGRAM", "SANDBOX_PY3_TASK")

PROJECT_SOURCES_FIXTURE = "project_sources"


def filter_by_extension(
    path, include=None, exclude=None,
    files_only=True, root_relative=True, recursive=True,
):
    """
    Scan `path` for files and directories that satisfy given conditions
    and yield them one by one, alphabetically sorted

    :param path: which directory to scan
    :param include: list of desired extensions (for example, [".py", ".cpp"]). May be omitted
    :param exclude:  list of undesired extensions (for example, [".make"]) of file names if is not started with '.'. May be omitted
    :param files_only: skip directories
    :param root_relative: all paths will be relative to `path`
    :param recursive: descend into subdirectories, and their subdirectories, and...
    """

    assert any((include, exclude))

    def iterator():
        if recursive:
            for root, dirs, files in os.walk(path):
                for item_ in it.chain(dirs, files):
                    yield os.path.join(root, item_)
        else:
            for item_ in os.listdir(path):
                yield os.path.join(path, item_)

    for item in iterator():
        match = (
            (True if not include else any(item.endswith(ext) for ext in include)) and not
            (False if not exclude else any(
                item.endswith(ext) if ext.startswith(".") else os.path.basename(item) == ext
                for ext in exclude
            ))
        )
        skip = files_only and not os.path.isfile(item) or os.path.islink(item)
        if match and not skip:
            yield item if not root_relative else os.path.relpath(item, path)


def pytest_generate_tests(metafunc):
    def generate_files_fixture(fixture_name, include=None, exclude=None):
        filenames = filter_by_extension(projects_dir(), include=include, exclude=exclude)
        projects = collections.defaultdict(set)
        for filename in filenames:
            try:
                project, _ = filename.split("/", 1)
            except ValueError:
                project = "projects"
            projects[project].add(filename)

        unpacked = sorted(projects.items())
        metafunc.parametrize(
            fixture_name,
            argvalues=[value for __, value in unpacked],
            ids=[key for key, ___ in unpacked],
        )

    if PROJECT_SOURCES_FIXTURE in metafunc.fixturenames:
        generate_files_fixture(PROJECT_SOURCES_FIXTURE, include=[".py"])


@pytest.fixture()
def project_sources(request):
    return request.param


@pytest.fixture(scope="session")
def binary():
    return yatest.common.binary_path(os.path.join("sandbox", "tasks", "tests", "bin", "test-tasks"))


def arcadia_dir():
    return yatest.common.source_path()


def projects_dir():
    return os.path.join(arcadia_dir(), "sandbox", "projects")


@pytest.fixture(scope="session", name="projects_dir")
def projects_dir_fixture():
    return projects_dir()


@pytest.fixture(scope="session")
def extracted_arcadia_dir(binary):
    path = yatest.common.ram_drive_path() or os.getcwd()
    target_dir = os.path.join(path, "arcadia")
    sp.check_call([binary, "extract", "--target", target_dir])
    yield target_dir
    shutil.rmtree(target_dir)


@pytest.fixture(scope="session")
def extracted_projects_dir(extracted_arcadia_dir):
    return os.path.join(extracted_arcadia_dir, "sandbox", "projects")


@pytest.fixture(scope="session")
def sources_in_binary(extracted_projects_dir):
    return set(filter_by_extension(extracted_projects_dir, include=[".py"]))


@pytest.fixture(scope="session")
def whitelisted_sources():
    return {
        "autocheck/yql/stages.py",
        "sandbox/taskboxer/isolated/bin/__init__.py",
        "metrika/admins/birthday_reminder/binary/birthday_reminder/__init__.py",
        "metrika/admins/dicts/binary/dicts/__init__.py",
        "metrika/admins/dicts_http/binary/dicts_http/__init__.py",
        "metrika/admins/dicts_yt/bin/dicts_yt/__init__.py",
        "metrika/admins/share_keys_xml/binary/share_keys_xml/__init__.py",
    }


@pytest.fixture(scope="session")
def excluded_sources(projects_dir):
    exclusions = set()
    arcadia_dir = os.path.dirname(os.path.dirname(projects_dir))
    for root, _, _ in os.walk(projects_dir):
        source = os.path.join(root, yalibrary.makelists.MAKELIST_NAME)
        if not os.path.exists(source):
            continue

        build_list = yalibrary.makelists.from_file(source)
        nodes = filter(
            None, (
                build_list.find_nodes(node_name)
                for node_name in BINARY_NODES + LIBRARY_NODES
            )
        )
        if not nodes:
            continue

        nodes = nodes[0][0]

        # certain ya.make files point to directories other than that they belong to, so...
        real_path_prefix = root
        srcdir_macros = nodes.find_nodes("SRCDIR")
        if srcdir_macros:
            relative_path = srcdir_macros[0].get_values()[0].name
            real_path_prefix = os.path.join(arcadia_dir, relative_path)

        inside_namespace = False
        for macro in ("PY_SRCS", "TEST_SRCS"):
            desired = nodes.find_nodes(macro)
            if not desired:
                continue

            values_it = iter(desired[0].get_values())
            for value in values_it:
                if value.name in ("TOP_LEVEL", "NAMESPACE") or not value.name.endswith(".py"):
                    inside_namespace = True
                    if value.name == "NAMESPACE":
                        values_it.next()
                    continue

                if inside_namespace or nodes.name in BINARY_NODES:
                    exclusions.add(
                        os.path.relpath(
                            os.path.join(real_path_prefix, value.name),
                            projects_dir
                        )
                    )

    return exclusions


@pytest.fixture(scope="session")
def covered_sources(sources_in_binary, whitelisted_sources, excluded_sources):
    return sources_in_binary | whitelisted_sources | excluded_sources


class TestTasks(object):
    def test_project_sources_are_included_in_tasks_binary(self, covered_sources, project_sources):
        difference = project_sources - covered_sources
        if difference:
            message = "{}\n{}\n\t{}".format(
                "You must add ALL sources to PEERDIR of sandbox/projects or its inner directory "
                "that is reachable by PEERDIR from sandbox/projects",
                FAIL_MESSAGE,
                "\n\t".join(sorted(difference))
            )
            pytest.fail(message)

    def test_tasks(self, binary, extracted_arcadia_dir):
        try:
            sp.check_call(
                [binary, "test", "--target", extracted_arcadia_dir, "-v"], stdout=sys.stderr, stderr=sp.STDOUT
            )
        except sp.CalledProcessError as er:
            message = "Error on subprocess call: {}\n{}".format(er, FAIL_MESSAGE)
            pytest.fail(message)
