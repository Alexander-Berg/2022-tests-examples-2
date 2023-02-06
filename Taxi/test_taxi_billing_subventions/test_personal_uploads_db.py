import pytest

from taxi_billing_subventions import common
from taxi_billing_subventions.personal_uploads import db
from taxi_billing_subventions.personal_uploads import models


@pytest.mark.parametrize(
    'upload_json, doc_json',
    [('events_upload.json', 'events_upload_doc.json')],
)
@pytest.mark.nofilldb()
def test_upload_to_doc(upload_json, doc_json, load_py_json_dir):
    upload: models.Upload
    upload, expected_doc = load_py_json_dir(
        'test_upload_to_doc', upload_json, doc_json,
    )
    assert db.upload_to_doc(upload) == expected_doc


@pytest.mark.parametrize(
    'doc_json, upload_json',
    [('events_upload_doc.json', 'events_upload.json')],
)
@pytest.mark.nofilldb()
def test_doc_to_upload(doc_json, upload_json, load_py_json_dir):
    expected_upload: models.Upload
    doc, expected_upload = load_py_json_dir(
        'test_doc_to_upload', doc_json, upload_json,
    )
    actual_upload = db.doc_to_upload(doc)
    assert actual_upload.id == expected_upload.id
    assert actual_upload.initiator == expected_upload.initiator
    assert actual_upload.status == expected_upload.status
    assert actual_upload.version == expected_upload.version
    assert actual_upload.yt_path == expected_upload.yt_path
    assert actual_upload.events == expected_upload.events


@pytest.mark.now('2018-05-09T20:00:00')
@pytest.mark.parametrize(
    'driver_rule_json, initiator_json, zone_json, rule_doc_json',
    [
        (
            'driver_single_order_rule.json',
            'initiator.json',
            'zone.json',
            'single_order_rule_doc.json',
        ),
        (
            'driver_multi_order_rule.json',
            'initiator.json',
            'zone.json',
            'multi_order_rule_doc.json',
        ),
    ],
)
@pytest.mark.nofilldb()
def test_rule_doc_converter(
        driver_rule_json,
        initiator_json,
        zone_json,
        rule_doc_json,
        load_py_json_dir,
):
    driver_rule: models.DriverRule
    driver_rule, expected_doc, initiator, zone = load_py_json_dir(
        'test_rule_doc_converter',
        driver_rule_json,
        rule_doc_json,
        initiator_json,
        zone_json,
    )
    converter = db.RuleDocConverter(initiator, zone)

    actual_doc = converter.to_rule_doc(driver_rule)
    from pprint import pprint as pp
    pp(actual_doc)
    pp(expected_doc)
    assert actual_doc == expected_doc


@pytest.mark.parametrize(
    'driver_rule_json, initiator_json, driver_rule_link_doc_json',
    [
        (
            'driver_single_order_rule.json',
            'initiator.json',
            'driver_single_order_rule_link_doc.json',
        ),
    ],
)
@pytest.mark.now('2018-05-08T21:00:00')
@pytest.mark.nofilldb()
# pylint: disable=invalid-name
def test_driver_rule_link_doc_converter(
        driver_rule_json,
        initiator_json,
        driver_rule_link_doc_json,
        load_py_json_dir,
):
    driver_rule: models.DriverRule
    initiator: common.models.Initiator
    driver_rule, initiator, expected_doc = load_py_json_dir(
        'test_driver_rule_link_doc_converter',
        driver_rule_json,
        initiator_json,
        driver_rule_link_doc_json,
    )
    converter = db.DriverRuleLinkDocConverter(initiator)

    actual_doc = converter.to_driver_rule_link_doc(driver_rule)
    assert actual_doc == expected_doc
