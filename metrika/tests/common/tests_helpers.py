import metrika.admin.python.bishop.frontend.tests.helper as tests_helper

import metrika.admin.python.bishop.frontend.bishop.models as bp_models
import metrika.admin.python.bishop.frontend.bishop.helpers as bp_helpers


class TestHelpers(tests_helper.BishopTestCase):
    """
    Testing helpers
    bct stands for beautify_config_text
    """
    def test_btc_ignores_nonxml(self):
        text = '<1hello>oo'
        self.assertEqual(
            bp_helpers.beautify_config_text(text, 'non_xml_format'),
            text,
        )

    def test_btc_creates_xml_indent(self):
        text = bp_models.Template.objects.get(name='xml_without_indent.xml').text
        expected_text = '''<hello>
    <world>1</world>
</hello>
'''
        self.assertEqual(
            bp_helpers.beautify_config_text(text, 'xml'),
            expected_text,
        )

    def test_btc_preserve_xml_comments(self):
        text = bp_models.Template.objects.get(name='xml_with_comment_text.xml').text

        expected_text = '''<hello>
    <!-- hello comment -->
    <world>1</world>
</hello>
'''
        self.assertEqual(
            bp_helpers.beautify_config_text(text, 'xml'),
            expected_text,
        )

    def test_btc_preserve_cdata(self):
        text = bp_models.Template.objects.get(name='xml_with_cdata_text.xml').text

        expected_text = '''<hello>
    <world><![CDATA[inside_cdata]]></world>
</hello>
'''
        self.assertEqual(
            bp_helpers.beautify_config_text(text, 'xml'),
            expected_text,
        )
