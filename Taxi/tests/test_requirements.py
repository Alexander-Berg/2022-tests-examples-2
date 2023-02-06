import os
import pytest
import re


def strip_comments_and_index(code):
    code = str(code)
    return re.sub(r'(#|-i\s).*', '', code)


def parse_line(line):
    print(line)
    assert '==' in line
    name_version = line.split('==')
    assert len(name_version) == 2
    return name_version


def parse_requirements_file(filepath):
    with open(filepath) as f:
        return dict(
            parse_line(line)
            for line in strip_comments_and_index(f.read()).strip().split()
        )


@pytest.fixture
def test_module_dir(request):
    fullname = str(request.fspath)
    return os.path.dirname(fullname)


def check_requirements(requirements, constraints):
    # this packages are not in pip freeze for some reason
    package_exceptions = ['keras', 'sqlalchemy', 'Pillow', 'setuptools']
    for package, version in requirements.items():
        if package in package_exceptions:
            continue
        assert package in constraints
        assert version == constraints[package], f'mismatch {package} version'


def test_requirements(test_module_dir):
    repo_dir = os.path.join(test_module_dir, '..', '..')

    contraints = parse_requirements_file(
        os.path.join(repo_dir, 'venv-constraints.txt'),
    )
    for requirements_path in (
            'taxi_pyml/requirements.txt',
            'projects/requirements.txt',
            'signalq_pyml/requirements.txt',
            'dev-requirements.txt',
            'taxi_ml_cxx/build_requirements.txt',
    ):
        requirements = parse_requirements_file(
            os.path.join(repo_dir, requirements_path),
        )
        check_requirements(requirements, contraints)
