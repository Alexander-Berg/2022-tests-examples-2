# -- coding: utf8 --

from __future__ import unicode_literals

from django import test as django_test
from django.conf import settings
from django.conf import urls as django_urls
from django.views.decorators import csrf
import pytest

from taxiadmin.api import apiutils
from taxiadmin.api import urls


@pytest.mark.asyncenv('blocking')
def test_auth_by_token(monkeypatch):
    @csrf.csrf_exempt
    @apiutils.json_response
    def _ok_handler(request):
        return {}

    @csrf.csrf_exempt
    @apiutils.json_response
    def _wrong_handler(request):
        raise RuntimeError('Must not be called')

    monkeypatch.setattr(
        settings,
        'BLACKBOX_AUTH',
        True,
    )

    monkeypatch.setattr(
        urls,
        'urlpatterns',
        django_urls.patterns(
            'taxiadmin.api.views',
            django_urls.url(r'^test/path/$', _ok_handler),
            django_urls.url(r'^wrong/path/$', _wrong_handler),
        ),
    )

    client = django_test.Client()

    response = client.get('/api/test/path/')
    assert response.status_code == 401

    response = client.get(
        '/api/test/path/', HTTP_X_YATAXI_API_KEY='test_token',
    )
    assert response.status_code == 200

    response = client.get(
        '/api/wrong/path/', HTTP_X_YATAXI_API_KEY='test_token',
    )
    assert response.status_code == 401
