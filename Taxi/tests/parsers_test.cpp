#include <gtest/gtest.h>

#include <experiments3_common/models/kwargs.hpp>
#include <utils/experiments3/parsers.hpp>
#include <utils/known_apps.hpp>

namespace {
namespace exp3 = experiments3::models;

const std::string kApplication = "application";
const std::string kVersion = "version";
const std::string kZone = "zone";
const std::string kKey = "key";
const std::string kTags = "tags";
const std::string kUserId = "user_id";
const std::string kFoo = "foo";
const std::string kBar = "bar";
const std::string kPhoneId = "phone_id";
const std::string kPosition = "position";
const std::string kPoints = "points";
const std::string kPrice = "price";
const std::string kTimePoint = "time_point";

const std::string kIphone = "iphone";
const std::string kTaximeter = "taximeter";
const std::string kDefaultVersion = "9.8.7";

}  // namespace

TEST(ParsersTest, ExperimentsToJsonEmpty) {
  Json::Value json;
  EXPECT_THROW(experiments3::utils::JsonToKwargs(json), std::runtime_error);
}

TEST(ParsersTest, ExperimentsToJsonEmptyArray) {
  Json::Value builder = Json::arrayValue;
  EXPECT_NO_THROW(experiments3::utils::JsonToKwargs(builder));
}

TEST(ParsersTest, ExperimentsToJsonNotSupportedType) {
  Json::Value builder = Json::arrayValue;
  Json::Value item = Json::objectValue;
  item["type"] = "unknown_type";
  item["name"] = "name";
  item["value"] = "value";
  builder.append(std::move(item));
  EXPECT_THROW(experiments3::utils::JsonToKwargs(builder), std::runtime_error);
}

TEST(ParsersTest, ExperimentsToJsonSupportedType) {
  Json::Value builder = Json::arrayValue;
  Json::Value item = Json::objectValue;
  item["type"] = exp3::kKwargTypes.at(typeid(exp3::KwargTypeString));
  item["name"] = "name";
  item["value"] = "value";
  builder.append(std::move(item));
  EXPECT_NO_THROW(experiments3::utils::JsonToKwargs(builder));
}

TEST(ParsersTest, ExperimentsToJsonCompare) {
  experiments3::models::Kwargs kwargs1 = {
      {kZone, exp3::KwargTypeString{"msk"}},
      {kVersion, exp3::KwargTypeAppVersion{"9.8.7"}},
      {kApplication, exp3::KwargTypeString(models::applications::Iphone)},
      {kTags, exp3::KwargTypeSetString({"tag1", "tag2"})},
      {kPoints, exp3::KwargTypeSetInt({100, 200, 300})},
      {kFoo, exp3::KwargTypeBool(true)},
      {kBar, exp3::KwargTypeBool(false)},
      {kPosition, exp3::KwargTypePoint(34.4, 45.5)},
      {kPrice, exp3::KwargTypeDouble(100.5)},
      {kTimePoint, exp3::KwargTypeTimePoint(::utils::Double2TimePoint(200))},
      {kPhoneId, exp3::KwargTypeInt(12)}};

  Json::Value kwargs_json = experiments3::utils::KwargsToJson(kwargs1);
  experiments3::models::Kwargs kwargs2 =
      experiments3::utils::JsonToKwargs(kwargs_json);

  ASSERT_EQ(kwargs1, kwargs2);
}
