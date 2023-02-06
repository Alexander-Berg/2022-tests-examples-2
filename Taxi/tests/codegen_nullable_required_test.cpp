#include <userver/utest/utest.hpp>

#include <defs/definitions/required.hpp>
#include <userver/formats/json/inline.hpp>
#include <userver/formats/json/value_builder.hpp>
#include <userver/formats/serialize/common_containers.hpp>

using formats::json::ValueBuilder;

TEST(ObjectWithNullableOptional, Empty) {
  ValueBuilder vb{};
  EXPECT_EQ(vb.ExtractValue().As<handlers::ObjectWithNullableOptional>(),
            handlers::ObjectWithNullableOptional{});
}

namespace {
const auto kFields = {"str", "enum", "int", "array", "object"};
}

TEST(ObjectWithNullableOptional, Null) {
  for (const auto& field : kFields) {
    ValueBuilder vb{};
    vb[field] = {};
    EXPECT_EQ(vb.ExtractValue().As<handlers::ObjectWithNullableOptional>(),
              handlers::ObjectWithNullableOptional{});
  }
}

TEST(ObjectWithNullableOptional, Value) {
  ValueBuilder vb{};
  vb["str"] = "abba";
  EXPECT_EQ(vb.ExtractValue().As<handlers::ObjectWithNullableOptional>(),
            handlers::ObjectWithNullableOptional{"abba"});
}
