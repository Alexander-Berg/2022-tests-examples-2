import json
import logging
import os

logger = logging.getLogger('TAXIDWH_4990_compress_import')


def init_env_config():
    if 'TAXIDWH_ENV_CONFIG' in os.environ:
        raise RuntimeError('TAXIDWH_ENV_CONFIG is not empty')

    substitution = {
        'yt': {
            'default_cluster': 'arnold'
        }
    }
    os.environ['TAXIDWH_ENV_CONFIG'] = json.dumps(substitution)


if __name__ == '__main__':
    init_env_config()

    from dmp_suite.yt import operation as op

    print(op.get_yt_children('//home/eda-dwh'))
