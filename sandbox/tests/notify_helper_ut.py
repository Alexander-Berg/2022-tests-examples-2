# -*- coding: utf-8 -*-

import unittest
import mock

from sandbox.projects.common import string
from sandbox.projects.release_machine import notify_helper as nh


class CheckEmailNotification(unittest.TestCase):
    def testMailBody(self):
        task = mock.Mock()
        task.id = 111111
        task.author = "author"

        self.assertListEqual(
            string.dedent("""
                <html><body>Hello there!<br/>
                Here is very important message for you!<br/>
                Sandbox task: <a href="https://sandbox.yandex-team.ru/task/111111/view">111111</a>.<br/>
                Task author: <a href="https://staff.yandex-team.ru/author">author</a><br/>
                --<br/>
                Please do not hesitate to reply to this letter in case of bug reports or any other questions.<br/>
                Release Machine Team will guide you.<br/>
                Virtually yours, <a href="https://nda.ya.ru/3UW83a">Release Machine</a></body></html>
            """).strip().split("<br/>\n"),
            nh.mail_body(task, "Hello there!\nHere is very important message for you!").split("<br/>\n")
        )

    def testRecipients(self):
        self.assertSetEqual({"p", "q"}, set(nh.mail_recipients(["p", "q@yandex-team.ru"], humans_only=False)))
        task = mock.Mock()
        task.author = "q"
        self.assertSetEqual({"p", "q"}, set(nh.mail_recipients(["p"], humans_only=False, task=task)))
        self.assertSetEqual({"p", "q"}, set(nh.mail_recipients("p", humans_only=False, task=task)))
        self.assertSetEqual({"q"}, set(nh.mail_recipients([], humans_only=False, task=task)))
        self.assertSetEqual(
            {"p", "q"}, set(nh.mail_recipients({"p", "q@yandex-team.ru"}, humans_only=False, task=task))
        )
        with self.assertRaises(TypeError):
            nh.mail_recipients(None)


if __name__ == '__main__':
    unittest.main()
