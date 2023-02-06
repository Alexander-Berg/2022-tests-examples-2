#include <userver/utest/utest.hpp>

#include "internal/user_preferences/impl/plus_user_preferences_repository.hpp"

#include "tests/internal/models_test.hpp"
#include "tests/mocks/plus_client.hpp"

namespace sweet_home::user_preferences {

namespace {

namespace handle_plus = clients::plus::v1_subscriptions_settings::get;

static const std::string kSettingSubscriptionRenewalForPoint =
    "subscription_renewal_for_points";
const bool kDefaultSettingValue = true;
const std::string kDefaultYandexUid = "default_yandex_uid";
const std::string kDefaultServiceId = "service_id";

}  // namespace

UTEST(TestPlusGetUserPreferencesRepository, HappyPath) {
  auto plus_client_mock = mocks::PlusClientMock();
  auto user_preferences_repository =
      impl::PlusUserPreferencesRepository(plus_client_mock);

  const auto response =
      user_preferences_repository.GetUserPreferencesForService(
          kDefaultYandexUid, kDefaultServiceId);

  ASSERT_EQ(response.yandex_uid, kDefaultYandexUid);
  ASSERT_EQ(response.concurrency_version, "1");
  ASSERT_EQ(response.preferences.size(), 1);

  const auto& preferences = response.preferences;
  ASSERT_EQ(preferences[0].setting_id, kSettingSubscriptionRenewalForPoint);
  ASSERT_EQ(preferences[0].value.type, setting::SettingType::kBoolean);
  ASSERT_EQ(std::get<bool>(preferences[0].value.value), kDefaultSettingValue);
}

UTEST(TestPlusGetUserPreferencesRepository, PlusThrows500) {
  auto v_1_subscriptions_settings_get_handler =
      [](const handle_plus::Request &
         /*request*/) -> handle_plus::Response200 {
    throw std::runtime_error("some error");
  };
  auto plus_client_mock =
      mocks::PlusClientMock(nullptr, v_1_subscriptions_settings_get_handler);
  auto user_preferences_repository =
      impl::PlusUserPreferencesRepository(plus_client_mock);
  ASSERT_THROW(user_preferences_repository.GetUserPreferencesForService(
                   kDefaultYandexUid, kDefaultServiceId),
               RepositoryError);
}

UTEST(TestPlusGetUserPreferencesRepository, PlusReturnOnlyVersion) {
  auto v_1_subscriptions_settings_get_handler =
      [](const handle_plus::Request &
         /*request*/) -> handle_plus::Response200 {
    handle_plus::Response200 response;
    response.version = "1";
    return response;
  };
  auto plus_client_mock =
      mocks::PlusClientMock(nullptr, v_1_subscriptions_settings_get_handler);
  auto user_preferences_repository =
      impl::PlusUserPreferencesRepository(plus_client_mock);
  auto response = user_preferences_repository.GetUserPreferencesForService(
      kDefaultYandexUid, kDefaultServiceId);
  ASSERT_EQ(response.concurrency_version, "1");
  ASSERT_EQ(response.yandex_uid, kDefaultYandexUid);
  ASSERT_EQ(response.preferences.empty(), true);
}

}  // namespace sweet_home::user_preferences
