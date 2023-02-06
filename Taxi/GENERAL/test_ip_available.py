import logging
import json
import sys

import requests

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.DEBUG, format='%(levelname)s %(message)s', stream=sys.stdout,
)


def request(url, token):
    data = f"""
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
xmlns:ns="urn://x-artefacts-gnivc-ru/inplat/servin/\
OpenApiMessageConsumerService/types/1.0">
    <soapenv:Header/>
    <soapenv:Body>
        <ns:GetMessageRequest>
            <ns:Message>
                <tns:AuthRequest xmlns:tns="urn://x-artefacts-gnivc-ru/\
ais3/kkt/AuthService/types/1.0">
                    <tns:AuthAppInfo>
                        <tns:MasterToken>{token}</tns:MasterToken>
                    </tns:AuthAppInfo>
                </tns:AuthRequest>
            </ns:Message>
        </ns:GetMessageRequest>
    </soapenv:Body>
</soapenv:Envelope>
    """  # noqa:N400
    return requests.post(url, data)


def get_tokens(path):
    with open(path) as f:
        data = json.load(f)
        return data['selfemployed_fns']


def main():
    url = sys.argv[1]

    tokens = get_tokens('/etc/yandex/taxi-secdist/taxi.json')
    token_taxi = tokens['FNS_MASTER_TOKEN']
    token_eda = tokens['FNS_EDA_MASTER_TOKEN']

    result_taxi = request(url, token_taxi)
    logger.info('TAXI status %s', result_taxi.status_code)
    logger.info('TAXI text %s', result_taxi.text)

    result_eda = request(url, token_eda)
    logger.info('EDA status %s', result_eda.status_code)
    logger.info('EDA text %s', result_eda.text)


if __name__ == '__main__':
    main()
