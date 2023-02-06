#include <testing/taxi_config.hpp>
#include <userver/utest/utest.hpp>

#include "utils/get_place_enabled_info.hpp"

namespace eats_restapp_places::utils {

/*
1. Причина НЕ в AUTOSTOP_DISABLE_REASONS (в 1м ифе)
    1.1. Причина В REASONS_SELF (DISABLE_REASON_RUSH_HOUR, 28)
        -> true
     1.2. Причина НЕ в REASONS_SELF (DISABLE_REASON_MENU_UPDATE, 0)
        -> false
2. Причина В AUTOSTOP_DISABLE_REASONS (пропускаем 1й if)
    2.1. НЕТ core_disable_details_.available_at (заходим во 2й if)
        2.1.1. Причина В REASONS_SELF
    (DISABLE_REASON_AUTO_STOP_ORDER_CANCEL, 90) -> true
        2.1.2. Причина НЕ в REASONS_SELF (
    DISABLE_REASON_AUTO_STOP_CAN_NOT_COOK, 91) -> false
    2.2. ЕСТЬ core_disable_details_.available_at (пропускаем 2й if)
        2.2.1. Причина ЕСТЬ в auto_stop_rules_
            2.2.1.1. auto_stop_rule.self_enable_allowed = true
                (reason 90) -> true
            2.2.1.2. auto_stop_rule.self_enable_allowed = false
                (reason 91) -> false
        2.2.2. Причины НЕТ в auto_stop_rules_
            2.2.2.1. Причина НЕ в REASONS_SELF
                (DISABLE_REASON_AUTO_STOP_CAN_NOT_COOK, 92) -> false
*/

struct TestCase {
  int reason;
  bool has_field_available_at;
  bool expected_result;
};

class CheckCanBeEnabled : public ::testing::TestWithParam<TestCase> {};

TEST_P(CheckCanBeEnabled, EnabledTest) {
  // берутся дефолтные значения из конфигов
  const auto config =
      dynamic_config::GetDefaultSnapshot().Get<taxi_config::TaxiConfig>();
  const auto restaurant_disable_details_config =
      config.eats_restapp_places_restaurant_disable_details;
  const auto restaurant_disable_lists_config =
      config.eats_restapp_places_restaurant_disable_lists;
  std::vector<clients::eats_core::AutostopRule> auto_stop_rules_list = {};

  const auto& test_case = GetParam();
  clients::eats_core::PlaceDisabledetails disable_details;
  disable_details.reason = test_case.reason;

  if (test_case.has_field_available_at) {
    disable_details.available_at = std::chrono::system_clock::from_time_t(42);
    std::vector<clients::eats_core::AutostopRule> auto_stop_rules_list = {
        {90, 111, true}, {91, 222, false}};
  }

  PlaceEnabledInfo place_enabled_info(
      disable_details, restaurant_disable_details_config,
      restaurant_disable_lists_config, auto_stop_rules_list);

  ASSERT_EQ(place_enabled_info.CheckCanBeEnabled(), test_case.expected_result);
}

INSTANTIATE_TEST_SUITE_P(
    CheckCanBeEnabledTest, CheckCanBeEnabled,
    ::testing::Values(TestCase{28, false, true}, TestCase{0, false, false},
                      TestCase{90, false, true}, TestCase{91, false, false},
                      TestCase{90, true, true}, TestCase{91, true, false},
                      TestCase{92, true, false}));

}  // namespace eats_restapp_places::utils
