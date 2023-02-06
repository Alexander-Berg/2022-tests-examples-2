#include <userver/utest/utest.hpp>

#include <defs/api/promo.hpp>
#include <defs/definitions.hpp>
#include <experiments3/eats_restapp_promo_settings.hpp>
#include <utils/promo_features_validators/brand_orders_count.hpp>

namespace eats_restapp_promo::utils {

TEST(ValivatationBrandOrdersCountDataFull, DontThrowExceptionForNullValues) {
  ASSERT_NO_THROW(
      ValidateBrandOrdersCount(models::PromoConfiguration(), std::nullopt));
  ASSERT_NO_THROW(ValidateBrandOrdersCount(models::PromoConfiguration(),
                                           std::vector<int>{1, 2}));
}

TEST(ValivatationBrandOrdersCountDataFull,
     ThrowExceptionForUnvailabeBrandOrdersCount) {
  models::PromoConfiguration configuration;
  types::ValueOrderIndexesConfiguration settings;
  settings.available_order_indexes = std::vector<int>{1, 3, 5};
  configuration.order_indexes_settings = settings;
  ASSERT_THROW(
      ValidateBrandOrdersCount(configuration, std::vector<int>{1, 2, 5}),
      models::ValidationError);
}

TEST(ValivatationBrandOrdersCountDataFull,
     NoThrowExceptionForAvailabeBrandOrdersCount) {
  models::PromoConfiguration configuration;
  types::ValueOrderIndexesConfiguration settings;
  settings.available_order_indexes = std::vector<int>{1, 3, 5};
  configuration.order_indexes_settings = settings;
  ASSERT_NO_THROW(
      ValidateBrandOrdersCount(configuration, std::vector<int>{1, 3}));
}

TEST(ValivatationBrandOrdersCountDataFull,
     NoThrowExceptionForRequestEmptyBrandOrdersCount) {
  models::PromoConfiguration configuration;
  types::ValueOrderIndexesConfiguration settings;
  settings.available_order_indexes = std::vector<int>{1, 3, 5};
  configuration.order_indexes_settings = settings;
  ASSERT_NO_THROW(ValidateBrandOrdersCount(configuration, std::vector<int>()));
}

TEST(ValivatationBrandOrdersCountDataFull,
     ThrowExceptionForEmptySettingsBrandOrdersCount) {
  models::PromoConfiguration configuration;
  types::ValueOrderIndexesConfiguration settings;
  settings.available_order_indexes = std::vector<int>();
  configuration.order_indexes_settings = settings;
  ASSERT_THROW(
      ValidateBrandOrdersCount(configuration, std::vector<int>{1, 2, 5}),
      models::ValidationError);
}

TEST(ValivatationBrandOrdersCountDataFull,
     NoThrowExceptionForEmptyBrandOrdersCount) {
  models::PromoConfiguration configuration;
  types::ValueOrderIndexesConfiguration settings;
  settings.available_order_indexes = std::vector<int>();
  configuration.order_indexes_settings = settings;
  ASSERT_NO_THROW(ValidateBrandOrdersCount(configuration, std::vector<int>()));
}

}  // namespace eats_restapp_promo::utils
