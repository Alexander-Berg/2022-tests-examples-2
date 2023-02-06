#include <core/context/experiments3.hpp>
#include <core/context/tariff_requirements/tariff_requirements_impl.hpp>
#include <core/context/zone.hpp>
#include <experiments3/routestats_requirements_crutch.hpp>
#include <handlers/v1/routestats/post/request.hpp>
#include <tariff_settings/models.hpp>
#include <userver/utest/utest.hpp>

namespace routestats::core {

namespace {
static const std::string kCategoryName = "express";
static const std::string kRequirementName = "door_to_door";
core::Zone MockZoneWithCategories(bool with_category = true,
                                  bool with_requirement = true) {
  core::Zone zone;
  if (with_category) {
    taxi_tariffs::models::Category category;
    category.name = kCategoryName;
    if (with_requirement) {
      category.client_requirements.push_back(kRequirementName);
    }
    zone.tariff_settings.categories.emplace({category});
  }
  return zone;
}

core::Experiments MockExperiment(bool with_requirements = true) {
  using experiments3::RoutestatsRequirementsCrutch;
  using formats::json::ValueBuilder;

  ValueBuilder CrutchExp{};
  CrutchExp["enabled"] = true;
  CrutchExp["requirements"] = ValueBuilder(formats::common::Type::kArray);

  if (with_requirements) {
    CrutchExp["requirements"].PushBack(kCategoryName);
  }

  core::ExpMappedData exp_mapped_data{};
  exp_mapped_data[RoutestatsRequirementsCrutch::kName] = {
      RoutestatsRequirementsCrutch::kName, CrutchExp.ExtractValue(), {}};
  return {std::move(exp_mapped_data)};
}

handlers::RoutestatsRequest MockRoutestatsRequest(
    bool is_tariff_requirements_filled = true,
    bool is_requirements_filled = true) {
  handlers::RoutestatsRequest request;
  request.tariff_requirements.emplace();
  request.requirements.emplace();
  if (is_tariff_requirements_filled) {
    handlers::RequestTariffRequirement tariff_requirement;
    tariff_requirement.class_ = kCategoryName;
    request.tariff_requirements->push_back(tariff_requirement);
  }
  if (is_requirements_filled) {
    request.requirements->extra[kRequirementName] = true;
  }
  return request;
}

void AssetTariffRequirementsState(
    const std::unordered_map<std::string, Requirements>& tariff_requirements) {
  ASSERT_EQ(tariff_requirements.size(), 1);
  ASSERT_TRUE(tariff_requirements.count(kCategoryName));
  ASSERT_TRUE(tariff_requirements.at(kCategoryName).empty());
}
}  // namespace

TEST(TestRequirementsBuilder, emptyTariffRequirements) {
  const auto& request = MockRoutestatsRequest(false);
  const auto& zone = MockZoneWithCategories();
  const auto& experiment = MockExperiment();
  const auto& tariff_requirements = BuildTariffRequirements(
      request.requirements, request.tariff_requirements, zone, experiment);

  ASSERT_TRUE(tariff_requirements.empty());
}

TEST(TestRequirementsBuilder, emptyExperiment) {
  const auto& request = MockRoutestatsRequest();
  const auto& zone = MockZoneWithCategories();
  const auto& experiment = MockExperiment(false);
  const auto& tariff_requirements = BuildTariffRequirements(
      request.requirements, request.tariff_requirements, zone, experiment);

  AssetTariffRequirementsState(tariff_requirements);
}

TEST(TestRequirementsBuilder, notCategories) {
  const auto& request = MockRoutestatsRequest();
  const auto& zone = MockZoneWithCategories(false);
  const auto& experiment = MockExperiment();
  const auto& tariff_requirements = BuildTariffRequirements(
      request.requirements, request.tariff_requirements, zone, experiment);

  AssetTariffRequirementsState(tariff_requirements);
}

TEST(TestRequirementsBuilder, notCategoriesRequirements) {
  const auto& request = MockRoutestatsRequest();
  const auto& zone = MockZoneWithCategories(true, false);
  const auto& experiment = MockExperiment();
  const auto& tariff_requirements = BuildTariffRequirements(
      request.requirements, request.tariff_requirements, zone, experiment);

  AssetTariffRequirementsState(tariff_requirements);
}

TEST(TestRequirementsBuilder, notRequirements) {
  const auto& request = MockRoutestatsRequest(true, false);
  const auto& zone = MockZoneWithCategories();
  const auto& experiment = MockExperiment();
  const auto& tariff_requirements = BuildTariffRequirements(
      request.requirements, request.tariff_requirements, zone, experiment);

  AssetTariffRequirementsState(tariff_requirements);
}

}  // namespace routestats::core
