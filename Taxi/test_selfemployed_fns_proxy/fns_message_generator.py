import datetime as dt
import os

import lxml.etree
import pytest

_SEND_MESSAGE_REQUEST_PATH = 'fns_message_templates/send_message_request.xml'
_SEND_MESSAGE_RESPONSE_PATH = 'fns_message_templates/send_message_response.xml'
_GET_MESSAGE_REQUEST_PATH = 'fns_message_templates/get_message_request.xml'
_GET_MESSAGE_RESPONSE_PATH = 'fns_message_templates/get_message_response.xml'
_FNS_AUTH_REQUEST_PATH = 'fns_message_templates/fns_auth_request.xml'
_FNS_AUTH_RESPONSE_PATH = 'fns_message_templates/fns_auth_response.xml'
_DIR_PATH = os.path.dirname(os.path.realpath(__file__))

_ERROR_MESSAGE_NAME = 'SmzPlatformError'


class MessageGenerator:
    @classmethod
    def send_message_request(cls, message_name: str, message_content: dict):
        message_template = cls._read_template(_SEND_MESSAGE_REQUEST_PATH)
        message_raw = message_template.format(
            message_name=cls._to_camel_case(message_name),
            message_content=cls._to_basic_xml(
                message_content, prefix_keys='ns1:',
            ),
        )
        return cls.format_xml(message_raw)

    @classmethod
    def send_message_response(cls, message_id: str):
        message_template = cls._read_template(_SEND_MESSAGE_RESPONSE_PATH)
        message_raw = message_template.format(message_id=message_id)
        return cls.format_xml(message_raw)

    @classmethod
    def get_message_request(cls, message_id: str):
        message_template = cls._read_template(_GET_MESSAGE_REQUEST_PATH)
        message_raw = message_template.format(message_id=message_id)
        return cls.format_xml(message_raw)

    @classmethod
    def get_message_response(cls, message_name: str, message_content: dict):
        message_template = cls._read_template(_GET_MESSAGE_RESPONSE_PATH)
        message_raw = message_template.format(
            message_name=cls._to_camel_case(message_name),
            message_content=cls._to_basic_xml(message_content),
        )
        return cls.format_xml(message_raw)

    @classmethod
    def get_message_error_response(
            cls, error_code: str, error_message: str, args: dict = None,
    ):
        message_template = cls._read_template(_GET_MESSAGE_RESPONSE_PATH)
        message_content: dict = {'code': error_code, 'message': error_message}
        if args:
            message_content['args'] = [
                {'key': key.upper(), 'value': value}
                for key, value in args.items()
            ]
        message_raw = message_template.format(
            message_name=cls._to_camel_case(_ERROR_MESSAGE_NAME),
            message_content=cls._to_basic_xml(message_content),
        )
        return cls.format_xml(message_raw)

    @classmethod
    def fns_auth_request(cls, secret: str):
        message_template = cls._read_template(_FNS_AUTH_REQUEST_PATH)
        message_raw = message_template.format(secret=secret)
        return cls.format_xml(message_raw)

    @classmethod
    def fns_auth_response(cls, auth_token: str, expire_time: dt.datetime):
        message_template = cls._read_template(_FNS_AUTH_RESPONSE_PATH)
        message_raw = message_template.format(
            auth_token=auth_token, expire_time=expire_time.isoformat(),
        )
        return cls.format_xml(message_raw)

    @classmethod
    def _read_template(cls, path):
        with open(os.path.join(_DIR_PATH, path)) as file:
            return file.read()

    @classmethod
    def _to_basic_xml(cls, data, prefix_keys: str = ''):
        assert not isinstance(data, list), 'Cannot convert list to xml'
        if isinstance(data, dict):
            result = ''
            for key, value in data.items():
                xml_key = prefix_keys + cls._to_camel_case(key)
                values = [value] if not isinstance(value, list) else value
                for item in values:
                    result += (
                        f'<{xml_key}>{cls._to_basic_xml(item)}</{xml_key}>'
                    )
            return result

        if isinstance(data, dt.datetime):
            return data.isoformat()

        return str(data)

    @classmethod
    def _to_camel_case(cls, snake_str: str):
        components = snake_str.split('_')
        return ''.join(x[0].upper() + x[1:] for x in components)

    @classmethod
    def format_xml(cls, xml_data: str) -> str:
        parser = lxml.etree.XMLParser(remove_blank_text=True)
        etree = lxml.etree.fromstring(xml_data.encode(), parser=parser)
        return lxml.etree.tostring(etree, encoding='unicode')


@pytest.fixture
def fns_messages():
    return MessageGenerator()
