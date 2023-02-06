# pylint: disable=invalid-name

import pytest

from taxi_billing_subventions.personal_uploads import models
from taxi_billing_subventions.personal_uploads import type_aliases as ta


@pytest.mark.parametrize(
    'upload_json, expected',
    [
        ('init_upload.json', False),
        ('in_progress_upload.json', False),
        ('succeeded_upload.json', True),
        ('failed_upload.json', True),
    ],
)
@pytest.mark.nofilldb()
def test_is_finished(upload_json, expected, load_py_json_dir):
    upload: models.Upload = load_py_json_dir('test_is_finished', upload_json)
    assert upload.is_finished is expected


@pytest.mark.parametrize('upload_json', ['in_progress_upload.json'])
@pytest.mark.nofilldb()
def test_succeed(upload_json, load_py_json_dir):
    upload: models.Upload = load_py_json_dir('test_succeed', upload_json)
    upload.succeed()
    assert upload.status == models.UploadStatus.SUCCEEDED


@pytest.mark.parametrize('upload_json', ['in_progress_upload.json'])
@pytest.mark.nofilldb()
def test_fail(upload_json, load_py_json_dir):
    upload: models.Upload = load_py_json_dir('test_fail', upload_json)
    reason = models.UploadStatusChangedReason.PARSE_ERROR
    upload.fail(reason, ['first', 'second'])
    assert upload.status == models.UploadStatus.FAILED
    last_event = upload.events[-1]
    assert isinstance(last_event, models.UploadStatusChanged)
    assert last_event.reason == reason
    assert last_event.messages == ['first', 'second']


@pytest.mark.parametrize(
    'upload_json, rules_json',
    [
        ('init_upload.json', 'rule.json'),
        ('in_progress_upload.json', 'rule.json'),
    ],
)
@pytest.mark.nofilldb()
def test_start(upload_json, rules_json, load_py_json_dir):
    upload: models.Upload
    rules: ta.PersonalRules
    upload, rules = load_py_json_dir('test_start', upload_json, rules_json)
    upload.start(rules, 'some_hash')
    assert upload.status == models.UploadStatus.IN_PROGRESS
    assert upload.input_hash == 'some_hash'
    assert upload.num_rules == 1


@pytest.mark.parametrize(
    'upload_json, rules_json',
    [('in_progress_another_hash_upload.json', 'rule.json')],
)
@pytest.mark.nofilldb()
def test_start_failure(upload_json, rules_json, load_py_json_dir):
    upload: models.Upload
    rules: ta.DriverRules
    upload, rules = load_py_json_dir(
        'test_start_failure', upload_json, rules_json,
    )
    with pytest.raises(models.UploadStartError):
        upload.start(rules, 'another_hash')
