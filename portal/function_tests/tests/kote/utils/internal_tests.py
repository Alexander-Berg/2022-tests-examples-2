from client import URLClient
import pytest
import yaml


def run_internal_tests():
    HOME_77966_test_post()


def HOME_77966_test_post():
    with open('tests/kote/tests/framework_test/test_post.yaml') as f:
        test_params = yaml.safe_load(f)
    test_client = URLClient(config=test_params['config'])
    req = test_client.prepare_request({})
    assert req.method == 'POST' and req.data == '{"blocks": [{"enabled": 0, "id": "tg_news_extended"}], "skin": "night"}', 'Failed internal POST-requests test'
