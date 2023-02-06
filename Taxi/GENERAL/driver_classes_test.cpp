#include <userver/utest/utest.hpp>

#include <memory>
#include <string>

#include <userver/dynamic_config/storage_mock.hpp>

#include <taximeter-version-settings/taximeter_features.hpp>
#include <virtual-tariffs/models/requirements.hpp>
#include <virtual-tariffs/models/virtual_tariffs.hpp>

#include <filters/corp/virtual_tariffs_classes/virtual_tariffs_classes.hpp>
#include <filters/efficiency/fetch_tags/fetch_tags.hpp>
#include <filters/infrastructure/fetch_driver/fetch_driver.hpp>
#include <filters/infrastructure/fetch_final_classes/fetch_final_classes.hpp>
#include <filters/infrastructure/fetch_unique_driver/fetch_unique_driver.hpp>

using candidates::GeoMember;
using namespace candidates::filters;
using namespace candidates::filters::infrastructure;
using namespace candidates::filters::efficiency;
using namespace candidates::filters::corp;
using namespace virtual_tariffs::models;

namespace {

const candidates::filters::FilterInfo kEmptyInfo;

const std::string kSettingsConfig = R"({
  "__default__": {
    "disabled": [
      "9.05",
      "8.99"
    ],
    "feature_support": {
      "android_bug_fix": "9.00",
      "default_feature": "8.80"
    },
    "min": "7.00"
  },
  "taximeter-beta": {
    "disabled": [
      "9.03",
      "8.99"
    ],
    "feature_support": {
      "beta_feature": "9.01",
    "default_feature": "8.80"
    },
    "min": "8.00"
    },
    "taximeter-ios": {
    "disabled": [
    "1.03",
    "1.99"
    ],
    "feature_support": {
    "default_feature": "1.00",
    "ios_feature": "1.23"
    },
    "min": "1.00"
    }
})";

namespace features {
const std::string kDefault{"default_feature"};
const std::string kAndroid{"android_bug_fix"};
const std::string kIos{"ios_feature"};
const std::string kFake{"fake_feature"};
const std::string kBeta{"beta_feature"};
}  // namespace features

using Features = std::vector<std::vector<std::string>>;

struct TestData {
  std::string request;  // order.virtual_tariffs
  std::string useragent;
  bool allow = false;
};

class TaximeterVersionFeaturesParametric
    : public ::testing::TestWithParam<TestData> {
 protected:
  const dynamic_config::StorageMock config_storage_{
      {config::kTaximeterFeatures, formats::json::FromString(kSettingsConfig)}};
  const dynamic_config::Snapshot config_ = config_storage_.GetSnapshot();
};

SpecialRequirements GetSpecialRequirements() {
  static const OperationId kOperationId = OperationId::kContainsAll;
  static const RequirementId kRequirementId = RequirementId::kTaximeterFeatures;
  Features features = {
      {features::kDefault, features::kAndroid, features::kBeta},  // 0
      {features::kDefault, features::kAndroid, features::kFake},  // 1
      {features::kDefault, features::kAndroid},                   // 2
      {features::kDefault},                                       // 3
      {features::kAndroid},                                       // 4
      {features::kIos},                                           // 5
      {features::kBeta},                                          // 6
  };
  SpecialRequirements special_requirements;
  int counter = 0;
  for (auto&& value : features) {
    auto requirement_name = "feature" + std::to_string(counter);
    special_requirements[requirement_name].requirements = {
        {Requirement(ContextId::kDriver, kRequirementId, kOperationId,
                     std::move(value), requirement_name)}};
    ++counter;
  }
  return special_requirements;
}

std::unique_ptr<VirtualTariffs> MakeVirtualTariffs(
    const std::string& request_string, dynamic_config::Snapshot config) {
  const auto features = config[::config::kTaximeterFeatures];

  virtual_tariffs::models::ReplaceFunctor features_functor =
      [features](virtual_tariffs::models::Requirement& requirement) {
        requirement.ReplaceFunctor<config::TaximeterFeatures::FeaturesIds>(
            [&features](const std::vector<std::string>& arguments) {
              const auto required_features = features.GetFeaturesIds(arguments);
              if (required_features.size() != arguments.size()) {
                throw Exception("test_filter",
                                "some taximeter features are not found in "
                                "config, features in requirement: ");
              }
              return required_features;
            });
      };

  const virtual_tariffs::models::ReplaceMap replace_map = {
      {virtual_tariffs::models::RequirementId::kTaximeterFeatures,
       features_functor},
  };

  static const auto special_requirements = GetSpecialRequirements();

  return std::make_unique<VirtualTariffs>(
      formats::json::FromString(request_string), special_requirements,
      replace_map, std::move(config));
}

}  // namespace

UTEST_P(TaximeterVersionFeaturesParametric, Test) {
  Context context;

  FetchFinalClasses::Set(context, {"econom", "business"});
  const auto member = GeoMember{{0, 0}, "dbid_uuid"};

  auto params = GetParam();

  models::Driver driver;
  driver.app = ua_parser::TaximeterApp::FromUserAgent(params.useragent);
  FetchDriver::Set(context,
                   std::make_shared<models::Driver>(std::move(driver)));
  FetchUniqueDriver::Set(
      context, std::make_shared<models::UniqueDriver>(models::UniqueDriver()));
  FetchTags::Set(context, tags::models::IdsVec());

  try {
    auto virtual_tariffs_ptr = MakeVirtualTariffs(params.request, config_);
    VirtualTariffsClasses filter(kEmptyInfo, std::move(virtual_tariffs_ptr));
    EXPECT_EQ(filter.Process(member, context),
              (params.allow ? Result::kAllow : Result::kDisallow))
        << filter.Get().ToString();
  } catch (const candidates::filters::Exception&) {
    EXPECT_FALSE(params.allow);
  }
}

INSTANTIATE_UTEST_SUITE_P(
    TaximeterVersionFeatures, TaximeterVersionFeaturesParametric,
    ::testing::Values(TestData{R"(
{
  "order": {
      "virtual_tariffs": [
          {
            "class": "econom",
            "special_requirements": [
              {
                 "id": "feature0"
              }
            ]
          }
       ]
  }
}
)",
                               "Taximeter-Beta 9.01", true},
                      TestData{R"(
{
  "order": {
      "virtual_tariffs": [
          {
            "class": "econom",
            "special_requirements": [
              {
                 "id": "feature0"
              }
            ]
          },
          {
            "class": "business",
            "special_requirements": [
              {
                 "id": "feature0"
              }
            ]
          }
       ]
  }
}
)",
                               "Taximeter-Beta 9.00", false},
                      TestData{R"(
{
  "order": {
      "virtual_tariffs": [
          {
            "class": "econom",
            "special_requirements": [
              {
                 "id": "feature5"
              }
            ]
          },
          {
            "class": "business",
            "special_requirements": [
              {
                 "id": "feature1"
              }
            ]
          }
       ]
  }
}
)",
                               "Taximeter-Beta 9.01", false},
                      TestData{R"(
{
  "order": {
      "virtual_tariffs": [
          {
            "class": "econom",
            "special_requirements": [
              {
                 "id": "feature2"
              }
            ]
          },
          {
            "class": "business",
            "special_requirements": [
              {
                 "id": "feature5"
              }
            ]
          }
       ]
  }
}
)",
                               "Taximeter-Beta 9.01", true}));
