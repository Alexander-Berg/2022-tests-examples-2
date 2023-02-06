import base64
import json


INVALID_MAIL_REQUEST_BODIES = [
    'not_an_xml_at_all',
    '<a>A valid xml but not an email at all</a>',
    (
        '<mails><some_tag>Correct root tag, wrong inner tag'
        '</some_tag></mails>'
    ),
    (
        '<mails><mail>mail tag</mail>'
        '<some_tag>Incorrect extra tag</some_tag></mails>'
    ),
]

VAILD_MAIL_REQUEST_BODY = '<mails><mail>Correct inner tag</mail></mails>'

VALID_B64_JSON_DATA = base64.b64encode(json.dumps({}).encode()).decode()
