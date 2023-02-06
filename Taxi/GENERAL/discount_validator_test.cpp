#include "discount_validator.hpp"
#include <testing/taxi_config.hpp>
#include <userver/dynamic_config/fwd.hpp>
#include <userver/dynamic_config/value.hpp>
#include <userver/utest/utest.hpp>

TEST(ValidateDiscount, ValidateTripsRestrictions__InvalidBrand) {
  handlers::Rule rule;
  rule.trips_restriction = {{{1, 2}, "invalid", "card"}};
  const dynamic_config::ValueDict<std::string> application_map_brand{
      "APPLICATION_MAP_BRAND",
      {{"__default__", "yataxi"}, {"uber_android", "yauber"}}};

  auto storage = dynamic_config::MakeDefaultStorage(
      {{taxi_config::APPLICATION_MAP_BRAND, application_map_brand}});

  ASSERT_THROW(models::ValidateDiscount(rule, "full_money_discounts",
                                        storage.GetSnapshot()),
               discounts::models::Error);
}

TEST(ValidateDiscount, ValidateTripsRestrictions__ValidBrand) {
  handlers::Rule rule;
  rule.trips_restriction = {{{1, 2}, "yauber", "card"}};
  const dynamic_config::ValueDict<std::string> application_map_brand{
      "APPLICATION_MAP_BRAND",
      {{"__default__", "yataxi"}, {"uber_android", "yauber"}}};

  auto storage = dynamic_config::MakeDefaultStorage(
      {{taxi_config::APPLICATION_MAP_BRAND, application_map_brand}});

  ASSERT_NO_THROW(models::ValidateDiscount(rule, "full_money_discounts",
                                           storage.GetSnapshot()));
}

TEST(ValidateDiscount, ValidateHasMoney) {
  handlers::Rule rule;
  rule.values_with_schedules = {handlers::ValueWithSchedule{}};
  rule.values_with_schedules[0].money_value = handlers::Discount{};
  static const std::array<handlers::HierarchyName, 3>
      kCanHasMoneyHierarchyNames{
          handlers::HierarchyName::kFullMoneyDiscounts,
          handlers::HierarchyName::kExperimentalMoneyDiscounts,
          handlers::HierarchyName::kPaymentMethodMoneyDiscounts};
  for (const auto hierarchy_name : kCanHasMoneyHierarchyNames) {
    EXPECT_NO_THROW(models::ValidateDiscount(
        rule, ToString(hierarchy_name), dynamic_config::GetDefaultSnapshot()));
  }
  static const std::array<handlers::HierarchyName, 6>
      kCanNotHasMoneyHierarchyNames{
          handlers::HierarchyName::kFullDiscounts,
          handlers::HierarchyName::kExperimentalDiscounts,
          handlers::HierarchyName::kPaymentMethodDiscounts,
          handlers::HierarchyName::kFullCashbackDiscounts,
          handlers::HierarchyName::kExperimentalCashbackDiscounts,
          handlers::HierarchyName::kPaymentMethodCashbackDiscounts};
  for (const auto hierarchy_name : kCanNotHasMoneyHierarchyNames) {
    EXPECT_THROW(models::ValidateDiscount(rule, ToString(hierarchy_name),
                                          dynamic_config::GetDefaultSnapshot()),
                 discounts::models::Error);
  }
}

TEST(ValidateDiscount, ValidateHasCashback) {
  handlers::Rule rule;
  rule.values_with_schedules = {handlers::ValueWithSchedule{}};
  rule.values_with_schedules[0].cashback_value = handlers::Discount{};
  static const std::array<handlers::HierarchyName, 3>
      kCanHasCashbackHierarchyNames{
          handlers::HierarchyName::kFullCashbackDiscounts,
          handlers::HierarchyName::kExperimentalCashbackDiscounts,
          handlers::HierarchyName::kPaymentMethodCashbackDiscounts};
  for (const auto hierarchy_name : kCanHasCashbackHierarchyNames) {
    EXPECT_NO_THROW(models::ValidateDiscount(
        rule, ToString(hierarchy_name), dynamic_config::GetDefaultSnapshot()))
        << ToString(hierarchy_name);
  }
  static const std::array<handlers::HierarchyName, 6>
      kCanNotHasCashbackHierarchyNames{
          handlers::HierarchyName::kFullDiscounts,
          handlers::HierarchyName::kPaymentMethodDiscounts,
          handlers::HierarchyName::kExperimentalDiscounts,
          handlers::HierarchyName::kFullMoneyDiscounts,
          handlers::HierarchyName::kExperimentalMoneyDiscounts,
          handlers::HierarchyName::kPaymentMethodMoneyDiscounts,
      };
  for (const auto hierarchy_name : kCanNotHasCashbackHierarchyNames) {
    EXPECT_THROW(models::ValidateDiscount(rule, ToString(hierarchy_name),
                                          dynamic_config::GetDefaultSnapshot()),
                 discounts::models::Error)
        << ToString(hierarchy_name);
  }
}
