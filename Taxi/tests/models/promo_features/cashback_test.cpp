#include <userver/utest/utest.hpp>

#include <defs/api/promo.hpp>
#include <defs/definitions.hpp>
#include <defs/internal/stored_data.hpp>
#include <experiments3/eats_restapp_promo_settings.hpp>

#include <models/promo_features/cashback.hpp>
#include <types/discount_data.hpp>
#include <types/stored_data.hpp>

namespace eats_restapp_promo::models::promo_features {

namespace {

struct Validator {
  void ValidateCashback(const std::optional<std::vector<double>>&,
                        const std::vector<int64_t>&,
                        std::chrono::system_clock::time_point,
                        std::chrono::system_clock::time_point) const {
    return;
  }
};

const std::vector<handlers::PromoBonus> kOldResponseBonuses = {
    handlers::PromoBonus{"1", 5, std::vector<double>{1, 2}},
    handlers::PromoBonus{"3", {}, std::vector<double>{1}}};

const std::vector<handlers::PromoBonus> kNewResponseBonuses = {
    handlers::PromoBonus{{}, {}, std::vector<double>{10, 11}}};

const std::vector<handlers::PromoBonus> kMergeredResponseBonuses = {
    kOldResponseBonuses[0], kOldResponseBonuses[1], kNewResponseBonuses[0]};

const std::vector<::defs::internal::stored_data::StoredPromoBonus>
    kOldStoredBonuses = {::defs::internal::stored_data::StoredPromoBonus{
                             "1", 5, std::vector<double>{1, 2}, {}, {}, {}},
                         ::defs::internal::stored_data::StoredPromoBonus{
                             "3", {}, std::vector<double>{1}, {}, {}, {}}};

const std::vector<::defs::internal::stored_data::StoredPromoBonus>
    kNewStoredBonuses = {::defs::internal::stored_data::StoredPromoBonus{
        {}, {}, std::vector<double>{10, 11}, {}, {}, {}}};

const std::vector<::defs::internal::stored_data::StoredPromoBonus>
    kMergeredStoredBonuses = {kOldStoredBonuses[0], kOldStoredBonuses[1],
                              kNewStoredBonuses[0]};

formats::json::ValueBuilder MakeStorageBonuses(
    const std::vector<::defs::internal::stored_data::StoredPromoBonus>& res) {
  formats::json::ValueBuilder kStorageBonuses;
  kStorageBonuses["bonuses"] = res;
  return kStorageBonuses;
}

const std::vector<double> kRequestCashback = {3, 4};

}  // namespace

struct CashbackData {
  handlers::PromoRequest data;

  handlers::Promo response;
  handlers::Promo expected_response;
  types::StoredDataRaw stored_data;
  types::StoredDataRaw expected_stored_data;
  types::DiscountDataRaw discount_data;
  types::DiscountDataRaw expected_discount_data;
};

class CashbackDataFull : public ::testing::TestWithParam<CashbackData> {};

const std::vector<CashbackData> kCashbackData{
    {handlers::PromoRequest(), handlers::Promo(), handlers::Promo(),
     types::StoredDataRaw(), types::StoredDataRaw(), types::DiscountDataRaw(),
     types::DiscountDataRaw()},
    {handlers::PromoRequest{{}, {}, {}, {}, std::vector<double>{10, 11}, {}},
     handlers::Promo{{}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}},
     handlers::Promo{
         {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, kNewResponseBonuses},
     types::StoredDataRaw{{}, {}, {}, {}, {}, {}},
     types::StoredDataRaw{
         {}, {}, {}, {}, MakeStorageBonuses(kNewStoredBonuses), {}},
     types::DiscountDataRaw(),
     types::DiscountDataRaw{{},
                            {},
                            std::vector<double>{10, 11},
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
                            {},
                            {}}},
    {handlers::PromoRequest(),
     handlers::Promo{
         1, {}, "name", {}, {}, {}, {}, {}, {}, {}, kOldResponseBonuses},
     handlers::Promo{
         1, {}, "name", {}, {}, {}, {}, {}, {}, {}, kOldResponseBonuses},
     types::StoredDataRaw{
         {1, 2}, {}, {}, {}, MakeStorageBonuses(kOldStoredBonuses), {}},
     types::StoredDataRaw{
         {1, 2}, {}, {}, {}, MakeStorageBonuses(kOldStoredBonuses), {}},
     types::DiscountDataRaw{{},
                            {1, 2},
                            kRequestCashback,
                            {},
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
     types::DiscountDataRaw{
         {}, {1, 2}, {}, {}, {}, 1, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}}},
    {handlers::PromoRequest{{}, {}, {}, {}, std::vector<double>{10, 11}},
     handlers::Promo{
         1, {}, "name", {}, {}, {}, {}, {}, {}, {}, kOldResponseBonuses},
     handlers::Promo{
         1, {}, "name", {}, {}, {}, {}, {}, {}, {}, kMergeredResponseBonuses},
     types::StoredDataRaw{
         {1, 2}, {}, {}, {}, MakeStorageBonuses(kOldStoredBonuses), {}},
     types::StoredDataRaw{
         {1, 2}, {}, {}, {}, MakeStorageBonuses(kMergeredStoredBonuses), {}},
     types::DiscountDataRaw{{},
                            {1, 2},
                            kRequestCashback,
                            {},
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
                            std::vector<double>{10, 11},
                            {},
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

INSTANTIATE_TEST_SUITE_P(CashbackData, CashbackDataFull,
                         ::testing::ValuesIn(kCashbackData));

TEST_P(CashbackDataFull, check_casback_feature) {
  auto param = GetParam();
  models::PromoSettings settings;
  auto cashback = Cashback(Validator(), settings, {}, param.data);

  cashback.UpdateResponse(param.response);
  ASSERT_EQ(param.response, param.expected_response);

  cashback.UpdateStoredData(param.stored_data);
  ASSERT_EQ(param.stored_data, param.expected_stored_data);

  cashback.UpdateDiscountData(param.discount_data);
  ASSERT_EQ(param.discount_data, param.expected_discount_data);
}

}  // namespace eats_restapp_promo::models::promo_features
