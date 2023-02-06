#include <userver/utest/utest.hpp>

#include <taxi_config/variables/USERVER_SAMPLE_OPTIONAL_DEFAULT_DICT.hpp>

#include <userver/formats/json/serialize.hpp>
#include <userver/formats/json/value_builder.hpp>

namespace {

using OptionalDefaultDict = taxi_config::userver_sample_optional_default_dict::
    UserverSampleOptionalDefaultDict;

}  // namespace

TEST(CodegenOptionalDefaultDict, Empty) {
  constexpr const char* kDoc = "{}";

  const auto json = formats::json::FromString(kDoc);
  const auto obj = json.As<OptionalDefaultDict>();

  EXPECT_EQ(std::nullopt, obj.optional_default_dict);
}

TEST(CodegenOptionalDefaultDict, Full) {
  constexpr const char* kDoc =
      "{\"optional_default_dict\": {\"__default__\": 42}}";

  const auto json = formats::json::FromString(kDoc);
  const auto obj = json.As<OptionalDefaultDict>();

  ASSERT_TRUE(obj.optional_default_dict);
  EXPECT_EQ(42, obj.optional_default_dict->GetDefaultValue());
}
