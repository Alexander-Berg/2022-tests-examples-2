#include <defs/definitions.hpp>
#include <userver/utest/utest.hpp>

#include <userver/formats/json/serialize.hpp>
#include <userver/formats/json/value_builder.hpp>

TEST(AllOf, Parse) {
  constexpr const char* kDoc = "{\"x\": 1, \"y\": 2.1, \"z\": \"abc\" }";

  const auto json = formats::json::FromString(kDoc);
  const auto obj = json.As<handlers::AllOf>();

  EXPECT_EQ(1, obj.x);
  EXPECT_EQ(2.1, obj.y);
  EXPECT_EQ("abc", obj.z);

  const auto obj2 =
      formats::json::ValueBuilder(obj).ExtractValue().As<handlers::AllOf>();

  // compare field-to-field as double is not comparable
  EXPECT_EQ(obj.x, obj.x);
  EXPECT_EQ(obj.y, obj.y);
  EXPECT_EQ(obj.z, obj.z);
}

TEST(AllOf, SkipParseExtra) {
  constexpr const char* kDoc = "{\"z\": \"abc\", \"garbage\": 1}";

  const auto json = formats::json::FromString(kDoc);
  const auto obj = json.As<handlers::AllOf>();

  EXPECT_EQ(static_cast<const handlers::ExtraZ&>(obj).extra.GetSize(), 0);
}
