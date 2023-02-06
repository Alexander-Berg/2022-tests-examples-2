import copy
import datetime as dt

import six
import pytest

import sandbox.common.api as common_api
import sandbox.common.enum as common_enum


class Api(common_api.Api):
    pass


class SchemaInner(Api.Schema):
    f1 = common_api.Boolean("B1")
    f2 = common_api.Boolean("B2")


class Schema(Api.Schema):
    f1 = common_api.Integer("Test1", required=True)
    f2 = common_api.String("Test2")
    f3 = common_api.Object("Test3")
    f4 = SchemaInner("Test3")


class SchemaInnerMap(Api.Schema):
    inner_map = common_api.Map(Schema, "Inner map schema")


class InlineSchema(Api.InlineSchema):
    i1 = common_api.Object("Test1")
    i2 = common_api.Object("Test2")


class InlineSchemaChild(InlineSchema):
    i3 = common_api.Object("Test3")


class TestApiInputOutput(object):
    def test__string(self):
        param = common_api.String()
        param_default = common_api.String(default="asdf")
        param_required = common_api.String(required=True)
        param_required_default = common_api.String(required=True, default="qwer")

        assert not param
        assert param.decode(None) is None
        assert param.encode(None) is None
        assert param.decode("qwer") == "qwer"
        assert param.encode("qwer") == "qwer"
        assert param.decode(123) == "123"
        assert param.encode(123) == "123"

        assert not param_default
        assert param_default.decode(None) == "asdf"
        assert param_default.decode("") == ""
        assert param_default.decode("qwer") == "qwer"

        assert param_required
        with pytest.raises(ValueError):
            param_required.decode(None)
        with pytest.raises(ValueError):
            param_required.decode(None)

        assert param_required_default
        with pytest.raises(ValueError):
            param_required_default.decode(None)
        with pytest.raises(ValueError):
            param_required_default.encode(None)

    def test__datetime(self):
        value = dt.datetime.utcnow()
        value_str = value.isoformat() + "Z"
        param = common_api.DateTime()
        param_default = common_api.DateTime(default=value)
        param_required = common_api.DateTime(required=True)

        assert not param
        assert param.decode(None) is None
        assert param.decode(value_str) == value
        assert param.encode(None) is None
        assert param.encode(value) == value_str
        assert param.encode(value_str) == value_str

        assert not param_default
        assert param_default.decode(None) == value
        assert param_default.encode(None) == value_str

        assert param_required
        with pytest.raises(ValueError):
            param_required.decode(None)
        with pytest.raises(ValueError):
            param_required.encode(None)
        assert param_required.decode(value_str) == value

    def test__datetimerange(self):
        value = [dt.datetime.utcnow(), dt.datetime.now()]
        value_str = "{}Z..{}Z".format(value[0].isoformat(), value[1].isoformat())
        param = common_api.DateTimeRange()
        param_default = common_api.DateTimeRange(default=value)
        param_required = common_api.DateTimeRange(required=True)

        assert not param
        assert param.decode(None) is None
        assert param.decode(value_str) == value
        assert param.encode(None) is None
        assert param.encode(value) == value_str
        assert param.encode(value_str) == value_str

        assert not param_default
        assert param_default.decode(None) == value
        assert param_default.encode(None) == value_str

        assert param_required
        with pytest.raises(ValueError):
            param_required.decode(None)
        with pytest.raises(ValueError):
            param_required.encode(None)
        assert param_required.decode(value_str) == value

    def test__enum(self):
        class Enum(common_enum.Enum):
            A = None
            B = None
            C = None

        param_empty = common_api.Enum()
        param = common_api.Enum(values=Enum)
        param_default = common_api.Enum(default=Enum.A, values=Enum)
        param_required = common_api.Enum(required=True, values=Enum)

        assert not param_empty
        assert param_empty.decode(None) is None
        assert param_empty.encode(None) is None
        with pytest.raises(ValueError):
            param_empty.decode(Enum.A)
        with pytest.raises(ValueError):
            param_empty.encode(Enum.A)

        assert not param
        assert param.decode(None) is None
        # noinspection PyTypeChecker
        for item in Enum:
            assert param.decode(item) == item
        with pytest.raises(ValueError):
            param.decode("D")
        assert param.encode(None) is None
        # noinspection PyTypeChecker
        for item in Enum:
            assert param.encode(item) == item
        with pytest.raises(ValueError):
            param.decode("D")

        assert not param_default
        assert param_default.decode(None) == Enum.A
        assert param_default.encode(None) == Enum.A

        assert param_required
        with pytest.raises(ValueError):
            param_required.decode(None)
        with pytest.raises(ValueError):
            param_required.encode(None)
        assert param_required.decode(Enum.B) == Enum.B
        assert param_required.encode(Enum.C) == Enum.C

    def test__integer(self):
        param = common_api.Integer()
        param_default = common_api.Integer(default=123)
        param_required = common_api.Integer(required=True)
        param_required_default = common_api.Integer(required=True, default=321)

        assert not param
        assert param.decode(None) is None
        assert param.encode(None) is None
        assert param.decode(111) == 111
        assert param.encode(222) == 222
        assert param.decode("333") == 333
        assert param.encode("444") == 444
        for v in ("", "qwer"):
            with pytest.raises(ValueError):
                param.decode(v)
            with pytest.raises(ValueError):
                param.encode(v)

        assert not param_default
        assert param_default.decode(None) == 123
        assert param_default.encode(None) == 123

        assert param_required
        with pytest.raises(ValueError):
            param_required.decode(None)
        with pytest.raises(ValueError):
            param_required.encode(None)

        assert param_required_default
        with pytest.raises(ValueError):
            param_required_default.decode(None)
        with pytest.raises(ValueError):
            param_required_default.encode(None)

    def test__id(self):
        param = common_api.Id(required=False)
        param_default = common_api.Id(required=False, default=123)
        param_required = common_api.Id()
        param_required_default = common_api.Id(default=321)

        assert not param
        assert param.decode(None) is None
        assert param.encode(None) is None
        assert param.decode(111) == 111
        assert param.encode(222) == 222
        assert param.decode("333") == 333
        assert param.encode("444") == 444
        for v in ("", "qwer", 0, -123):
            with pytest.raises(ValueError):
                param.decode(v)
            with pytest.raises(ValueError):
                param.encode(v)

        assert not param_default
        assert param_default.decode(None) == 123
        assert param_default.encode(None) == 123

        assert param_required
        with pytest.raises(ValueError):
            param_required.decode(None)
        with pytest.raises(ValueError):
            param_required.encode(None)

        assert param_required_default
        with pytest.raises(ValueError):
            param_required_default.decode(None)
        with pytest.raises(ValueError):
            param_required_default.encode(None)

    def test__number(self):
        param = common_api.Number()
        param_default1 = common_api.Number(default=123)
        param_default2 = common_api.Number(default=123.456)
        param_required = common_api.Number(required=True)
        param_required_default = common_api.Number(required=True, default=321.654)

        assert not param
        assert param.decode(None) is None
        assert param.encode(None) is None
        assert param.decode(111) == 111
        assert param.encode(111) == 111
        assert param.decode(222.333) == 222.333
        assert param.encode(222.333) == 222.333
        assert param.decode("333.222") == 333.222
        assert param.encode("333.222") == 333.222
        assert param.decode("444") == 444
        assert param.encode("444") == 444
        for v in ("", "qwer"):
            with pytest.raises(ValueError):
                param.decode(v)
            with pytest.raises(ValueError):
                param.encode(v)

        assert not param_default1
        assert param_default1.decode(None) == 123

        assert not param_default2
        assert param_default2.decode(None) == 123.456

        assert param_required
        with pytest.raises(ValueError):
            param_required.decode(None)
        with pytest.raises(ValueError):
            param_required.encode(None)

        assert param_required_default
        with pytest.raises(ValueError):
            param_required_default.decode(None)
        with pytest.raises(ValueError):
            param_required_default.encode(None)

    def test__boolean(self):
        param = common_api.Boolean()
        param_default1 = common_api.Boolean(default=False)
        param_default2 = common_api.Boolean(default=True)
        param_required = common_api.Boolean(required=True)
        param_required_default = common_api.Boolean(required=True, default=True)

        assert not param
        assert param.decode(None) is None
        assert param.encode(None) is None
        for v in (False, 0, "0", "false", "no", "off"):
            assert param.decode(v) is False
        for v in (False, 0, ""):
            assert param.encode(v) is False
        for v in (True, 1, "1", "true", "yes", "on"):
            assert param.decode(v) is True
        for v in (True, 1, "a"):
            assert param.encode(v) is True
        for v in ("", "qwer", "2", 123):
            with pytest.raises(ValueError):
                param.decode(v)

        assert not param_default1
        assert param_default1.decode(None) is False
        assert param_default1.encode(None) is False

        assert not param_default2
        assert param_default2.decode(None) is True
        assert param_default2.encode(None) is True

        assert param_required
        with pytest.raises(ValueError):
            param_required.decode(None)
        with pytest.raises(ValueError):
            param_required.encode(None)

        assert param_required_default
        with pytest.raises(ValueError):
            param_required_default.decode(None)
        with pytest.raises(ValueError):
            param_required_default.encode(None)

    def test__object(self):
        param = common_api.Object()
        value = {"qwer": 123, 321: "asdf"}
        param_default1 = common_api.Object(default={})
        param_default2 = common_api.Object(default=value)
        param_required = common_api.Object(required=True)
        param_required_default = common_api.Object(required=True, default=value)

        assert not param
        assert param.decode(None) is None
        assert param.encode(None) is None
        assert param.decode({}) == {}
        assert param.encode({}) == {}
        assert param.decode(value) == value
        assert param.encode(value) == value
        for v in ("", "qwer", 123, []):
            with pytest.raises(ValueError):
                param.decode(v)
            with pytest.raises(ValueError):
                param.encode(v)

        assert not param_default1
        assert param_default1.decode(None) == {}
        assert param_default1.encode(None) == {}

        assert not param_default2
        assert param_default2.decode(None) == value
        assert param_default2.encode(None) == value

        assert param_required
        with pytest.raises(ValueError):
            param_required.decode(None)
        with pytest.raises(ValueError):
            param_required.encode(None)

        assert param_required_default
        with pytest.raises(ValueError):
            param_required_default.decode(None)
        with pytest.raises(ValueError):
            param_required_default.encode(None)

    def test__array(self):
        with pytest.raises(AssertionError):
            common_api.Array()
        param1 = common_api.Array(common_api.String)
        param2 = common_api.Array(common_api.Integer)
        param3 = common_api.Array(common_api.Integer, collection_format=common_api.ArrayFormat.MULTI)
        value1 = ["a", "b", "c"]
        value2 = [1, 2, 3]
        param_default1 = common_api.Array(common_api.String, default=value1)
        param_default2 = common_api.Array(common_api.Integer, default=value2)
        param_default3 = common_api.Array(common_api.String, default=[])
        param_required = common_api.Array(common_api.String, required=True)
        param_required_default = common_api.Array(common_api.String, required=True, default=value1)

        assert not param1
        assert param1.decode(None) is None
        assert param1.encode(None) is None
        assert param1.decode("") == []
        assert param1.encode([]) == []
        assert param1.decode(",".join(value1)) == value1
        assert param1.encode(value1) == value1
        for v in (123, {}, []):
            with pytest.raises(ValueError):
                param1.decode(v)

        assert not param2
        assert param2.decode(",".join(map(str, value2))) == value2
        assert param2.encode(value2) == value2
        for v in ("qwer", 123, {}, ",".join(value1)):
            with pytest.raises(ValueError):
                param2.decode(v)
        for v in ("qwer", ",".join(value1), ",".join(map(str, value2))):
            with pytest.raises(ValueError):
                param2.encode(v)

        assert not param3
        assert param3.decode(None) is None
        assert param3.encode(None) is None
        assert param3.decode("123") == [123]
        assert param3.encode([]) == []
        assert param3.decode(value2) == value2
        assert param3.encode(value2) == value2
        for v in ("", "qwer", value1, ",".join(value1)):
            with pytest.raises(ValueError):
                param3.decode(v)

        assert not param_default1
        assert param_default1.decode(None) == value1
        assert param_default1.encode(None) == value1

        assert not param_default2
        assert param_default2.decode(None) == value2
        assert param_default2.encode(None) == value2

        assert not param_default3
        assert param_default3.decode(None) == []
        assert param_default3.encode(None) == []

        assert param_required
        with pytest.raises(ValueError):
            param_required.decode(None)
        with pytest.raises(ValueError):
            param_required.encode(None)

        assert param_required_default
        with pytest.raises(ValueError):
            param_required_default.decode(None)
        with pytest.raises(ValueError):
            param_required_default.encode(None)

    def test__extra_fields(self):
        class TestSchema(common_api.Api.Schema):
            req_test = common_api.Integer("Test1", required=True)
            test = common_api.String("Test1")

        test_data = {"req_test": 8, "extra_test": "extra data"}

        result = TestSchema("Testing schema").decode(test_data)
        assert result.req_test == test_data["req_test"]
        assert not hasattr(result, "extra_test")

    def test__schema(self):
        pass  # TODO

    @pytest.mark.parametrize('method', ('encode', 'decode'))
    @pytest.mark.parametrize('data', (
        {"f1": 42, "f2": "42"},
        {"f1": 42, "f2": "42", "f3": {"f4": {"f5": {}}}},
        {"f1": 42, "f2": "42", "f4": {"f1": False, "f2": True}}
    ))
    def test__schema_immutable(self, data, method):
        initial = copy.deepcopy(data)
        getattr(Schema, method)(data)
        assert data == initial

    def test__map(self):
        test_data = {
            "key1": {
                "f1": 1
            },
            "key2": {
                "f1": 2,
                "f2": "v3"
            }
        }
        test_schema = SchemaInnerMap.create(inner_map=test_data)
        assert isinstance(test_schema.inner_map, dict)
        assert "key1" in test_schema.inner_map
        assert "key2" in test_schema.inner_map
        assert isinstance(test_schema.inner_map["key1"], Schema)
        assert isinstance(test_schema.inner_map["key2"], Schema)
        assert test_schema.inner_map["key1"].f1 == 1
        assert test_schema.inner_map["key2"].f1 == 2
        assert test_schema.inner_map["key2"].f2 == "v3"

    def test__inline_schema(self):
        def recursive_dict_check(d1, d2):
            assert type(d1) == type(d2)

            if isinstance(d1, dict):
                assert len(d1) == len(d2)
                for k, v in six.iteritems(d1):
                    assert k in d2
                    recursive_dict_check(v, d2[k])
            elif isinstance(d1, list):
                assert len(d1) == len(d2)
                for i in range(len(d1)):
                    recursive_dict_check(d1[i], d2[i])
            else:
                assert d1 == d2

        class TestInlineSchema(Schema):
            inline1 = InlineSchema(
                overrides={"i1": common_api.Integer("inline test 1"), "i2": common_api.Boolean("inline test 2")}
            )
            inline2 = InlineSchema(
                overrides={
                    "i1": common_api.String("inline test 3"),
                    "i2": common_api.Array(common_api.String, "inline test 2")
                }
            )
            inline3 = InlineSchemaChild(
                overrides={
                    "i1": common_api.Boolean("inline child test 1"),
                    "i2": common_api.Integer("inline child test 2"),
                    "i3": common_api.String("inline child test 3"),
                }
            )

        test_dict = {
            "f1": 1,
            "f2": "t1",
            "f3": {"o": "1"},
            "inline1": {
                "i1": 10,
                "i2": True
            },
            "inline2": {
                "i1": "iii1",
                "i2": ["t1", "t2"]
            },
            "inline3": {
                "i1": False,
                "i2": 15,
                "i3": "iii3"
            }
        }

        o = TestInlineSchema.create(**test_dict)
        assert o.f1 == test_dict["f1"]
        assert o.f2 == test_dict["f2"]
        assert o.f3 == test_dict["f3"]
        assert o.inline1.i1 == test_dict["inline1"]["i1"]
        assert o.inline1.i2 == test_dict["inline1"]["i2"]
        assert o.inline2.i1 == test_dict["inline2"]["i1"]
        assert tuple(o.inline2.i2) == tuple(test_dict["inline2"]["i2"])
        assert o.inline3.i1 == test_dict["inline3"]["i1"]
        assert o.inline3.i2 == test_dict["inline3"]["i2"]
        assert o.inline3.i3 == test_dict["inline3"]["i3"]

        test_dict2 = copy.deepcopy(test_dict)
        test_dict2["inline3"]["i2"] = {"3": 5}
        with pytest.raises(TypeError):
            TestInlineSchema.create(**test_dict2)

        d = dict(TestInlineSchema)
        test_output = {
            "properties": {
                "f1": {"format": "int64", "type": "integer"},
                "f2": {"type": "string"},
                "f3": {"type": "object"},
                "f4": {"$ref": "#/definitions/SchemaInner"},
                "inline1": {
                    "properties": {
                        "i1": {"format": "int64", "type": "integer"},
                        "i2": {"type": "boolean"}
                    }
                },
                "inline2": {
                    "properties": {
                        "i1": {"type": "string"},
                        "i2": {"items": {"type": "string"}, "type": "array"}
                    }
                },
                "inline3": {
                    "properties": {
                        "i1": {"type": "boolean"},
                        "i2": {"format": "int64", "type": "integer"},
                        "i3": {"type": "string"}
                    }
                }
            },
            "required": ["f1"]
        }
        recursive_dict_check(d, test_output)


class TestRequest(object):
    def test__params_order(self):
        pass  # TODO
