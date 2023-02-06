import json
import difflib
import pytest
import os

from library.python import fs

from release_machine.public.config_templates import renderer


@pytest.fixture
def test_rmci_config_template_input():
    import yatest.common

    path = os.path.join(
        os.path.dirname(yatest.common.test_source_path()),
        "tests",
        "resources",
        "test_rmci_config_template_input.json",
    )

    return json.loads(fs.read_file_unicode(path))


@pytest.fixture
def test_rmci_config_template_output():
    import yatest.common

    path = os.path.join(
        os.path.dirname(yatest.common.test_source_path()),
        "tests",
        "resources",
        "test_rmci_config_template_output.py.out",
    )

    return fs.read_file_unicode(path)


def test_rmci_config_template(test_rmci_config_template_input, test_rmci_config_template_output):

    template_kwargs = test_rmci_config_template_input
    template_expected_result = test_rmci_config_template_output
    template_rendered_result = renderer.render_template("rmci_config_template.jinja2", **template_kwargs)

    assert template_rendered_result.strip(), "Render result is empty!"

    assert template_rendered_result == template_expected_result, "".join(difflib.context_diff(
        template_rendered_result.split(),
        template_expected_result.split(),
        fromfile="rendered",
        tofile="expected",
    ))
