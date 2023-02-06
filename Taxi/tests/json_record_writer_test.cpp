#include "json_record_writer.hpp"

#include <gtest/gtest.h>
#include <cstring>

namespace {
struct from_to {
  const char* const test_name;
  const std::string_view in_key;
  const std::string_view in_value;
  const char* const result;
  const char* const result_simple_bypass = nullptr;
};

inline std::string PrintToString(const from_to& d) { return d.test_name; }

using FromTo = std::initializer_list<from_to>;
using Escaping = utils::JsonRecordWriter::Escaping;
}  // namespace

class StreamJsonTest : public ::testing::TestWithParam<from_to> {};

INSTANTIATE_TEST_SUITE_P(
    /*no prefix*/, StreamJsonTest,
    ::testing::ValuesIn(FromTo{
        {"basic", "key", "value", R"({"key":"value"})"},
        {"special_chars", "\n\r\b\f", "\f\b\r\n", R"({"\n\r\b\f":"\f\b\r\n"})"},
        {"quotes", "qwe\"qwe", "\"qwe\"", R"({"qwe\"qwe":"\"qwe\""})"},
        {"slash_zero", {"\\\0", 2}, {"\\\0", 2}, R"({"\\\u0000":"\\\u0000"})"},
        {"json_spec_chars", "\1\2\3", "\x1f\x1a\x0f",
         R"({"\u0001\u0002\u0003":"\u001f\u001a\u000f"})"},

        {"utf8_invalid_code_point", "\xc0\xaf", "\xe0\x9f\x80",
         R"({"\\0xc0\\0xaf":"\\0xe0\\0x9f\\0x80"})"},

        {"utf8_valid_code_points", "\xf4\x80\x83\x92", "\xed\x80\xbf",
         "{\"\xf4\x80\x83\x92\":\"\xed\x80\xbf\"}"},

        {"special_chars_escaped", "\\n\\r\\b\\f", "\\f\\b\\r\\n",
         R"({"\\n\\r\\b\\f":"\\f\\b\\r\\n"})", R"({"\n\r\b\f":"\f\b\r\n"})"},

        {"utf8_valid_escaped", "\\u0001\\u0002\\u0003", "\\u001f\\u001a\\u000f",
         R"({"\\u0001\\u0002\\u0003":"\\u001f\\u001a\\u000f"})",
         R"({"\u0001\u0002\u0003":"\u001f\u001a\u000f"})"},

        {"utf8_upper_escaped", "\\u0001\\u0002\\u0003", "\\u001F\\u001A\\u000F",
         R"({"\\u0001\\u0002\\u0003":"\\u001F\\u001A\\u000F"})",
         R"({"\u0001\u0002\u0003":"\u001F\u001A\u000F"})"},

        {"from_prod", "body",
         R"(\\"name\\":\\"Россия\\",\\"source_id\\":\\"8053926\\",\\"title\\":\\"Неглинная улица\\")",
         R"({"body":"\\\\\"name\\\\\":\\\\\"Россия\\\\\",\\\\\"source_id\\\\\":\\\\\"8053926\\\\\",\\\\\"title\\\\\":\\\\\"Неглинная улица\\\\\""})",
         R"({"body":"\\\"name\\\":\\\"Россия\\\",\\\"source_id\\\":\\\"8053926\\\",\\\"title\\\":\\\"Неглинная улица\\\""})"},
    }),
    ::testing::PrintToStringParamName());

TEST_P(StreamJsonTest, EsacpeAll) {
  std::string res;
  auto d = GetParam();
  utils::JsonRecordWriter{res, Escaping::EscapeAll}.AddKeyValue(d.in_key,
                                                                d.in_value);
  EXPECT_EQ(res, d.result);
}

TEST_P(StreamJsonTest, SimpleEsacpeBypass) {
  std::string res;
  auto d = GetParam();
  utils::JsonRecordWriter{res, Escaping::SimpleEscapeBypass}.AddKeyValue(
      d.in_key, d.in_value);
  EXPECT_EQ(res, d.result_simple_bypass ? d.result_simple_bypass : d.result);
}

TEST(StreamJson2Fields, ComasValidation) {
  std::string res;

  utils::JsonRecordWriter{res, Escaping::EscapeAll}
      .AddKeyValue("key1", "value1")
      .AddKeyValue("key2", "value2");

  EXPECT_EQ(res, R"({"key1":"value1","key2":"value2"})");
}

TEST(StreamJson2Fields, Raw) {
  std::string res;
  utils::JsonRecordWriter{res, Escaping::EscapeAll}
      .AddRawData(R"("key1":"value1")")
      .AddRawData(R"("key2":"value2")");

  EXPECT_EQ(res, R"({"key1":"value1","key2":"value2"})");
}

TEST(StreamJson2Fields, EscapeAndRaw) {
  std::string res;
  utils::JsonRecordWriter{res, Escaping::EscapeAll}
      .AddKeyValue("key0", "value0")
      .AddRawData(R"("key1":"value1")")
      .AddRawData(R"("key2":"value2")");

  EXPECT_EQ(res, R"({"key0":"value0","key1":"value1","key2":"value2"})");
}

TEST(JsonArrayValues, TestEmptyArray) {
  std::string res;
  utils::JsonRecordWriter{res, Escaping::EscapeAll}
      .AddKey("empty_array")
      .StartArray()
      .FinishArray();
  EXPECT_EQ(res, R"({"empty_array":[]})");
}

TEST(JsonArrayValues, TestStringArray) {
  std::string res;
  utils::JsonRecordWriter{res, Escaping::EscapeAll}
      .AddKey("string_array")
      .StartArray()
      .AddValue("element1")
      .AddValue("element2")
      .FinishArray();
  EXPECT_EQ(res, R"({"string_array":["element1","element2"]})");
}

TEST(JsonArrayValues, TestNumbersArray) {
  std::string res;
  utils::JsonRecordWriter{res, Escaping::EscapeAll}
      .AddKey("string_array")
      .StartArray()
      .AddRawValue("123")
      .AddRawValue("456")
      .FinishArray();
  EXPECT_EQ(res, R"({"string_array":[123,456]})");
}

TEST(JsonArrayValues, TestObjectsArray) {
  std::string res;
  {
    utils::JsonRecordWriter writer{res, Escaping::EscapeAll};
    writer.AddKey("object_array").StartArray();
    writer.StartObject().AddKeyValue("key1", "value1").FinishObject();
    writer.StartObject().AddKeyValue("key1", "value2").FinishObject();
    writer.FinishArray();
  }
  EXPECT_EQ(res, R"({"object_array":[{"key1":"value1"},{"key1":"value2"}]})");
}

TEST(JsonObjectValues, TestObjectValue) {
  std::string res;
  utils::JsonRecordWriter{res, Escaping::EscapeAll}
      .AddKey("object")
      .StartObject()
      .AddKeyValue("key1", "value1")
      .AddKeyValue("key2", "value2")
      .FinishObject();
  EXPECT_EQ(res, R"({"object":{"key1":"value1","key2":"value2"}})");
}
