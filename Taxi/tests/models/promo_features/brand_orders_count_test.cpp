#include <userver/utest/utest.hpp>

#include <defs/api/promo.hpp>
#include <defs/definitions.hpp>
#include <defs/internal/stored_data.hpp>
#include <experiments3/eats_restapp_promo_settings.hpp>

#include <models/promo_features/brand_orders_count.hpp>
#include <types/discount_data.hpp>
#include <types/stored_data.hpp>

namespace eats_restapp_promo::models::promo_features {

namespace {

struct Validator {
  void ValidateBrandOrdersCount(const models::PromoSettings&,
                                const std::optional<std::vector<int>>&) const {
    return;
  }
};

const std::vector<handlers::PromoRequirement> kOldResponseRequirement = {
    handlers::PromoRequirement{1.1, {}, {}, {}, std::vector<int>{2, 3}, {}, {}},
    handlers::PromoRequirement{0.1, {}, {}, {}, std::vector<int>{4}, {}, {}}};

const std::vector<handlers::PromoRequirement> kNewResponseRequirement = {
    handlers::PromoRequirement{{}, {}, {}, {}, std::vector<int>{5, 8}, {}, {}}};

const std::vector<handlers::PromoRequirement> kMergeredResponseRequirement{
    kOldResponseRequirement[0], kOldResponseRequirement[1],
    kNewResponseRequirement[0]};

const std::vector<handlers::PromoRequirement>
    kNewResponseRequirementWithDefaultValue = {handlers::PromoRequirement{
        {}, {}, {}, {}, std::vector<int>{1}, {}, {}}};

const std::vector<handlers::PromoRequirement>
    kMergeredResponseRequirementWithDefaultValue{
        kOldResponseRequirement[0], kOldResponseRequirement[1],
        kNewResponseRequirementWithDefaultValue[0]};

const std::vector<::defs::internal::stored_data::StoredPromoRequirement>
    kOldStoredRequirement = {
        ::defs::internal::stored_data::StoredPromoRequirement{
            1.1,
            {},
            {},
            {},
            std::vector<::defs::internal::stored_data::BrandOrdersCount>{
                ::defs::internal::stored_data::BrandOrdersCount{1, 2},
                ::defs::internal::stored_data::BrandOrdersCount{2, 3}},
            {},
            1,
            {},
            {},
            {}},
        ::defs::internal::stored_data::StoredPromoRequirement{
            0.1,
            {},
            {},
            {},
            std::vector<::defs::internal::stored_data::BrandOrdersCount>{
                ::defs::internal::stored_data::BrandOrdersCount{3, 4}},
            {},
            0,
            {},
            {},
            {}}};

const std::vector<::defs::internal::stored_data::StoredPromoRequirement>
    kNewStoredRequirement = {
        ::defs::internal::stored_data::StoredPromoRequirement{
            {},
            {},
            {},
            {},
            std::vector<::defs::internal::stored_data::BrandOrdersCount>{
                ::defs::internal::stored_data::BrandOrdersCount{4, 5},
                ::defs::internal::stored_data::BrandOrdersCount{7, 8}},
            {},
            {},
            {},
            {},
            {}}};

const std::vector<::defs::internal::stored_data::StoredPromoRequirement>
    kMergeredStoredRequirement = {kOldStoredRequirement[0],
                                  kOldStoredRequirement[1],
                                  kNewStoredRequirement[0]};

const std::vector<::defs::internal::stored_data::StoredPromoRequirement>
    kNewStoredRequirementWithDefaultValue = {
        ::defs::internal::stored_data::StoredPromoRequirement{
            {},
            {},
            {},
            {},
            std::vector<::defs::internal::stored_data::BrandOrdersCount>{
                ::defs::internal::stored_data::BrandOrdersCount{0, 1}},
            {},
            {},
            {},
            {},
            {}}};

const std::vector<::defs::internal::stored_data::StoredPromoRequirement>
    kMergeredStoredRequirementWithDefaultValue = {
        kOldStoredRequirement[0], kOldStoredRequirement[1],
        kNewStoredRequirementWithDefaultValue[0]};

formats::json::ValueBuilder MakeStorageRequirements(
    const std::vector<::defs::internal::stored_data::StoredPromoRequirement>&
        res) {
  formats::json::ValueBuilder kStorageRequirements;
  kStorageRequirements["requirements"] = res;
  return kStorageRequirements;
}

const std::vector<::defs::internal::discount_data::BrandOrdersCount>
    kOldRequestBrandOrdersCount = {
        ::defs::internal::discount_data::BrandOrdersCount{2, 3},
        ::defs::internal::discount_data::BrandOrdersCount{3, 4},
};

const std::vector<::defs::internal::discount_data::BrandOrdersCount>
    kNewRequestBrandOrdersCount = {
        ::defs::internal::discount_data::BrandOrdersCount{4, 5},
        ::defs::internal::discount_data::BrandOrdersCount{7, 8}};

const std::vector<::defs::internal::discount_data::BrandOrdersCount>
    kMergeredRequestBrandOrdersCount = {
        kOldRequestBrandOrdersCount[0], kOldRequestBrandOrdersCount[1],
        kNewRequestBrandOrdersCount[0], kNewRequestBrandOrdersCount[1]};

const std::vector<::defs::internal::discount_data::BrandOrdersCount>
    kNewRequestBrandOrdersCountWithDefaultValue = {
        ::defs::internal::discount_data::BrandOrdersCount{0, 1}};

const std::vector<::defs::internal::discount_data::BrandOrdersCount>
    kMergeredRequestBrandOrdersCountWithDefaultValue = {
        kOldRequestBrandOrdersCount[0], kOldRequestBrandOrdersCount[1],
        kNewRequestBrandOrdersCountWithDefaultValue[0]};

}  // namespace

struct BrandOrdersCountData {
  handlers::PromoRequest data;

  handlers::Promo response;
  handlers::Promo expected_response;
  types::StoredDataRaw stored_data;
  types::StoredDataRaw expected_stored_data;
  types::DiscountDataRaw discount_data;
  types::DiscountDataRaw expected_discount_data;
};

class BrandOrdersCountDataFull
    : public ::testing::TestWithParam<BrandOrdersCountData> {};

const std::vector<BrandOrdersCountData> kBrandOrdersCountData{
    {handlers::PromoRequest(), handlers::Promo(), handlers::Promo(),
     types::StoredDataRaw(), types::StoredDataRaw(), types::DiscountDataRaw(),
     types::DiscountDataRaw()},
    {handlers::PromoRequest{
         {}, {}, {}, {}, {}, {}, {}, {}, std::vector<int>{5, 8}},
     handlers::Promo(),
     handlers::Promo{
         {}, {}, {}, {}, {}, {}, {}, {}, {}, kNewResponseRequirement, {}},
     types::StoredDataRaw(),
     types::StoredDataRaw{
         {}, {}, {}, MakeStorageRequirements(kNewStoredRequirement), {}, {}},
     types::DiscountDataRaw(),
     types::DiscountDataRaw{{},
                            {},
                            {},
                            kNewRequestBrandOrdersCount,
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
                            {}}},
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
                            kOldRequestBrandOrdersCount,
                            {},
                            1,
                            {},
                            {},
                            {},
                            {},
                            {},
                            {},
                            {},
                            {},
                            {},
                            {}},
     types::DiscountDataRaw{{},
                            {1, 2},
                            {},
                            kOldRequestBrandOrdersCount,
                            {},
                            1,
                            {},
                            {},
                            {},
                            {},
                            {},
                            {},
                            {},
                            {},
                            {},
                            {}}},
    {handlers::PromoRequest{
         {}, {}, {}, {}, {}, {}, {}, {}, std::vector<int>{5, 8}},
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
                            kOldRequestBrandOrdersCount,
                            {},
                            1,
                            {},
                            {},
                            {},
                            {},
                            {},
                            {},
                            {},
                            {},
                            {},
                            {}},
     types::DiscountDataRaw{{},
                            {1, 2},
                            {},
                            kMergeredRequestBrandOrdersCount,
                            {},
                            1,
                            {},
                            {},
                            {},
                            {},
                            {},
                            {},
                            {},
                            {},
                            {},
                            {}}}};

INSTANTIATE_TEST_SUITE_P(BrandOrdersCountData, BrandOrdersCountDataFull,
                         ::testing::ValuesIn(kBrandOrdersCountData));

TEST_P(BrandOrdersCountDataFull, check_brand_order_price_feature) {
  auto param = GetParam();
  models::PromoSettings settings;
  auto brand_orders_count =
      BrandOrdersCount(Validator(), settings, {}, param.data);

  brand_orders_count.UpdateResponse(param.response);
  ASSERT_EQ(param.response, param.expected_response);

  brand_orders_count.UpdateStoredData(param.stored_data);
  ASSERT_EQ(param.stored_data, param.expected_stored_data);

  brand_orders_count.UpdateDiscountData(param.discount_data);
  ASSERT_EQ(param.discount_data, param.expected_discount_data);
}

}  // namespace eats_restapp_promo::models::promo_features
