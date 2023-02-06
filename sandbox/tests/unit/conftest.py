import pytest

from sandbox.projects.billing.tasks.Faas.BillingFaasBuildTask import (
    ManifestValidatorCore,
)


@pytest.fixture
def core():
    core = ManifestValidatorCore(False, 0)
    return core
