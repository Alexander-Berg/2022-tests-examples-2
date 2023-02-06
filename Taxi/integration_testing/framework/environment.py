import datetime
import enum
import ipaddress
import json
import logging
import re
import subprocess
import time
from typing import Callable, Dict, List, Tuple, Union

import docker
import docker.errors as docker_errors
import docker.models.containers as docker_containers
import docker.models.images as docker_images
import docker.types as docker_types
import requests
import ulid2
import urllib3
import yatest.common
from yatest.common import network as yatest_network


class EnvironmentSetupError(Exception):
    pass


class PortProto(enum.Enum):
    TCP = 0
    UDP = 1


def parse_docker_port(docker_port: Union[int, str]) -> Tuple[int, Union[PortProto, None]]:
    if isinstance(docker_port, int):
        return docker_port, None

    if docker_port is None:
        raise ValueError('Invalid value None for port')

    match = re.match('^(?P<PORT>\\d+)(/(?P<PROTO>(tcp)|(udp)))?$', docker_port, re.RegexFlag.IGNORECASE)

    if match is None:
        raise ValueError(f'Invalid port {docker_port}')

    port = int(match.group('PORT'))
    proto_str = match.group('PROTO')
    proto = None if proto_str is None else PortProto[proto_str.upper()]
    return port, proto


class TestContainer:
    def __init__(
        self,
        name: str,
        container: docker_containers.Container,
        ports: Dict[str, int],
        healthcheck=None,
    ):
        self.name = name
        self.container = container
        self.ports = ports
        self.healthcheck = healthcheck

    def stop(self, timeout: int = None):
        '''
        Stops a container. Similar to the ``docker stop`` command.

        Args:
            timeout (int): Timeout in seconds to wait for the container to
                stop before sending a ``SIGKILL``. Default: 10

        Raises:
            :py:class:`docker.errors.APIError`
                If the server returns an error.
        '''
        if self.container.status == 'running':
            self.container.stop()

    def kill(self, signal=None):
        '''
        Kill or send a signal to the container.

        Args:
            signal (str or int): The signal to send. Defaults to ``SIGKILL``

        Raises:
            :py:class:`docker.errors.APIError`
                If the server returns an error.
        '''

        self.container.kill(signal)

    def remove(self):
        '''
        Remove this container. Similar to the ``docker rm`` command.

        Raises:
            :py:class:`docker.errors.APIError`
                If the server returns an error.
        '''
        self.container.remove()

    def get_endpoint(self, port: Union[str, int]) -> str:
        port_str = port if isinstance(port, str) else str(port)

        result = None if self.ports is None else self.ports.get(port_str)

        if result is None:
            raise ValueError(f'Port {port_str} not defined for {self.name}')

        return f'localhost:{result}'


class EnvironmentManager:
    def __init__(self, image_tag_factory: Callable[[str], str]):
        self.image_tag_factory = image_tag_factory
        self.ulid = ulid2.generate_ulid_as_base32()
        self.client = docker.from_env()
        self.network = self.init_docker_network()
        self.services: List[TestContainer] = []
        self.images: List[docker_images.Image] = []
        self.port_manager = yatest_network.PortManager()

    def init_docker_network(self):
        ipv4_networks = (x for x in ipaddress.IPv4Network('172.16.0.0/16').subnets(prefixlen_diff=8))
        ipv6_networks = (x for x in ipaddress.IPv6Network('2001:3984:398a:0000::/56').subnets(prefixlen_diff=8))

        while True:
            try:
                ipv4_busy: List[ipaddress.IPv4Network] = []
                ipv6_busy: List[ipaddress.IPv6Network] = []
                networks = self.client.networks.list()

                for network in networks:
                    for ipam_config in network.attrs.get('IPAM', dict()).get('Config', []):
                        subnet = ipam_config.get('Subnet')
                        if subnet:
                            try:
                                subnet_object = ipaddress.ip_network(subnet)
                                if isinstance(subnet_object, ipaddress.IPv4Network):
                                    ipv4_busy.append(subnet_object)
                                elif isinstance(subnet_object, ipaddress.IPv6Network):
                                    ipv6_busy.append(subnet_object)
                                else:
                                    logging.warning(f'{str(subnet_object)} is neither ipv4 nor ipv6 network')
                            except ValueError as ex:
                                logging.warning(f'An error occurred when parsing existing docker subnet {subnet}', ex)

                ipv4_subnet = next(ipv4_networks)
                while ipv4_subnet in ipv4_busy:
                    ipv4_subnet = next(ipv4_networks)

                ipv6_subnet = next(ipv6_networks)
                while ipv6_subnet in ipv6_busy:
                    ipv6_subnet = next(ipv6_networks)

                network_name = f'{self.ulid}-taxi-internal'
                logging.debug(f'Creating network {network_name}: {str(ipv4_subnet)}, {str(ipv6_subnet)}')

                return self.client.networks.create(
                    name=network_name,
                    driver='bridge',
                    enable_ipv6=True,

                    ipam=docker_types.IPAMConfig(
                        driver='default',
                        pool_configs=[
                            docker_types.IPAMPool(subnet=str(ipv4_subnet)),
                            docker_types.IPAMPool(subnet=str(ipv6_subnet)),
                        ],
                    ),
                )
            except docker_errors.APIError as ex:
                if ex.explanation != 'Pool overlaps with other one on this address space':
                    raise EnvironmentSetupError('An error occurred when initializing docker network') from ex

    def add_container(
        self,
        name: str,
        image: str,
        package_json: str = None,
        command: str = None,
        healthcheck=None,
        hostname: str = None,
        privileged: bool = False,
        environment=None,
        working_dir=None,
        archive: bytes = None,
        tmpfs=None,
        ports: List[Union[str, int]] = None,
        aliases: List[str] = None,
    ):
        logging.debug(f'Creating container {name}')

        image_tag = self.image_tag_factory(name)
        if image_tag is not None:
            image = f'{image}:{image_tag}'

        if package_json is not None and image_tag == 'test':
            subprocess.run([
                yatest.common.binary_path('devtools/ya/bin/ya-bin'),
                'package',
                '--docker',
                '--docker-repository',
                'taxi',
                package_json
            ])
        else:
            try:
                self.client.images.get(image)
            except docker_errors.ImageNotFound:
                logging.debug(f'Pulling image {image}')
                self.client.images.pull(
                    image[: image.index(':')], image[image.index(':') + 1:],
                )

        docker_ports = None

        if ports is not None and any(ports):
            docker_ports = {}

            for docker_port in ports:
                port, proto = parse_docker_port(docker_port)

                if proto is None or proto == PortProto.TCP:
                    host_port = self.port_manager.get_tcp_port()
                elif proto == PortProto.UDP:
                    host_port = self.port_manager.get_udp_port()
                else:
                    raise ValueError(f'Unexpected port proto {proto}')

                docker_ports[str(docker_port)] = host_port

        docker_cntnr = self.client.containers.create(
            name=f'{self.ulid}-{name}',
            image=image,
            command=command,
            cap_add=['SYS_PTRACE'],
            privileged=privileged,
            hostname=hostname,
            environment=environment,
            working_dir=working_dir,
            tmpfs=tmpfs,
            ports=docker_ports,
        )

        self.network.connect(
            docker_cntnr.id,
            aliases=aliases,
        )

        if archive:
            trials = 0
            while True:
                try:
                    trials += 1
                    docker_cntnr.put_archive('/', archive)
                    break
                except docker_errors.APIError:
                    if trials >= 3:
                        raise
                    else:
                        time.sleep(0.1)

        docker_cntnr.start()

        cntnr = TestContainer(
            name,
            docker_cntnr,
            docker_ports,
            healthcheck,
        )

        self.services.append(cntnr)

        return cntnr

    def build_image(
        self,
        path: str,
        tag: str,
        nocache: bool = False,
        rm: bool = True,
        timeout: int = None,
        pull: bool = True,
        forcerm: bool = True,
        dockerfile: str = None,
        buildargs: Dict = None,
    ):
        '''
        Build an image and return it. Similar to the ``docker build``
        command. Either ``path`` or ``fileobj`` must be set.

        If you have a tar file for the Docker build context (including a
        Dockerfile) already, pass a readable file-like object to ``fileobj``
        and also pass ``custom_context=True``. If the stream is compressed
        also, set ``encoding`` to the correct value (e.g ``gzip``).

        If you want to get the raw output of the build, use the
        :py:meth:`~docker.api.build.BuildApiMixin.build` method in the
        low-level API.

        Args:
            path (str): Path to the directory containing the Dockerfile
            tag (str): A tag to add to the final image
            nocache (bool): Don't use the cache when set to ``True``
            rm (bool): Remove intermediate containers
            timeout (int): HTTP timeout
            pull (bool): Downloads any updates to the FROM image in Dockerfiles
            forcerm (bool): Always remove intermediate containers, even after
                unsuccessful builds
            dockerfile (str): path within the build context to the Dockerfile
            buildargs (dict): A dictionary of build arguments

        Returns:
            (tuple): The first item is the :py:class:`Image` object for the
                image that was build. The second item is a generator of the
                build logs as JSON-decoded objects.

        Raises:
            :py:class:`docker.errors.BuildError`
                If there is an error during the build.
            :py:class:`docker.errors.APIError`
                If the server returns any other error.
            ``TypeError``
                If neither ``path`` nor ``fileobj`` is specified.
        '''

        logging.debug(f'Building image {tag}')

        # TODO: add a flag to skip building
        try:
            image, _ = self.client.images.build(
                path=path,
                tag=tag,
                nocache=nocache,
                rm=rm,
                timeout=timeout,
                pull=pull,
                forcerm=forcerm,
                dockerfile=dockerfile,
                buildargs=buildargs,
            )

        except docker_errors.BuildError as ex:
            logging.error(f'an error occurred when building image {tag}: {ex}')
            logging.error('\n'.join([json.dumps(x) for x in ex.build_log]))
            raise

        self.images.append(image)

        return image

    def wait_until_healthy(self):
        for cntnr in self.services:
            self.wait_container_healthy(cntnr)

    def is_running(self, cntnr: TestContainer):
        docker_container = self.client.containers.get(
            cntnr.container.id,
        )
        return docker_container.status == 'running'

    def get_ipv6(self, cntnr: TestContainer) -> str:
        docker_container = self.client.containers.get(
            cntnr.container.id,
        )
        return docker_container.attrs['NetworkSettings']['Networks'][self.network.name]['GlobalIPv6Address']

    def wait_container_healthy(
        self,
        cntnr: TestContainer,
        url: str = None,
        timeout: datetime.timedelta = datetime.timedelta(seconds=60),
    ):
        if url is None:
            if cntnr.healthcheck:
                test = cntnr.healthcheck.get('test')
                logging.debug(f'pinging http://{cntnr.name}.yandex.taxi.net/ping')
                if test and '/ping' in test and '80' in cntnr.ports:
                    # url = f'http://{self.name}.yandex.taxi.net/ping'
                    url = f'http://{cntnr.get_endpoint(80)}/ping'

        if url is None:
            logging.info(f'skipped healthcheck for {cntnr.name}')
            return

        started = datetime.datetime.now()
        while True:
            try:
                if self.is_running(cntnr):
                    with requests.get(
                        url, timeout=timeout.total_seconds(),
                    ) as response:
                        if response.status_code == 200:
                            break
            except requests.exceptions.ConnectionError:
                pass
            except ConnectionError:
                pass
            except urllib3.exceptions.HTTPError:
                pass

            if datetime.datetime.now() > started + timeout:
                try:
                    logs = cntnr.container.logs(tail=1000)
                    logging.error(logs.decode('UTF-8'))
                except docker_errors.APIError as ex:
                    logging.error(
                        f'An error occurred when reading log output of '
                        f'{cntnr.name} service: {ex}',
                    )

                raise TimeoutError(f'{cntnr.name} is not healthy.')

    def cleanup(self):
        logging.debug('Cleaning up test environment')
        for cntnr in reversed(self.services):
            try:
                cntnr.kill()
            except Exception as ex:
                logging.error(
                    f'An error occurred when stopping container '
                    f'{cntnr.name}: {str(ex)}.',
                )

            try:
                cntnr.remove()
            except Exception as ex:
                logging.error(
                    f'An error occurred when removing container '
                    f'{cntnr.name}: {str(ex)}.',
                )

        for image in reversed(self.images):
            try:
                self.client.images.remove(
                    image=image.id, force=True, noprune=False)
            except Exception as ex:
                logging.error(
                    f'An error occurred when removing image '
                    f'{image.id}: {str(ex)}.',
                )

        try:
            self.network.remove()
        except docker_errors.APIError as ex:
            logging.error(
                f'An error occurred when removing network '
                f'{self.network.name}: {str(ex)}.',
            )

        self.port_manager.release()
