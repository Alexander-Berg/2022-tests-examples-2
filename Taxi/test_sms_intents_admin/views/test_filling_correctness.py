from sms_intents_admin.generated.service.swagger.models import api
from sms_intents_admin.views import intent


def test_correctness_ok(load_json):
    settings = api.Settings.deserialize(load_json('correctness_ok.json'))
    assert intent.is_correct(settings) is True


def test_correctness_bad_texts(load_json):
    settings = api.Settings.deserialize(
        load_json('correctness_bad_texts.json'),
    )
    assert intent.is_correct(settings) is False
