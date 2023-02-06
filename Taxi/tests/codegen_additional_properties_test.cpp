#include <defs/definitions.hpp>
#include <userver/utest/utest.hpp>

#include <userver/formats/json/inline.hpp>
#include <userver/formats/json/serialize.hpp>
#include <userver/formats/json/string_builder.hpp>
#include <userver/formats/json/value_builder.hpp>

TEST(AdditionalProperties, Parse) {
  constexpr const char* kDoc = "{\"x\": \"2345\", \"smth\": 1, \"bar\": -22}";

  const auto json = formats::json::FromString(kDoc);
  const auto obj = json.As<handlers::PropertiesWithExtra>();

  EXPECT_EQ("2345", obj.x);
  EXPECT_EQ((std::unordered_map<std::string, int>{{"smth", 1}, {"bar", -22}}),
            obj.extra);
}

TEST(AdditionalProperties, SerializeEmptyExtra) {
  handlers::OnlyExtra obj;
  auto result = formats::json::ValueBuilder(obj).ExtractValue();
  EXPECT_TRUE(result.IsObject());
  EXPECT_EQ(result.GetSize(), 0);

  const auto standard_empty_obj = formats::json::MakeObject();

  handlers::OnlyExtra null_obj;
  null_obj.extra = formats::json::Value{};

  const auto to = formats::serialize::To<formats::json::Value>{};
  const auto serialize_json =
      formats::json::ToString(handlers::Serialize(null_obj, to));
  EXPECT_EQ(formats::json::FromString(serialize_json), standard_empty_obj);

  formats::json::StringBuilder obj_sw;
  handlers::WriteToStream(null_obj, obj_sw);
  const auto stream_json = obj_sw.GetString();
  EXPECT_EQ(formats::json::FromString(stream_json), standard_empty_obj);
}

TEST(AdditionalProperties, ParseEmptyExtra) {
  constexpr const char* kDoc = "{}";

  const auto json = formats::json::FromString(kDoc);
  const auto obj = json.As<handlers::OnlyExtra>();

  EXPECT_TRUE(obj.extra.IsObject());
  EXPECT_EQ(obj.extra.GetSize(), 0);
}

TEST(AdditionalProperties, SerializeEmpty) {
  handlers::AllOfA0 empty;
  auto result = formats::json::ValueBuilder(empty).ExtractValue();
  EXPECT_TRUE(result.IsObject());
  EXPECT_EQ(0, result.GetSize());
}
