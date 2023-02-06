# syntax=docker/dockerfile:1
FROM registry.yandex.net/taxi/taxi-integration-bionic-base:latest

RUN update-alternatives --install /usr/bin/cc cc /usr/bin/clang-9 100 && \
    update-alternatives --install /usr/bin/c++ c++ /usr/bin/clang++-9 100

RUN apt update || true
RUN apt install -y \
    libavcodec-dev \
    libavformat-dev \
    libavutil-dev \
    libswscale-dev \
    libgtest-dev \
    liblapack-dev \
    libblas-dev \
    liblapack-dev \ 
    libyaml-cpp-dev \
    rapidjson-dev \
    libcurl4-openssl-dev \
    libcurlpp-dev

COPY . /home/cctv-repo/
WORKDIR /home/cctv-repo/
RUN make build-processor

FROM golang:1.18-alpine AS rtsp
WORKDIR /s
COPY third_party/rtsp-simple-server/go.mod third_party/rtsp-simple-server/go.sum ./
RUN go mod download
COPY third_party/rtsp-simple-server/ ./

RUN export CGO_ENABLED=0 \
	&& go build -o /rtsp-simple-server

FROM nvidia/cuda:11.0.3-cudnn8-runtime-ubuntu18.04

RUN export this_distro="$(cat /etc/os-release | grep '^ID=' | awk -F'=' '{print $2}')" \
&& export this_version="$(cat /etc/os-release | grep '^VERSION_ID=' | awk -F'=' '{print $2}' | sed 's/[^0-9]*//g')" \
&& apt-key adv --fetch-keys "https://developer.download.nvidia.com/compute/cuda/repos/${this_distro}${this_version}/x86_64/3bf863cc.pub"

RUN apt update && apt install -y \
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
    wget \
    net-tools \
    vim \
    zlib1g \
    libcurl4-openssl-dev \
    libcurlpp-dev \
    nvidia-utils-470 \
    libilmbase12 \
    libopenexr22 \
    libdc1394-22 \
    libavresample3 \
    ffmpeg \
    openssl \
    nginx

WORKDIR /var/yandex/cctv/processor
RUN mkdir /var/yandex/cctv/processor -p
RUN chmod 0755 /var/yandex/cctv/processor -R
RUN mkdir /var/log/yandex/cctv -p
RUN chmod 0755 /var/log/yandex/cctv -R
COPY --from=rtsp /rtsp-simple-server /usr/bin/rtsp-server
COPY --from=rtsp /s/rtsp-simple-server.yml /etc/yandex/rtsp-server/conf.yml
COPY --from=rtsp /s/run_ffmpeg.sh /etc/yandex/rtsp-server/run_ffmpeg.sh
RUN chmod +x /etc/yandex/rtsp-server/run_ffmpeg.sh
RUN mkdir -p /var/log/yandex/rtsp-server
COPY --from=0 /home/cctv-repo/build/onnxruntime/lib/ /usr/lib/
COPY --from=0 /usr/lib/x86_64-linux-gnu/libyaml-cpp.so.0.6 /usr/lib/x86_64-linux-gnu/libyaml-cpp.so.0.6
COPY --from=0 /home/cctv-repo/build/engine-models /var/yandex/cctv/processor/engine-models
COPY --from=0 /home/cctv-repo/tests/data/people_walking.mp4 /var/yandex/cctv/processor/tests/people_walking.mp4
COPY --from=0 /home/cctv-repo/processor/config/yandex-cctv-processor-config.yaml /etc/yandex/cctv/processor/config.yaml
COPY --from=0 /home/cctv-repo/build/processor/yandex-cctv-processor /usr/bin/
COPY --from=0 /home/cctv-repo/processor/tools/test_deploy/nginx/yandex-cctv-processor.conf /etc/nginx/conf.d/
RUN rm /etc/nginx/sites-enabled/default -f
COPY --from=0 /home/cctv-repo/processor/tools/test_deploy/scripts/yandex-cctv-processor-start.sh /usr/bin
RUN mkdir -p /usr/local/share/ca-certificates/
RUN wget https://crls.yandex.net/YandexInternalRootCA.crt -O /usr/local/share/ca-certificates/YandexInternalRootCA.crt
RUN update-ca-certificates

EXPOSE 80

CMD ["bash", "yandex-cctv-processor-start.sh"]
