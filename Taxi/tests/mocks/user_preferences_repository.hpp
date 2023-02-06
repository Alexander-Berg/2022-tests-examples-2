#pragma once

#include "internal/user_preferences/repository.hpp"

#include "tests/internal/models_test.hpp"

#include <functional>

namespace sweet_home::mocks {

using GetUserPreferencesForServiceHandler =
    std::function<user_preferences::UserPreferences(const std::string&,
                                                    const std::string&)>;
using ChangeUserPreferencesHandler =
    std::function<user_preferences::UserPreferences(
        const std::vector<user_preferences::Preference>&, const std::string&,
        const std::string&)>;

class UserPreferencesRepositoryMock
    : public user_preferences::UserPreferencesRepository {
 private:
  GetUserPreferencesForServiceHandler handler_get_user_preferences_ = nullptr;
  ChangeUserPreferencesHandler handler_change_user_preferences_ = nullptr;

 public:
  UserPreferencesRepositoryMock(){};

  void SetStub_GetPreferences(
      const GetUserPreferencesForServiceHandler& handler) {
    handler_get_user_preferences_ = handler;
  }

  void SetStub_ChangePreferences(const ChangeUserPreferencesHandler& handler) {
    handler_change_user_preferences_ = handler;
  }

  user_preferences::UserPreferences GetUserPreferencesForService(
      const std::string& yandex_uid,
      const std::string& service_id) const override {
    if (handler_get_user_preferences_) {
      return handler_get_user_preferences_(yandex_uid, service_id);
    }
    return tests::MakeUserPreferences(
        {tests::MakePreference("global_setting_id", "some_value")},
        "some_version", yandex_uid);
  }

  user_preferences::UserPreferences ChangeUserPreferences(
      const std::vector<user_preferences::Preference>& preferences,
      const std::string& yandex_uid,
      const std::string& concurrency_version) const override {
    if (handler_change_user_preferences_) {
      handler_change_user_preferences_(preferences, yandex_uid,
                                       concurrency_version);
    }
    return tests::MakeUserPreferences(
        {tests::MakePreference("subscription_renewal_for_points",
                               setting::SettingType::kBoolean, true)},
        std::to_string(std::stoi(concurrency_version) + 1), yandex_uid);
  }
};

}  // namespace sweet_home::mocks
