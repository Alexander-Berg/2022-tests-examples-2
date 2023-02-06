import pytest


class YaTranslateContext:
    def __init__(self):
        self.langs = ['ru', 'en', 'de', 'az', 'ro']

    def set_supported_langs(self, langs):
        self.langs = langs


@pytest.fixture(autouse=True)
def mock_ya_translate(mockserver):
    ya_translate_context = YaTranslateContext()

    @mockserver.json_handler('/ya_translate/getLangs', True)
    def get_langs(request):
        langs = ya_translate_context.langs
        return {'dirs': [], 'langs': {lang: 'lang_name' for lang in langs}}
