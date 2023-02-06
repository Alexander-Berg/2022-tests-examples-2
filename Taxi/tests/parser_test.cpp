#include <gtest/gtest.h>

#include "api-over-data/parser/parser.hpp"

#include <mongo/bson/bsonmisc.h>
#include <mongo/mongo.hpp>
namespace {
::mongo::BSONObj MakeTestDocument() {
  return ::mongo::BSONObjBuilder()
      .append("inner_int_row", 123)
      .append("inner_string_row", "inner_string_row")
      .append("int_row", 345)
      .append("string_row", "string_row")
      .obj();
}

struct Inner {
  int inner_int_row = 0;
  std::string inner_string_row = "";
};

struct TestStruct {
  Inner inner;
  std::string string_row = "";
  int int_row = 0;
};

inline std::string UnpackString(const ::mongo::BSONObj& doc) {
  return utils::mongo::ToString(doc["string_row"]);
}

inline int UnpackInt(const ::mongo::BSONObj& doc) {
  return utils::mongo::ToInt(doc["int_row"]);
}

inline std::string UnpackInnerString(const ::mongo::BSONObj& doc) {
  return utils::mongo::ToString(doc["inner_string_row"]);
}

inline int UnpackInnerInt(const ::mongo::BSONObj& doc) {
  return utils::mongo::ToInt(doc["inner_int_row"]);
}
}  // namespace
TEST(Parser, ParserTest) {
  api_over_data::Parser<TestStruct> parser;
  api_over_data::Parser<Inner> inner_parser;
  inner_parser.AddParserOption(&Inner::inner_int_row, UnpackInnerInt)
      .AddParserOption(&Inner::inner_string_row, UnpackInnerString);
  parser.AddParserOption(&TestStruct::int_row, UnpackInt)
      .AddParserOption(&TestStruct::string_row, UnpackString)
      .AddParserOption(&TestStruct::inner, inner_parser);
  auto result = parser.Parse(MakeTestDocument());
  EXPECT_EQ(result.int_row, 345);
  EXPECT_EQ(result.inner.inner_int_row, 123);
  EXPECT_EQ(result.string_row, "string_row");
  EXPECT_EQ(result.inner.inner_string_row, "inner_string_row");
}
