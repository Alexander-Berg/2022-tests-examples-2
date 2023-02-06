#include "taximeter_version_features.hpp"

#include <gtest/gtest.h>

#include <pro_app_parser/app_family.hpp>

#include <userver/dynamic_config/snapshot.hpp>
#include <userver/dynamic_config/storage_mock.hpp>
#include <userver/formats/json.hpp>

#include <taxi_config/variables/TAXIMETER_VERSION_FEATURES.hpp>
#include <userver/utest/utest.hpp>

namespace {

namespace features = configs::taximeter_version_features;

class CheckFamily : public ::testing::TestWithParam<
                        std::tuple<std::string, features::Platform,
                                   features::Version, std::optional<bool>>> {};
}  // namespace

TEST_P(CheckFamily, Check) {
  static const features::VersionMap kMap{
      {pro_app_parser::kAppFamilyTaximeter,
       {
           {features::Platform::kAndroid, features::Version("1.0")},
           {features::Platform::kIos, features::Version("2.0")},
       }},
      {pro_app_parser::kAppFamilyUberdriver,
       {
           {features::Platform::kAndroid, features::Version("3.0")},
       }},
  };

  const auto [family, platform, version, res] = GetParam();
  EXPECT_EQ(res, features::Check(kMap, family, platform, version));
}

INSTANTIATE_TEST_SUITE_P(
    TaximeterVersionFeatures, CheckFamily,
    ::testing::Values(
        std::make_tuple(pro_app_parser::kAppFamilyVezet,
                        features::Platform::kAndroid, "1.0", std::nullopt),
        std::make_tuple(pro_app_parser::kAppFamilyUberdriver,
                        features::Platform::kIos, "1.0", std::nullopt),
        std::make_tuple(pro_app_parser::kAppFamilyTaximeter,
                        features::Platform::kIos, "1.0", false),
        std::make_tuple(pro_app_parser::kAppFamilyUberdriver,
                        features::Platform::kAndroid, "1.0", false),
        std::make_tuple(pro_app_parser::kAppFamilyTaximeter,
                        features::Platform::kAndroid, "1.0", true),
        std::make_tuple(pro_app_parser::kAppFamilyTaximeter,
                        features::Platform::kIos, "2.0", true),
        std::make_tuple(pro_app_parser::kAppFamilyUberdriver,
                        features::Platform::kAndroid, "3.0", true),
        std::make_tuple(pro_app_parser::kAppFamilyTaximeter,
                        features::Platform::kAndroid, "2.0", true),
        std::make_tuple(pro_app_parser::kAppFamilyTaximeter,
                        features::Platform::kIos, "3.0", true),
        std::make_tuple(pro_app_parser::kAppFamilyUberdriver,
                        features::Platform::kAndroid, "3.0", true)));

UTEST(TaximeterVersionFeatures, Wrapper) {
  const auto features_conf = R"({
    "classes": {
      "econom": {
        "taximeter": {
          "android": "1.0",
          "ios": "2.0"
        },
        "uberdriver": {
          "android": "3.0"
        }
      },
      "comfortplus": {
        "taximeter": {
          "android": "4.0",
          "ios": "5.0"
        },
        "uberdriver": {
          "android": "6.0"
        }
      }
    }
  })";

  const dynamic_config::StorageMock config_storage{
      {taxi_config::TAXIMETER_VERSION_FEATURES,
       formats::json::FromString(features_conf)}};

  features::Wrapper wrapper(config_storage.GetSnapshot());

  // GetGroup
  EXPECT_TRUE(wrapper.GetGroup("unknown").empty());
  EXPECT_TRUE(wrapper.GetGroup(features::groups::kClasses, {}).empty());

  auto res = wrapper.GetGroup(features::groups::kClasses, {"unknown"});
  ASSERT_FALSE(res.empty());
  EXPECT_TRUE(res.begin()->second.empty());

  EXPECT_EQ(2lu, wrapper.GetGroup(features::groups::kClasses).size());
  EXPECT_EQ(1lu,
            wrapper.GetGroup(features::groups::kClasses, {"econom"}).size());
  EXPECT_EQ(
      2lu,
      wrapper.GetGroup(features::groups::kClasses, {"econom", "comfortplus"})
          .size());
  EXPECT_EQ(3lu, wrapper
                     .GetGroup(features::groups::kClasses,
                               {"econom", "comfortplus", "unknown"})
                     .size());

  EXPECT_EQ(
      wrapper.GetGroup(features::groups::kClasses),
      wrapper.GetGroup(features::groups::kClasses, {"econom", "comfortplus"}));

  // GetKey
  EXPECT_TRUE(wrapper.GetKey("unknown", "unknown").empty());
  EXPECT_TRUE(wrapper.GetKey(features::groups::kClasses, "unknown").empty());

  EXPECT_EQ(2lu, wrapper.GetKey(features::groups::kClasses, "econom").size());
  EXPECT_EQ(2lu,
            wrapper.GetKey(features::groups::kClasses, "comfortplus").size());
}
