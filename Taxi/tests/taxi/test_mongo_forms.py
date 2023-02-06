from __future__ import unicode_literals

import copy
import datetime

import pytest

from taxi.util import dates
from taxi.util import mongo_forms


def test_bool_field():
    class F1(mongo_forms.Form):
        field1 = mongo_forms.BoolField()
        field2 = mongo_forms.BoolField(mongo_key='f2')
        field3 = mongo_forms.BoolField(json_key='f3')
        field4 = mongo_forms.BoolField(optional=True)
        field5 = mongo_forms.BoolField(allow_none=True)

    json_doc = {
        'field1': True,
        'field2': False,
        'f3': True,
        'field4': False,
        'field5': True,
    }

    form = F1.from_json(json_doc)
    assert form.field1 is True
    assert form.field2 is False
    assert form.field3 is True
    assert form.field4 is False
    assert form.field5 is True
    assert form.to_json() == json_doc
    assert form.to_mongo() == {
        'field1': True,
        'f2': False,
        'field3': True,
        'field4': False,
        'field5': True,
    }
    assert F1.from_mongo(form.to_mongo()).to_json() == json_doc
    assert form.to_update() == {
        '$set': {
            'field1': True,
            'f2': False,
            'field3': True,
            'field4': False,
            'field5': True,
        },
    }

    json_doc.pop('field4')
    form = F1.from_json(json_doc)
    assert form.field4 is None
    assert form.to_json() == json_doc
    assert form.to_mongo() == {
        'field1': True,
        'f2': False,
        'field3': True,
        'field5': True,
    }
    assert F1.from_mongo(form.to_mongo()).to_json() == json_doc
    assert form.to_update() == {
        '$set': {'field1': True, 'f2': False, 'field3': True, 'field5': True},
        '$unset': {'field4': True},
    }

    json_doc['extra'] = True
    with pytest.raises(mongo_forms.ValidationError):
        F1.from_json(json_doc)
    json_doc.pop('extra')

    json_doc.pop('field1')
    with pytest.raises(mongo_forms.ValidationError):
        F1.from_json(json_doc)

    json_doc['field1'] = None
    with pytest.raises(mongo_forms.ValidationError):
        F1.from_json(json_doc)

    json_doc['field1'] = 1
    with pytest.raises(mongo_forms.ValidationError):
        F1.from_json(json_doc)

    json_doc['field1'] = True
    F1.from_json(json_doc)


def test_fields():
    class Form(mongo_forms.Form):
        bool_field = mongo_forms.BoolField()
        numeric_field = mongo_forms.NumericField()
        int_field = mongo_forms.IntField()
        string_field = mongo_forms.StringField()
        datetime_field = mongo_forms.DatetimeField()
        date_field = mongo_forms.DateField()

    now = dates.parse_timestring('2016-01-01T10:00:00.0+0000')
    json_doc = {
        'bool_field': True,
        'numeric_field': 4.5,
        'int_field': 10,
        'string_field': 'asdf',
        'datetime_field': dates.timestring(now),
        'date_field': '2016-10-01',
    }
    form = Form.from_json(json_doc)
    assert form.bool_field is True
    assert form.numeric_field == 4.5
    assert form.int_field == 10
    assert form.string_field == 'asdf'
    assert form.datetime_field == now
    assert form.date_field == datetime.date(2016, 10, 1)
    doc = form.to_mongo()
    assert doc == {
        'bool_field': True,
        'numeric_field': 4.5,
        'int_field': 10,
        'string_field': 'asdf',
        'datetime_field': now,
        'date_field': datetime.datetime(2016, 10, 1),
    }
    assert json_doc == Form.from_mongo(doc).to_json()
    assert form.to_update() == {
        '$set': {
            'bool_field': True,
            'numeric_field': 4.5,
            'int_field': 10,
            'string_field': 'asdf',
            'datetime_field': now,
            'date_field': datetime.datetime(2016, 10, 1),
        },
    }


# pylint: disable=invalid-name
def test_dict_field():
    class Form(mongo_forms.Form):
        field1 = mongo_forms.DictField(optional=True)
        field1.f1 = mongo_forms.DateField()
        field2 = mongo_forms.DictField(
            json_key='j2', mongo_key='m2', allow_none=True,
        )
        field2.f1 = mongo_forms.DateField()
        field3 = mongo_forms.DictField()
        field3.field1 = mongo_forms.DateField(optional=True)
        field3.field2 = mongo_forms.DateField(
            json_key='j2', mongo_key='m2', allow_none=True,
        )
        field3.field3 = mongo_forms.DictField()
        field3.field3.field1 = mongo_forms.DateField()

    now1 = '2016-10-21'
    dnow1 = datetime.date(2016, 10, 21)
    mnow1 = datetime.datetime(2016, 10, 21)
    now2 = '2016-10-30'
    dnow2 = datetime.date(2016, 10, 30)
    mnow2 = datetime.datetime(2016, 10, 30)

    json_doc = {
        'field1': {'f1': now1},
        'j2': {'f1': now2},
        'field3': {'field1': now1, 'j2': now2, 'field3': {'field1': now1}},
    }
    form = Form.from_json(json_doc)
    assert form.field1.f1 == dnow1
    assert form.field2.f1 == dnow2
    assert form.field3.field1 == dnow1
    assert form.field3.field2 == dnow2
    assert form.field3.field3.field1 == dnow1
    assert form.to_json() == json_doc
    assert form.to_mongo() == {
        'field1': {'f1': mnow1},
        'm2': {'f1': mnow2},
        'field3': {'field1': mnow1, 'm2': mnow2, 'field3': {'field1': mnow1}},
    }
    assert form.to_update() == {'$set': form.to_mongo()}
    doc = copy.deepcopy(json_doc)
    del doc['field1']['f1']
    with pytest.raises(mongo_forms.ValidationError):
        Form.from_json(doc)
    del doc['field1']
    Form.from_json(doc)
    del doc['field3']['field1']
    Form.from_json(doc)
    del doc['field3']['field3']['field1']
    with pytest.raises(mongo_forms.ValidationError):
        Form.from_json(doc)
    doc['field3']['field3']['field1'] = None
    with pytest.raises(mongo_forms.ValidationError):
        Form.from_json(doc)
    doc = copy.deepcopy(json_doc)
    doc['field3']['j2'] = None
    Form.from_json(doc)
    doc['j2'] = None
    Form.from_json(doc).to_mongo()
    Form.from_json(doc).to_json()
    Form.from_json(doc).to_update()
    doc['field2'] = None
    with pytest.raises(mongo_forms.ValidationError):
        Form.from_json(doc)


def test_list_field():
    class Form(mongo_forms.Form):
        field1 = mongo_forms.ListField(mongo_forms.StringField())
        field2 = mongo_forms.ListField()
        field2.el_type = mongo_forms.BoolField(allow_none=True)
        field3 = mongo_forms.ListField(mongo_forms.BoolField(allow_none=True))
        field4 = mongo_forms.ListField()
        field4.el_type = mongo_forms.ListField(min_len=2, max_len=3)
        field4.el_type.el_type = mongo_forms.BoolField()

    json_doc = {
        'field1': ['a', 'b'],
        'field2': [True, False, None],
        'field3': [True, False, None],
        'field4': [[True, False], [True, False, True]],
    }
    form = Form.from_json(json_doc)
    assert form.field1 == ['a', 'b']
    assert form.field2 == [True, False, None]
    assert form.field3 == [True, False, None]
    assert form.field4 == [[True, False], [True, False, True]]
    assert form.to_json() == json_doc
    assert form.to_mongo() == json_doc
    assert Form.from_mongo(json_doc).to_json() == json_doc
    doc = copy.deepcopy(json_doc)
    doc['field1'].append(None)
    with pytest.raises(mongo_forms.ValidationError):
        Form.from_json(doc)
    doc = copy.deepcopy(json_doc)
    doc['field4'].append(None)
    with pytest.raises(mongo_forms.ValidationError):
        Form.from_json(doc)


def test_string_regex():
    class Form(mongo_forms.Form):
        f1 = mongo_forms.StringField(regex=r'^\d+$')

    Form.from_json({'f1': '1'})
    Form.from_json({'f1': '0987654321'})
    with pytest.raises(mongo_forms.ValidationError):
        Form.from_json({'f1': '-0987654321'})
    with pytest.raises(mongo_forms.ValidationError):
        Form.from_json({'f1': '0987654321a'})
    with pytest.raises(mongo_forms.ValidationError):
        Form.from_json({'f1': '0987a654321'})
    with pytest.raises(mongo_forms.ValidationError):
        Form.from_json({'f1': 'a0987654321'})
    with pytest.raises(mongo_forms.ValidationError):
        Form.from_json({'f1': ''})
    with pytest.raises(mongo_forms.ValidationError):
        Form.from_json({'f1': 'a'})


def test_enum_field():
    class Form(mongo_forms.Form):
        f1 = mongo_forms.EnumField({'aa', 'bb', 'cc'})

    Form.from_json({'f1': 'aa'})
    Form.from_json({'f1': 'bb'})
    Form.from_json({'f1': 'cc'})
    with pytest.raises(mongo_forms.ValidationError):
        Form.from_json({'f1': 'ee'})
    with pytest.raises(mongo_forms.ValidationError):
        Form.from_json({'f1': 123})


@pytest.mark.parametrize(
    'arguments, value, should_be_valid',
    [
        ({}, 1, True),
        ({}, -1, True),
        ({}, 15.35, True),
        ({}, 1000, True),
        ({'gte': 3}, 3, True),
        ({'gte': 3}, 3.5, True),
        ({'gte': 3}, 4, True),
        ({'gte': 3}, 2.99, False),
        ({'gte': 3}, 1, False),
        ({'lte': 5}, 5, True),
        ({'lte': 5}, 4.5, True),
        ({'lte': 5}, 4, True),
        ({'lte': 5}, 5.01, False),
        ({'lte': 5}, 6, False),
        ({'gt': 4}, 4.5, True),
        ({'gt': 4}, 5, True),
        ({'gt': 4}, 4, False),
        ({'gt': 4}, 3.99, False),
        ({'gt': 4}, 3, False),
        ({'lt': 9}, 8.99, True),
        ({'lt': 9}, 8, True),
        ({'lt': 9}, 9, False),
        ({'lt': 9}, 9.5, False),
        ({'lt': 9}, 10, False),
    ],
)
def test_numeric_field(arguments, value, should_be_valid):
    field = mongo_forms.NumericField(**arguments)
    if should_be_valid:
        field.validate(value)
    else:
        with pytest.raises(mongo_forms.ValidationError):
            field.validate(value)
