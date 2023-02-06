import os
import functools

from sandbox import sdk2
from sandbox.sdk2.helpers.process import subprocess as sp


class TestSSHKey(object):
    SSH_KEY = "-----BEGIN RSA PRIVATE KEY-----\n"\
              "MIIEpAIBAAKCAQEA1WGiKiFb3zgt+7YLeK8wqJ4SGUyu2Jqyy3MfHMdHbOG2Y3db\n"\
              "ruC90Cs7Yqaz54N3uNCNR/cJVoW8Wggz3Ow50ke/U1JFrLPCe3il3cJQISySpvS9\n"\
              "XP5AHib0FVd57D6lIDAec2Ts8uJ3mlxX/jbRIC6qOJYkfnewLy+D2COwppUztayi\n"\
              "tY/5eoyS4m4IQtaK0l5Zi9PlM0ITGoI5F/8X2NAuNL1btRCsjwkyGC4lM52edCxH\n"\
              "ieq4u7sE5kCTuva/IUXKnyjBKpli5XYWSHnpT2LfoAlFr+OYSEvMaoiSAqxHMzWc\n"\
              "LUgAQyiYyVlJeTdp8WtqtzlkaeU3PsBvKJyLXQIDAQABAoIBAQCrItz+0TZv9wza\n"\
              "Po1Aw7FQ60Y0yE3LJ3eSuMgROrrMVtMDP21m+pUB6kp8upq7abORpKJLP5RbsnL3\n"\
              "+nAuFb/iKO0IFIoREzM99+t/yiKeGLOd99gQR1KBXFiS7U+57Bxfjng9sIph2sR2\n"\
              "Ju3j028yUnrvW2v1imTh00f5B9bcIoMCqve8deWvhYgL1odY5jznIjrLjPP5cnCK\n"\
              "My3Sk3oEKbxAY0CClLeRsESyqPmbEKX6hAIrOzTDTNVlVmP3nbj1z62jYhsN2xOY\n"\
              "NyBV0+ZUpqsw7rAotcRPdZWB77h3Sm2EMEmOXsTnVqqNEfecmgzSRhAT4ShtkpyY\n"\
              "ojb4WoVBAoGBAPBtpMjsOBMKVXtIcGUwuH0hbN8u3JIzB11Cq1fu5M/o6Hal3AEq\n"\
              "LkfwRtyzxA7b08CD1p5bKTvemoX7m9vBc5G7rxSc5JfvYkCDj3WPvsrWBhFDihOT\n"\
              "tPLe5n4u2+1KGBiyZIgEFSVyeUWWZNAfYEdnUiaEGIYGjHaFLLAhQHsJAoGBAOMz\n"\
              "i7OG8QumvRv6brGO6OiA6kye/bJzJnMJfXBNz0h5gYh/1ULJC249/njLuk1W+BUT\n"\
              "hMssGX8hhQSq8Gsb/yMN5fIp0MI9v1L+K5cuPmVlDETwX6tAJVku8PSygdIR0gXG\n"\
              "CU3pUP8ecErVOclrDdyqo39bOb7S9lwCBpzQ5p61AoGAIWUpYVsmQsbJrtEWA4gr\n"\
              "5/2PkMSCkLAT0sli4VjmYVaZi3loQKUqPoXKYfd6QRIZrIDje6Vv6cf2sKuNL44E\n"\
              "TnbCT9unCM+QVyOu9oZb2vK1bwpxkFyQ4rdBTr+VfrUu+ac1vYrLoSLwY1ELebkR\n"\
              "93kLeRwaB+u68O94kJJd0XkCgYBkCllUJnHS2ItiW2YMRsnlPoZsUIGS5sMiWiZi\n"\
              "odBIsD/KE8eajZ274A5BsCsLTOUVmq+ZKoTbhq3kfUQ5VW2FSORcOe9S6A9rgsE8\n"\
              "4z7UNKcvX8wwQqFvYIz2ofcpwXEB285TAQ4KF6QIP1UfjEThSj2NoWSO0qNppfa1\n"\
              "bAJwFQKBgQCaYx3JM0AbtfxQxn3jI6NvCESUb2VNF9BirNOh0YJN+12ZrXcjIMng\n"\
              "Wo9pcdjrTxL7q2TCTx8oqP9LyFx8HjjNNRGdqq1C/JW7C0wdYmCpmyVzTzxiXoU2\n"\
              "l3MPQpc82S9AX+ETUFy7z8d46Q7hoFL9f+y96Lshh6yMlYhk3yr/ag==\n"\
              "-----END RSA PRIVATE KEY-----"

    SSH_KEY_FINGERPRINTS = [
        "2048 e2:8a:dc:1c:57:45:ba:83:fc:1e:1f:8e:6d:b3:ed:24 (stdin) (RSA)",
        "2048 SHA256:1r9rHzJT44Au0V1i43qAduSsXpOotOw9gwPtX67Twq4 (stdin) (RSA)",
    ]

    def _check_ssh_key_is_available(self):
        stdout, _ = sp.Popen(["ssh-add", "-l"], stdout=sp.PIPE, stderr=None).communicate()
        assert stdout.strip() in self.SSH_KEY_FINGERPRINTS

    def test__ssh_key(self, request, monkeypatch):
        task = type("FakeTask", (object,), {"get_vault_data": lambda s, a, b: self.SSH_KEY})()
        monkeypatch.setattr(sdk2.Vault, "data", functools.partial(lambda *_: self.SSH_KEY, sdk2.Vault))

        # Kill ssh-agent after test completion
        request.addfinalizer(lambda: sdk2.ssh.SshAgent().kill())

        with sdk2.ssh.Key(task, "user", "rsa_key"):
            with sdk2.ssh.Key(task, "user", "rsa_key"):
                assert os.environ["SSH_AUTH_SOCK"]
                assert os.environ["SSH_AGENT_PID"]
                self._check_ssh_key_is_available()
            self._check_ssh_key_is_available()
