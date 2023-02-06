#include <gtest/gtest.h>

#include "json_adapter.hpp"

namespace {
struct TestStruct {
  std::string StringField1;
  int IntField1;
  double DoubleField1;
};

struct TestStruct2 {
  std::string StringField1;
  TestStruct StructField1;
};

JSON_SERIALIZABLE(TestStruct, StringField1, IntField1, DoubleField1)
JSON_SERIALIZABLE(TestStruct2, StringField1, StructField1)

}  // namespace

TEST(json_adapter, flat_struct) {
  TestStruct st{"String1", 42, 3.14};
  Json::Value res = PackToJson(st);
  ASSERT_EQ(res["StringField1"].asString(), "String1");
  ASSERT_EQ(res["IntField1"].asInt(), 42);
  ASSERT_EQ(res["DoubleField1"].asDouble(), 3.140000);
}

TEST(json_adapter, compund_struct) {
  TestStruct2 st{"String1", {"String1", 42, 3.14}};
  Json::Value res = PackToJson(st);
  ASSERT_EQ(res["StringField1"].asString(), "String1");
  ASSERT_EQ(res["StructField1"]["StringField1"].asString(), "String1");
  ASSERT_EQ(res["StructField1"]["IntField1"].asInt(), 42);
  ASSERT_EQ(res["StructField1"]["DoubleField1"].asDouble(), 3.140000);
}
