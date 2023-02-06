import mock


class FakeConfig(object):
    def __init__(self, config, values, config_getter=None):
        self.patches = []
        self.patches.append(
            mock.patch.dict(config, values)
        )
        if config_getter:
            new_config = dict(config)
            new_config.update(values)
            self.patches.append(mock.patch(config_getter, return_value=new_config))

    def start(self):
        for patch in self.patches:
            patch.start()

    def stop(self):
        for patch in reversed(self.patches):
            patch.stop()

    def __enter__(self):
        self.start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
