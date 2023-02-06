#include "views/routestats/tracker.hpp"
#include <gtest/gtest.h>
#include "views/routestats/requirements.hpp"
#include "views/routestats/visibility.hpp"

TEST(RoutestatsTracker, SplitClassesTest) {
  namespace rsi = views::routestats::internal;
  namespace vr = views::requirements;
  const auto& reqs1 =
      models::requirements::Requirements{{"some_req_1", "value"}};
  const auto& reqs2 =
      models::requirements::Requirements{{"some_req_2", "value"}};
  const auto& args_as_map1 = models::requirements::ClassesByRequirementsMap{
      {reqs1, {"econom", "business", "comfortplus", "vip"}}};
  const auto& f = rsi::SplitClassesAndConvertArgsMapToArguments;

  {
    const auto& result = f(args_as_map1, {});
    const auto& expected =
        rsi::Args{{reqs1, {"econom", "business", "comfortplus", "vip"}}};
    ASSERT_EQ(result, expected);
  }
  {
    const auto& result = f(args_as_map1, {{"econom"}});
    const auto& expected = rsi::Args{
        {reqs1, {"econom"}}, {reqs1, {"business", "comfortplus", "vip"}}};
    ASSERT_EQ(result, expected);
  }
  {
    const auto& result = f(args_as_map1, {{"econom", "business"}});
    const auto& expected = rsi::Args{{reqs1, {"econom", "business"}},
                                     {reqs1, {"comfortplus", "vip"}}};
    ASSERT_EQ(result, expected);
  }
  {
    const auto& result =
        f(args_as_map1, {{"econom", "business"}, {"comfortplus"}});
    const auto& expected = rsi::Args{{reqs1, {"econom", "business"}},
                                     {reqs1, {"comfortplus"}},
                                     {reqs1, {"vip"}}};
    ASSERT_EQ(result, expected);
  }
  {
    const auto& result =
        f(args_as_map1, {{"econom", "business"}, {"comfortplus", "vip"}});
    const auto& expected = rsi::Args{{reqs1, {"econom", "business"}},
                                     {reqs1, {"comfortplus", "vip"}}};
    ASSERT_EQ(result, expected);
  }

  const auto& args_as_map2 = models::requirements::ClassesByRequirementsMap{
      {reqs1, {"econom", "business"}}, {reqs2, {"comfortplus", "vip"}}};
  {
    const auto& result = f(args_as_map2, {{"econom"}, {"comfortplus"}});
    const auto& expected = rsi::Args{{reqs2, {"comfortplus"}},
                                     {reqs2, {"vip"}},
                                     {reqs1, {"econom"}},
                                     {reqs1, {"business"}}};
    ASSERT_EQ(result, expected);
  }
}

TEST(RoutestatsTracker, PrepareArgs) {
  namespace rs = views::routestats::internal;
  LogExtra log_extra;
  {
    // no specific requirements - prepare one set of args
    models::requirements::Requirements requirements = {{"non_specific1", {}},
                                                       {"non_specific2", {}}};

    requirements::Descriptions requirement_descriptions;

    models::requirements::Description non_specific1;
    non_specific1.name = "non_specific1";
    requirement_descriptions.emplace_back(non_specific1);

    models::requirements::Description non_specific2;
    non_specific2.name = "non_specific2";
    requirement_descriptions.emplace_back(non_specific2);

    const std::vector<std::string>& categories = {"econom", "child_tariff"};

    models::TariffSettings tariff_settings;

    models::TariffSettings::Category ts_category1;
    ts_category1.class_type = models::Classes::ChildTariff;
    ts_category1.client_requirements = {"non_specific1", "non_specific2"};
    tariff_settings.categories.emplace_back(ts_category1);

    models::TariffSettings::Category ts_category2;
    ts_category2.class_type = models::Classes::Econom;
    ts_category2.client_requirements = {"non_specific1"};
    tariff_settings.categories.emplace_back(ts_category2);
    rs::Args args = rs::PrepareArgsForTracker(
        requirements, boost::none, categories, tariff_settings,
        requirement_descriptions, std::nullopt, std::nullopt, log_extra);
    EXPECT_EQ(args.size(), 1U);
    const auto& reqs = args[0].first;
    const auto& cat = args[0].second;
    EXPECT_EQ(reqs, requirements);
    EXPECT_EQ(cat, categories);
  }
  {
    // tracker with classes requirements
    models::requirements::Requirements common_requirements = {};
    models::requirements::Requirements requirements = {{"non_specific1", {}},
                                                       {"non_specific2", {}}};
    models::requirements::ClassesRequirements classes_requirements;
    classes_requirements[models::Classes::Econom] = requirements;
    classes_requirements[models::Classes::ChildTariff] = requirements;

    requirements::Descriptions requirement_descriptions;

    models::requirements::Description non_specific1;
    non_specific1.name = "non_specific1";
    requirement_descriptions.emplace_back(non_specific1);

    models::requirements::Description non_specific2;
    non_specific2.name = "non_specific2";
    requirement_descriptions.emplace_back(non_specific2);

    const std::vector<std::string>& categories = {"child_tariff", "econom"};

    models::TariffSettings tariff_settings;

    models::TariffSettings::Category ts_category1;
    ts_category1.class_type = models::Classes::ChildTariff;
    ts_category1.client_requirements = {"non_specific1", "non_specific2"};
    tariff_settings.categories.emplace_back(ts_category1);

    models::TariffSettings::Category ts_category2;
    ts_category2.class_type = models::Classes::Econom;
    ts_category2.client_requirements = {"non_specific1", "non_specific2"};
    tariff_settings.categories.emplace_back(ts_category2);
    rs::Args args = rs::PrepareArgsForTracker(
        common_requirements, classes_requirements, categories, tariff_settings,
        requirement_descriptions, std::nullopt, std::nullopt, log_extra);
    EXPECT_EQ(args.size(), 1U);
    const auto& reqs = args[0].first;
    EXPECT_EQ(reqs, requirements);
    auto& cat = args[0].second;
    std::sort(cat.begin(), cat.end());
    EXPECT_EQ(cat, categories);
  }
  {
    // no non-specific categories - prepare one set of args
    models::requirements::Requirements requirements = {{"non_specific", {}},
                                                       {"specific", {}}};

    requirements::Descriptions requirement_descriptions;

    models::requirements::Description non_specific;
    non_specific.name = "non_specific";
    requirement_descriptions.emplace_back(non_specific);

    models::requirements::Description specific;
    specific.name = "specific";
    specific.tariff_specific = true;
    requirement_descriptions.emplace_back(specific);

    const std::vector<std::string>& categories = {"child_tariff"};

    models::TariffSettings tariff_settings;

    models::TariffSettings::Category ts_category1;
    ts_category1.class_type = models::Classes::ChildTariff;
    ts_category1.client_requirements = {"non_specific", "specific"};
    tariff_settings.categories.emplace_back(ts_category1);

    models::TariffSettings::Category ts_category2;
    ts_category2.class_type = models::Classes::Econom;
    ts_category2.client_requirements = {"non_specific"};
    tariff_settings.categories.emplace_back(ts_category2);
    rs::Args args = rs::PrepareArgsForTracker(
        requirements, boost::none, categories, tariff_settings,
        requirement_descriptions, std::nullopt, std::nullopt, log_extra);
    EXPECT_EQ(args.size(), 1U);
    const auto& reqs = args[0].first;
    const auto& cat = args[0].second;
    EXPECT_EQ(reqs, requirements);
    EXPECT_EQ(cat, categories);
  }
  {
    // overridden category
    models::requirements::Requirements requirements = {
        {"non_specific", {}}, {"specific_overridden", {}}};

    requirements::Descriptions requirement_descriptions;

    models::requirements::Description non_specific;
    non_specific.name = "non_specific";
    requirement_descriptions.emplace_back(non_specific);

    models::requirements::Description specific_overridden;
    specific_overridden.name = "specific_overridden";
    specific_overridden.tariff_specific = true;
    requirement_descriptions.emplace_back(specific_overridden);

    const std::vector<std::string>& categories = {"child_tariff", "econom"};

    models::TariffSettings tariff_settings;

    models::TariffSettings::Category ts_category1;
    ts_category1.class_type = models::Classes::ChildTariff;
    ts_category1.client_requirements = {"non_specific"};
    ts_category1.tariff_specific_overrides["specific_overridden"] = false;
    tariff_settings.categories.emplace_back(ts_category1);

    models::TariffSettings::Category ts_category2;
    ts_category2.class_type = models::Classes::Econom;
    ts_category2.client_requirements = {"non_specific"};
    tariff_settings.categories.emplace_back(ts_category2);

    models::requirements::Requirements expected_req1 = {{"non_specific", {}}};
    const std::vector<std::string>& expected_cat1 = {"econom"};
    models::requirements::Requirements expected_req2 = {
        {"non_specific", {}}, {"specific_overridden", {}}};
    const std::vector<std::string>& expected_cat2 = {"child_tariff"};

    rs::Args args = rs::PrepareArgsForTracker(
        requirements, boost::none, categories, tariff_settings,
        requirement_descriptions, std::nullopt, std::nullopt, log_extra);

    EXPECT_EQ(args.size(), 2U);
    EXPECT_EQ(args[0].first, expected_req1);
    EXPECT_EQ(args[0].second, expected_cat1);
    EXPECT_EQ(args[1].first, expected_req2);
    EXPECT_EQ(args[1].second, expected_cat2);
  }
  {
    // mixed categories and mixed requirements - more than one set of
    // arguments
    models::requirements::Requirements requirements = {{"non_specific", {}},
                                                       {"specific", {}}};

    requirements::Descriptions requirement_descriptions;

    models::requirements::Description non_specific;
    non_specific.name = "non_specific";
    requirement_descriptions.emplace_back(non_specific);

    models::requirements::Description specific;
    specific.name = "specific";
    specific.tariff_specific = true;
    requirement_descriptions.emplace_back(specific);

    const std::vector<std::string>& categories = {"child_tariff", "econom"};

    models::TariffSettings tariff_settings;

    models::TariffSettings::Category ts_category1;
    ts_category1.class_type = models::Classes::ChildTariff;
    ts_category1.client_requirements = {"non_specific", "specific"};
    tariff_settings.categories.emplace_back(ts_category1);

    models::TariffSettings::Category ts_category2;
    ts_category2.class_type = models::Classes::Econom;
    ts_category2.client_requirements = {"non_specific"};
    tariff_settings.categories.emplace_back(ts_category2);
    rs::Args args = rs::PrepareArgsForTracker(
        requirements, boost::none, categories, tariff_settings,
        requirement_descriptions, std::nullopt, std::nullopt, log_extra);
    EXPECT_EQ(args.size(), 2U);
    models::requirements::Requirements expected_req1 = {{"non_specific", {}}};
    models::requirements::Requirements expected_req2 = {{"non_specific", {}},
                                                        {"specific", {}}};
    const std::vector<std::string>& expected_cat1 = {"econom"};
    const std::vector<std::string>& expected_cat2 = {"child_tariff"};
    EXPECT_EQ(args[0].first, expected_req1);
    EXPECT_EQ(args[1].first, expected_req2);
    EXPECT_EQ(args[0].second, expected_cat1);
    EXPECT_EQ(args[1].second, expected_cat2);
  }
}
