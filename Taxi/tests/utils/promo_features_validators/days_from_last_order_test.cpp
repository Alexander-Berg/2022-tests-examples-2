#include <userver/utest/utest.hpp>

#include <defs/api/promo.hpp>
#include <defs/definitions.hpp>
#include <experiments3/eats_restapp_promo_settings.hpp>
#include <utils/promo_features_validators/days_from_last_order.hpp>

namespace eats_restapp_promo::utils {

TEST(ValivatationDaysFromLastOrderDataFull, DontThrowExceptionForNullValues) {
  ASSERT_NO_THROW(
      ValidateDaysFromLastOrder(models::PromoConfiguration(), std::nullopt));
  ASSERT_NO_THROW(ValidateDaysFromLastOrder(models::PromoConfiguration(), 1));
}

TEST(ValivatationDaysFromLastOrderDataFull,
     ThrowExceptionForUnvailabeDaysFromLastOrder) {
  models::PromoConfiguration configuration;
  types::ValueDaysFromLastOrderConfiguration settings;
  settings.available_days_from_last_order = std::vector<
      experiments3::eats_restapp_promo_settings::DaysFromLastOrderValue>{
      {1, "1"}, {3, "3"}, {5, "5"}};
  configuration.days_from_last_order_settings = settings;
  ASSERT_THROW(ValidateDaysFromLastOrder(configuration, 4),
               models::ValidationError);
}

TEST(ValivatationDaysFromLastOrderDataFull,
     NoThrowExceptionForAvailabeDaysFromLastOrder) {
  models::PromoConfiguration configuration;
  types::ValueDaysFromLastOrderConfiguration settings;
  settings.available_days_from_last_order = std::vector<
      experiments3::eats_restapp_promo_settings::DaysFromLastOrderValue>{
      {1, "1"}, {3, "3"}, {5, "5"}};
  configuration.days_from_last_order_settings = settings;
  ASSERT_NO_THROW(ValidateDaysFromLastOrder(configuration, 3));
}

TEST(ValivatationDaysFromLastOrderDataFull,
     ThrowExceptionForEmptyDaysFromLastOrder) {
  models::PromoConfiguration configuration;
  types::ValueDaysFromLastOrderConfiguration settings;
  settings.available_days_from_last_order = std::vector<
      experiments3::eats_restapp_promo_settings::DaysFromLastOrderValue>();
  configuration.days_from_last_order_settings = settings;
  ASSERT_THROW(ValidateDaysFromLastOrder(configuration, 4),
               models::ValidationError);
}

}  // namespace eats_restapp_promo::utils
