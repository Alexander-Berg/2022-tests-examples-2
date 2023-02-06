#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/classes_config.hpp>
#include <config/config.hpp>
#include <models/tariffs.hpp>
#include <models/tariffs/visibility_helper.hpp>

namespace {

config::Config GetConfig() {
  config::DocsMap docs_map = config::DocsMapForTest();

  docs_map.Override("ALL_CATEGORIES", BSON_ARRAY("econom"
                                                 << "business"
                                                 << "uberx"
                                                 << "uberblack"
                                                 << "uberstart"));
  docs_map.Override("APPLICATION_BRAND_CATEGORIES_SETS",
                    BSON("__default__" << BSON_ARRAY("econom"
                                                     << "business")
                                       << "yauber"
                                       << BSON_ARRAY("uberx"
                                                     << "uberblack"
                                                     << "uberselect"
                                                     << "uberkids"
                                                     << "uberstart")));

  return config::Config(docs_map);
}

config::ClassesConfig GetClassesConfig() {
  return GetConfig().Get<config::ClassesConfig>();
}

models::TariffSettings::Category BuildCategoryWithSettings(
    const models::ClassType category_type,
    const boost::optional<std::string>& show_experiment = boost::none,
    const boost::optional<std::string>& hide_experiment = boost::none,
    const boost::optional<bool>& visible_by_default = boost::none,
    const boost::optional<bool>& visible_on_site = boost::none) {
  models::TariffSettings::Category category;
  category.class_type = category_type;
  category.visibility_settings = models::TariffSettings::VisibilitySettings();
  category.visibility_settings->show_experiment = show_experiment;
  category.visibility_settings->hide_experiment = hide_experiment;
  category.visibility_settings->visible_by_default = visible_by_default;
  category.visibility_settings->visible_on_site = visible_on_site;
  return category;
}

models::TariffSettings::Category BuildCategoryWithoutSettings(
    const models::ClassType category_type) {
  models::TariffSettings::Category category;
  category.class_type = category_type;
  return category;
}

models::tariff_settings_dict BuildTariffSettings(
    const std::string& zone, const models::TariffSettings::Category& category) {
  models::TariffSettings settings;
  settings.categories = {category};
  models::tariff_settings_dict tariff_settings;
  tariff_settings[zone] = std::move(settings);
  return tariff_settings;
}

TEST(TestVisibilityHelper, Yandex) {
  const auto& config = GetConfig();
  const auto& helper =
      tariff::VisibilityHelper::ApplicationBrandTariffs("yataxi", config);

  EXPECT_TRUE(helper.IsCategoryVisible(
      models::ClassesMapper::GetName(models::Classes::Econom), "moscow", {},
      GetClassesConfig(), {}, {}, {}, true, {}, boost::none));
  EXPECT_TRUE(helper.IsCategoryVisible(
      models::ClassesMapper::GetName(models::Classes::Business), "moscow", {},
      GetClassesConfig(), {}, {}, {}, true, {}, boost::none));
  EXPECT_FALSE(helper.IsCategoryVisible(
      models::ClassesMapper::GetName(models::Classes::Vip), "moscow", {},
      GetClassesConfig(), {}, {}, {}, true, {}, boost::none));
  EXPECT_FALSE(helper.IsCategoryVisible(
      models::ClassesMapper::GetName(models::Classes::UberX), "moscow", {},
      GetClassesConfig(), {}, {}, {}, true, {}, boost::none));

  EXPECT_FALSE(helper.CategoryShouldBeSkipped(
      models::ClassesMapper::GetName(models::Classes::Econom), "moscow", {},
      GetClassesConfig(), false, {}, {}, {}, true, boost::none));
  EXPECT_TRUE(helper.CategoryShouldBeSkipped(
      models::ClassesMapper::GetName(models::Classes::UberX), "moscow", {},
      GetClassesConfig(), false, {}, {}, {}, true, boost::none));
  EXPECT_TRUE(helper.CategoryShouldBeSkipped(
      models::ClassesMapper::GetName(models::Classes::UberStart), "moscow", {},
      GetClassesConfig(), false, {}, {}, {}, true, boost::none));
}

TEST(TestVisibilityHelper, Uber) {
  const auto& config = GetConfig();
  const auto& helper =
      tariff::VisibilityHelper::ApplicationBrandTariffs("yauber", config);

  EXPECT_FALSE(helper.IsCategoryVisible(
      models::ClassesMapper::GetName(models::Classes::Econom), "moscow", {},
      GetClassesConfig(), {}, {}, {}, true, {}, boost::none));
  EXPECT_FALSE(helper.IsCategoryVisible(
      models::ClassesMapper::GetName(models::Classes::Business), "moscow", {},
      GetClassesConfig(), {}, {}, {}, true, {}, boost::none));
  EXPECT_FALSE(helper.IsCategoryVisible(
      models::ClassesMapper::GetName(models::Classes::Vip), "moscow", {},
      GetClassesConfig(), {}, {}, {}, true, {}, boost::none));
  EXPECT_TRUE(helper.IsCategoryVisible(
      models::ClassesMapper::GetName(models::Classes::UberX), "moscow", {},
      GetClassesConfig(), {}, {}, {}, true, {}, boost::none));

  EXPECT_TRUE(helper.CategoryShouldBeSkipped(
      models::ClassesMapper::GetName(models::Classes::Econom), "moscow", {},
      GetClassesConfig(), false, {}, {}, {}, true, boost::none));
  EXPECT_FALSE(helper.CategoryShouldBeSkipped(
      models::ClassesMapper::GetName(models::Classes::UberX), "moscow", {},
      GetClassesConfig(), false, {}, {}, {}, true, boost::none));
  EXPECT_FALSE(helper.CategoryShouldBeSkipped(
      models::ClassesMapper::GetName(models::Classes::UberStart), "moscow", {},
      GetClassesConfig(), false, {}, {}, {}, true, boost::none));
}

TEST(TestVisibilityHelper, YandexCutted) {
  const auto& config = GetConfig();
  const auto& helper = tariff::VisibilityHelper::ApplicationBrandTariffs(
      "yataxi", config, nullptr, {models::Classes::Business});

  EXPECT_FALSE(helper.IsCategoryVisible(
      models::ClassesMapper::GetName(models::Classes::Econom), "moscow", {},
      GetClassesConfig(), {}, {}, {}, true, {}, boost::none));
  EXPECT_TRUE(helper.IsCategoryVisible(
      models::ClassesMapper::GetName(models::Classes::Business), "moscow", {},
      GetClassesConfig(), {}, {}, {}, true, {}, boost::none));
}

namespace test_visibility_with_ts {
struct TestParams {
  const models::ClassType category;
  const std::string zone;
  const models::tariff_settings_dict tariff_settings;
  const bool visibility_default_value;
  const std::set<std::string> experiments;
  const std::string test_name;
  const bool expected_should_be_skipped;
  const bool expected_is_visible;
  const bool expected_is_visible_on_site;
};

class TestVisibilityHelperWithTS : public testing::TestWithParam<TestParams> {};

const std::vector<TestParams> kCheckParams = {
    {models::Classes::Econom,
     "moscow",
     BuildTariffSettings("moscow", BuildCategoryWithSettings(
                                       models::Classes::Econom, boost::none,
                                       boost::none, boost::none, boost::none)),
     false,
     {},
     "not_visible_by_default_1",
     true,
     false,
     false},
    {models::Classes::Econom,
     "moscow",
     BuildTariffSettings("moscow", BuildCategoryWithSettings(
                                       models::Classes::Econom, boost::none,
                                       boost::none, false, boost::none)),
     false,
     {},
     "not_visible_by_default_2",
     true,
     false,
     false},
    {models::Classes::Econom,
     "moscow",
     BuildTariffSettings("moscow", BuildCategoryWithSettings(
                                       models::Classes::Econom, boost::none,
                                       boost::none, true, boost::none)),
     false,
     {},
     "visible_by_default",
     false,
     true,
     true},
    {models::Classes::Unknown,
     "moscow",
     BuildTariffSettings("moscow", BuildCategoryWithSettings(
                                       models::Classes::Econom, boost::none,
                                       boost::none, true, boost::none)),
     false,
     {},
     "not_visible_category_not_found",
     true,
     false,
     false},
    {models::Classes::Econom,
     "unknown",
     BuildTariffSettings("moscow", BuildCategoryWithSettings(
                                       models::Classes::Econom, boost::none,
                                       boost::none, true, boost::none)),
     false,
     {},
     "not_visible_zone_not_found",
     true,
     false,
     false},
    {models::Classes::Econom,
     "moscow",
     BuildTariffSettings("moscow",
                         BuildCategoryWithoutSettings(models::Classes::Econom)),
     false,
     {},
     "not_visible_no_visibility_settings",
     true,
     false,
     false},
    {models::Classes::Econom,
     "moscow",
     BuildTariffSettings(
         "moscow", BuildCategoryWithSettings(models::Classes::Econom,
                                             std::string("show_exp"),
                                             boost::none, false, boost::none)),
     false,
     {"show_exp"},
     "visible_by_show_experiment",
     false,
     true,
     true},
    {models::Classes::Econom,
     "moscow",
     BuildTariffSettings(
         "moscow",
         BuildCategoryWithSettings(models::Classes::Econom, boost::none,
                                   std::string("hide_exp"), true, boost::none)),
     false,
     {"hide_exp"},
     "hidden_by_hide_experiment",
     true,
     false,
     false}

};

TEST_P(TestVisibilityHelperWithTS, UsingTariffSettings) {
  const auto& config = GetConfig();
  const auto& helper =
      tariff::VisibilityHelper::ApplicationBrandTariffs("yandex", config);
  const auto& params = GetParam();
  const auto& cat_name = models::ClassesMapper::GetName(params.category);
  EXPECT_EQ(
      helper.IsCategoryVisible(cat_name, params.zone, params.tariff_settings,
                               GetClassesConfig(), {}, params.experiments,
                               {true, true}, params.visibility_default_value),
      params.expected_is_visible);
  EXPECT_EQ(helper.CategoryShouldBeSkipped(
                cat_name, params.zone, params.tariff_settings,
                GetClassesConfig(), false, {}, params.experiments, {true, true},
                params.visibility_default_value),
            params.expected_should_be_skipped);
  EXPECT_EQ(helper.IsCategoryVisibleForFrontend(
                cat_name, params.zone, params.tariff_settings,
                GetClassesConfig(), {}, params.experiments, {true, true},
                params.visibility_default_value, {}, {}),
            params.expected_is_visible_on_site);
}

INSTANTIATE_TEST_CASE_P(, TestVisibilityHelperWithTS,
                        ::testing::ValuesIn(kCheckParams), );

}  // namespace test_visibility_with_ts

namespace test_visibility_with_categories {
struct TestParams {
  const models::TariffSettings::Category category;
  const bool visibility_default_value;
  const std::set<std::string> experiments;
  const std::string test_name;
  const bool expected_should_be_skipped;
  const bool expected_is_visible;
  const bool expected_is_visible_on_site;
};

class TestVisibilityHelperWithCategories
    : public testing::TestWithParam<TestParams> {};

const std::vector<TestParams> kCheckParams = {
    {BuildCategoryWithSettings(models::Classes::Econom, boost::none,
                               boost::none, boost::none, boost::none),
     false,
     {},
     "not_visible_by_default_1",
     true,
     false,
     false},
    {BuildCategoryWithSettings(models::Classes::Econom, boost::none,
                               boost::none, false, boost::none),
     false,
     {},
     "not_visible_by_default_2",
     true,
     false,
     false},
    {BuildCategoryWithSettings(models::Classes::Econom, boost::none,
                               boost::none, true, boost::none),
     false,
     {},
     "visible_by_default",
     false,
     true,
     true},
    {BuildCategoryWithoutSettings(models::Classes::Econom),
     false,
     {},
     "not_visible_no_visibility_settings",
     true,
     false,
     false},
    {BuildCategoryWithSettings(models::Classes::Econom, std::string("show_exp"),
                               boost::none, false, boost::none),
     false,
     {"show_exp"},
     "visible_by_show_experiment",
     false,
     true,
     true},
    {BuildCategoryWithSettings(models::Classes::Econom, boost::none,
                               std::string("hide_exp"), true, boost::none),
     false,
     {"hide_exp"},
     "hidden_by_hide_experiment",
     true,
     false,
     false}

};

TEST_P(TestVisibilityHelperWithCategories, UsingCategories) {
  const auto& config = GetConfig();
  const auto& helper =
      tariff::VisibilityHelper::ApplicationBrandTariffs("yandex", config);
  const auto& params = GetParam();
  EXPECT_EQ(
      helper.IsCategoryVisible(params.category, "doesnt matter",
                               GetClassesConfig(), {}, params.experiments,
                               {true, true}, params.visibility_default_value),
      params.expected_is_visible);
  EXPECT_EQ(helper.CategoryShouldBeSkipped(params.category, "doesnt matter",
                                           GetClassesConfig(), false, {},
                                           params.experiments, {true, true},
                                           params.visibility_default_value),
            params.expected_should_be_skipped);
  EXPECT_EQ(helper.IsCategoryVisibleForFrontend(
                params.category, "doesnt matter", GetClassesConfig(), {},
                params.experiments, {true, true},
                params.visibility_default_value, {}, {}),
            params.expected_is_visible_on_site);
}

INSTANTIATE_TEST_CASE_P(, TestVisibilityHelperWithCategories,
                        ::testing::ValuesIn(kCheckParams), );

}  // namespace test_visibility_with_categories

}  // namespace
