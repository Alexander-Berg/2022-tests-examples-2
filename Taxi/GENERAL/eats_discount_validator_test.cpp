#include "eats_discount_validator.hpp"

#include <userver/utest/utest.hpp>

TEST(EatsDiscountValidator, ValidatePromo) {
  using Promo = handlers::Promo;
  using PromoTypes = taxi_config::eats_discounts_promo_types::VariableType;

  PromoTypes default_promo_types{{}};
  PromoTypes normal_promo_types{{{"type", "name", "description"}}};

  EXPECT_NO_THROW(models::EatsDiscountValidator::ValidatePromo(
      Promo{"name", "descript", "picture_uri", "type"}, normal_promo_types));
  EXPECT_NO_THROW(models::EatsDiscountValidator::ValidatePromo(
      Promo{"name", std::nullopt, "picture_uri", "type"}, normal_promo_types));
  EXPECT_NO_THROW(models::EatsDiscountValidator::ValidatePromo(
      Promo{std::nullopt, std::nullopt, std::nullopt, "type"},
      normal_promo_types));
  EXPECT_NO_THROW(models::EatsDiscountValidator::ValidatePromo(
      Promo{"name", "descript", "picture_uri", std::nullopt},
      default_promo_types));

  EXPECT_THROW(models::EatsDiscountValidator::ValidatePromo(
                   Promo{std::nullopt, "descript", std::nullopt, "other_type"},
                   normal_promo_types),
               discounts::models::Error);
  EXPECT_THROW(
      models::EatsDiscountValidator::ValidatePromo(
          Promo{std::nullopt, std::nullopt, std::nullopt, std::nullopt},
          default_promo_types),
      discounts::models::Error);
  EXPECT_THROW(models::EatsDiscountValidator::ValidatePromo(
                   Promo{"name", "descript", std::nullopt, std::nullopt},
                   default_promo_types),
               discounts::models::Error);
  EXPECT_THROW(models::EatsDiscountValidator::ValidatePromo(
                   Promo{"name", "descript", "picture_uri", "type"},
                   default_promo_types),
               discounts::models::Error);
}
