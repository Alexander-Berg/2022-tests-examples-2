from sandbox.projects.paysys.tasks.monitorings.PaysysMonitoringsApplier import helpers


class TestLogToColoredHTML:
    def test_empty(self):
        assert helpers.log_to_colored_html(["\n"]) == '<html><body><pre><font color="black"></font>\n</pre></body></html>'

    def test_empty2(self):
        assert helpers.log_to_colored_html(["test\n"]) == '<html><body><pre><font color="black">test</font>\n</pre></body></html>'

    def test_info(self):
        assert helpers.log_to_colored_html(["2019-08-24 20:23:54.851 INFO Valid projects for apply: [configs.paysys]\n"]) == '<html><body><pre>2019-08-24 20:23:54.851 <font color="green"><b>INFO</b> Valid projects for apply: [configs.paysys]</font>\n</pre></body></html>'  # noqa

    def test_info_dangling(self):
        assert helpers.log_to_colored_html(["2019-08-24 20:23:54.851 INFO Valid projects for apply: [configs.paysys]\n", "    Traceback:\n"]) == '<html><body><pre>2019-08-24 20:23:54.851 <font color="green"><b>INFO</b> Valid projects for apply: [configs.paysys]</font>\n<font color="green">    Traceback:</font>\n</pre></body></html>'  # noqa

    def test_info_dangling2(self):
        assert helpers.log_to_colored_html(["2019-08-24 20:23:54.851 INFO Valid projects for apply: [configs.paysys]\n", "    Traceback: one two three four\n"]) == '<html><body><pre>2019-08-24 20:23:54.851 <font color="green"><b>INFO</b> Valid projects for apply: [configs.paysys]</font>\n<font color="green">    Traceback: one two three four</font>\n</pre></body></html>'  # noqa
