# coding=utf-8

from sandbox.common.types import misc
from sandbox.projects.metrika.admins.lxc_containers import utils
from sandbox.projects.sandbox import resources, sandbox_lxc_image

CUSTOM_PACKAGES = [
    "wget",
    "ca-certificates",
    "apt-transport-https",
    "build-essential",
    "curl",
    "yandex-internal-root-ca",
    "yandex-openjdk17"
]

CUSTOM_SCRIPT = [
    "set -x"
    """tee /etc/apt/sources.list.d/nodesource.com.list<<EOF
deb https://deb.nodesource.com/node_12.x bionic main
deb-src https://deb.nodesource.com/node_12.x bionic main
EOF""",
    "curl -sSfL https://deb.nodesource.com/gpgkey/nodesource.gpg.key | apt-key add -",
    "apt-get update -y -qq",
    "apt-get install -y nodejs",
    "curl -o allure-2.17.2.tgz -Ls https://github.com/allure-framework/allure2/releases/download/2.17.2/allure-2.17.2.tgz",
    "tar -zxvf allure-2.17.2.tgz -C /opt/",
    "ln -s /opt/allure-2.17.2/bin/allure /usr/bin/allure",
    "npm install -g playwright",
    "npm install -D got@11.5.0",
    "npx playwright install-deps"
]


class CreateFrontendTestsLxcContainer(utils.NoCloneWarningMixin, sandbox_lxc_image.SandboxLxcImage):
    """
    Сборка контейера с окружением для запуска тестов фронта
    """

    class Requirements(sandbox_lxc_image.SandboxLxcImage.Requirements):
        dns = misc.DnsType.DNS64

    class Parameters(sandbox_lxc_image.SandboxLxcImage.Parameters):
        description = "Metrika Frontend Tests Bionic"
        resource_description = sandbox_lxc_image.SandboxLxcImage.Parameters.resource_description(default="Metrika Frontend Tests Environment with Node")
        custom_image = sandbox_lxc_image.SandboxLxcImage.Parameters.custom_image(default=True)
        ubuntu_release = sandbox_lxc_image.SandboxLxcImage.Parameters.ubuntu_release(default=sandbox_lxc_image.UbuntuRelease.BIONIC)
        resource_type = sandbox_lxc_image.SandboxLxcImage.Parameters.resource_type(default=resources.LXC_CONTAINER.name)
        install_common = sandbox_lxc_image.SandboxLxcImage.Parameters.install_common(default=True)
        custom_packages = sandbox_lxc_image.SandboxLxcImage.Parameters.custom_packages(default=" ".join(CUSTOM_PACKAGES))
        custom_script = sandbox_lxc_image.SandboxLxcImage.Parameters.custom_script(default="\n".join(CUSTOM_SCRIPT))
        custom_attrs = sandbox_lxc_image.SandboxLxcImage.Parameters.custom_attrs(default={"ttl": "inf", "purpose": "frontend-tests"})
