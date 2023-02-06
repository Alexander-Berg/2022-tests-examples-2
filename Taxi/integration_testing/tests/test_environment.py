import pytest

from taxi.integration_testing.framework import environment


@pytest.mark.parametrize(('docker_port', 'expected_port', 'expected_proto'), [
    ('80/tcp', 80, environment.PortProto.TCP),
    ('443/udp', 443, environment.PortProto.UDP),
    ('5433', 5433, None),
    (27017, 27017, None),
])
def test_parse_valid_docker_port(docker_port, expected_port, expected_proto):
    port, proto = environment.parse_docker_port(docker_port)
    assert port == expected_port
    assert proto == expected_proto


def test_parse_invalid_docker_port():
    with pytest.raises(ValueError):
        environment.parse_docker_port('invalid')


def test_parse_empty_docker_port():
    with pytest.raises(ValueError):
        environment.parse_docker_port(None)
