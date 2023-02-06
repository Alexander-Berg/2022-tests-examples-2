FROM registry.yandex.net/eda/eda-rtc-bionic-common:20211001122958

ENV PYTHONUNBUFFERED 1
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

RUN python3.7 -m pip install --upgrade pip
RUN python3.7 -m pip install --prefer-binary \
    --extra-index-url https://pypi.yandex-team.ru/simple/ \
    --ignore-installed PyYAML \
    requests==2.25.1 \
    python-dotenv==0.18.0 \
    Jinja2~=3.0.1 \
    psycopg2-binary==2.9.1 \
    startrek-client==2.5 \
    yandex-passport-vault-client==1.5.2 \
    yandex-tracker-client==2.0 \
    ydb==1.0.4 \
    pytest==6.2.5 \
    responses==0.16.0 \
    pytest-responses==0.5.0 \
    pandas==1.3.5 \
    ujson==5.1.0 \
    testpalm-api-client==4.0.2

WORKDIR /var/autotests_metrics/service_tests

ENTRYPOINT ["/bin/bash"]
