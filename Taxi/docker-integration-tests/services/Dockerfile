ARG platform=xenial
FROM registry.yandex.net/taxi/taxi-integration-${platform}-base

ARG project

# Copy install scripts and deb files if exists
COPY scripts ${project}* /taxi/services/${project}/

ARG packages

# Install all packages
RUN /taxi/services/${project}/install_packages.sh
