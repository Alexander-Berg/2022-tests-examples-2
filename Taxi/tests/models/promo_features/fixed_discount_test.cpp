#include <userver/utest/utest.hpp>

#include <defs/api/promo.hpp>
#include <defs/definitions.hpp>
#include <defs/internal/stored_data.hpp>
#include <experiments3/eats_restapp_promo_settings.hpp>

#include <models/promo_features/fixed_discount.hpp>
#include <types/discount_data.hpp>
#include <types/stored_data.hpp>

namespace eats_restapp_promo::models::promo_features {

namespace {

struct Validator {};

const std::vector<handlers::PromoBonus> kOldResponseBonuses = {
    handlers::PromoBonus{"1", 5, std::vector<double>{1, 2}, {}, {}, 5.0},
    handlers::PromoBonus{"3", {}, std::vector<double>{1}, {}, {}, 10.0}};

const std::vector<::defs::internal::stored_data::StoredPromoBonus>
    kOldStoredBonuses = {::defs::internal::stored_data::StoredPromoBonus{
                             "1", 5, std::vector<double>{1, 2}, {}, {}, {}},
                         ::defs::internal::stored_data::StoredPromoBonus{
                             "3", {}, std::vector<double>{1}, {}, {}, {}}};

formats::json::ValueBuilder MakeStorageBonuses(
    const std::vector<::defs::internal::stored_data::StoredPromoBonus>& res) {
  formats::json::ValueBuilder kStorageBonuses;
  kStorageBonuses["bonuses"] = res;
  return kStorageBonuses;
}

}  // namespace

struct FixedDiscountData {
  handlers::PromoRequest data;

  handlers::Promo response;
  handlers::Promo expected_response;
  types::StoredDataRaw stored_data;
  types::StoredDataRaw expected_stored_data;
  types::DiscountDataRaw discount_data;
  types::DiscountDataRaw expected_discount_data;
};

class FixedDiscountDataFull
    : public ::testing::TestWithParam<FixedDiscountData> {};

const std::vector<FixedDiscountData> kFixedDiscountData{
    {handlers::PromoRequest(), handlers::Promo(), handlers::Promo(),
     types::StoredDataRaw(), types::StoredDataRaw(), types::DiscountDataRaw(),
     types::DiscountDataRaw()},
    {handlers::PromoRequest(),
     handlers::Promo{
         1, {}, "name", {}, {}, {}, {}, {}, {}, {}, kOldResponseBonuses},
     handlers::Promo{
         1, {}, "name", {}, {}, {}, {}, {}, {}, {}, kOldResponseBonuses},
     types::StoredDataRaw{
         {1, 2}, {}, {}, {}, MakeStorageBonuses(kOldStoredBonuses), {}},
     types::StoredDataRaw{
         {1, 2}, {}, {}, {}, MakeStorageBonuses(kOldStoredBonuses), {}},
     types::DiscountDataRaw{
         {}, {1, 2}, {}, {}, {}, 1, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}},
     types::DiscountDataRaw{
         {}, {1, 2}, {}, {}, {}, 1, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}}}};

INSTANTIATE_TEST_SUITE_P(FixedDiscountData, FixedDiscountDataFull,
                         ::testing::ValuesIn(kFixedDiscountData));

TEST_P(FixedDiscountDataFull, check_fixed_discount_feature) {
  auto param = GetParam();
  models::PromoSettings settings;
  auto fixed_discount = FixedDiscount(Validator(), settings, {}, param.data);

  fixed_discount.UpdateResponse(param.response);
  ASSERT_EQ(param.response.bonuses.size(),
            param.expected_response.bonuses.size());

  fixed_discount.UpdateStoredData(param.stored_data);
  ASSERT_EQ(param.stored_data, param.expected_stored_data);

  fixed_discount.UpdateDiscountData(param.discount_data);
  ASSERT_EQ(param.discount_data, param.expected_discount_data);
}

}  // namespace eats_restapp_promo::models::promo_features
