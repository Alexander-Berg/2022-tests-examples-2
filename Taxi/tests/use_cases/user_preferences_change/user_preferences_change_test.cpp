#include <userver/utest/utest.hpp>

#include "use_cases/user_preferences_change/user_preferences_change.hpp"

#include "tests/use_cases/user_preferences_change/output_models_test.hpp"

#include "tests/internal/models_test.hpp"
#include "tests/mocks/setting_definition_repository.hpp"
#include "tests/mocks/user_preferences_repository.hpp"

namespace sweet_home::user_preferences_change {

namespace {

static const std::string kDefaultYandexUid = "yandex_uid";
static const std::string kDefaultServiceId = "service_id";

Deps PrepareDeps() {
  Deps deps;

  deps.user_preferences_repository =
      std::make_shared<mocks::UserPreferencesRepositoryMock>();

  auto setting_definition_repository_mock =
      std::make_shared<mocks::SettingDefinitionRepositoryMock>();
  setting_definition_repository_mock->SetStub_GetDefinitions(
      [](const std::string&) {
        return tests::MakeSettingDefinitionMap({tests::MakeDefinition(
            "subscription_renewal_for_points", setting::SettingType::kBoolean,
            true, false, true)});
      });
  deps.setting_repository = setting_definition_repository_mock;

  return deps;
}

}  // namespace

TEST(TestChangeUserPreference, HappyPath) {
  // deps
  auto deps = PrepareDeps();

  std::vector<user_preferences::Preference> preferences{tests::MakePreference(
      "subscription_renewal_for_points", setting::SettingType::kBoolean, true)};

  // call
  auto result = ChangeUserPreferences(deps, preferences, kDefaultYandexUid,
                                      kDefaultServiceId, "1");

  ASSERT_EQ(result.version, "2");
  ASSERT_EQ(result.preferences.size(), 1);

  output_models::Preference expected_preference =
      tests::output_models::MakePreference("subscription_renewal_for_points",
                                           true, setting::SettingType::kBoolean,
                                           true, false);
  tests::output_models::AssertPreference(result.preferences[0],
                                         expected_preference);
}

TEST(TestChangeUserPreference, RepositoryThrowsConflictError) {
  // deps
  auto deps = PrepareDeps();
  auto user_preferences_mock =
      std::make_shared<mocks::UserPreferencesRepositoryMock>();
  user_preferences_mock->SetStub_ChangePreferences(
      [](const std::vector<user_preferences::Preference>&, const std::string&,
         const std::string&) -> user_preferences::UserPreferences {
        throw user_preferences::VersionConflict("");
      });
  deps.user_preferences_repository = user_preferences_mock;

  std::vector<user_preferences::Preference> preferences{tests::MakePreference(
      "subscription_renewal_for_points", setting::SettingType::kBoolean, true)};

  // call and assert
  ASSERT_THROW(ChangeUserPreferences(deps, preferences, kDefaultYandexUid,
                                     kDefaultServiceId, "1"),
               VersionConflict);
}

TEST(TestChangeUserPreference, RepositoryThrowsRepositoryError) {
  // deps
  auto deps = PrepareDeps();
  auto user_preferences_mock =
      std::make_shared<mocks::UserPreferencesRepositoryMock>();
  user_preferences_mock->SetStub_ChangePreferences(
      [](const std::vector<user_preferences::Preference>&, const std::string&,
         const std::string&) -> user_preferences::UserPreferences {
        throw user_preferences::RepositoryError("");
      });
  deps.user_preferences_repository = user_preferences_mock;

  std::vector<user_preferences::Preference> preferences{tests::MakePreference(
      "subscription_renewal_for_points", setting::SettingType::kBoolean, true)};

  // call and assert
  ASSERT_THROW(ChangeUserPreferences(deps, preferences, kDefaultYandexUid,
                                     kDefaultServiceId, "1"),
               UseCaseError);
}

TEST(TestChangeUserPreference, SettingDefinishionNotFoundChangePartOfSettings) {
  // deps
  auto deps = PrepareDeps();
  auto user_preferences_mock =
      std::make_shared<mocks::UserPreferencesRepositoryMock>();
  user_preferences_mock->SetStub_ChangePreferences(
      [](const std::vector<user_preferences::Preference>& preferences,
         const std::string& yandex_uid,
         const std::string& version) -> user_preferences::UserPreferences {
        if (preferences.size() > 1) {
          throw user_preferences::RepositoryError("");
        }
        return tests::MakeUserPreferences(
            {tests::MakePreference("subscription_renewal_for_points",
                                   setting::SettingType::kBoolean, true)},
            std::to_string(std::stoi(version) + 1), yandex_uid);
      });
  deps.user_preferences_repository = user_preferences_mock;

  std::vector<user_preferences::Preference> preferences{
      tests::MakePreference("subscription_renewal_for_points",
                            setting::SettingType::kBoolean, true),
      tests::MakePreference("unknown_setting", setting::SettingType::kBoolean,
                            true)};

  // call
  auto result = ChangeUserPreferences(deps, preferences, kDefaultYandexUid,
                                      kDefaultServiceId, "1");

  ASSERT_EQ(result.version, "2");
  ASSERT_EQ(result.preferences.size(), 1);

  output_models::Preference expected_preference =
      tests::output_models::MakePreference("subscription_renewal_for_points",
                                           true, setting::SettingType::kBoolean,
                                           true, false);
  tests::output_models::AssertPreference(result.preferences[0],
                                         expected_preference);
}

TEST(TestChangeUserPreference, SettingDefinishionNotFoundEmptyAns) {
  // deps
  auto deps = PrepareDeps();

  std::vector<user_preferences::Preference> preferences{tests::MakePreference(
      "unknown_setting", setting::SettingType::kBoolean, true)};

  // call
  auto result = ChangeUserPreferences(deps, preferences, kDefaultYandexUid,
                                      kDefaultServiceId, "1");

  ASSERT_TRUE(result.version.empty());
  ASSERT_EQ(result.preferences.size(), 0);
}

}  // namespace sweet_home::user_preferences_change
