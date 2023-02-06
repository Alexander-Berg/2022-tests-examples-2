#include "brandings.hpp"
#include <defs/all_definitions.hpp>
#include <userver/formats/json.hpp>
#include <userver/utest/utest.hpp>

TEST(GetBrandingKeys, Empty) {
  handlers::Rule raw_discount;
  EXPECT_FALSE(utils::GetBrandingKeys(raw_discount));
}

TEST(GetBrandingKeys, EmptyBrandings) {
  handlers::Rule raw_discount;
  handlers::DiscountMeta discount_meta;
  discount_meta.branding_keys = handlers::BrandingKeys{
      handlers::BrandingTankerKeys{}, handlers::BrandingTankerKeys{}};
  raw_discount.discount_meta = discount_meta;
  EXPECT_FALSE(utils::GetBrandingKeys(raw_discount));
}

TEST(GetBrandingKeys, Ok) {
  handlers::Rule raw_discount;
  handlers::DiscountMeta discount_meta;
  discount_meta.branding_keys = handlers::BrandingKeys{
      {}, handlers::BrandingTankerKeys{"test_combined_card_title", {}, {}}};
  raw_discount.discount_meta = discount_meta;
  EXPECT_TRUE(utils::GetBrandingKeys(raw_discount));
}
