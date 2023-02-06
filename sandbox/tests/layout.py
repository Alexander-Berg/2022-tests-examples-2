import io
import base64
import tarfile

import yatest.common

from sandbox.deploy import layouts


class TestSecretsDict(dict):

    def __init__(self, *args, **kwargs):
        self._encoded2secret = {}
        super(TestSecretsDict, self).__init__(*args, **kwargs)

    def get_secret(self, encoded_value):
        return self._encoded2secret.get(encoded_value)

    def __getitem__(self, item):
        secret = "secret with key '{}'".format(item)
        encoded_secret = base64.b64encode(secret)
        self._encoded2secret[encoded_secret] = secret
        return encoded_secret

    def __contains__(self, item):
        return True


def test_secrets_locations(monkeypatch):
    monkeypatch.setattr(
        layouts,
        "FULL_LAYOUTS_FOLDER",
        yatest.common.source_path("sandbox/deploy/layout"),
    )

    file_reprs = []
    secrets_dict = TestSecretsDict()
    layouts_dict = layouts.build_layouts(secrets_dict)
    for layout_name, encoded_tar_bytes in layouts_dict.items():
        layout_file = io.BytesIO(base64.b64decode(encoded_tar_bytes))
        tar = tarfile.open(fileobj=layout_file)
        for tarinfo in tar:
            if tarinfo.isfile():
                file_content = tar.extractfile(tarinfo).read()
                secret = secrets_dict.get_secret(file_content)
                if secret:
                    file_reprs.append("{}:{} = {}".format(layout_name, tarinfo.name, secret))

    return "\n".join(sorted(file_reprs))
