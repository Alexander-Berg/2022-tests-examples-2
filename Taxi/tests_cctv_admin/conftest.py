# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import base64

import pytest

from cctv_admin_plugins import *  # noqa: F403 F401

# pylint: disable=import-only-modules
from tests_cctv_admin.gcm_aes_cipher import GcmAesCipher as Cipher


@pytest.fixture(autouse=True)
def cipher():
    kek = base64.b64decode(b'kDjNonVyRyaS/TuuQis0Sbm2yw9o/kcMn9aU9/clKq8=')
    return Cipher(kek)
