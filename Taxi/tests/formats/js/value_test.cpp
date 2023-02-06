#include <tests/common.hpp>

struct JsValue : Fixture {
  static constexpr auto FromString = formats::js::FromString;
  using ParseException = formats::js::ParseException;
};

TEST_F(JsValue, ParsingInvalidRootType) {
  ExecuteInV8([]() {
    EXPECT_NO_THROW(FromString("{}"));
    EXPECT_TRUE(FromString("{}").IsObject());
    EXPECT_NO_THROW(FromString("[]"));
    EXPECT_TRUE(FromString("[]").IsArray());

    EXPECT_NO_THROW(FromString("null"));
    EXPECT_NO_THROW(FromString("true"));
    EXPECT_NO_THROW(FromString("false"));
    EXPECT_NO_THROW(FromString("0"));
    EXPECT_NO_THROW(FromString("1.5"));
    EXPECT_NO_THROW(FromString("-1.2e-0123"));
    EXPECT_NO_THROW(FromString("-1.2E34"));
    EXPECT_NO_THROW(FromString("1.2E+34"));
    EXPECT_NO_THROW(FromString(R"("string")"));
    EXPECT_NO_THROW(FromString(R"("")"));

    EXPECT_THROW_MSG_CONTAINS(FromString("NULL"), ParseException,
                              "Unexpected token");
    EXPECT_THROW_MSG_CONTAINS(FromString("True"), ParseException,
                              "Unexpected token");
    EXPECT_THROW_MSG_CONTAINS(FromString("00"), ParseException,
                              "Unexpected number");
    EXPECT_THROW_MSG_CONTAINS(FromString(""), ParseException,
                              "Unexpected end of JSON");
    EXPECT_THROW_MSG_CONTAINS(FromString("inf"), ParseException,
                              "Unexpected token");
    EXPECT_THROW_MSG_CONTAINS(FromString("#INF"), ParseException,
                              "Unexpected token");
    EXPECT_THROW_MSG_CONTAINS(FromString("nan"), ParseException,
                              "Unexpected token");
    EXPECT_THROW_MSG_CONTAINS(FromString("NaN"), ParseException,
                              "Unexpected token");

    EXPECT_THROW_MSG_CONTAINS(FromString(R"({"field": 'string'})"),
                              ParseException, "Unexpected token");
    EXPECT_THROW_MSG_CONTAINS(FromString("{}{}"), ParseException,
                              "Unexpected token");
  });
}

void TestLargeDoubleValueAsInt64(const std::string& json_str,
                                 int64_t expected_value, bool expect_ok) {
  auto js = formats::js::FromString(json_str);
  int64_t parsed_value = 0;
  if (expect_ok) {
    EXPECT_NO_THROW(parsed_value = js["value"].As<int64_t>())
        << "js: " << json_str;
    EXPECT_EQ(parsed_value, expected_value)
        << "js: " << json_str
        << ", parsed double: " << js["value"].As<double>();
  } else {
    EXPECT_THROW(parsed_value = js["value"].As<int64_t>(),
                 formats::js::TypeMismatchException)
        << "js: " << json_str;
  }
}

class TestIncorrectValueException : public std::runtime_error {
 public:
  using std::runtime_error::runtime_error;
};

void CheckExactValues(int bits) {
  int64_t start = (1L << bits);
  for (int add = -20; add <= 0; ++add) {
    int64_t value = start + add;
    std::string json_str = R"({"value": )" + std::to_string(value) + ".0}";
    auto js = formats::js::FromString(json_str);
    double dval = js["value"].As<double>();
    int64_t ival = static_cast<int64_t>(dval);
    if (ival != value) throw TestIncorrectValueException("test");
  }
}

TEST_F(JsValue, LargeDoubleValueAsInt64) {
  ExecuteInV8([]() {
    const int kMaxCorrectBits = 53;

    for (int bits = kMaxCorrectBits; bits >= kMaxCorrectBits - 5; --bits) {
      int64_t start = (1L << bits);
      int max_add = bits == kMaxCorrectBits ? -1 : 20;
      for (int add = max_add; add >= -20; --add) {
        int64_t value = start + add;
        std::string json_str = R"({"value": )" + std::to_string(value) + ".0}";
        TestLargeDoubleValueAsInt64(json_str, value, true);
        json_str = R"({"value": )" + std::to_string(-value) + ".0}";
        TestLargeDoubleValueAsInt64(json_str, -value, true);
      }
    }

    EXPECT_THROW(CheckExactValues(kMaxCorrectBits + 1),
                 TestIncorrectValueException);

    // 2 ** 53 == 9007199254740992
    TestLargeDoubleValueAsInt64(R"({"value": 9007199254740992.0})",
                                9007199254740992, false);
    TestLargeDoubleValueAsInt64(R"({"value": 9007199254740993.0})",
                                9007199254740993, false);
    TestLargeDoubleValueAsInt64(R"({"value": -9007199254740992.0})",
                                -9007199254740992, false);
    TestLargeDoubleValueAsInt64(R"({"value": -9007199254740993.0})",
                                -9007199254740993, false);
  });
}

TEST_F(JsValue, ParseNanInf) {
  ExecuteInV8([]() {
    EXPECT_THROW(FromString(R"({"field": NaN})"), ParseException);
    EXPECT_THROW(FromString(R"({"field": Inf})"), ParseException);
    EXPECT_THROW(FromString(R"({"field": -Inf})"), ParseException);
  });
}

TEST_F(JsValue, NulString) {
  ExecuteInV8([]() {
    std::string i_contain_nuls = "test";
    i_contain_nuls += '\x00';
    i_contain_nuls += "test";

    auto s = formats::js::ValueBuilder(i_contain_nuls)
                 .ExtractValue()
                 .As<std::string>();
    EXPECT_EQ(i_contain_nuls, s);
  });
}

TEST_F(JsValue, NullAsDefaulted) {
  ExecuteInV8([]() {
    auto js = FromString(R"~({"nulled": null})~");

    EXPECT_EQ(js["nulled"].As<int>({}), 0);
    EXPECT_EQ(js["nulled"].As<std::vector<int>>({}), std::vector<int>{});

    EXPECT_EQ(js["nulled"].As<int>(42), 42);

    std::vector<int> value{4, 2};
    EXPECT_EQ(js["nulled"].As<std::vector<int>>(value), value);
  });
}

TEST_F(JsValue, Iterator) {
  ExecuteInV8([]() {
    auto value = formats::js::FromString(R"(
      {
        "a": {
          "a": 1,
          "b": 2,
          "c": 3,
          "d": 4,
          "e": 5,
          "f": 6
        },
        "b": [1, 2, 3, 4, 5, 6]
      }
    )");

    std::string keys;
    uint32_t sum = 0;

    for (const auto& [key, property] : formats::common::Items(value["a"])) {
      keys += key;
      sum += property.As<uint32_t>();
    }

    for (const auto& item : value["b"]) {
      sum += item.As<uint32_t>();
    }

    EXPECT_EQ("abcdef", keys);
    EXPECT_EQ(42, sum);
  });
}

TEST_F(JsValue, ExampleUsage) {
  ExecuteInV8([]() {
    /// [Sample formats::js::Value usage]
    // #include <formats/js/serialize.hpp>

    formats::js::Value js = formats::js::FromString(R"({
      "key1": 1,
      "key2": {"key3":"val"}
    })");

    const auto key1 = js["key1"].As<int>();
    EXPECT_EQ(key1, 1);

    const auto key3 = js["key2"]["key3"].As<std::string>();
    EXPECT_EQ(key3, "val");
    /// [Sample formats::js::Value usage]
  });
}

/// [Sample formats::js::Value::As<T>() usage]
namespace my_namespace {

struct MyKeyValue {
  std::string field1;
  int field2;
};
//  The function must be declared in the namespace of your type
MyKeyValue Parse(const formats::js::Value& js, formats::parse::To<MyKeyValue>) {
  return MyKeyValue{
      js["field1"].As<std::string>(""),
      js["field2"].As<int>(1),  // return `1` if "field2" is missing
  };
}

TEST_F(JsValue, ExampleUsageMyStruct) {
  ExecuteInV8([]() {
    formats::js::Value js = formats::js::FromString(R"({
      "my_value": {
          "field1": "one",
          "field2": 1
      }
    })");
    auto data = js["my_value"].As<MyKeyValue>();
    EXPECT_EQ(data.field1, "one");
    EXPECT_EQ(data.field2, 1);
  });
}
}  // namespace my_namespace
/// [Sample formats::js::Value::As<T>() usage]
