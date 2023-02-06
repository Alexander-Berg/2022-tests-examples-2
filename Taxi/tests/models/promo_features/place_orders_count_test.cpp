#include <userver/utest/utest.hpp>

#include <defs/api/promo.hpp>
#include <defs/definitions.hpp>
#include <defs/internal/stored_data.hpp>
#include <experiments3/eats_restapp_promo_settings.hpp>

#include <models/promo_features/place_orders_count.hpp>
#include <types/discount_data.hpp>
#include <types/stored_data.hpp>

namespace eats_restapp_promo::models::promo_features {

namespace {

struct Validator {};

const std::vector<handlers::PromoRequirement> kOldResponseRequirement = {
    handlers::PromoRequirement{1.1, {}, {}, {}, std::vector<int>{2, 3}, {}, {}},
    handlers::PromoRequirement{0.1, {}, {}, {}, std::vector<int>{4}, {}, {}}};

const std::vector<::defs::internal::stored_data::StoredPromoRequirement>
    kOldStoredRequirement = {
        ::defs::internal::stored_data::StoredPromoRequirement{
            1.1,
            {},
            {},
            {},
            {},
            {},
            1,
            std::vector<::defs::internal::stored_data::PlaceOrdersCount>{
                ::defs::internal::stored_data::PlaceOrdersCount{1, 2},
                ::defs::internal::stored_data::PlaceOrdersCount{2, 3}},
            {},
            {}},
        ::defs::internal::stored_data::StoredPromoRequirement{
            0.1,
            {},
            {},
            {},
            {},
            {},
            0,
            std::vector<::defs::internal::stored_data::PlaceOrdersCount>{
                ::defs::internal::stored_data::PlaceOrdersCount{3, 4}},
            {},
            {}}};

formats::json::ValueBuilder MakeStorageRequirements(
    const std::vector<::defs::internal::stored_data::StoredPromoRequirement>&
        res) {
  formats::json::ValueBuilder kStorageRequirements;
  kStorageRequirements["requirements"] = res;
  return kStorageRequirements;
}

const std::vector<::defs::internal::discount_data::PlaceOrdersCount>
    kOldRequestPlaceOrdersCount = {
        ::defs::internal::discount_data::PlaceOrdersCount{2, 3},
        ::defs::internal::discount_data::PlaceOrdersCount{3, 4},
};

}  // namespace

struct PlaceOrdersCountData {
  handlers::PromoRequest data;

  handlers::Promo response;
  handlers::Promo expected_response;
  types::StoredDataRaw stored_data;
  types::StoredDataRaw expected_stored_data;
  types::DiscountDataRaw discount_data;
  types::DiscountDataRaw expected_discount_data;
};

class PlaceOrdersCountDataFull
    : public ::testing::TestWithParam<PlaceOrdersCountData> {};

const std::vector<PlaceOrdersCountData> kPlaceOrdersCountData{
    {handlers::PromoRequest(), handlers::Promo(), handlers::Promo(),
     types::StoredDataRaw(), types::StoredDataRaw(), types::DiscountDataRaw(),
     types::DiscountDataRaw()},
    {handlers::PromoRequest(),
     handlers::Promo{
         1, {}, "name", {}, {}, {}, {}, {}, {}, kOldResponseRequirement, {}},
     handlers::Promo{
         1, {}, "name", {}, {}, {}, {}, {}, {}, kOldResponseRequirement, {}},
     types::StoredDataRaw{{1, 2},
                          {},
                          {},
                          MakeStorageRequirements(kOldStoredRequirement),
                          {},
                          {}},
     types::StoredDataRaw{{1, 2},
                          {},
                          {},
                          MakeStorageRequirements(kOldStoredRequirement),
                          {},
                          {}},
     types::DiscountDataRaw{{},
                            {1, 2},
                            {},
                            {},
                            {},
                            1,
                            {},
                            {},
                            {},
                            {},
                            {},
                            kOldRequestPlaceOrdersCount,
                            {},
                            {},
                            {},
                            {}},
     types::DiscountDataRaw{{},
                            {1, 2},
                            {},
                            {},
                            {},
                            1,
                            {},
                            {},
                            {},
                            {},
                            {},
                            kOldRequestPlaceOrdersCount,
                            {},
                            {},
                            {},
                            {}}}};

INSTANTIATE_TEST_SUITE_P(PlaceOrdersCountData, PlaceOrdersCountDataFull,
                         ::testing::ValuesIn(kPlaceOrdersCountData));

TEST_P(PlaceOrdersCountDataFull, check_place_order_price_feature) {
  auto param = GetParam();
  models::PromoSettings settings;
  auto place_orders_count =
      PlaceOrdersCount(Validator(), settings, {}, param.data);

  place_orders_count.UpdateResponse(param.response);
  ASSERT_EQ(param.response, param.expected_response);

  place_orders_count.UpdateStoredData(param.stored_data);
  ASSERT_EQ(param.stored_data, param.expected_stored_data);

  place_orders_count.UpdateDiscountData(param.discount_data);
  ASSERT_EQ(param.discount_data, param.expected_discount_data);
}

}  // namespace eats_restapp_promo::models::promo_features
