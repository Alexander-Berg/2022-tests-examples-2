import argparse
import collections
import datetime
import json
import requests
import six
import tqdm

from projects.common.nile import environment as penv
from projects.support.data_context import plotva_loader
from projects.support.decision_makers import project_config


PUT_LOGS_TO_YT_TABLE = (
    '//home/taxi_ml/production/support/tmp/logs_for_test_shooting'
)
LOGS_NUMBER = 1000
URL = 'http://{}{}'
MODELS_URI = [
    '/autoreply_general/v1',
    '/autoreply_general/v2',
    '/drivers_support/v1',
    '/drivers_support/v2',
    '/eats/support/v1',
    '/smm_support/v1',
    '/music_support/v1',
    '/parks_support/v1',
    '/yadrive_support/v1',
]


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-file', type=str, required=True)
    parser.add_argument('--host', type=str, required=True)
    parser.add_argument('--tvm-key', type=str, required=False)
    parser.add_argument('--logs-number', type=int, default=LOGS_NUMBER)
    parser.add_argument('--yt-proxy', type=str, default=penv.DEFAULT_CLUSTER)

    args = parser.parse_args()

    cluster = project_config.get_project_cluster()

    job = cluster.job('support-shooting')

    context = plotva_loader.DataContext(
        job,
        begin_dttm=datetime.datetime.now() - datetime.timedelta(1),
        end_dttm=datetime.datetime.now(),
    )

    logs = context.get_http_requests(models_uri=MODELS_URI).random(
        args.logs_number,
    )
    logs.put(PUT_LOGS_TO_YT_TABLE)

    job.run()

    logs = cluster.read(PUT_LOGS_TO_YT_TABLE).as_dataframe()

    statistics = collections.defaultdict(collections.Counter)
    for request_body, response_body, uri, meta_code in tqdm.tqdm(
            zip(
                logs.request_body,
                logs.response_body,
                logs.uri,
                logs.meta_code,
            ),
            total=args.logs_number,
    ):
        headers = {}
        if args.tvm_key is not None:
            headers = {'X-Ya-Service-Ticket': args.tvm_key}
        uri = six.ensure_str(uri)
        response = requests.post(
            URL.format(args.host, uri),
            json=json.loads(request_body),
            headers=headers,
        )
        statistics[uri]['requests'] += 1
        if response.status_code == 200:
            response = response.json()
            if 'status' in response:
                statistics[uri][response['status']] += 1
            if six.ensure_str(meta_code) == '200':
                response_body = json.loads(response_body)
                statistics[uri]['same_topic_as_in_prod'] += response.get(
                    'topic',
                ) == response_body.get('topic')
        elif 400 <= response.status_code < 500:
            statistics[uri]['4xx'] += 1
        elif response.status_code >= 500:
            statistics[uri]['5xx'] += 1

    cluster.driver.write_file(
        args.output_file,
        six.ensure_binary(
            json.dumps(statistics, indent=2, ensure_ascii=False),
        ),
    )
