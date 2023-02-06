import json

from nile.api.v1 import clusters
from nile.api.v1 import filters as nf
from nile.api.v1 import extractors as ne


yt_spec = {
    'layer_paths': [
        '//home/taxi_ml/bin/taximl-py3-yt-layer.tar.gz',
        '//porto_layers/ubuntu-xenial-base.tar.xz'
    ]
}

logs_dir='//home/logfeller/logs/taxi-pyml-yandex-taxi-pymlaas-protocol-log/1d'
job = clusters.yt.Hahn().job().env(
    yt_spec_defaults={
        'mapper': yt_spec,
        'reducer': yt_spec,
        'scheduling_tag_filter': 'porto'
    }
)

job.table(logs_dir + '/2019-06-04').filter(
    nf.equals('_type', b'request_body'),  # pay attention! bytes literal
    nf.custom(lambda uri: uri and b'places_ranking' in uri)
).project(
    ne.all(),
    request=ne.custom(lambda body: json.loads(body))
).put('//home/taxi_ml/tmp/eats/ranking/requests')

job.run()
