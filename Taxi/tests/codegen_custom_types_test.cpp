#include <defs/definitions.hpp>
#include <userver/utest/utest.hpp>

#include <userver/formats/json/serialize.hpp>
#include <userver/formats/json/value_builder.hpp>

TEST(CodegenCustomTypes, Parse) {
  constexpr const char* kDoc =
      "{\"int\": 1, \"int_opt\": 2, "
      "\"string\": \"android\", "
      "\"string_opt\": \"sms\", "
      "\"object\": {\"lon\": 1.1, \"lat\": 2.2}, "
      "\"object_opt\": {\"lon\": 1.2, \"lat\": 2.3}}";

  const auto json = formats::json::FromString(kDoc);
  const auto obj = json.As<handlers::CustomTypes>();

  EXPECT_EQ(obj.int_, std::chrono::seconds(1));
  EXPECT_EQ(obj.int_opt, std::chrono::seconds(2));
  EXPECT_TRUE(geometry::AreClosePositions(
      obj.object.GetUnderlying(),
      geometry::Position(geometry::Longitude::from_value(1.1),
                         geometry::Latitude::from_value(2.2))));

  ASSERT_TRUE(obj.object_opt);
  EXPECT_TRUE(geometry::AreClosePositions(
      obj.object_opt->GetUnderlying(),
      geometry::Position(geometry::Longitude::from_value(1.2),
                         geometry::Latitude::from_value(2.3))));

  const auto obj2 = formats::json::ValueBuilder(obj)
                        .ExtractValue()
                        .As<handlers::CustomTypes>();

  EXPECT_EQ(obj.int_, obj2.int_);
  EXPECT_EQ(obj.int_opt, obj2.int_opt);
  EXPECT_EQ(obj.string, obj2.string);
  EXPECT_EQ(obj.string_opt, obj2.string_opt);
  ASSERT_TRUE(obj2.object_opt);
  EXPECT_TRUE(geometry::AreClosePositions(obj.object_opt->GetUnderlying(),
                                          obj2.object_opt->GetUnderlying()));
}

TEST(CodegenCustomTypes, ParseOptional) {
  constexpr const char* kDoc =
      "{\"int\": 1,"
      "\"string\": \"android\", "
      "\"object\": {\"lon\": 1.1, \"lat\": 2.2}}";

  const auto json = formats::json::FromString(kDoc);
  const auto obj = json.As<handlers::CustomTypes>();

  EXPECT_EQ(obj.int_, std::chrono::seconds(1));
  EXPECT_FALSE(obj.int_opt);
  EXPECT_FALSE(obj.string_opt);
  EXPECT_TRUE(geometry::AreClosePositions(
      obj.object.GetUnderlying(),
      geometry::Position(geometry::Longitude::from_value(1.1),
                         geometry::Latitude::from_value(2.2))));

  EXPECT_FALSE(obj.object_opt);

  const auto obj2 = formats::json::ValueBuilder(obj)
                        .ExtractValue()
                        .As<handlers::CustomTypes>();

  EXPECT_EQ(obj.int_, obj2.int_);
  EXPECT_FALSE(obj.int_opt);
  EXPECT_EQ(obj.string, obj2.string);
  EXPECT_FALSE(obj2.object_opt);
}
