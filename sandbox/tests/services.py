import inspect

from sandbox.common import format as common_format
from sandbox.deploy import services as services_servants
from sandbox.services import modules as services_modules


class TestServants(object):
    BULLET = "\n\t* "

    def test__services_declaration(self):
        servants = filter(
            lambda cls: (
                inspect.isclass(cls) and
                issubclass(cls, services_servants.Service) and
                cls is not services_servants.Service
            ),
            services_servants.__dict__.values()
        )

        used_ports = set()
        for servant in sorted(servants):
            assert servant.api_port is not None, "API port for {} is not set".format(servant.__name__)
            assert servant.api_port not in used_ports, (
                "API port {} declared for servant {} is already used by another one".format(
                    servant.api_port, servant.__name__
                )
            )

            used_ports.add(servant.api_port)

            assert "__name__" in servant.__dict__, (
                "sandbox.deploy.services.{} is missing \"__name__\" assignment in class body "
                "(you probably want it to be \"{}\")".format(
                    servant.__name__, common_format.ident(servant.__name__).lower()
                )
            )

        declarations = set(s.__dict__["__name__"] for s in servants)
        implementations = set(services_modules.service_registry.keys())

        missing_services = declarations - implementations
        assert not missing_services, (
            "Servants whose __name__ is missing in services.modules.service_registry:{}{}".format(
                self.BULLET, self.BULLET.join(sorted(missing_services))
            )
        )

        missing_servants = implementations - declarations
        assert not missing_servants, (
            "Services without servants declared in deploy.services module:{}{}".format(
                self.BULLET, self.BULLET.join(sorted(missing_servants))
            )
        )
