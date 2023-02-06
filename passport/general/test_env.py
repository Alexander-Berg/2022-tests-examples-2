from passport.backend.qa.autotests.base.settings.common import DEFAULT_USER_AGENT
from passport.backend.utils.common import random_ipv6


class TestEnv:
    def __init__(self, defaults):
        for attr in ['_env', '_stack']:
            super().__setattr__(attr, None)
        super().__setattr__('defaults', defaults)

        self.reset()

    def reset(self):
        self._env = self._build_env()
        self._stack = list()

    def __getattr__(self, attr):
        if attr not in self.defaults:
            return super().__getattr__(attr)
        return self._env[attr]

    def __setattr__(self, attr, value):
        if attr not in self.defaults:
            return super().__setattr__(attr, value)
        self._env[attr] = value

    def __enter__(self):
        self.push()
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.pop()

    def push(self):
        self._envs.append(self._env)
        self._env = dict(self._env)

    def pop(self):
        self._env = self._envs.pop()

    def _build_env(self):
        env = dict()
        for attr, default in self.defaults.items():
            if callable(default):
                default = default()
            env[attr] = default
        return env


test_env = TestEnv(
    defaults=dict(
        user_agent=DEFAULT_USER_AGENT,
        user_ip=random_ipv6,
    ),
)
