#include <defs/api/api.hpp>
#include <userver/utest/utest.hpp>

#include <codegen/format.hpp>

#include <userver/formats/json/serialize.hpp>
#include <userver/formats/json/value_builder.hpp>
#include <userver/logging/log.hpp>

TEST(IntEnum, Parse) {
  constexpr const char* kDoc =
      "{\"good\": 1, \"wrong\": 2.1, \"invalid\": \"10\", \"negative\": -8 }";

  const auto json = formats::json::FromString(kDoc);

  EXPECT_EQ(handlers::IntEnum::k1, json["good"].As<handlers::IntEnum>());
  EXPECT_EQ(handlers::IntEnum::k_8, json["negative"].As<handlers::IntEnum>());
  EXPECT_THROW(json["wrong"].As<handlers::IntEnum>(),
               formats::json::TypeMismatchException);
  EXPECT_THROW(json["invalid"].As<handlers::IntEnum>(),
               formats::json::Exception);
}

TEST(Enum, Log) { LOG_INFO() << handlers::TesingEnum::kFoo; }

TEST(Enum, Formatting) {
  EXPECT_EQ(fmt::format("{}", handlers::TesingEnum::kFoo), "foo");
  EXPECT_EQ(fmt::format("{}", handlers::TesingEnum::kBar), "bar");
}

TEST(IntEnum, Log) { LOG_INFO() << handlers::IntEnum::k1; }

TEST(IntEnum, Formatting) {
  EXPECT_EQ(fmt::format("{}", handlers::IntEnum::k1), "1");
  EXPECT_EQ(fmt::format("{}", handlers::IntEnum::k9223372036854775807),
            "9223372036854775807");
}

TEST(IntEnum, Serialize) {
  auto json_1 = formats::json::ValueBuilder(1).ExtractValue();
  auto json_neg8 = formats::json::ValueBuilder(-8).ExtractValue();

  ASSERT_EQ(json_1, handlers::Serialize(
                        handlers::IntEnum::k1,
                        formats::serialize::To<formats::json::Value>()));
  ASSERT_EQ(json_neg8, handlers::Serialize(
                           handlers::IntEnum::k_8,
                           formats::serialize::To<formats::json::Value>()));
  // allow serialization of non-universe values
  ASSERT_NO_THROW(
      handlers::Serialize(static_cast<handlers::IntEnum>(-1),
                          formats::serialize::To<formats::json::Value>()));
}

TEST(IntEnum, ToStringInvalid) {
  auto x = static_cast<handlers::ErrorBaseCode>(-1);
  ASSERT_THROW(ToString(x), std::runtime_error);
}
