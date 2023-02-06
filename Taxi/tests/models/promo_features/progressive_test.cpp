#include <userver/utest/utest.hpp>

#include <defs/api/promo.hpp>
#include <defs/definitions.hpp>
#include <defs/internal/stored_data.hpp>
#include <experiments3/eats_restapp_promo_settings.hpp>

#include <models/promo_features/progressive.hpp>
#include <types/discount_data.hpp>
#include <types/stored_data.hpp>

namespace eats_restapp_promo::models::promo_features {

namespace {

struct Validator {
  void ValidateProgressive(
      const models::PromoSettings&, const types::RequestInfo&,
      const std::optional<std::vector<handlers::Progressive>>& progressive,
      std::optional<types::ItemsMap>& items) const {
    if (!progressive.has_value()) {
      return;
    }
    types::ItemsMap result_items = {
        {"item1", types::MenuItem{1, "1", "1"}},
        {"item2", types::MenuItem{2, "2", "2"}},
        {"item10", types::MenuItem{10, "10", "10"}},
        {"item20", types::MenuItem{20, "20", "20"}},
        {"item100", types::MenuItem{100, "100", "100"}},
        {"item200", types::MenuItem{200, "200", "200"}}};
    items = result_items;
  }
};

const std::vector<handlers::Progressive> kOldProgressive = {
    handlers::Progressive{{50.0},
                          {std::vector<std::string>{"item1", "item2"}}}};

const std::vector<handlers::Progressive> kNewProgressive = {
    handlers::Progressive{{10.0},
                          {std::vector<std::string>{"item10", "item100"}}},
    handlers::Progressive{{20.0},
                          {std::vector<std::string>{"item20", "item200"}}}};

const std::vector<handlers::PromoBonus> kOldResponseBonuses = {
    handlers::PromoBonus{"1", 5, std::vector<double>{1, 2}, kOldProgressive}};

const std::vector<handlers::PromoBonus> kNewResponseBonuses = {
    handlers::PromoBonus{{}, {}, {}, kNewProgressive}};

const std::vector<handlers::PromoBonus> kMergeredResponseBonuses = {
    kOldResponseBonuses[0], kNewResponseBonuses[0]};

const std::vector<::defs::internal::stored_data::StoredPromoBonus>
    kOldStoredBonuses = {::defs::internal::stored_data::StoredPromoBonus{
        "1", 5, std::vector<double>{1, 2}, kOldProgressive, {}, {}}};

const std::vector<::defs::internal::stored_data::StoredPromoBonus>
    kNewStoredBonuses = {::defs::internal::stored_data::StoredPromoBonus{
        {}, {}, {}, kNewProgressive, {}, {}}};

const std::vector<::defs::internal::stored_data::StoredPromoBonus>
    kMergeredStoredBonuses = {kOldStoredBonuses[0], kNewStoredBonuses[0]};

formats::json::ValueBuilder MakeStorageBonuses(
    const std::vector<::defs::internal::stored_data::StoredPromoBonus>& res) {
  formats::json::ValueBuilder kStorageBonuses;
  kStorageBonuses["bonuses"] = res;
  return kStorageBonuses;
}

const std::vector<::defs::internal::discount_data::Progressive>
    kOldRequestProgressive = {::defs::internal::discount_data::Progressive{
        {"10", "100"}, {{{"1"}, {"2"}}}}};

const std::vector<::defs::internal::discount_data::Progressive>
    kNewRequestProgressive = {::defs::internal::discount_data::Progressive{
                                  {"10", "100"}, {{{"10"}, {"100"}}}},
                              ::defs::internal::discount_data::Progressive{
                                  {"20", "100"}, {{{"20"}, {"200"}}}}};

const std::vector<::defs::internal::discount_data::Progressive>
    kMergeredRequestProgressive = {kOldRequestProgressive[0],
                                   kNewRequestProgressive[0],
                                   kNewRequestProgressive[1]};

}  // namespace

struct ProgressiveData {
  handlers::PromoRequest data;

  handlers::Promo response;
  handlers::Promo expected_response;
  types::StoredDataRaw stored_data;
  types::StoredDataRaw expected_stored_data;
  types::DiscountDataRaw discount_data;
  types::DiscountDataRaw expected_discount_data;
};

class ProgressiveDataFull : public ::testing::TestWithParam<ProgressiveData> {};

const std::vector<ProgressiveData> kProgressiveData{
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
         {}, {1, 2}, {}, {}, {}, 1, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}}},
    {handlers::PromoRequest{
         {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, kNewProgressive},
     handlers::Promo(),
     handlers::Promo{
         {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, kNewResponseBonuses},
     types::StoredDataRaw(),
     types::StoredDataRaw{
         {}, {}, {}, {}, MakeStorageBonuses(kNewStoredBonuses), {}},
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
                            {},
                            kNewRequestProgressive,
                            {},
                            {}}},
    {handlers::PromoRequest{
         {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, kNewProgressive},
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
                            {},
                            kOldRequestProgressive,
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
                            {},
                            kMergeredRequestProgressive,
                            {},
                            {}}}};

INSTANTIATE_TEST_SUITE_P(ProgressiveData, ProgressiveDataFull,
                         ::testing::ValuesIn(kProgressiveData));

TEST_P(ProgressiveDataFull, check_progressive_feature) {
  auto param = GetParam();
  models::PromoSettings settings;
  auto progressive = Progressive(Validator(), settings, {}, param.data);

  progressive.UpdateResponse(param.response);
  ASSERT_EQ(param.response, param.expected_response);

  progressive.UpdateStoredData(param.stored_data);
  ASSERT_EQ(param.stored_data, param.expected_stored_data);

  progressive.UpdateDiscountData(param.discount_data);
  ASSERT_EQ(param.discount_data, param.expected_discount_data);
}

}  // namespace eats_restapp_promo::models::promo_features
