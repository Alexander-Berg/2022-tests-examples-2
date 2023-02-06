#include <gtest/gtest.h>
#include <boost/optional/optional_io.hpp>

#include <userver/formats/parse/boost_optional.hpp>
#include <userver/formats/serialize/boost_optional.hpp>

#include <ml/common/introspection/comparison.hpp>
#include <ml/common/introspection/json.hpp>
#include <ml/common/json.hpp>

using ml::common::introspection::operator==;
using ml::common::introspection::operator!=;
using ml::common::introspection::json::Parse;
using ml::common::introspection::json::Serialize;

#include "common/utils.hpp"

struct TypicalStruct {
  int i;
  std::string s;
  float f;
  std::vector<int> v;

  static auto fields() { return std::make_tuple("i", "s", "f", "v"); }

  template <typename T>
  static auto introspect(T&& obj) {
    return std::tie(obj.i, obj.s, obj.f, obj.v);
  }
};

struct StrangeStruct {
  int i;

  static auto fields() { return std::make_tuple("i"); }

  template <typename T>
  static auto introspect(T&& obj) {
    return std::tie(obj.i);
  }

  // everything works as usual except this redefined operator
  bool operator==(const StrangeStruct&) { return false; }
};

TEST(Comparison, TypicalStruct) {
  TypicalStruct s{1, "s", .3, {3, 4, 5}};
  ASSERT_TRUE(s == s);
}

TEST(Comparison, StrangeStruct) {
  StrangeStruct s{1};
  ASSERT_FALSE(s == s);
}

struct WithOptionalStruct {
  std::optional<int> optional_int;
  std::optional<int> optional_default_int = 3;
  boost::optional<int> boost_optional_int;
  boost::optional<int> boost_optional_default_int = 5;

  static auto fields() {
    return std::make_tuple("optional_int", "optional_default_int",
                           "boost_optional_int", "boost_optional_default_int");
  }

  template <typename T>
  static auto introspect(T&& o) {
    return std::tie(o.optional_int, o.optional_default_int,
                    o.boost_optional_int, o.boost_optional_default_int);
  }
};

TEST(Json, ParseSimple) {
  auto obj = ml::common::FromJsonString<TypicalStruct>(
      R"({"i":4,"s":"str","f":3,"v":[1,2,3]})");
  ASSERT_EQ(obj.i, 4);
  ASSERT_EQ(obj.s, "str");
  ASSERT_EQ(obj.f, 3.);
  std::vector<int> expected_v{1, 2, 3};
  ASSERT_EQ(obj.v, expected_v);
}

TEST(Json, FailParseSimple) {
  std::string bad_json = R"({"s":"str","f":3,"v":[1,2,3]})";
  ASSERT_ANY_THROW(ml::common::FromJsonString<TypicalStruct>(bad_json));
}

TEST(Json, SerializeOptional) {
  WithOptionalStruct obj;
  obj.boost_optional_int = 4;

  ASSERT_EQ(
      ml::common::ToJsonString(obj),
      R"({"optional_default_int":3,"boost_optional_int":4,"boost_optional_default_int":5})");
}

TEST(Json, ParseOptional) {
  auto obj = ml::common::FromJsonString<WithOptionalStruct>(
      R"({"boost_optional_int":4,"boost_optional_default_int":6})");
  ASSERT_EQ(obj.optional_int, std::nullopt);
  ASSERT_EQ(obj.optional_default_int, 3);
  ASSERT_EQ(obj.boost_optional_int, 4);
  ASSERT_EQ(obj.boost_optional_default_int, 6);
}

struct CustomStruct {
  int i;
  std::optional<std::string> s_opt;

  static auto fields() { return std::make_tuple("i", "s_opt"); }

  template <typename T>
  static auto introspect(T&& obj) {
    return std::tie(obj.i, obj.s_opt);
  }
};

CustomStruct Parse(const formats::json::Value& /*elem*/,
                   formats::parse::To<CustomStruct>) {
  return CustomStruct{400, "magic"};
}

formats::json::Value Serialize(const CustomStruct& /*value*/,
                               formats::serialize::To<formats::json::Value>) {
  formats::json::ValueBuilder builder(formats::json::Type::kObject);
  builder["magic"] = "only_magic";
  return builder.ExtractValue();
}

TEST(Custom, Compare) {
  CustomStruct s1{1, std::nullopt};
  CustomStruct s2{1, "str"};
  ASSERT_TRUE(s1 != s2);
}

TEST(Custom, Parse) {
  auto obj =
      ml::common::FromJsonString<CustomStruct>(R"({"i":4,"s_opt":"str"})");
  ASSERT_EQ(obj.i, 400);
  ASSERT_EQ(obj.s_opt, "magic");
}

TEST(Custom, Serialize) {
  CustomStruct obj{4, "str"};
  ASSERT_EQ(ml::common::ToJsonString(obj), R"({"magic":"only_magic"})");
}
