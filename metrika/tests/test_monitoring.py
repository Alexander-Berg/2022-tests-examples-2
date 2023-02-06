import metrika.pylib.monitoring as mmon
import metrika.pylib.structures.dotdict as mdd
import metrika.pylib.monitoring.juggler_api as mjapi
import pytest


@pytest.mark.parametrize(
    'code,message,expected_code_str,expected_code_int,expected_message',
    [
        (0, 'okay', 'OK', 0, 'okay'),
        (1, 'not ok', 'WARN', 1, 'not ok'),
        (2, 'bad', 'CRIT', 2, 'bad'),
        ('ok', 'ok', 'OK', 0, 'ok'),
        ('warn', 'w', 'WARN', 1, 'w'),
        ('Crit', 'cr', 'CRIT', 2, 'cr'),
        ('okay', 'OK', 'CRIT', 2, 'Unknown status code: okay, original description: OK'),
        (3, 'Ok', 'CRIT', 2, 'Unknown status code: 3, original description: Ok'),
    ],
)
def test_valudate_event(code, message, expected_code_str, expected_code_int, expected_message):
    event = mmon.validate_event(code, message)

    assert event.int_code == expected_code_int
    assert event.str_code == expected_code_str
    assert event.description == expected_message


@pytest.mark.parametrize(
    'code,message,expected_message',
    [
        (666, 'wow, this is test message!', 'wow, this is test message!'),
        (555, None, 'Critical'),
        (1, None, 'Warning'),
        (0, None, 'Ok'),
    ],
)
def test_accumulator_append(accumulator, monkeypatch, code, message, expected_message):
    def mock_validate_event(code, message):
        event = mdd.DotDict(int_code=code, description=message)
        return event

    monkeypatch.setattr(mmon, 'validate_event', mock_validate_event)

    accumulator.append(code, message=message)
    assert accumulator.total_result[code] == [expected_message]


@pytest.mark.parametrize(
    'newline_replace_char,code,message,expected_message',
    [
        (None, 666, 'wow,\nthis\nis\ntest\nmessage!', 'wow,\\nthis\\nis\\ntest\\nmessage!'),
        ('NL', 666, 'wow,\nthis\nis\ntest\nmessage!', 'wow,NLthisNLisNLtestNLmessage!'),
    ],
)
def test_accumulator_append_w_neline_replace(accumulator, monkeypatch, newline_replace_char, code, message, expected_message):
    def mock_validate_event(code, message):
        event = mdd.DotDict(int_code=code, description=message)
        return event

    monkeypatch.setattr(mmon, 'validate_event', mock_validate_event)

    accumulator.newline_replace = True
    if newline_replace_char is not None:
        accumulator.newline_replace_char = newline_replace_char
    accumulator.append(code, message=message)
    assert accumulator.total_result[code] == [expected_message]


@pytest.mark.parametrize(
    'show_code_names,code,messages,expected_message',
    [
        (False, 0, ['hello', 'world'], 'hello, world'),
        (False, 2, ['hello', 'world'], 'hello, world'),
        (True, 0, ['hello', 'world'], '{}: hello, world'.format(mmon.STATUS_MAP[0])),
        (True, 2, ['hello', 'world'], '{}: hello, world'.format(mmon.STATUS_MAP[2])),
    ]
)
def test_accumulator_format_msg_str(accumulator, show_code_names, code, messages, expected_message):
    accumulator.show_code_names = show_code_names
    assert accumulator._format_msg_str(code, messages) == expected_message


def test_format_msg_str(accumulator):
    accum = mmon.Accumulator(show_code_names=True)
    assert accum._format_msg_str(1, ['1', '2']) == 'WARN: 1, 2'

    accum = mmon.Accumulator(show_code_names=False)
    assert accum._format_msg_str(1, ['1', '2']) == '1, 2'


def test_calculate_overall_code(accumulator):
    accumulator.total_result = {0: 'Zero', 666: ':)'}
    assert accumulator.calculate_overall_code() == 666


def test_accumulator_get_overall_status():
    accum = mmon.Accumulator(show_code_names=True)
    accum.append("Ok", "Hello, ok!")
    accum.get_overall_status()
    assert accum.show_code_names is False

    accum = mmon.Accumulator(show_code_names=True, only_crit=True)
    accum.append("Ok", "Hello, ok!")
    accum.append("Warn", "Hello, warn!")
    accum.get_overall_status()
    assert accum.show_code_names is False

    accum = mmon.Accumulator()
    assert accum.get_overall_status() == (1, mmon.OVERALL_STATUS_NO_DATA_ERR_MESSAGE)

    accum = mmon.Accumulator(ignore_no_data=True)
    assert accum.get_overall_status() == (0, mmon.OVERALL_STATUS_NO_DATA_OK_MESSAGE)

    accum = mmon.Accumulator(hide_ok=True)
    accum.append("Ok", "Hello, ok!")
    assert accum.get_overall_status() == (0, mmon.OVERALL_STATUS_OK_MESSAGE)


def test_accumulator_get_overall_status_not_only_crit(monkeypatch):
    def mock_get_not_only_crit_overall_status(*args, **kwargs):
        return ['awesome message']

    accum = mmon.Accumulator(only_crit=False)
    monkeypatch.setattr(accum, 'get_not_only_crit_overall_status', mock_get_not_only_crit_overall_status)

    accum.append("Ok", "Hello, ok!")
    accum.append("Warn", "Hello, warn!")
    assert accum.get_overall_status() == (1, 'awesome message')


def test_accumulator_get_overall_status_only_crit():
    accum = mmon.Accumulator(only_crit=True)

    accum.append("Ok", "Hello, ok!")
    accum.append("Warn", "Hello, warn!")
    assert accum.get_overall_status() == (1, 'Hello, warn!')


def test_juggler_api_init():
    mjapi.JugglerAPI(token='')
