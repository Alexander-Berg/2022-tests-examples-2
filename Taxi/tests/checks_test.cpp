#include <gmock/gmock.h>
#include <gtest/gtest.h>

#include <array>
#include <string>
#include <unordered_map>
#include <vector>

#include <fmt/format.h>

#include <userver/dynamic_config/storage_mock.hpp>
#include <userver/formats/json/serialize.hpp>
#include <userver/utest/parameter_names.hpp>

#include <taxi_config/variables/ALICE_ALLOWED_TARIFFS.hpp>
#include <taxi_config/variables/APPLICATION_BRAND_CATEGORIES_SETS.hpp>
#include <taxi_config/variables/TARIFF_CATEGORIES_ENABLED_BY_VERSION.hpp>

#include <tariff_settings/models.hpp>
#include "checks.hpp"
#include "experiments3.hpp"

namespace tariff_categories_visibility::tests {

namespace {

const Brand kEmptyBrand = {};
const std::optional<AppVars> kEmptyAppVars = {};
const std::optional<UserSource> kEmptyUserSource = {};
const ZoneName kEmptyZoneName = {};
const std::optional<PhoneId> kEmptyPhoneId = {};
const std::optional<PaymentOption> kEmptyPaymentOption = {};
const std::unordered_set<std::string> kEmptyExperiments = {};

using CategoriesVisibility = std::unordered_map<Category, bool>;

CategoriesVisibility BuildCategoriesVisibilityMap(
    const std::unordered_set<std::string>& visible_categories,
    const std::unordered_set<std::string>& not_visible_categories) {
  CategoriesVisibility result;
  for (const auto& category : visible_categories) {
    result[Category{category}] = true;
  }
  for (const auto& category : not_visible_categories) {
    if (result.count(Category{category}) > 0) {
      throw std::runtime_error(fmt::format(
          "category '{}' cannot be both visible and not visible", category));
    }
    result[Category{category}] = false;
  }
  return result;
}

void CheckCategoriesVisibility(
    const VisibilityCheck& check, const CheckContext& check_context,
    const dynamic_config::Snapshot& config,
    const CategoriesVisibility& categories_visibility) {
  for (const auto& [category, is_visible] : categories_visibility) {
    EXPECT_EQ(check(category, check_context, config), is_visible)
        << fmt::format("Visibility for category '{}' is incorrect",
                       category.GetUnderlying());
  }
}

class ExperimentsHelperMock : public ExperimentsHelper {
  using ExperimentsHelper::ExperimentsHelper;

 public:
  MOCK_METHOD(bool, IsVisibilityExperimentEnabled,
              (const std::string&, const AppVars&, std::optional<PhoneId>,
               std::optional<PaymentOption>),
              (const, override));
};

class CheckContextHelper {
  ZoneName zone_;
  UserContext user_context;
  std::shared_ptr<const ExperimentsHelper> exp3_helper_;
  CheckContext context;

 public:
  CheckContextHelper(const Brand& brand, const std::optional<AppVars>& app_vars,
                     const std::optional<UserSource>& user_source,
                     const ZoneName& zone_name,
                     const std::optional<PhoneId>& phone_id,
                     const std::optional<PaymentOption>& payment_option,
                     const OptUserExperiments& experiments,
                     std::shared_ptr<const ExperimentsHelper> exp3_helper,
                     const TariffSettingsMapPtr tariff_settings_ptr)
      : zone_{zone_name},
        user_context{brand,    app_vars,       user_source,
                     phone_id, payment_option, experiments},
        exp3_helper_{std::move(exp3_helper)},
        context{user_context, zone_, *exp3_helper_, tariff_settings_ptr} {}
  CheckContext Get() const { return context; }
};

CheckContextHelper CheckContextFromBrand(const Brand& brand) {
  return {brand,
          kEmptyAppVars,
          kEmptyUserSource,
          kEmptyZoneName,
          kEmptyPhoneId,
          kEmptyPaymentOption,
          kEmptyExperiments,
          std::make_shared<ExperimentsHelper>(nullptr),
          TariffSettingsMapPtr(nullptr)};
}

CheckContextHelper CheckContextFromUserSource(
    const std::optional<UserSource>& user_source) {
  return {kEmptyBrand,
          kEmptyAppVars,
          user_source,
          kEmptyZoneName,
          kEmptyPhoneId,
          kEmptyPaymentOption,
          kEmptyExperiments,
          std::make_shared<ExperimentsHelper>(nullptr),
          TariffSettingsMapPtr(nullptr)};
}

CheckContextHelper CheckContextFromZoneNameAndExp(
    const ZoneName& zone_name, const OptUserExperiments& experiments,
    std::shared_ptr<ExperimentsHelper> exp3_helper,
    TariffSettingsMapPtr tariff_settings_ptr) {
  return {kEmptyBrand,
          AppVars{},
          kEmptyUserSource,
          zone_name,
          kEmptyPhoneId,
          kEmptyPaymentOption,
          experiments,
          std::move(exp3_helper),
          std::move(tariff_settings_ptr)};
}

CheckContextHelper CheckContextFromAppVars(
    const std::optional<AppVars>& app_vars) {
  return {kEmptyBrand,
          app_vars,
          kEmptyUserSource,
          kEmptyZoneName,
          kEmptyPhoneId,
          kEmptyPaymentOption,
          kEmptyExperiments,
          std::make_shared<ExperimentsHelper>(nullptr),
          TariffSettingsMapPtr(nullptr)};
}

CheckContextHelper EmptyCheckContext() {
  return {kEmptyBrand,
          kEmptyAppVars,
          kEmptyUserSource,
          kEmptyZoneName,
          kEmptyPhoneId,
          kEmptyPaymentOption,
          kEmptyExperiments,
          std::make_shared<ExperimentsHelper>(nullptr),
          TariffSettingsMapPtr(nullptr)};
}

}  // namespace

namespace brand_check {

struct TestParams {
  std::string brand;
  std::string test_name;

  TestParams(const std::string& brand) : brand(brand), test_name(brand) {}
};

class TestBrandCheckDefault : public testing::TestWithParam<TestParams> {};

const std::vector<TestParams> kDefaultBrandTestParams = {
    {"yataxi"},
    {"yauber"},
    {"yango"},
};

TEST_P(TestBrandCheckDefault, OnlyDefaultBrand) {
  const dynamic_config::StorageMock config{
      {taxi_config::APPLICATION_BRAND_CATEGORIES_SETS,
       {
           {"__default__",
            {"econom", "comfort", "business", "ultima", "delivery"}},
       }}};

  const auto expected_categories_visibility = BuildCategoriesVisibilityMap(
      {"econom", "comfort", "business", "ultima", "delivery"},
      {"comfort+", "elite", "uberx", "uberstart"});

  const auto context = CheckContextFromBrand(Brand{GetParam().brand});

  CheckCategoriesVisibility(IsCategoryVisibleByBrand, context.Get(),
                            config.GetSnapshot(),
                            expected_categories_visibility);
}

INSTANTIATE_TEST_SUITE_P(/* no prefix */, TestBrandCheckDefault,
                         testing::ValuesIn(kDefaultBrandTestParams),
                         ::utest::PrintTestName());

TEST(TestBrandCheck, NonDefaultBrand) {
  const dynamic_config::StorageMock config{
      {taxi_config::APPLICATION_BRAND_CATEGORIES_SETS,
       {
           {"__default__", {"econom", "comfort", "business"}},
           {"yauber", {"uberstart", "uberx"}},
       }}};
  const auto expected_categories_visibility = BuildCategoriesVisibilityMap(
      {"uberstart", "uberx"},
      {"econom", "comfort", "business", "ultima", "delivery"});

  const auto context = CheckContextFromBrand(Brand{"yauber"});

  CheckCategoriesVisibility(IsCategoryVisibleByBrand, context.Get(),
                            config.GetSnapshot(),
                            expected_categories_visibility);
}

}  // namespace brand_check

namespace app_version_check {

TEST(TestAppVersionCheckEmptySettings, BasicTest) {
  const dynamic_config::StorageMock config{
      {taxi_config::TARIFF_CATEGORIES_ENABLED_BY_VERSION, {}}};
  const auto expected_categories_visibility = BuildCategoriesVisibilityMap(
      {"econom", "comfort", "business", "ultima", "delivery"}, {});

  const auto context = EmptyCheckContext();

  CheckCategoriesVisibility(IsCategoryVisibleByAppVersion, context.Get(),
                            config.GetSnapshot(),
                            expected_categories_visibility);
}

struct TestParams {
  std::optional<AppVars> app_vars;
  std::unordered_set<std::string> visible_categories;
  std::unordered_set<std::string> not_visible_categories;
  std::string test_name;
};

class TestAppVersionCheck : public testing::TestWithParam<TestParams> {};

AppVars BuildAppVars(std::string application,
                     std::array<std::string, 3> version) {
  return {{
      {"app_name", application},
      {"app_ver1", version[0]},
      {"app_ver2", version[1]},
      {"app_ver3", version[2]},
  }};
}

const std::vector<TestParams> kBasicTestParams = {
    {
        std::nullopt,
        {"econom", "comfort", "business", "ultima"},
        {"delivery"},
        "EmptyAppVars",
    },
    {
        BuildAppVars("android", {"0", "5", "8"}),
        {"econom", "comfort", "business", "ultima"},
        {"delivery"},
        "OldVersion",
    },
    {
        BuildAppVars("iphone", {"0", "5", "8"}),
        {"econom", "comfort", "business", "ultima"},
        {"delivery"},
        "WrongApp",
    },
    {
        BuildAppVars("android", {"1", "5", "8"}),
        {"econom", "comfort", "business", "ultima", "delivery"},
        {},
        "CorrectAppAndVersion",
    },
};

TEST_P(TestAppVersionCheck, BasicTest) {
  const dynamic_config::StorageMock config{
      {taxi_config::TARIFF_CATEGORIES_ENABLED_BY_VERSION,
       {{{"delivery", {{{"android", {{1, 0, 0}}}}}}}}}};

  const auto& params = GetParam();
  const auto expected_categories_visibility = BuildCategoriesVisibilityMap(
      params.visible_categories, params.not_visible_categories);

  const auto context = CheckContextFromAppVars(params.app_vars);

  CheckCategoriesVisibility(IsCategoryVisibleByAppVersion, context.Get(),
                            config.GetSnapshot(),
                            expected_categories_visibility);
}

INSTANTIATE_TEST_SUITE_P(/* no prefix */, TestAppVersionCheck,
                         testing::ValuesIn(kBasicTestParams),
                         ::utest::PrintTestName());

}  // namespace app_version_check

namespace user_source_check {

struct TestParams {
  std::optional<UserSource> user_source;
  std::unordered_set<std::string> visible_categories;
  std::unordered_set<std::string> not_visible_categories;
  std::string test_name;
};

class TestUserSourceCheck : public testing::TestWithParam<TestParams> {};

const std::vector<TestParams> kBasicTestParams = {
    {
        std::nullopt,
        {"econom", "comfort", "business", "ultima", "delivery"},
        {},
        "EmptyUserSource",
    },
    {
        UserSource{"call_center"},
        {"econom", "comfort", "business", "ultima", "delivery"},
        {},
        "NotLimitedUserSourceCallCenter",
    },
    {
        UserSource{"wizard"},
        {"econom", "comfort", "business", "ultima", "delivery"},
        {},
        "NotLimitedUserSourceWizard",
    },
    {
        UserSource{"alice"},
        {"econom", "comfort"},
        {"business", "ultima", "delivery"},
        "LimitedUserSource",
    },
};

TEST_P(TestUserSourceCheck, BasicTest) {
  const dynamic_config::StorageMock config{
      {taxi_config::ALICE_ALLOWED_TARIFFS, {"econom", "comfort"}}};

  const auto& params = GetParam();
  const auto expected_categories_visibility = BuildCategoriesVisibilityMap(
      params.visible_categories, params.not_visible_categories);

  const auto context = CheckContextFromUserSource(params.user_source);

  CheckCategoriesVisibility(IsCategoryVisibleByUserSource, context.Get(),
                            config.GetSnapshot(),
                            expected_categories_visibility);
}

INSTANTIATE_TEST_SUITE_P(/* no prefix */, TestUserSourceCheck,
                         testing::ValuesIn(kBasicTestParams),
                         ::utest::PrintTestName());

}  // namespace user_source_check

namespace experiments_check {

struct TestParams {
  std::string zone_name;
  std::unordered_set<std::string> experiments;
  std::unordered_set<std::string> visible_categories;
  std::unordered_set<std::string> not_visible_categories;
  TariffSettingsMap tariff_settings;

  std::string test_name;
};

struct DelayedMatch {
  bool enabled;

  std::string test_name;
};

taxi_tariffs::models::Category BuildCategoryWithSettings(
    const std::string& name,
    const std::optional<bool> visible_by_default = std::nullopt,
    const std::optional<std::string>& show_experiment = std::nullopt,
    const std::optional<std::string>& hide_experiment = std::nullopt,
    const std::optional<bool> visible_on_site = std::nullopt) {
  taxi_tariffs::models::Category cat;
  cat.visibility_settings = clients::taxi_tariffs::VisibilitySettings();
  cat.name = name;
  cat.visibility_settings->visible_by_default = visible_by_default;
  cat.visibility_settings->show_experiment = show_experiment;
  cat.visibility_settings->hide_experiment = hide_experiment;
  cat.visibility_settings->visible_on_site = visible_on_site;
  return cat;
}

taxi_tariffs::models::TariffSettings BuildTariffSettings(
    const std::vector<taxi_tariffs::models::Category>& categories) {
  taxi_tariffs::models::TariffSettings settings;
  if (!categories.empty()) {
    settings.categories = categories;
  }
  return settings;
}

class TestExperimentsCheck
    : public testing::TestWithParam<std::tuple<DelayedMatch, TestParams>> {};

const std::string kShowBusinessExperiment = R"({
  "business": {
    "visible_by_default": false,
    "show_experiment": "show_business"
  }
})";

const auto kShowBusinessCategory =
    BuildCategoryWithSettings("business", false, "show_business", std::nullopt);

const std::string kHideBusinessExperiment = R"({
  "business": {
    "visible_by_default": true,
    "hide_experiment": "hide_business"
  }
})";
const auto kHideBusinessCategory =
    BuildCategoryWithSettings("business", true, std::nullopt, "hide_business");

const std::vector<TestParams> kBasicTestParams = {
    {
        "moscow",
        {"hide_business"},
        {"econom", "comfort"},
        {"business"},
        {{"moscow",
          BuildTariffSettings({BuildCategoryWithSettings("econom", true),
                               BuildCategoryWithSettings("comfort", true),
                               kHideBusinessCategory})}},
        "HideByExperimentSettingsProvider",
    },
    {
        "moscow",
        {"show_business"},
        {"business"},
        {"econom", "comfort"},
        {{"moscow",
          BuildTariffSettings({BuildCategoryWithSettings("econom", false),
                               BuildCategoryWithSettings("comfort", false),
                               kShowBusinessCategory})}},
        "ShowByExperimentSettingsProvider",
    },
    {
        "moscow",
        {},
        {},
        {"business", "econom", "comfort"},
        {},
        "DefaultSettingsProviderBehavior",
    },
    {
        "moscow",
        {},
        {},
        {"business", "econom", "comfort"},
        {{"moscow",
          BuildTariffSettings({BuildCategoryWithSettings("econom"),
                               BuildCategoryWithSettings("comfort"),
                               BuildCategoryWithSettings("business")})}},
        "EmptyCategoriesSettingsProviderBehavior",
    },
};

const std::vector<DelayedMatch> kDelayedMatchTestParams = {
    {false, "DelayMatchedDisabled"},
    {true, "DelayMatchedEnabled"},
};

TEST_P(TestExperimentsCheck, BasicTest) {
  const auto delayed_match_enabled = std::get<0>(GetParam()).enabled;
  const auto& params = std::get<1>(GetParam());
  const dynamic_config::StorageMock config{};

  const auto expected_categories_visibility = BuildCategoriesVisibilityMap(
      params.visible_categories, params.not_visible_categories);

  const auto zone_name = ZoneName{params.zone_name};
  const auto user_experiments =
      delayed_match_enabled ? OptUserExperiments{} : params.experiments;

  // It is safe to pass nullptr as exp3_cache as long as we mock all methods
  // called during test run.
  auto exp3_helper = std::make_shared<ExperimentsHelperMock>(nullptr);
  auto tariff_settings_ptr =
      utils::MakeSharedReadable<TariffSettingsMap>(params.tariff_settings);

  auto exp3_mock = [&params](const std::string& exp_name, const AppVars&,
                             const std::optional<PhoneId>&,
                             const std::optional<PaymentOption>&) {
    return params.experiments.count(exp_name) > 0;
  };

  if (delayed_match_enabled) {
    EXPECT_CALL(*exp3_helper,
                IsVisibilityExperimentEnabled(testing::_, testing::_,
                                              testing::_, testing::_))
        .Times(testing::AnyNumber())
        .WillRepeatedly(testing::Invoke(exp3_mock));
  }

  const auto context = CheckContextFromZoneNameAndExp(
      zone_name, user_experiments, exp3_helper, tariff_settings_ptr);

  CheckCategoriesVisibility(IsCategoryVisibleByExperiments, context.Get(),
                            config.GetSnapshot(),
                            expected_categories_visibility);
}

INSTANTIATE_TEST_SUITE_P(
    /* no prefix */, TestExperimentsCheck,
    testing::Combine(testing::ValuesIn(kDelayedMatchTestParams),
                     testing::ValuesIn(kBasicTestParams)),
    ::utest::PrintTestName());

}  // namespace experiments_check

}  // namespace tariff_categories_visibility::tests
