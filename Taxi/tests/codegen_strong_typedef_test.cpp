#include <userver/utest/utest.hpp>

#include <typeinfo>

// Test for TAXICOMMON-4934.
// Should be before <defs/definitions/strong_typedef.hpp>
namespace handlers::lib_sample {}

// Test for TAXICOMMON-4934.
// Should be before <defs/definitions/strong_typedef.hpp>
namespace handlers::localization::price_format {
void CurrencyTag();
}

#include <defs/definitions/strong_typedef.hpp>
#include <userver/formats/json/serialize.hpp>
#include <userver/formats/json/value_builder.hpp>

using namespace formats::json::parser;

TEST(Codegen, StrongTypedefStringParse) {
  const auto json = formats::json::FromString(R"({"currency": "RUB"})");
  const auto obj = json.As<handlers::ObjectWithCurrency>();

  static_assert(
      std::is_same_v<decltype(*obj.currency), const price_format::Currency&>);

  EXPECT_EQ(obj, (handlers::ObjectWithCurrency{price_format::Currency{"RUB"}}));
}

TEST(Codegen, StrongTypedefStringSerialize) {
  handlers::ObjectWithCurrency obj{price_format::Currency{"RUB"}};

  EXPECT_EQ(obj,
            Serialize(obj, ::formats::serialize::To<::formats::json::Value>())
                .As<handlers::ObjectWithCurrency>());
}

TEST(Codegen, StrongTypedefIntParse) {
  const auto json = formats::json::FromString(R"({"revision-id": 1234})");
  const auto obj = json.As<handlers::ObjectWithCurrency>();

  static_assert(
      std::is_same_v<decltype(*obj.revision_id), const lib_sample::Sample&>);

  EXPECT_EQ(obj,
            (handlers::ObjectWithCurrency{{}, {}, lib_sample::Sample{1234}}));
}

TEST(Codegen, StrongTypedefIntSerialize) {
  handlers::ObjectWithCurrency obj{{}, {}, lib_sample::Sample{1234}};

  EXPECT_EQ(obj,
            Serialize(obj, ::formats::serialize::To<::formats::json::Value>())
                .As<handlers::ObjectWithCurrency>());
}
