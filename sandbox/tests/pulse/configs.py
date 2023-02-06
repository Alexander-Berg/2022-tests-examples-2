from sandbox.projects.sandbox_ci.pulse import config


class TestConfigs(object):
    def test_process_config(self, pulse_genisys_fixture, pulse_config_fixture):
        res = config.process_config(pulse_genisys_fixture)

        assert res == pulse_config_fixture
