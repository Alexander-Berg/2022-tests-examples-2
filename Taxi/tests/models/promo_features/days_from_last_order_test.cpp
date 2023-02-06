#include <userver/utest/utest.hpp>

#include <defs/api/promo.hpp>
#include <defs/definitions.hpp>
#include <defs/internal/stored_data.hpp>
#include <experiments3/eats_restapp_promo_settings.hpp>

#include <models/promo_features/days_from_last_order.hpp>
#include <types/discount_data.hpp>
#include <types/stored_data.hpp>

namespace eats_restapp_promo::models::promo_features {

namespace {

struct Validator {
  void ValidateDaysFromLastOrder(const models::PromoSettings&,
                                 const std::optional<int>&) const {
    return;
  }
};

const std::vector<handlers::PromoRequirement> kOldResponseRequirement = {
    handlers::PromoRequirement{1.1, {}, {}, {}, std::vector<int>{2, 3}, 6, {}},
    handlers::PromoRequirement{0.1, {}, {}, {}, std::vector<int>{4}, 7, {}}};

const std::vector<handlers::PromoRequirement> kNewResponseRequirement = {
    handlers::PromoRequirement{{}, {}, {}, {}, {}, 5, {}}};

const std::vector<handlers::PromoRequirement> kMergeredResponseRequirement = {
    kOldResponseRequirement[0], kOldResponseRequirement[1],
    kNewResponseRequirement[0]};

const std::vector<::defs::internal::stored_data::StoredPromoRequirement>
    kOldStoredRequirement = {
        ::defs::internal::stored_data::StoredPromoRequirement{
            1.1, {}, {}, {}, {}, {}, 1, {}, 5, {}},
        ::defs::internal::stored_data::StoredPromoRequirement{
            0.1, {}, {}, {}, {}, {}, 0, {}, 4, {}}};

const std::vector<::defs::internal::stored_data::StoredPromoRequirement>
    kNewStoredRequirement = {
        ::defs::internal::stored_data::StoredPromoRequirement{
            {}, {}, {}, {}, {}, {}, {}, {}, 5, {}}};

const std::vector<::defs::internal::stored_data::StoredPromoRequirement>
    kMergeredStoredRequirement = {kOldStoredRequirement[0],
                                  kOldStoredRequirement[1],
                                  kNewStoredRequirement[0]};

formats::json::ValueBuilder MakeStorageRequirements(
    const std::vector<::defs::internal::stored_data::StoredPromoRequirement>&
        res) {
  formats::json::ValueBuilder kStorageRequirements;
  kStorageRequirements["requirements"] = res;
  return kStorageRequirements;
}

const ::defs::internal::discount_data::DaysFromLastOrder
    kOldRequestDaysFromLastOrder = {2, 3};

const ::defs::internal::discount_data::DaysFromLastOrder
    kNewRequestDaysFromLastOrder = {7200, 52560000};

}  // namespace

struct DaysFromLastOrderData {
  handlers::PromoRequest data;

  handlers::Promo response;
  handlers::Promo expected_response;
  types::StoredDataRaw stored_data;
  types::StoredDataRaw expected_stored_data;
  types::DiscountDataRaw discount_data;
  types::DiscountDataRaw expected_discount_data;
};

class DaysFromLastOrderDataFull
    : public ::testing::TestWithParam<DaysFromLastOrderData> {};

const std::vector<DaysFromLastOrderData> kDaysFromLastOrderData{
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
                            {},
                            kOldRequestDaysFromLastOrder,
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
                            {},
                            kOldRequestDaysFromLastOrder,
                            {},
                            {},
                            {}}},
    {handlers::PromoRequest{{}, {}, {}, {}, {}, {}, 5, {}},
     handlers::Promo{
         1, {}, "name", {}, {}, {}, {}, {}, {}, kOldResponseRequirement, {}},
     handlers::Promo{1,
                     {},
                     "name",
                     {},
                     {},
                     {},
                     {},
                     {},
                     {},
                     kMergeredResponseRequirement,
                     {}},
     types::StoredDataRaw{{1, 2},
                          {},
                          {},
                          MakeStorageRequirements(kOldStoredRequirement),
                          {},
                          {}},
     types::StoredDataRaw{{1, 2},
                          {},
                          {},
                          MakeStorageRequirements(kMergeredStoredRequirement),
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
                            {},
                            kOldRequestDaysFromLastOrder,
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
                            {},
                            kNewRequestDaysFromLastOrder,
                            {},
                            {},
                            {}}},
    {handlers::PromoRequest{{}, {}, {}, {}, {}, {}, 5, {}}, handlers::Promo(),
     handlers::Promo{
         {}, {}, {}, {}, {}, {}, {}, {}, {}, kNewResponseRequirement, {}},
     types::StoredDataRaw(),
     types::StoredDataRaw{
         {}, {}, {}, MakeStorageRequirements(kNewStoredRequirement), {}, {}},
     types::DiscountDataRaw(),
     types::DiscountDataRaw{{},
                            {},
                            {},
                            {},
                            {},
                            {},
                            {},
                            {},
                            {},
                            {},
                            {},
                            {},
                            kNewRequestDaysFromLastOrder,
                            {},
                            {},
                            {}}}};

INSTANTIATE_TEST_SUITE_P(DaysFromLastOrderData, DaysFromLastOrderDataFull,
                         ::testing::ValuesIn(kDaysFromLastOrderData));

TEST_P(DaysFromLastOrderDataFull, check_brand_order_price_feature) {
  auto param = GetParam();
  models::PromoSettings settings;
  auto days_from_last_order =
      DaysFromLastOrder(Validator(), settings, {}, param.data);

  days_from_last_order.UpdateResponse(param.response);
  ASSERT_EQ(param.response, param.expected_response);

  days_from_last_order.UpdateStoredData(param.stored_data);
  ASSERT_EQ(param.stored_data, param.expected_stored_data);

  days_from_last_order.UpdateDiscountData(param.discount_data);
  ASSERT_EQ(param.discount_data, param.expected_discount_data);
}

}  // namespace eats_restapp_promo::models::promo_features
