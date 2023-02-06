# pylint: disable=redefined-outer-name
import parks_certifications_worker.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = [
    'parks_certifications_worker.generated.service.pytest_plugins',
]
