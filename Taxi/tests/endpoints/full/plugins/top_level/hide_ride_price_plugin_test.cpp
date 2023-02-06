#include <gtest/gtest.h>

#include <endpoints/full/plugins/hide_ride_price/plugin.hpp>

#include <experiments3/corp_hide_ride_price.hpp>
#include <tests/context/taxi_config_mock_test.hpp>
#include <tests/context/translator_mock_test.hpp>
#include <tests/context_mock_test.hpp>

namespace routestats::full::brandings {

namespace {

static test::TranslationHandler translation_handler =
    [](const core::Translation& translation,
       const std::string& locale) -> std::optional<std::string> {
  if ("hide_ride_price" == translation->main_key.key) return "***";
  return translation->main_key.key + "##" + locale;
};

formats::json::Value MakeHideRidePriceExp(
    bool enabled, const std::vector<std::string>& classes) {
  using formats::json::ValueBuilder;

  ValueBuilder exp_builder{};
  exp_builder["enabled"] = enabled;

  exp_builder["clients"] = ValueBuilder(formats::common::Type::kArray);
  for (const auto& class_ : classes) {
    exp_builder["clients"].PushBack(class_);
  }

  return exp_builder.ExtractValue();
}

core::Experiments MockExperiments(
    const std::vector<std::string>& branding_classes) {
  core::ExpMappedData experiments;
  using CorpHideRidePrice = experiments3::CorpHideRidePrice;

  experiments[CorpHideRidePrice::kName] = {
      CorpHideRidePrice::kName,
      MakeHideRidePriceExp(true, branding_classes),
      {}};

  return {std::move(experiments)};
}

full::ContextData PrepareDefaultContext(bool in_experiment) {
  full::ContextData context = test::full::GetDefaultContext();

  context.experiments.uservices_routestats_exps =
      MockExperiments({"hide_price0"});
  context.input.original_request.payment = ::handlers::RequestPayment{
      "corp", in_experiment ? "corp-hide_price0" : "corp-hide_priceXXX",
      std::nullopt};

  return context;
}

std::vector<core::ServiceLevel> MockServiceLevels(
    const std::unordered_map<
        std::string, std::optional<core::DescriptionParts>>& service_levels) {
  std::vector<core::ServiceLevel> result;

  for (const auto& [class_, description_parts] : service_levels) {
    core::ServiceLevel service_level;
    service_level.class_ = class_;
    service_level.description_parts = description_parts;
    result.push_back(std::move(service_level));
  }
  return result;
}

std::vector<core::ServiceLevel> PrepareServiceLevels() {
  return MockServiceLevels({{"econom", std::nullopt},
                            {"ultima", core::DescriptionParts{"", "", ""}}});
}

}  // namespace

TEST(TestHideRidePrice, InExperiment) {
  HideRidePricePlugin plugin;
  full::ContextData test_ctx = PrepareDefaultContext(true);
  auto service_levels = PrepareServiceLevels();

  test_ctx.rendering.translator =
      std::make_shared<test::TranslatorMock>(translation_handler);
  auto extensions = plugin.ExtendServiceLevels(
      test::full::MakeTopLevelContext(test_ctx), service_levels);

  for (auto& level : service_levels) {
    if (extensions.count(level.class_)) {
      extensions.at(level.class_)->Apply("hide_ride_price_plugin", level);
    }
  }

  for (const auto& level : service_levels) {
    if (level.class_ == "ultima") {
      ASSERT_EQ(level.description_parts->value, "***");
    }
  }
}

TEST(TestHideRidePrice, NotInExperiment) {
  HideRidePricePlugin plugin;
  full::ContextData test_ctx = PrepareDefaultContext(false);
  auto service_levels = PrepareServiceLevels();

  test_ctx.rendering.translator =
      std::make_shared<test::TranslatorMock>(translation_handler);
  auto extensions = plugin.ExtendServiceLevels(
      test::full::MakeTopLevelContext(test_ctx), service_levels);

  for (auto& level : service_levels) {
    if (extensions.count(level.class_)) {
      extensions.at(level.class_)->Apply("hide_ride_price_plugin", level);
    }
  }

  for (const auto& level : service_levels) {
    if (level.class_ == "ultima") {
      ASSERT_NE(level.description_parts->value, "***");
    }
  }
}

}  // namespace routestats::full::brandings
