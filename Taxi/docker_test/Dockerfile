FROM registry.yandex.net/taxi/taxi-integration-bionic-base:latest

RUN apt update || true
RUN apt install -y \
    libavcodec57 \
    libavformat57 \
    libavutil55 \
    libblas3 \
    libboost-date-time1.65.1 \
    libboost-filesystem1.65.1 \
    libboost-program-options1.65.1 \
    libboost-system1.65.1 \
    libc6 \
    libgcc1 \
    libjpeg8 \
    liblapack3 \
    libpng16-16 \
    libstdc++6 \
    libswscale4 \
    zlib1g \
    libyaml-cpp0.6 \
    libcurl4 \
    libcurlpp0 \
    libilmbase12 \
    libopenexr22 \
    libdc1394-22 \
    libavresample3

COPY . /home/cctv-repo/
WORKDIR /home/cctv-repo/
ENTRYPOINT taxi-pytest3 processor/
