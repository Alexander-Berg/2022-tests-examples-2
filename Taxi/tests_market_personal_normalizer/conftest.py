# pylint: disable=wildcard-import, unused-wildcard-import, import-error
# pylint: disable=import-only-modules
from market_personal_normalizer_plugins import *  # noqa: F403 F401

from tests_market_personal_normalizer.mock_api_impl.personal import (  # noqa
    _mock_personal_emails_store,
)
from tests_market_personal_normalizer.mock_api_impl.personal import (  # noqa
    _mock_personal_phones_store,
)
