#include <userver/utest/utest.hpp>

#include <defs/api/promo.hpp>
#include <defs/definitions.hpp>
#include <experiments3/eats_restapp_promo_settings.hpp>

#include <models/promo_features/item_ids.hpp>
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
    types::ItemsMap result_items = {{"10", types::MenuItem{0, "100", "100"}},
                                    {"11", types::MenuItem{1, "110", "110"}},
                                    {"12", types::MenuItem{2, "120", "120"}}};
    items = result_items;
  }
};

const std::vector<handlers::PromoRequirement> kOldResponseRequirements = {
    handlers::PromoRequirement{{},
                               std::vector<int64_t>{1, 2},
                               types::ItemIds{"1", "2"},
                               {},
                               {},
                               {},
                               {}},
    handlers::PromoRequirement{
        {}, std::vector<int64_t>{6}, types::ItemIds{"5"}, {}, {}, {}, {}}};

const std::vector<handlers::PromoRequirement> kNewResponseRequirements = {
    handlers::PromoRequirement{
        {}, {}, types::ItemIds{"10", "11", "12"}, {}, {}, {}, {}}};

const std::vector<handlers::PromoRequirement> kMergeredResponseRequirements = {
    kOldResponseRequirements[0], kOldResponseRequirements[1],
    kNewResponseRequirements[0]};

formats::json::ValueBuilder MakeStorageRequirements(
    const std::vector<handlers::PromoRequirement>& res) {
  formats::json::ValueBuilder kStorageRequirements;
  kStorageRequirements["requirements"] = res;
  return kStorageRequirements;
}

const std::unordered_map<std::string, std::string> kInitTranslationArgs = {
    {"for_full_menu", "for_full_menu"}, {"for_item_ids", "for_item_ids"}};
const std::unordered_map<std::string, std::string> kFullMenuTranslationArgs = {
    {"for_full_menu", "for_full_menu"}, {"for_item_ids", ""}};
const std::unordered_map<std::string, std::string> kItemsTranslationArgs = {
    {"for_full_menu", ""}, {"for_item_ids", "for_item_ids"}};

}  // namespace

struct ItemIdsData {
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

class ItemIdsDataFull : public ::testing::TestWithParam<ItemIdsData> {};

const std::vector<ItemIdsData> kItemIdsData{
    {handlers::PromoRequest(), handlers::Promo(), handlers::Promo(),
     types::StoredDataRaw(), types::StoredDataRaw(), types::DiscountDataRaw(),
     types::DiscountDataRaw(), kInitTranslationArgs, kFullMenuTranslationArgs},
    {handlers::PromoRequest(),
     handlers::Promo{
         1, {}, "name", {}, {}, {}, {}, {}, {}, kOldResponseRequirements, {}},
     handlers::Promo{
         1, {}, "name", {}, {}, {}, {}, {}, {}, kOldResponseRequirements, {}},
     types::StoredDataRaw{{1, 2},
                          {},
                          {},
                          MakeStorageRequirements(kOldResponseRequirements),
                          {},
                          {}},
     types::StoredDataRaw{{1, 2},
                          {},
                          {},
                          MakeStorageRequirements(kOldResponseRequirements),
                          {},
                          {}},
     types::DiscountDataRaw{
         {}, {1, 2}, {}, {}, {}, 1, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}},
     types::DiscountDataRaw{
         {}, {1, 2}, {}, {}, {}, 1, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}},
     kInitTranslationArgs, kFullMenuTranslationArgs},
    {handlers::PromoRequest{{},
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
                            {},
                            {},
                            std::vector<std::string>{"10", "11", "12"}},
     handlers::Promo(),
     handlers::Promo{
         {}, {}, {}, {}, {}, {}, {}, {}, {}, kNewResponseRequirements, {}},
     types::StoredDataRaw(),
     types::StoredDataRaw{
         {}, {}, {}, MakeStorageRequirements(kNewResponseRequirements), {}, {}},
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
                            types::ItemIds{"0", "1", "2"},
                            {},
                            {},
                            {},
                            {},
                            {},
                            {}},
     kInitTranslationArgs, kItemsTranslationArgs},
    {handlers::PromoRequest{{},
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
                            {},
                            {},
                            std::vector<std::string>{"10", "11", "12"}},
     handlers::Promo{
         1, {}, "name", {}, {}, {}, {}, {}, {}, kOldResponseRequirements, {}},
     handlers::Promo{1,
                     {},
                     "name",
                     {},
                     {},
                     {},
                     {},
                     {},
                     {},
                     kMergeredResponseRequirements,
                     {}},
     types::StoredDataRaw{{1, 2},
                          {},
                          {},
                          MakeStorageRequirements(kOldResponseRequirements),
                          {},
                          {}},
     types::StoredDataRaw{
         {1, 2},
         {},
         {},
         MakeStorageRequirements(kMergeredResponseRequirements),
         {},
         {}},
     types::DiscountDataRaw{
         {}, {1, 2}, {}, {}, {}, 1, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}},
     types::DiscountDataRaw{{},
                            {1, 2},
                            {},
                            {},
                            {},
                            1,
                            {},
                            {},
                            {},
                            types::ItemIds{"0", "1", "2"},
                            {},
                            {},
                            {},
                            {},
                            {},
                            {}},
     kInitTranslationArgs, kItemsTranslationArgs}};

INSTANTIATE_TEST_SUITE_P(ItemIdsData, ItemIdsDataFull,
                         ::testing::ValuesIn(kItemIdsData));

TEST_P(ItemIdsDataFull, check_itm_ids_feature) {
  auto param = GetParam();
  models::PromoSettings settings;
  auto item_ids = ItemIds(Validator(), settings, {}, param.data);

  item_ids.UpdateResponse(param.response);
  ASSERT_EQ(param.response, param.expected_response);

  item_ids.UpdateStoredData(param.stored_data);
  ASSERT_EQ(param.stored_data, param.expected_stored_data);

  item_ids.UpdateDiscountData(param.discount_data);
  ASSERT_EQ(param.discount_data, param.expected_discount_data);

  item_ids.UpdateTranslationArgs(param.tr_args);
  ASSERT_EQ(param.tr_args, param.expected_tr_args);
}

}  // namespace eats_restapp_promo::models::promo_features
