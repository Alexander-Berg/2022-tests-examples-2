# pylint: disable=redefined-outer-name
import jinja2
from lxml import etree
import pytest

import sber_int_api.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['sber_int_api.generated.service.pytest_plugins']
REQUEST_TPL = jinja2.Template(
    """<?xml version="1.0" encoding="UTF-8"?>
<CIM CIMVERSION="2.0" DTDVERSION="2.2">
    <DECLARATION>
        <DECLGROUP>
            <VALUE.OBJECT>
                <INSTANCE CLASSNAME="{{classname}}">
                {% for name, value in properties.items() %}
                    <PROPERTY TYPE="string" NAME="{{name}}">
                        <VALUE>{{value}}</VALUE>
                    </PROPERTY>
                {% endfor %}
                </INSTANCE>
            </VALUE.OBJECT>
        </DECLGROUP>
    </DECLARATION>
</CIM>""",
)


@pytest.fixture
def simple_secdist(simple_secdist):
    simple_secdist['settings_override'].update({'sber_email_password': '123'})
    return simple_secdist


@pytest.fixture
def handler(cron_context):
    from sber_int_api.crontasks import sync_email_requests
    from sber_int_api.email_api import xml

    xml_parser = etree.XMLParser(
        remove_blank_text=True, resolve_entities=False, no_network=True,
    )
    xml_parser.resolvers.add(  # pylint: disable=no-member
        xml.FakeDTDResolver(),
    )

    async def wrap(classname: str, properties: dict):
        incoming_xml = REQUEST_TPL.render(
            classname=classname, properties=properties,
        ).encode('utf-8')
        requests = xml.parse_requests(incoming_xml)
        responses = await sync_email_requests.main_process(
            cron_context, *requests,
        )
        success_responses = [
            response for response in responses if response is not None
        ]
        outgoing_xml = xml.create_xml_file(success_responses)
        root = etree.fromstring(outgoing_xml, xml_parser)
        return {
            instance.attrib['CLASSNAME']: xml.parse_properties(instance)
            for instance in xml.instance_iter(root)
        }

    return wrap
