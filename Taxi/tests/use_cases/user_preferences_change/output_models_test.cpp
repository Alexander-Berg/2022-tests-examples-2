#include "output_models_test.hpp"

#include <userver/utest/utest.hpp>

namespace sweet_home::tests::output_models {

user_preferences_change::output_models::Preference MakePreference(
    std::string setting_id, setting::SettingsValueVariant value,
    setting::SettingType type, bool enabled, bool is_local) {
  user_preferences_change::output_models::Preference result;

  const auto metrica_name = setting_id + "_metrica_name";
  result.setting_id = setting_id;
  result.value = value;
  result.type = type;
  result.enabled = enabled;
  result.is_local = is_local;
  result.metrica_name = metrica_name;

  return result;
}

void AssertPreference(
    const user_preferences_change::output_models::Preference& left,
    const user_preferences_change::output_models::Preference& right) {
  ASSERT_EQ(left.setting_id, right.setting_id);
  ASSERT_EQ(left.value, right.value);
  ASSERT_EQ(left.type, right.type);
  ASSERT_EQ(left.enabled, right.enabled);
  ASSERT_EQ(left.is_local, right.is_local);
  if (left.metrica_name) {
    ASSERT_TRUE(right.metrica_name) << "left is " << *left.metrica_name;
    ASSERT_EQ(*left.metrica_name, *right.metrica_name);
  } else {
    ASSERT_FALSE(right.metrica_name) << "right is " << *right.metrica_name;
  }
}

}  // namespace sweet_home::tests::output_models
