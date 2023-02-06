# pylint: disable=protected-access
from aiohttp import web
import pytest

from generated.clients_libs.supportai import supportai_lib as supportai_models


@pytest.mark.now('2019-01-01T12:00:00+0000')
async def test_metric_send(web_context, mockserver, monkeypatch):
    monkeypatch.setattr(
        'supportai_api.generated.web.api_metrics.plugin._get_public_key',
        lambda x: (
            'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDh0WVoF7xvFImwKnAIFAH1RtBij'
            '72GCfRe7DMt9x4Z/QUsZNfxzkFblRnndioiJbrck9i9ICMJ22LbnEUjXfKbG9E4hn'
            'wYcJKDnLdglmQCQ2Bc6dDI8GjGNHWy1eclyITgC2sXS5n4WzHX1rNV7NHieFA2iha'
            'yr7SPJCVEixd3i8BrRnHmRibqqFmH3ubB+XedKcFo3feC9BAS9DledJJky/1vVcS/'
            'aYo54H0s0AFi5bFyavMA5GE64QqMlS0Od97ghzgnReY/LxuHK1XT23V55yQRQiCXB'
            'j9LFTSDxRmP5I7mjhvPBk8pVSQw0O1mVQIp8gEKDyosBnglI9og1EQlqWQfNSxR9N'
            'ZtwS74072x0Gb2uvWecgDkfqX35DoPfGETRGefl3MonK2ONGg7weDyHEmpmp6DqDc'
            '8Kl+Jb0B+jyXCCaB2Fr8Vvvyvxiq6f4gNIRTqPcb0XiuKI4nMWzM8OJdHR32OXL1U'
            'g8YtRmVLaIPxfyCyHfo/whwoGWSDK6s='
        ),
    )

    info_call_count = 0
    statistics_call_count = 0

    @mockserver.json_handler('/supportai-license-server/info')
    # pylint: disable=unused-variable
    async def _(request):
        nonlocal info_call_count
        info_call_count += 1

        return web.json_response(
            status=200,
            data={
                'signature': (
                    'QDtTgjVyFE1KLuOVKwYjMLFj6QvN/CnMX3VATiu8NNfE/N3yhn+8q6WvX'
                    'zWvpZz2PcsSqf7B1PJ195WnmOr3lMf1XtQ23UJMz5scZ9X3vORWcd7+IK'
                    'dsZ/DY40PAXYKQRFLl2ZhA2TxitDmxJ0uH5MxOmwcS3tqSK4Ev3wLEjOM'
                    'NgHyZxtRI1JkWP1LYeVUhdELeSif/cdBBvqcDD/9UEyp91NQhAYw5CDba'
                    'N6Zglci3KdKfFTwWmo6W4Avsy5jdM+gIGesdEBijt81HkrcgHBBJMrqpC'
                    'eN1l31sTh9yq9MF7F/ufevUFcQka+UtxBtKI4sgC0wK+sfUdxrDlh3NOM'
                    'W/KJ142JcHUmo7/Jr8BwTMW9Wj+VyjMUfe0vOB+4jw0OZxlh2RcJcK9lx'
                    'tRhrx2KRmOrMC4nU+jsa1xYOzrbk3M9H2MrFJtR9Cp2Nk00rREE3E5Tc5'
                    '0gsuNZKUpZwd/EDRYrrA7blV3O7wlSrzsJmBajf5liXAETdv6T0cBo9+'
                ),
                'iv': 'BaYefh8gHjVfYoL4uBs73Q==',
                'key_hash': 'GMisMz6VD3XB6oduGfYAOFWxdNj9FQq4/HiOax0OWEI=',
                'timestamp': '1546333200.0',
            },
        )

    @mockserver.json_handler('/supportai-license-server/statistics')
    # pylint: disable=unused-variable
    async def _(request):
        nonlocal statistics_call_count
        statistics_call_count += 1

        return web.json_response(status=200)

    web_context.supportai_box_wrapper._box_enabled = True
    for _ in range(50):
        await web_context.api_metrics.add_statistics_record(
            chat_id='12345',
            project_id='test_project',
            in_experiment=False,
            response=supportai_models.SupportResponse(),
            iteration=1,
            user='totalchest',
        )
        await web_context.api_metrics.refresh_cache()

    assert info_call_count
    assert statistics_call_count
