#include <userver/utest/utest.hpp>

#include <defs/api/promo.hpp>
#include <defs/definitions.hpp>
#include <defs/internal/stored_data.hpp>
#include <experiments3/eats_restapp_promo_settings.hpp>

#include <models/promo_features/item_id.hpp>
#include <types/discount_data.hpp>
#include <types/stored_data.hpp>

namespace eats_restapp_promo::models::promo_features {

namespace {

struct Validator {
  void ValidateItemIds(const models::PromoSettings&, const types::RequestInfo&,
                       std::optional<types::ItemIds>& origin_item_ids,
                       std::optional<types::ItemsMap>& items) const {
    if (!origin_item_ids.has_value()) {
      return;
    }
    types::ItemsMap result_items = {
        {"6", types::MenuItem{60, "66", "66"}},
    };
    items = result_items;
  }
};

const std::vector<handlers::PromoBonus> kOldResponseBonuses = {
    handlers::PromoBonus{"1", 5, std::vector<double>{1, 2}},
    handlers::PromoBonus{"3", {}, std::vector<double>{1}}};

const std::vector<handlers::PromoBonus> kNewResponseBonuses = {
    handlers::PromoBonus{"6", {}, {}}};

const std::vector<handlers::PromoBonus> kMergeredResponseBonuses = {
    kOldResponseBonuses[0], kOldResponseBonuses[1], kNewResponseBonuses[0]};

const std::vector<::defs::internal::stored_data::StoredPromoBonus>
    kOldStoredBonuses = {::defs::internal::stored_data::StoredPromoBonus{
                             "1", 5, std::vector<double>{1, 2}, {}, {}, {}},
                         ::defs::internal::stored_data::StoredPromoBonus{
                             "3", {}, std::vector<double>{1}, {}, {}, {}}};

const std::vector<::defs::internal::stored_data::StoredPromoBonus>
    kNewStoredBonuses = {::defs::internal::stored_data::StoredPromoBonus{
        "6", {}, {}, {}, {}, {}}};

const std::vector<::defs::internal::stored_data::StoredPromoBonus>
    kMergeredStoredBonuses = {kOldStoredBonuses[0], kOldStoredBonuses[1],
                              kNewStoredBonuses[0]};

formats::json::ValueBuilder MakeStorageBonuses(
    const std::vector<::defs::internal::stored_data::StoredPromoBonus>& res) {
  formats::json::ValueBuilder kStorageBonuses;
  kStorageBonuses["bonuses"] = res;
  return kStorageBonuses;
}

}  // namespace

struct ItemIdData {
  handlers::PromoRequest data;

  handlers::Promo response;
  handlers::Promo expected_response;
  types::StoredDataRaw stored_data;
  types::StoredDataRaw expected_stored_data;
  types::DiscountDataRaw discount_data;
  types::DiscountDataRaw expected_discount_data;
  std::unordered_map<std::string, std::string> tr_args;
  std::unordered_map<std::string, std::string> expected_tr_args;
};

class ItemIdDataFull : public ::testing::TestWithParam<ItemIdData> {};

const std::vector<ItemIdData> kItemIdData{
    {handlers::PromoRequest(),
     handlers::Promo(),
     handlers::Promo(),
     types::StoredDataRaw(),
     types::StoredDataRaw(),
     types::DiscountDataRaw(),
     types::DiscountDataRaw(),
     {},
     {}},
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
         {}, {1, 2}, {}, {}, {}, 1, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}},
     {},
     {}},
    {handlers::PromoRequest{{}, {}, {}, {}, {}, {}, {}, {}, {}, {}, "6"},
     handlers::Promo(),
     handlers::Promo{
         {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, kNewResponseBonuses},
     types::StoredDataRaw(),
     types::StoredDataRaw{
         {}, {}, {}, {}, MakeStorageBonuses(kNewStoredBonuses), {}},
     types::DiscountDataRaw(),
     types::DiscountDataRaw{
         {}, {}, {}, {}, {}, {}, {}, {}, "60", {}, {}, {}, {}, {}, {}, {}},
     {},
     {{"item_name", "66"}}},
    {handlers::PromoRequest{{}, {}, {}, {}, {}, {}, {}, {}, {}, {}, "6"},
     handlers::Promo{
         1, {}, "name", {}, {}, {}, {}, {}, {}, {}, kOldResponseBonuses},
     handlers::Promo{
         1, {}, "name", {}, {}, {}, {}, {}, {}, {}, kMergeredResponseBonuses},
     types::StoredDataRaw{
         {1, 2}, {}, {}, {}, MakeStorageBonuses(kOldStoredBonuses), {}},
     types::StoredDataRaw{
         {1, 2}, {}, {}, {}, MakeStorageBonuses(kMergeredStoredBonuses), {}},
     types::DiscountDataRaw{
         {}, {1, 2}, {}, {}, {}, 1, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}},
     types::DiscountDataRaw{
         {}, {1, 2}, {}, {}, {}, 1, {}, {}, "60", {}, {}, {}, {}, {}, {}, {}},
     {},
     {{"item_name", "66"}}}};

INSTANTIATE_TEST_SUITE_P(ItemIdData, ItemIdDataFull,
                         ::testing::ValuesIn(kItemIdData));

TEST_P(ItemIdDataFull, check_item_id_feature) {
  auto param = GetParam();
  models::PromoSettings settings;
  auto item_id = ItemId(Validator(), settings, {}, param.data);

  item_id.UpdateResponse(param.response);
  ASSERT_EQ(param.response, param.expected_response);

  item_id.UpdateStoredData(param.stored_data);
  ASSERT_EQ(param.stored_data, param.expected_stored_data);

  item_id.UpdateDiscountData(param.discount_data);
  ASSERT_EQ(param.discount_data, param.expected_discount_data);

  item_id.UpdateTranslationArgs(param.tr_args);
  ASSERT_EQ(param.tr_args, param.expected_tr_args);
}

}  // namespace eats_restapp_promo::models::promo_features
