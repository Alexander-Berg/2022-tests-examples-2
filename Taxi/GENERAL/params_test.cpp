#include "utils/helpers/params.hpp"

#include <gtest/gtest.h>

class HelpersParams_GetMember : public testing::Test {
 public:
  HelpersParams_GetMember()
      : params_(GenerateJson()), bson_obj_(GenerateBson()) {}

  // void SetUp() override {}
  // void TearDown() override {}

 protected:
  utils::helpers::Params params_;
  mongo::BSONObj bson_obj_;

 private:
  static Json::Value GenerateJson() {
    Json::Value doc;

    doc["null"] = Json::nullValue;

    doc["str"] = "Hello";
    doc["int"] = -42;
    doc["uint"] = 42;
    doc["biguint"] = unsigned(Json::Value::maxInt) + 1;
    doc["double"] = 3.1415;
    doc["bool"] = true;

    doc["time_num"] = 1485437855;
    doc["time_str"] = "2017-01-26T16:37:35+0300";
    doc["time_str_ms"] = "2017-01-26T13:37:35.000Z";

    Json::Value arr(Json::arrayValue);
    arr.append("a");
    arr.append("b");
    arr.append("c");
    doc["arr"] = arr;

    Json::Value gpoint(Json::arrayValue);
    gpoint.append(1.11);
    gpoint.append(2.22);
    doc["gpoint"] = gpoint;

    Json::Value gpoint_int(Json::arrayValue);
    gpoint_int.append(1);
    gpoint_int.append(2);
    doc["gpoint_int"] = gpoint_int;

    Json::Value obj_string(Json::objectValue);
    obj_string["str1"] = "Hello";
    obj_string["str2"] = "World";
    doc["obj_string"] = obj_string;

    Json::Value obj_double(Json::objectValue);
    obj_double["double1"] = 1.2345;
    obj_double["double2"] = 2.3456;
    doc["obj_double"] = obj_double;

    Json::Value obj_arr(Json::objectValue);
    Json::Value sub_set1(Json::arrayValue);
    sub_set1.append("element1");
    sub_set1.append("element2");
    Json::Value sub_set2(Json::arrayValue);
    sub_set2.append("element3");
    sub_set2.append("element4");
    obj_arr["set1"] = sub_set1;
    obj_arr["set2"] = sub_set2;
    doc["obj_arr"] = obj_arr;

    Json::Value obj_obj(Json::objectValue);
    obj_obj["obj1"] = obj_string;
    Json::Value obj_string2(Json::objectValue);
    obj_string2["str1"] = "olleH";
    obj_string2["str2"] = "dlroW";
    obj_obj["obj2"] = obj_string2;
    doc["obj_obj"] = obj_obj;

    return doc;
  }

  static mongo::BSONObj GenerateBson() {
    mongo::BSONObjBuilder builder;

    builder.appendNull("null");

    builder.append("str", "Hello");
    builder.append("uint", 42);
    builder.append("double", 3.1415);
    builder.append("bool", true);

    builder.append("arr", BSON_ARRAY("a"
                                     << "b"
                                     << "c"));
    builder.append("gpoint", BSON_ARRAY(1.11 << 2.22));
    builder.append("gpoint_int", BSON_ARRAY(1 << 2));

    mongo::BSONObjBuilder map_builder;
    map_builder.appendNumber("field1", 552);
    map_builder.appendNumber("field2", 34);
    map_builder.appendNumber("field3", 70);
    map_builder.appendNumber("field4", 1354);
    builder.append("map", map_builder.obj());

    return builder.obj();
  }
};

TEST_F(HelpersParams_GetMember, String) {
  std::string str;

  EXPECT_THROW(params_.Fetch(str, "none"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(str, "null"), utils::helpers::JsonParseError);

  EXPECT_NO_THROW(params_.Fetch(str, "str"));
  EXPECT_STREQ("Hello", str.c_str());

  EXPECT_THROW(params_.Fetch(str, "uint"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(str, "double"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(str, "bool"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(str, "arr"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(str, "gpoint"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(str, "obj_string"),
               utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(str, "obj_double"),
               utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(str, "obj_arr"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(str, "obj_obj"), utils::helpers::JsonParseError);
}

TEST_F(HelpersParams_GetMember, OptionalString) {
  boost::optional<std::string> str;

  EXPECT_NO_THROW(params_.Fetch(str, "none"));
  EXPECT_FALSE(str);

  EXPECT_NO_THROW(params_.Fetch(str, "null"));
  EXPECT_FALSE(str);

  EXPECT_NO_THROW(params_.Fetch(str, "str"));
  ASSERT_TRUE(!!str);
  EXPECT_STREQ("Hello", str->c_str());

  EXPECT_THROW(params_.Fetch(str, "int"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(str, "uint"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(str, "double"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(str, "bool"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(str, "arr"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(str, "gpoint"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(str, "obj_string"),
               utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(str, "obj_double"),
               utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(str, "obj_arr"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(str, "obj_obj"), utils::helpers::JsonParseError);
}

TEST_F(HelpersParams_GetMember, Unsigned) {
  unsigned num = 0;

  EXPECT_THROW(params_.Fetch(num, "none"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(num, "null"), utils::helpers::JsonParseError);

  EXPECT_NO_THROW(params_.Fetch(num, "uint"));
  EXPECT_EQ(42u, num);

  EXPECT_NO_THROW(params_.Fetch(num, "double"));
  EXPECT_EQ(3u, num);

  EXPECT_THROW(params_.Fetch(num, "int"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.FetchOptional(num, "int"),
               utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(num, "str"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(num, "bool"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(num, "arr"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(num, "gpoint"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(num, "obj_string"),
               utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(num, "obj_double"),
               utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(num, "obj_arr"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(num, "obj_obj"), utils::helpers::JsonParseError);
}

TEST_F(HelpersParams_GetMember, OptionalUnsigned) {
  boost::optional<unsigned> num;

  EXPECT_NO_THROW(params_.Fetch(num, "none"));
  EXPECT_FALSE(num);

  EXPECT_NO_THROW(params_.Fetch(num, "null"));
  EXPECT_FALSE(num);

  EXPECT_NO_THROW(params_.Fetch(num, "uint"));
  ASSERT_TRUE(!!num);
  EXPECT_EQ(42u, num.get());

  EXPECT_NO_THROW(params_.Fetch(num, "biguint"));
  ASSERT_TRUE(!!num);
  EXPECT_EQ(unsigned(Json::Value::maxInt) + 1, num.get());

  EXPECT_NO_THROW(params_.Fetch(num, "double"));
  ASSERT_TRUE(!!num);
  EXPECT_EQ(3u, num.get());
  EXPECT_THROW(params_.Fetch(num, "int"), utils::helpers::JsonParseError);

  EXPECT_THROW(params_.Fetch(num, "str"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(num, "bool"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(num, "arr"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(num, "gpoint"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(num, "obj_string"),
               utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(num, "obj_double"),
               utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(num, "obj_arr"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(num, "obj_obj"), utils::helpers::JsonParseError);
}

TEST_F(HelpersParams_GetMember, Signed) {
  int num = 0;

  EXPECT_THROW(params_.Fetch(num, "none"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(num, "null"), utils::helpers::JsonParseError);

  EXPECT_NO_THROW(params_.Fetch(num, "int"));
  EXPECT_EQ(-42, num);

  EXPECT_NO_THROW(params_.Fetch(num, "uint"));
  EXPECT_EQ(42, num);

  EXPECT_NO_THROW(params_.Fetch(num, "double"));
  EXPECT_EQ(3, num);

  EXPECT_THROW(params_.Fetch(num, "biguint"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(num, "str"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(num, "bool"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(num, "arr"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(num, "gpoint"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(num, "obj_string"),
               utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(num, "obj_double"),
               utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(num, "obj_arr"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(num, "obj_obj"), utils::helpers::JsonParseError);
}

TEST_F(HelpersParams_GetMember, OptionalSigned) {
  boost::optional<int> num;

  EXPECT_NO_THROW(params_.Fetch(num, "none"));
  EXPECT_FALSE(num);

  EXPECT_NO_THROW(params_.Fetch(num, "null"));
  EXPECT_FALSE(num);

  EXPECT_NO_THROW(params_.Fetch(num, "uint"));
  ASSERT_TRUE(!!num);
  EXPECT_EQ(42, num.get());

  EXPECT_NO_THROW(params_.Fetch(num, "double"));
  ASSERT_TRUE(!!num);
  EXPECT_EQ(3, num.get());

  EXPECT_NO_THROW(params_.Fetch(num, "int"));
  ASSERT_TRUE(!!num);
  EXPECT_EQ(-42, num.get());

  EXPECT_THROW(params_.Fetch(num, "biguint"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(num, "str"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(num, "bool"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(num, "arr"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(num, "gpoint"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(num, "obj_string"),
               utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(num, "obj_double"),
               utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(num, "obj_arr"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(num, "obj_obj"), utils::helpers::JsonParseError);
}

TEST_F(HelpersParams_GetMember, Double) {
  double num = 0;

  EXPECT_THROW(params_.Fetch(num, "none"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(num, "null"), utils::helpers::JsonParseError);

  EXPECT_NO_THROW(params_.Fetch(num, "uint"));
  EXPECT_DOUBLE_EQ(42.0, num);

  EXPECT_NO_THROW(params_.Fetch(num, "double"));
  EXPECT_DOUBLE_EQ(3.1415, num);

  EXPECT_THROW(params_.Fetch(num, "str"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(num, "bool"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(num, "arr"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(num, "gpoint"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(num, "obj_string"),
               utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(num, "obj_double"),
               utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(num, "obj_arr"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(num, "obj_obj"), utils::helpers::JsonParseError);
}

TEST_F(HelpersParams_GetMember, OptionalDouble) {
  boost::optional<double> num;

  EXPECT_NO_THROW(params_.Fetch(num, "none"));
  EXPECT_FALSE(num);

  EXPECT_NO_THROW(params_.Fetch(num, "null"));
  EXPECT_FALSE(num);

  EXPECT_NO_THROW(params_.Fetch(num, "uint"));
  ASSERT_TRUE(!!num);
  EXPECT_DOUBLE_EQ(42.0, num.get());

  EXPECT_NO_THROW(params_.Fetch(num, "double"));
  ASSERT_TRUE(!!num);
  EXPECT_DOUBLE_EQ(3.1415, num.get());

  EXPECT_THROW(params_.Fetch(num, "str"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(num, "bool"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(num, "arr"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(num, "gpoint"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(num, "obj_string"),
               utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(num, "obj_double"),
               utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(num, "obj_arr"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(num, "obj_obj"), utils::helpers::JsonParseError);
}

TEST_F(HelpersParams_GetMember, Bool) {
  bool flag = false;

  EXPECT_THROW(params_.Fetch(flag, "none"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(flag, "null"), utils::helpers::JsonParseError);

  EXPECT_NO_THROW(params_.Fetch(flag, "bool"));
  EXPECT_TRUE(flag);

  EXPECT_THROW(params_.Fetch(flag, "str"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(flag, "uint"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(flag, "double"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(flag, "arr"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(flag, "gpoint"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(flag, "obj_string"),
               utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(flag, "obj_double"),
               utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(flag, "obj_arr"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(flag, "obj_obj"), utils::helpers::JsonParseError);
}

TEST_F(HelpersParams_GetMember, OptionalBool) {
  boost::optional<bool> flag;

  EXPECT_NO_THROW(params_.Fetch(flag, "none"));
  EXPECT_FALSE(flag);

  EXPECT_NO_THROW(params_.Fetch(flag, "null"));
  EXPECT_FALSE(flag);

  EXPECT_NO_THROW(params_.Fetch(flag, "bool"));
  ASSERT_TRUE(!!flag);
  EXPECT_TRUE(flag.get());

  EXPECT_THROW(params_.Fetch(flag, "str"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(flag, "uint"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(flag, "double"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(flag, "arr"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(flag, "gpoint"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(flag, "obj_string"),
               utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(flag, "obj_double"),
               utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(flag, "obj_arr"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(flag, "obj_obj"), utils::helpers::JsonParseError);
}

TEST_F(HelpersParams_GetMember, Time) {
  utils::TimePoint time;

  EXPECT_THROW(params_.Fetch(time, "none"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(time, "null"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(time, "bool"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(time, "str"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(time, "arr"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(time, "gpoint"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(time, "obj_string"),
               utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(time, "obj_double"),
               utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(time, "obj_arr"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(time, "obj_obj"), utils::helpers::JsonParseError);

  EXPECT_NO_THROW(params_.Fetch(time, "time_num"));
  EXPECT_NE(0, time.time_since_epoch().count());

  for (const char* name : {"time_str", "time_str_ms"}) {
    utils::TimePoint time_str;
    EXPECT_NO_THROW(params_.Fetch(time_str, name));
    EXPECT_NE(0, time_str.time_since_epoch().count()) << name;
    EXPECT_EQ(time, time_str) << name;
  }
}

TEST_F(HelpersParams_GetMember, Array) {
  std::set<std::string> arr;

  EXPECT_THROW(params_.Fetch(arr, "none"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(arr, "null"), utils::helpers::JsonParseError);

  EXPECT_NO_THROW(params_.Fetch(arr, "arr"));
  EXPECT_EQ(3u, arr.size());

  EXPECT_THROW(params_.Fetch(arr, "str"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(arr, "uint"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(arr, "double"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(arr, "bool"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(arr, "gpoint"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(arr, "obj_string"),
               utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(arr, "obj_double"),
               utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(arr, "obj_arr"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(arr, "obj_obj"), utils::helpers::JsonParseError);
}

TEST_F(HelpersParams_GetMember, OptionalArray) {
  boost::optional<std::set<std::string>> arr;

  EXPECT_NO_THROW(params_.Fetch(arr, "none"));
  EXPECT_FALSE(arr);

  EXPECT_NO_THROW(params_.Fetch(arr, "null"));
  EXPECT_FALSE(arr);

  EXPECT_NO_THROW(params_.Fetch(arr, "arr"));
  ASSERT_TRUE(!!arr);
  EXPECT_EQ(3u, arr->size());

  EXPECT_THROW(params_.Fetch(arr, "str"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(arr, "uint"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(arr, "double"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(arr, "bool"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(arr, "gpoint"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(arr, "obj_string"),
               utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(arr, "obj_double"),
               utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(arr, "obj_arr"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(arr, "obj_obj"), utils::helpers::JsonParseError);
}

TEST_F(HelpersParams_GetMember, GeoPoint) {
  utils::geometry::Point gpoint;

  EXPECT_THROW(params_.Fetch(gpoint, "none"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(gpoint, "null"), utils::helpers::JsonParseError);

  EXPECT_NO_THROW(params_.Fetch(gpoint, "gpoint"));
  EXPECT_DOUBLE_EQ(1.11, gpoint.lon);
  EXPECT_DOUBLE_EQ(2.22, gpoint.lat);

  EXPECT_NO_THROW(params_.Fetch(gpoint, "gpoint_int"));
  EXPECT_EQ(1, gpoint.lon);
  EXPECT_EQ(2, gpoint.lat);

  EXPECT_THROW(params_.Fetch(gpoint, "str"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(gpoint, "uint"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(gpoint, "double"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(gpoint, "bool"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(gpoint, "arr"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(gpoint, "obj_string"),
               utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(gpoint, "obj_double"),
               utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(gpoint, "obj_arr"),
               utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(gpoint, "obj_obj"),
               utils::helpers::JsonParseError);
}

TEST_F(HelpersParams_GetMember, OptionalGeoPoint) {
  boost::optional<utils::geometry::Point> gpoint;

  EXPECT_NO_THROW(params_.Fetch(gpoint, "none"));
  EXPECT_FALSE(gpoint);

  EXPECT_NO_THROW(params_.Fetch(gpoint, "null"));
  EXPECT_FALSE(gpoint);

  EXPECT_NO_THROW(params_.Fetch(gpoint, "gpoint"));
  ASSERT_TRUE(!!gpoint);
  EXPECT_DOUBLE_EQ(1.11, gpoint->lon);
  EXPECT_DOUBLE_EQ(2.22, gpoint->lat);

  EXPECT_THROW(params_.Fetch(gpoint, "str"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(gpoint, "uint"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(gpoint, "double"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(gpoint, "bool"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(gpoint, "arr"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(gpoint, "obj_string"),
               utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(gpoint, "obj_double"),
               utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(gpoint, "obj_arr"),
               utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(gpoint, "obj_obj"),
               utils::helpers::JsonParseError);
}

TEST_F(HelpersParams_GetMember, ObjectStrings) {
  std::unordered_map<std::string, std::string> obj_string;
  EXPECT_THROW(params_.Fetch(obj_string, "none"),
               utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(obj_string, "null"),
               utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(obj_string, "gpoint"),
               utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(obj_string, "str"),
               utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(obj_string, "uint"),
               utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(obj_string, "double"),
               utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(obj_string, "bool"),
               utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(obj_string, "arr"),
               utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(obj_string, "obj_double"),
               utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(obj_string, "obj_arr"),
               utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(obj_string, "obj_obj"),
               utils::helpers::JsonParseError);

  EXPECT_NO_THROW(params_.Fetch(obj_string, "obj_string"));
  EXPECT_EQ(2u, obj_string.size());
  EXPECT_STREQ("Hello", obj_string["str1"].c_str());
  EXPECT_STREQ("World", obj_string["str2"].c_str());
}

TEST_F(HelpersParams_GetMember, ObjectDoubles) {
  std::unordered_map<std::string, double> obj_double;
  EXPECT_THROW(params_.Fetch(obj_double, "none"),
               utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(obj_double, "null"),
               utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(obj_double, "gpoint"),
               utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(obj_double, "str"),
               utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(obj_double, "uint"),
               utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(obj_double, "double"),
               utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(obj_double, "bool"),
               utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(obj_double, "arr"),
               utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(obj_double, "obj_string"),
               utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(obj_double, "obj_arr"),
               utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(obj_double, "obj_obj"),
               utils::helpers::JsonParseError);

  EXPECT_NO_THROW(params_.Fetch(obj_double, "obj_double"));
  EXPECT_EQ(2u, obj_double.size());
  EXPECT_EQ(1.2345, obj_double["double1"]);
  EXPECT_EQ(2.3456, obj_double["double2"]);
}

TEST_F(HelpersParams_GetMember, ObjectSets) {
  std::map<std::string, std::set<std::string>> obj_arr;
  EXPECT_THROW(params_.Fetch(obj_arr, "none"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(obj_arr, "null"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(obj_arr, "gpoint"),
               utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(obj_arr, "str"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(obj_arr, "uint"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(obj_arr, "double"),
               utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(obj_arr, "bool"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(obj_arr, "arr"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(obj_arr, "obj_string"),
               utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(obj_arr, "obj_double"),
               utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(obj_arr, "obj_obj"),
               utils::helpers::JsonParseError);

  EXPECT_NO_THROW(params_.Fetch(obj_arr, "obj_arr"));
  EXPECT_NO_THROW(obj_arr.at("set1"));  //-V530
  EXPECT_NO_THROW(obj_arr.at("set2"));  //-V530
  auto& set1 = obj_arr["set1"];
  auto& set2 = obj_arr["set2"];
  EXPECT_TRUE(set1.find("element1") != set1.end());
  EXPECT_TRUE(set1.find("element2") != set1.end());
  EXPECT_TRUE(set2.find("element3") != set2.end());
  EXPECT_TRUE(set2.find("element4") != set2.end());
}

TEST_F(HelpersParams_GetMember, UnorderedObjectSets) {
  std::unordered_map<std::string, std::unordered_set<std::string>> obj_arr;
  EXPECT_THROW(params_.Fetch(obj_arr, "none"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(obj_arr, "null"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(obj_arr, "gpoint"),
               utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(obj_arr, "str"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(obj_arr, "uint"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(obj_arr, "double"),
               utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(obj_arr, "bool"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(obj_arr, "arr"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(obj_arr, "obj_string"),
               utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(obj_arr, "obj_double"),
               utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(obj_arr, "obj_obj"),
               utils::helpers::JsonParseError);

  EXPECT_NO_THROW(params_.Fetch(obj_arr, "obj_arr"));
  EXPECT_NO_THROW(obj_arr.at("set1"));  //-V530
  EXPECT_NO_THROW(obj_arr.at("set2"));  //-V530
  auto& set1 = obj_arr["set1"];
  auto& set2 = obj_arr["set2"];
  EXPECT_TRUE(set1.find("element1") != set1.end());
  EXPECT_TRUE(set1.find("element2") != set1.end());
  EXPECT_TRUE(set2.find("element3") != set2.end());
  EXPECT_TRUE(set2.find("element4") != set2.end());
}

TEST_F(HelpersParams_GetMember, UnorderedArrayArray) {
  std::unordered_map<std::string, std::unordered_map<std::string, std::string>>
      obj_obj;
  EXPECT_THROW(params_.Fetch(obj_obj, "none"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(obj_obj, "null"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(obj_obj, "gpoint"),
               utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(obj_obj, "str"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(obj_obj, "uint"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(obj_obj, "double"),
               utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(obj_obj, "bool"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(obj_obj, "arr"), utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(obj_obj, "obj_string"),
               utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(obj_obj, "obj_double"),
               utils::helpers::JsonParseError);
  EXPECT_THROW(params_.Fetch(obj_obj, "obj_arr"),
               utils::helpers::JsonParseError);

  EXPECT_NO_THROW(params_.Fetch(obj_obj, "obj_obj"));
  EXPECT_NO_THROW(obj_obj.at("obj1"));  //-V530
  EXPECT_NO_THROW(obj_obj.at("obj2"));  //-V530
  auto& obj_double = obj_obj["obj1"];
  auto& obj_string = obj_obj["obj2"];
  EXPECT_TRUE(obj_double["str1"] == "Hello");
  EXPECT_TRUE(obj_double["str2"] == "World");
  EXPECT_EQ(2u, obj_string.size());
  EXPECT_STREQ("olleH", obj_string["str1"].c_str());
  EXPECT_STREQ("dlroW", obj_string["str2"].c_str());
}

TEST_F(HelpersParams_GetMember, BsonArray) {
  using namespace utils::helpers;

  std::set<std::string> arr;

  EXPECT_THROW(FetchMember(arr, bson_obj_, "none"),
               utils::helpers::JsonParseError);
  EXPECT_THROW(FetchMember(arr, bson_obj_, "null"),
               utils::helpers::JsonParseError);

  EXPECT_NO_THROW(FetchMember(arr, bson_obj_, "arr"));
  EXPECT_EQ(3u, arr.size());

  EXPECT_THROW(FetchMember(arr, bson_obj_, "str"),
               utils::helpers::JsonParseError);
  EXPECT_THROW(FetchMember(arr, bson_obj_, "uint"),
               utils::helpers::JsonParseError);
  EXPECT_THROW(FetchMember(arr, bson_obj_, "double"),
               utils::helpers::JsonParseError);
  EXPECT_THROW(FetchMember(arr, bson_obj_, "bool"),
               utils::helpers::JsonParseError);
  EXPECT_THROW(FetchMember(arr, bson_obj_, "gpoint"),
               utils::helpers::JsonParseError);
}

TEST_F(HelpersParams_GetMember, BsonOptionalArray) {
  using namespace utils::helpers;

  boost::optional<std::set<std::string>> arr;

  EXPECT_NO_THROW(FetchMember(arr, bson_obj_, "none"));
  EXPECT_FALSE(arr);

  EXPECT_NO_THROW(FetchMember(arr, bson_obj_, "null"));
  EXPECT_FALSE(arr);

  EXPECT_NO_THROW(FetchMember(arr, bson_obj_, "arr"));
  ASSERT_TRUE(!!arr);
  EXPECT_EQ(3u, arr->size());

  EXPECT_THROW(FetchMember(arr, bson_obj_, "str"),
               utils::helpers::JsonParseError);
  EXPECT_THROW(FetchMember(arr, bson_obj_, "uint"),
               utils::helpers::JsonParseError);
  EXPECT_THROW(FetchMember(arr, bson_obj_, "double"),
               utils::helpers::JsonParseError);
  EXPECT_THROW(FetchMember(arr, bson_obj_, "bool"),
               utils::helpers::JsonParseError);
  EXPECT_THROW(FetchMember(arr, bson_obj_, "gpoint"),
               utils::helpers::JsonParseError);
}

TEST_F(HelpersParams_GetMember, BsonGeoPoint) {
  using utils::helpers::FetchMember;
  utils::geometry::Point gpoint;
  EXPECT_THROW(FetchMember(gpoint, bson_obj_, "none"),
               utils::helpers::JsonParseError);
  EXPECT_THROW(FetchMember(gpoint, bson_obj_, "null"),
               utils::helpers::JsonParseError);
  EXPECT_THROW(FetchMember(gpoint, bson_obj_, "arr"),
               utils::helpers::JsonParseError);
  EXPECT_THROW(FetchMember(gpoint, bson_obj_, "str"),
               utils::helpers::JsonParseError);
  EXPECT_THROW(FetchMember(gpoint, bson_obj_, "uint"),
               utils::helpers::JsonParseError);
  EXPECT_THROW(FetchMember(gpoint, bson_obj_, "double"),
               utils::helpers::JsonParseError);
  EXPECT_THROW(FetchMember(gpoint, bson_obj_, "bool"),
               utils::helpers::JsonParseError);

  EXPECT_NO_THROW(FetchMember(gpoint, bson_obj_, "gpoint"));
  EXPECT_DOUBLE_EQ(1.11, gpoint.lon);
  EXPECT_DOUBLE_EQ(2.22, gpoint.lat);

  EXPECT_NO_THROW(FetchMember(gpoint, bson_obj_, "gpoint_int"));
  EXPECT_EQ(1, gpoint.lon);
  EXPECT_EQ(2, gpoint.lat);
}

TEST_F(HelpersParams_GetMember, BsonMap) {
  using utils::helpers::FetchMember;

  std::unordered_map<std::string, size_t> map, expected_map;
  EXPECT_THROW(FetchMember(map, bson_obj_, "none"),
               utils::helpers::JsonParseError);
  EXPECT_THROW(FetchMember(map, bson_obj_, "null"),
               utils::helpers::JsonParseError);
  EXPECT_THROW(FetchMember(map, bson_obj_, "arr"),
               utils::helpers::JsonParseError);
  EXPECT_THROW(FetchMember(map, bson_obj_, "str"),
               utils::helpers::JsonParseError);
  EXPECT_THROW(FetchMember(map, bson_obj_, "uint"),
               utils::helpers::JsonParseError);
  EXPECT_THROW(FetchMember(map, bson_obj_, "double"),
               utils::helpers::JsonParseError);
  EXPECT_THROW(FetchMember(map, bson_obj_, "bool"),
               utils::helpers::JsonParseError);

  EXPECT_NO_THROW(FetchMember(map, bson_obj_, "map"));

  expected_map.emplace("field1", 552);
  expected_map.emplace("field2", 34);
  expected_map.emplace("field3", 70);
  expected_map.emplace("field4", 1354);
  EXPECT_EQ(map, expected_map);
}
