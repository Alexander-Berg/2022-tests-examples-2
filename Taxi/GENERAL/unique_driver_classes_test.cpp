#include <gtest/gtest.h>
#include <userver/utest/utest.hpp>

#include <testing/taxi_config.hpp>

#include "virtual_tariffs_classes.hpp"

#include <filters/efficiency/fetch_tags/fetch_tags.hpp>
#include <filters/infrastructure/fetch_driver/fetch_driver.hpp>
#include <filters/infrastructure/fetch_final_classes/fetch_final_classes.hpp>
#include <filters/infrastructure/fetch_unique_driver/fetch_unique_driver.hpp>

#include <virtual-tariffs/models/requirements.hpp>
#include <virtual-tariffs/models/virtual_tariffs.hpp>

#include <memory>
#include <string>

using candidates::GeoMember;
using namespace candidates::filters;
using namespace candidates::filters::infrastructure;
using namespace candidates::filters::efficiency;
using namespace candidates::filters::corp;
using namespace virtual_tariffs::models;

namespace {

const candidates::filters::FilterInfo kEmptyInfo;
struct TestData {
  std::string request;  // order.virtual_tariffs
  std::vector<std::string> exams;
  bool allow = false;
  std::optional<std::string> detail;
};

class ExamsParametric : public ::testing::TestWithParam<TestData> {};

SpecialRequirements GetSpecialRequirements() {
  static const OperationId kOperationId = OperationId::kContainsAll;
  static const RequirementId kRequirementId = RequirementId::kExams;
  std::vector<std::vector<std::string>> exams = {
      {"econom", "business"},
      {"econom"},
      {"business"},
  };
  SpecialRequirements special_requirements;
  int counter = 0;
  for (auto&& value : exams) {
    auto requirement_name = "feature" + std::to_string(counter);
    special_requirements[requirement_name].requirements = {
        {Requirement(ContextId::kUniqueDriver, kRequirementId, kOperationId,
                     std::move(value), requirement_name)}};
    ++counter;
  }
  return special_requirements;
}

std::unique_ptr<VirtualTariffs> MakeVirtualTariffs(
    const std::string& request_string) {
  std::unique_ptr<VirtualTariffs> result;
  RunInCoro([&result, &request_string]() {
    static const auto special_requirements = GetSpecialRequirements();
    virtual_tariffs::models::ReplaceFunctor exams_functor =
        [](virtual_tariffs::models::Requirement& requirement) {
          requirement.ReplaceFunctor<decltype(
              std::declval<models::UniqueDriver>().exams)>(
              [](const std::vector<std::string>& arguments) {
                return decltype(std::declval<models::UniqueDriver>().exams)(
                    arguments);
              });
        };

    const virtual_tariffs::models::ReplaceMap replace_map = {
        {virtual_tariffs::models::RequirementId::kExams, exams_functor},
    };
    result = std::make_unique<VirtualTariffs>(
        formats::json::FromString(request_string), special_requirements,
        replace_map, dynamic_config::GetDefaultSnapshot());
  });
  return result;
}

}  // namespace

TEST_P(ExamsParametric, Test) {
  Context context;
  context.need_details = true;

  FetchFinalClasses::Set(context, {"econom", "business"});
  const auto member = GeoMember{{0, 0}, "dbid_uuid"};

  auto params = GetParam();

  auto virtual_tariffs_ptr = MakeVirtualTariffs(params.request);
  models::UniqueDriver unique_driver;
  RunInCoro([&unique_driver, &params]() {
    unique_driver.exams = models::drivers::Exams(params.exams);
  });
  FetchUniqueDriver::Set(context, std::make_shared<models::UniqueDriver>(
                                      std::move(unique_driver)));
  FetchTags::Set(context, tags::models::IdsVec());
  FetchDriver::Set(context, std::make_shared<models::Driver>(models::Driver()));

  VirtualTariffsClasses filter(kEmptyInfo, std::move(virtual_tariffs_ptr));

  EXPECT_EQ(filter.Process(member, context),
            (params.allow ? Result::kAllow : Result::kDisallow))
      << filter.Get().ToString();
  if (params.detail) {
    EXPECT_NE(
        std::find_if(context.GetDetails().begin(), context.GetDetails().end(),
                     [&params](const Context::Detail& other) {
                       return params.detail == other.desc;
                     }),
        context.GetDetails().end());
  } else {
    EXPECT_TRUE(context.GetDetails().empty());
  }
}

INSTANTIATE_TEST_SUITE_P(Exams, ExamsParametric,
                         ::testing::Values(TestData{R"(
{
  "order": {
      "virtual_tariffs": [
          {
            "class": "econom",
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
                                                    {"econom"},
                                                    true,
                                                    std::nullopt},
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
                                                    {"econom"},
                                                    false,
                                                    "econom by feature0"},
                                           TestData{R"(
{
  "order": {
      "virtual_tariffs": [
          {
            "class": "econom",
            "special_requirements": [
              {
                 "id": "feature1"
              }
            ]
          },
          {
            "class": "business",
            "special_requirements": [
              {
                 "id": "feature2"
              }
            ]
          }
       ]
  }
}
)",
                                                    {"econom", "business"},
                                                    true,
                                                    std::nullopt},
                                           TestData{R"(
{
  "order": {
      "virtual_tariffs": [
          {
            "class": "econom",
            "special_requirements": [
              {
                 "id": "feature1"
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
                                                    {"business"},
                                                    false,
                                                    "econom by feature1"}));
