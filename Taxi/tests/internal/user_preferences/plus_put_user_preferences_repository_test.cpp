#include <userver/utest/utest.hpp>

#include "internal/user_preferences/impl/plus_user_preferences_repository.hpp"

#include "tests/internal/models_test.hpp"
#include "tests/mocks/plus_client.hpp"

namespace sweet_home::user_preferences {

namespace {

namespace handle_plus = clients::plus::v1_subscriptions_settings::put;

static const std::string kSubscriptionRenewalForPoints =
    "subscription_renewal_for_points";
static const std::string kDefaultYandexUid = "default_yandex_uid";

user_preferences::Preference MakePreference(const std::string& setting_id,
                                            bool value) {
  return {setting_id, {setting::SettingType::kBoolean, value}};
}

}  // namespace

UTEST(TestPlusUserPreferencesRepository, HappyPath) {
  auto plus_client_mock = mocks::PlusClientMock();
  auto user_preferences_repository =
      impl::PlusUserPreferencesRepository(plus_client_mock);

  std::vector<Preference> preferences{
      MakePreference(kSubscriptionRenewalForPoints, true)};

  const auto response = user_preferences_repository.ChangeUserPreferences(
      preferences, kDefaultYandexUid, "1");

  ASSERT_EQ(response.yandex_uid, kDefaultYandexUid);
  ASSERT_EQ(response.concurrency_version, "2");
  ASSERT_EQ(response.preferences.size(), 1);

  const auto& changed_preferences = response.preferences;
  ASSERT_EQ(changed_preferences[0].setting_id, kSubscriptionRenewalForPoints);
  ASSERT_EQ(changed_preferences[0].value.type, setting::SettingType::kBoolean);
  ASSERT_EQ(std::get<bool>(changed_preferences[0].value.value), true);
}

UTEST(TestPlusUserPreferencesRepository, UnknownSettingId) {
  auto plus_client_mock = mocks::PlusClientMock();
  auto user_preferences_repository =
      impl::PlusUserPreferencesRepository(plus_client_mock);

  std::vector<Preference> preferences{MakePreference("some_new_setting", true)};

  ASSERT_THROW(user_preferences_repository.ChangeUserPreferences(
                   preferences, kDefaultYandexUid, "1"),
               UnsupportedSettingsToChange);
}

UTEST(TestPlusUserPreferencesRepository, WrongValueTypeForSetting) {
  auto plus_client_mock = mocks::PlusClientMock();
  auto user_preferences_repository =
      impl::PlusUserPreferencesRepository(plus_client_mock);

  std::vector<Preference> preferences{
      tests::MakePreference(kSubscriptionRenewalForPoints, "some_value")};

  ASSERT_THROW(user_preferences_repository.ChangeUserPreferences(
                   preferences, kDefaultYandexUid, "1"),
               UnsupportedSettingsToChange);
}

UTEST(TestPlusUserPreferencesRepository, PlusReturn409) {
  auto v_1_subscriptions_settings_put_handler =
      [](const handle_plus::Request &
         /*request*/) -> handle_plus::Response200 {
    throw handle_plus::Response409();
  };
  auto plus_client_mock =
      mocks::PlusClientMock(v_1_subscriptions_settings_put_handler);
  auto user_preferences_repository =
      impl::PlusUserPreferencesRepository(plus_client_mock);

  std::vector<Preference> preferences{
      MakePreference(kSubscriptionRenewalForPoints, true)};

  ASSERT_THROW(user_preferences_repository.ChangeUserPreferences(
                   preferences, kDefaultYandexUid, "1"),
               VersionConflict);
}

UTEST(TestPlusUserPreferencesRepository, WrongDataFromPlus) {
  auto v_1_subscriptions_settings_put_handler =
      [](const handle_plus::Request& request) {
        handle_plus::Response200 response;
        response.version = std::to_string(std::stoi(request.body.version) + 1);
        return response;
      };
  auto plus_client_mock =
      mocks::PlusClientMock(v_1_subscriptions_settings_put_handler);
  auto user_preferences_repository =
      impl::PlusUserPreferencesRepository(plus_client_mock);

  std::vector<Preference> preferences{
      MakePreference(kSubscriptionRenewalForPoints, true)};

  ASSERT_THROW(user_preferences_repository.ChangeUserPreferences(
                   preferences, kDefaultYandexUid, "1"),
               RepositoryError);
}

}  // namespace sweet_home::user_preferences
