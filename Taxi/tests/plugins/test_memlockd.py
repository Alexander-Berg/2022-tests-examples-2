import pytest


@pytest.mark.xfail(reason='memlockd is disabled')
def test_memlockd(
        generate_services_and_libraries, default_repository, default_base,
):
    default_repository['services/test-service/service.yaml']['memlockd'] = {
        'enabled': True,
    }
    generate_services_and_libraries(
        default_repository, 'test_memlockd', default_base,
    )
