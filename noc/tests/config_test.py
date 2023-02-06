from rtnmgr_agent.config import Config


class TestConfig:
    def setup(self):
        self.config = Config("configs/rtnmgr-agent.cfg", "")

    def test_value(self):
        assert "42" == self.config.DO_NOT_REMOVE_TEST_VARIABLE
        assert "127.0.0.2" == self.config.get("NONE_VALUE", "127.0.0.2")
