FROM snakepacker/python:3.8 as python38

ENV TZ Etc/UTC

ENV LANG ru_RU.UTF-8
RUN locale-gen en_US.UTF-8 ru_RU.UTF-8 && \
    dpkg-reconfigure tzdata locales

RUN apt-install wget python3-venv
RUN mkdir -p ~/.postgresql && \
    wget "https://crls.yandex.net/allCAs.pem" -O /usr/share/ca-certificates/YandexInternalRootCA.crt && \
    chmod 0644 /usr/share/ca-certificates/YandexInternalRootCA.crt

RUN apt-install libpq-dev python3-dev gcc-x86-64-linux-gnu

RUN python3.8 -m venv /usr/share/python3/app

RUN /usr/share/python3/app/bin/pip install wheel
ENV PATH="/usr/share/python3/app/bin:${PATH}"

ADD requirements*.txt /tmp/

RUN pip install -Ur /tmp/requirements.txt && pip uninstall -y psycopg2-binary && pip install psycopg2

RUN apt-get update && apt-get upgrade -y && rm -fr /var/lib/apt/lists /var/lib/cache/* /var/log/*

ADD ext-number-mon-mock /usr/share/python3/app

CMD ["python3.8", "/usr/share/python3/app"]

