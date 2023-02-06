#include "bson.hpp"

#include <gtest/gtest.h>

class Bson2Json : public testing::Test {
 public:
  Bson2Json() : bson_obj_(GenerateBson()) {}

  template <typename T>
  static Json::Value Call(const T& obj) {
    return utils::helpers::Bson2Json(obj);
  }

  // void SetUp() override {}
  // void TearDown() override {}

 protected:
  mongo::BSONObj bson_obj_;

 private:
  static mongo::BSONObj GenerateBson() {
    mongo::BSONObjBuilder builder;

    builder.appendNull("null");

    builder.appendNumber("int", static_cast<int>(13));
    builder.appendNumber("long", static_cast<long long>(14));
    builder.appendDate("date", 15);
    builder.appendTimestamp("timestamp", mongo::Timestamp_t(16, 0));

    builder.appendNumber("double", 3.1415);

    builder.appendBool("bool", true);

    builder.append("str", "hello_world");

    builder.append("array", BSON_ARRAY("a"
                                       << "b"
                                       << "c"));

    return builder.obj();
  }
};

TEST_F(Bson2Json, nullValue) {
  EXPECT_EQ(Json::nullValue, Call(bson_obj_["null"]).type());
}

TEST_F(Bson2Json, intValue) {
  EXPECT_EQ(Json::intValue, Call(bson_obj_["int"]).type());
  EXPECT_EQ(Json::intValue, Call(bson_obj_["long"]).type());
  EXPECT_EQ(Json::intValue, Call(bson_obj_["date"]).type());
  EXPECT_EQ(Json::intValue, Call(bson_obj_["timestamp"]).type());
}

TEST_F(Bson2Json, realValue) {
  EXPECT_EQ(Json::realValue, Call(bson_obj_["double"]).type());
}

TEST_F(Bson2Json, booleanValue) {
  EXPECT_EQ(Json::booleanValue, Call(bson_obj_["bool"]).type());
}

TEST_F(Bson2Json, stringValue) {
  EXPECT_EQ(Json::stringValue, Call(bson_obj_["str"]).type());
}

TEST_F(Bson2Json, arrayValue) {
  EXPECT_EQ(Json::arrayValue, Call(bson_obj_["array"]).type());
}

TEST_F(Bson2Json, objectValue) {
  EXPECT_EQ(Json::objectValue, Call(bson_obj_).type());
}

TEST(BsonArray2Json, StringArray) {
  const char* array[] = {"a", "b", "c"};
  const auto size = sizeof(array) / sizeof(*array);

  const auto& json_arr =
      utils::helpers::Bson2Json(BSON_ARRAY(array[0] << array[1] << array[2]));
  ASSERT_EQ(Json::arrayValue, json_arr.type());

  ASSERT_EQ(size, json_arr.size());
  for (auto i = Json::ArrayIndex{0}; i < size; ++i) {
    ASSERT_EQ(Json::stringValue, json_arr[i].type());
    EXPECT_STREQ(array[i], json_arr[i].asString().c_str());
  }
}

TEST(BSONFieldFromJSON, StrictInt) {
  mongo::BSONObjBuilder builder_from_json;
  utils::helpers::BSONFieldFromJSON(builder_from_json, "small_int",
                                    Json::Value(1));
  utils::helpers::BSONFieldFromJSON(
      builder_from_json, "big_int", Json::Value(Json::Int64{1l << 36}),
      utils::helpers::BSONConversionFlags::StrictInt);
  mongo::BSONObjBuilder builder;
  builder.append("small_int", 1);
  builder.appendIntOrLL("big_int", 1ll << 36);
  auto from_json = builder_from_json.obj();
  ASSERT_EQ(from_json, builder.obj());
  ASSERT_EQ(from_json.getField("big_int").type(), mongo::BSONType::NumberLong);
}

TEST(BSONFieldFromJSON, StrictIntComplexObject) {
  mongo::BSONObjBuilder builder_from_json;
  Json::Value json_obj(Json::objectValue);
  json_obj["big_int"] = Json::Int64{3l << 36};
  utils::helpers::BSONFieldFromJSON(
      builder_from_json, "complex_object", json_obj,
      utils::helpers::BSONConversionFlags::StrictInt);
  mongo::BSONObjBuilder complex_object_builder;
  complex_object_builder.appendIntOrLL("big_int", 3l << 36);
  mongo::BSONObjBuilder builder;
  builder.append("complex_object", complex_object_builder.obj());
  auto bson_from_json = builder_from_json.obj();
  ASSERT_EQ(bson_from_json, builder.obj());
  ASSERT_EQ(bson_from_json["complex_object"]["big_int"].type(),
            mongo::BSONType::NumberLong);
}

TEST(BSONFieldFromJSON, NoStrictInt) {
  mongo::BSONObjBuilder builder_from_json;
  utils::helpers::BSONFieldFromJSON(builder_from_json, "small_int",
                                    Json::Value(1));
  utils::helpers::BSONFieldFromJSON(builder_from_json, "big_int",
                                    Json::Value(Json::Int64{1l << 36}));
  mongo::BSONObjBuilder builder;
  builder.append("small_int", 1);
  builder.appendNumber("big_int", 1ll << 36);
  ASSERT_EQ(builder_from_json.obj(), builder.obj());
}

TEST(ApplyBsonPatch, OnlySet) {
  mongo::BSONObjBuilder source;
  source << "a"
         << "b"
         << "c"
         << "d";

  mongo::BSONObjBuilder set;
  set << "a"
      << "x"
      << "y"
      << "z";

  mongo::BSONObjBuilder expected;
  expected << "c"
           << "d"
           << "a"
           << "x"
           << "y"
           << "z";

  auto actual = utils::helpers::ApplyBsonPatch(source.obj(), set.obj(), {});

  ASSERT_EQ(actual, expected.obj());
}

TEST(ApplyBsonPatch, OnlyUnset) {
  mongo::BSONObjBuilder source;
  source << "a"
         << "b"
         << "c"
         << "d";

  mongo::BSONObjBuilder unset;
  unset << "a" << 1;

  mongo::BSONObjBuilder expected;
  expected << "c"
           << "d";

  auto actual = utils::helpers::ApplyBsonPatch(source.obj(), {}, unset.obj());

  ASSERT_EQ(actual, expected.obj());
}

TEST(ApplyBsonPatch, SetAndUnset) {
  mongo::BSONObjBuilder source;
  source << "a"
         << "b"
         << "c"
         << "d";

  mongo::BSONObjBuilder set;
  set << "a"
      << "x"
      << "y"
      << "z";

  mongo::BSONObjBuilder unset;
  unset << "a" << 1 << "y" << 1;

  mongo::BSONObjBuilder expected;
  expected << "c"
           << "d";

  auto actual =
      utils::helpers::ApplyBsonPatch(source.obj(), set.obj(), unset.obj());

  ASSERT_EQ(actual, expected.obj());
}
