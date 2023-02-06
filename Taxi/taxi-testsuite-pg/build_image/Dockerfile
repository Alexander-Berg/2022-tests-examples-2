FROM ubuntu:xenial

RUN apt-get update && apt-get install -y wget software-properties-common apt-transport-https

RUN wget --no-check-certificate -O - https://apt.llvm.org/llvm-snapshot.gpg.key | apt-key add - && \
    add-apt-repository 'deb http://apt.llvm.org/xenial/   llvm-toolchain-xenial-12  main'

RUN apt-get update && \
    apt-get install -y clang-12 make bison flex \
            libpython3-dev libreadline-dev zlib1g-dev \
            uuid-dev perl patch libreadline6-dev

COPY ./build.sh /build.sh

ENTRYPOINT ["/bin/bash", "/build.sh"]
