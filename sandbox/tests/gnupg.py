import sandbox.sandboxsdk.process as sdk_process
from sandbox.projects.common import gnupg


class TestGpgKey:
    PUBLIC_KEY = (
        "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"
        "SLsAIAAw==")

    SECRET_KEY = (
        "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")

    def test__gpg_key(self):
        task = type('FakeTask', (object, ), {
            'get_vault_data': lambda s, a, b: self.PUBLIC_KEY if b == 'pubring' else self.SECRET_KEY})()
        with gnupg.GpgKey(task, 'user', 'secring', 'pubring'):
            stdout, stderr = sdk_process.run_process(
                ['gpg', '--list-secret-keys'], outs_to_pipe=True).communicate()
            assert 'test key <test_key@yandex-team.ru>' in stdout.strip()
