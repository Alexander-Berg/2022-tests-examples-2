# pylint: disable=redefined-outer-name
from hiring_sf_xml_proxy.generated.web import run_monrun


async def test_example():
    msg = await run_monrun.run(
        ['hiring_sf_xml_proxy.monrun_checks.web_example', 'type_one'],
    )
    assert msg == '0; Check type: type_one'

    msg = await run_monrun.run(
        ['hiring_sf_xml_proxy.monrun_checks.web_example', 'type_two'],
    )
    assert msg == '0; Check type: type_two'
