ARG platform=xenial
FROM registry.yandex.net/taxi/taxi-integration-${platform}-base:latest
ADD ./volumes/deb/*.deb /taxi/deb/
RUN apt-get update -qq && apt-get install -y --no-install-recommends --allow-downgrades /taxi/deb/*.deb
