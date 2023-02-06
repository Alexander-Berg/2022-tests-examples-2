#include <userver/utest/utest.hpp>

#include <defs/api/promo.hpp>
#include <defs/definitions.hpp>
#include <experiments3/eats_restapp_promo_settings.hpp>
#include <utils/promo_features_validators/shipping_types.hpp>

namespace eats_restapp_promo::utils {

TEST(ValivatationShippingTypesDataFull, DontThrowExceptionForNullValues) {
  ASSERT_NO_THROW(
      ValidateShippingTypes(models::PromoConfiguration(), std::nullopt));
}

TEST(ValivatationShippingTypesDataFull,
     DontThrowExceptionForEmptySettingsShippingTypes) {
  ASSERT_NO_THROW(ValidateShippingTypes(
      models::PromoConfiguration(),
      std::vector<std::string>{"delivery", "pickup", "other"}));
}

TEST(ValivatationShippingTypesDataFull,
     ThrowExceptionForAnvailableShippingTypes) {
  models::PromoConfiguration configuration;
  types::ValueShippingTypesConfiguration settings;
  settings.available_shipping_types =
      std::vector<experiments3::eats_restapp_promo_settings::ShippingTypeValue>{
          {"delivery", "Доставка"}, {"pickup", "Недоставка"}};
  configuration.shipping_types = settings;
  ASSERT_THROW(ValidateShippingTypes(
                   configuration,
                   std::vector<std::string>{"delivery", "pickup", "other"}),
               models::ValidationError);
}

TEST(ValivatationShippingTypesDataFull,
     NoThrowExceptionForAvailableShippingTypes) {
  models::PromoConfiguration configuration;
  types::ValueShippingTypesConfiguration settings;
  settings.available_shipping_types =
      std::vector<experiments3::eats_restapp_promo_settings::ShippingTypeValue>{
          {"delivery", "Доставка"}, {"pickup", "Недоставка"}};
  configuration.shipping_types = settings;
  ASSERT_NO_THROW(ValidateShippingTypes(
      configuration, std::vector<std::string>{"pickup", "delivery"}));
}

}  // namespace eats_restapp_promo::utils
