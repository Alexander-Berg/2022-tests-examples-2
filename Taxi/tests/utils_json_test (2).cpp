#include <userver/utest/utest.hpp>

#include <utils/json.hpp>

#include <userver/formats/json/value_builder.hpp>

namespace {

formats::json::Value BuildObj1() {
  formats::json::ValueBuilder obj(formats::json::Type::kObject);
  obj["key1"] = "value1";

  formats::json::ValueBuilder subobj;
  subobj["int"] = 1;
  subobj["str"] = "one";
  subobj["num"] = 2.0;
  obj["key2"] = subobj.ExtractValue();

  return obj.ExtractValue();
}

formats::json::Value BuildObj2() {
  formats::json::ValueBuilder obj(formats::json::Type::kObject);
  obj["key2"] = "two";
  obj["key3"] = 10;
  return obj.ExtractValue();
}

formats::json::Value BuildMergedObj12() {
  formats::json::ValueBuilder obj(formats::json::Type::kObject);
  obj["key1"] = "value1";

  formats::json::ValueBuilder subobj;
  subobj["int"] = 1;
  subobj["str"] = "one";
  subobj["num"] = 2.0;
  obj["key2"] = subobj.ExtractValue();

  obj["key3"] = 10;
  return obj.ExtractValue();
}

formats::json::Value BuildMergedObj21() {
  formats::json::ValueBuilder obj(formats::json::Type::kObject);
  obj["key1"] = "value1";
  obj["key2"] = "two";
  obj["key3"] = 10;
  return obj.ExtractValue();
}

}  // namespace

TEST(Json, MergeJsonObjects) {
  const auto obj1 = BuildObj1();
  const auto obj2 = BuildObj2();
  const auto obj12 = BuildMergedObj12();
  const auto obj21 = BuildMergedObj21();

  EXPECT_EQ(utils::MergeJsonObjects(obj1, obj2), obj12);
  EXPECT_EQ(utils::MergeJsonObjects(obj2, obj1), obj21);
  EXPECT_EQ(utils::MergeJsonObjects(obj1, obj1), obj1);
  EXPECT_EQ(utils::MergeJsonObjects(obj2, obj2), obj2);
}
