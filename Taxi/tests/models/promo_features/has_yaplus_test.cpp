#include <userver/utest/utest.hpp>

#include <defs/api/promo.hpp>
#include <defs/definitions.hpp>
#include <defs/internal/stored_data.hpp>
#include <experiments3/eats_restapp_promo_settings.hpp>

#include <models/promo_features/has_yaplus.hpp>
#include <types/discount_data.hpp>
#include <types/stored_data.hpp>

namespace eats_restapp_promo::models::promo_features {

namespace {

struct Validator {};

const std::vector<handlers::PromoRequirement> kResponseRequirements = {
    handlers::PromoRequirement{1.1, {}, {}, {}, std::vector<int>{2, 3}, {}, {}},
    handlers::PromoRequirement{0.1, {}, {}, {}, std::vector<int>{4}, {}, {}}};

const std::vector<::defs::internal::stored_data::StoredPromoRequirement>
    kOldStoredRequirement = {
        ::defs::internal::stored_data::StoredPromoRequirement{
            1.1, {}, {}, {}, {}, {}, 1, {}, {}, {}},
        ::defs::internal::stored_data::StoredPromoRequirement{
            0.1, {}, {}, {}, {}, {}, 0, {}, {}, {}}};

const std::vector<::defs::internal::stored_data::StoredPromoRequirement>
    kNewStoredRequirement = {
        ::defs::internal::stored_data::StoredPromoRequirement{
            {}, {}, {}, {}, {}, {}, 1, {}, {}, {}}};

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

}  // namespace

struct HasYaplusData {
  handlers::PromoRequest data;

  handlers::Promo response;
  handlers::Promo expected_response;
  types::StoredDataRaw stored_data;
  types::StoredDataRaw expected_stored_data;
  types::DiscountDataRaw discount_data;
  types::DiscountDataRaw expected_discount_data;
};

class HasYaplusDataFull : public ::testing::TestWithParam<HasYaplusData> {};

const std::vector<HasYaplusData> kHasYaplusData{
    {handlers::PromoRequest{handlers::TypeOfPromo::kPlusFirstOrders},
     handlers::Promo(), handlers::Promo(), types::StoredDataRaw(),
     types::StoredDataRaw{
         {}, {}, {}, MakeStorageRequirements(kNewStoredRequirement), {}, {}},
     types::DiscountDataRaw(),
     types::DiscountDataRaw{
         {}, {}, {}, {}, {}, 1, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}}},
    {handlers::PromoRequest{handlers::TypeOfPromo::kPlusFirstOrders},
     handlers::Promo{
         1, {}, "name", {}, {}, {}, {}, {}, {}, kResponseRequirements, {}},
     handlers::Promo{
         1, {}, "name", {}, {}, {}, {}, {}, {}, kResponseRequirements, {}},
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
     types::DiscountDataRaw{
         {}, {1, 2}, {}, {}, {}, 0, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}},
     types::DiscountDataRaw{
         {}, {1, 2}, {}, {}, {}, 1, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}}},
    {handlers::PromoRequest{handlers::TypeOfPromo::kPlusHappyHours},
     handlers::Promo(), handlers::Promo(), types::StoredDataRaw(),
     types::StoredDataRaw{
         {}, {}, {}, MakeStorageRequirements(kNewStoredRequirement), {}, {}},
     types::DiscountDataRaw(),
     types::DiscountDataRaw{
         {}, {}, {}, {}, {}, 1, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}}},
    {handlers::PromoRequest{handlers::TypeOfPromo::kPlusHappyHours},
     handlers::Promo{
         1, {}, "name", {}, {}, {}, {}, {}, {}, kResponseRequirements, {}},
     handlers::Promo{
         1, {}, "name", {}, {}, {}, {}, {}, {}, kResponseRequirements, {}},
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
     types::DiscountDataRaw{
         {}, {1, 2}, {}, {}, {}, 0, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}},
     types::DiscountDataRaw{
         {}, {1, 2}, {}, {}, {}, 1, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}}},
    {handlers::PromoRequest{handlers::TypeOfPromo::kGift}, handlers::Promo(),
     handlers::Promo(), types::StoredDataRaw(), types::StoredDataRaw(),
     types::DiscountDataRaw(), types::DiscountDataRaw()},
    {handlers::PromoRequest{handlers::TypeOfPromo::kGift},
     handlers::Promo{
         1, {}, "name", {}, {}, {}, {}, {}, {}, kResponseRequirements, {}},
     handlers::Promo{
         1, {}, "name", {}, {}, {}, {}, {}, {}, kResponseRequirements, {}},
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
     types::DiscountDataRaw{
         {}, {1, 2}, {}, {}, {}, 0, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}},
     types::DiscountDataRaw{
         {}, {1, 2}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}}}};

INSTANTIATE_TEST_SUITE_P(HasYaplusData, HasYaplusDataFull,
                         ::testing::ValuesIn(kHasYaplusData));

TEST_P(HasYaplusDataFull, check_has_yaplus_feature) {
  auto param = GetParam();
  models::PromoSettings settings;
  auto has_yaplus = HasYaplus(Validator(), settings, {}, param.data);

  has_yaplus.UpdateResponse(param.response);
  ASSERT_EQ(param.response, param.expected_response);

  has_yaplus.UpdateStoredData(param.stored_data);
  ASSERT_EQ(param.stored_data, param.expected_stored_data);

  has_yaplus.UpdateDiscountData(param.discount_data);
  ASSERT_EQ(param.discount_data, param.expected_discount_data);
}

}  // namespace eats_restapp_promo::models::promo_features
