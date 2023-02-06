import contextlib

import pylint.testutils


class FuzzyMessageMatchCheckerTestcase(pylint.testutils.CheckerTestCase):
    @contextlib.contextmanager
    def assertFuzzyAddsMessages(self, *messages):
        """Assert that given method adds messages, ignoring messages' arguments.

        Acts exactly as assertAddsMessages, but injects None as arguments in
        each message (both given and raised ones), to enable ignoring the
        arguments and make assertion of messages creation less tedious.
        """
        messages = [message._replace(args=None) for message in messages]
        yield
        got = self.linter.release_messages()
        got = [message._replace(args=None) for message in got]
        no_msg = "No message."
        expected = "\n".join(repr(m) for m in messages) or no_msg
        got_str = "\n".join(repr(m) for m in got) or no_msg
        msg = (
            "Expected messages did not match actual.\n"
            f"\nExpected:\n{expected}\n\nGot:\n{got_str}\n"
        )
        assert got == list(messages), msg
