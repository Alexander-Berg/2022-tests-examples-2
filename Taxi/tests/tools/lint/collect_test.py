import os
import tempfile

import pytest
import pylint.reporters

from tools.lint.collect import Run, MessageWithNode


@pytest.mark.slow('FS access')
def test_reporter_injects_messages_with_node():
    reporter = pylint.reporters.CollectingReporter()

    code = """list = 1 # переопределяем built-in"""
    file = tempfile.NamedTemporaryFile('w', delete=False)
    with file as f:
        f.write(code)
    Run([file.name], reporter=reporter, do_exit=False)
    assert reporter.messages
    assert all(
        isinstance(message, MessageWithNode)
        for message in reporter.messages
    )
    os.remove(file.name)
