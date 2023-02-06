#include <userver/utest/utest.hpp>

#include <defs/api/promo.hpp>
#include <defs/definitions.hpp>
#include <experiments3/eats_restapp_promo_settings.hpp>

#include <models/promo_features/min_order_price.hpp>
#include <types/discount_data.hpp>
#include <types/stored_data.hpp>

namespace eats_restapp_promo::models::promo_features {

namespace {

struct Validator {
  void ValidateMinOrderPrice(
      const models::PromoSettings&, const types::RequestInfo&,
      const std::optional<handlers::MinMaxOrderPrice>&) const {
    return;
  }
};

const std::vector<handlers::PromoRequirement> kOldResponseRequirements = {
    handlers::PromoRequirement{1.0,
                               std::vector<int64_t>{1, 2},
                               std::vector<std::string>{"1", "2"},
                               {},
                               {},
                               {},
                               {}},
    handlers::PromoRequirement{2.0,
                               std::vector<int64_t>{6},
                               std::vector<std::string>{"5"},
                               {},
                               {},
                               {},
                               {}}};

const std::vector<handlers::PromoRequirement> kNewResponseRequirements = {
    handlers::PromoRequirement{100.0, {}, {}, {}, {}, {}, {}}};

const std::vector<handlers::PromoRequirement> kMergeredResponseRequirements = {
    kOldResponseRequirements[0], kOldResponseRequirements[1],
    kNewResponseRequirements[0]};

formats::json::ValueBuilder MakeStorageRequirements(
    const std::vector<handlers::PromoRequirement>& res) {
  formats::json::ValueBuilder kStorageRequirements;
  kStorageRequirements["requirements"] = res;
  return kStorageRequirements;
}

const ::defs::internal::discount_data::OrderPrice kOldRequestOrderPrice = {
    "10", "1000000"};
const ::defs::internal::discount_data::OrderPrice kNewRequestOrderPrice = {
    "100", "1000000"};
const ::defs::internal::discount_data::OrderPrice kNewRequestOrderPriceWithMax =
    {"100", "200"};

using MinMaxOrderPrice =
    experiments3::eats_restapp_promo_settings::MinMaxOrderPriceConfiguration;
using PromoInfoSettings =
    experiments3::eats_restapp_promo_settings::PromoConfiguration;

}  // namespace

struct MinOrderPriceData {
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

class MinOrderPriceDataFull
    : public ::testing::TestWithParam<MinOrderPriceData> {};

const std::vector<MinOrderPriceData> kMinOrderPriceData{
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
     {},
     {}},
    {handlers::PromoRequest{{}, {}, {}, {}, {}, 100},
     handlers::Promo(),
     handlers::Promo{
         {}, {}, {}, {}, {}, {}, {}, {}, {}, kNewResponseRequirements, {}},
     types::StoredDataRaw(),
     types::StoredDataRaw{
         {}, {}, {}, MakeStorageRequirements(kNewResponseRequirements), {}, {}},
     types::DiscountDataRaw(),
     types::DiscountDataRaw{kNewRequestOrderPrice,
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
                            {}},
     {},
     {{"min_order_price", "100"}}},
    {handlers::PromoRequest{{}, {}, {}, {}, {}, 100},
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
     types::DiscountDataRaw{kOldRequestOrderPrice,
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
                            {},
                            {},
                            {}},
     types::DiscountDataRaw{kNewRequestOrderPrice,
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
                            {},
                            {},
                            {}},
     {},
     {{"min_order_price", "100"}}}};

INSTANTIATE_TEST_SUITE_P(MinOrderPriceData, MinOrderPriceDataFull,
                         ::testing::ValuesIn(kMinOrderPriceData));

TEST_P(MinOrderPriceDataFull, check_min_order_price_feature) {
  auto param = GetParam();
  models::PromoSettings settings;
  auto min_order_price = MinOrderPrice(Validator(), settings, {}, param.data);

  min_order_price.UpdateResponse(param.response);
  ASSERT_EQ(param.response, param.expected_response);

  min_order_price.UpdateStoredData(param.stored_data);
  ASSERT_EQ(param.stored_data, param.expected_stored_data);

  min_order_price.UpdateDiscountData(param.discount_data);
  ASSERT_EQ(param.discount_data, param.expected_discount_data);

  min_order_price.UpdateTranslationArgs(param.tr_args);
  ASSERT_EQ(param.tr_args, param.expected_tr_args);
}

struct MaxOrderPriceData {
  handlers::PromoRequest data;
  handlers::Promo response;
  handlers::Promo expected_response;
  types::StoredDataRaw stored_data;
  types::StoredDataRaw expected_stored_data;
  types::DiscountDataRaw discount_data;
  types::DiscountDataRaw expected_discount_data;
  experiments3::eats_restapp_promo_settings::PromoConfiguration settings;
};

class MaxOrderPriceDataFull
    : public ::testing::TestWithParam<MaxOrderPriceData> {};

const std::vector<MaxOrderPriceData> kMaxOrderPriceData{
    {handlers::PromoRequest{{}, {}, {}, {}, {}, 100},
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
     types::DiscountDataRaw{kOldRequestOrderPrice,
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
                            {},
                            {},
                            {}},
     types::DiscountDataRaw{kNewRequestOrderPriceWithMax,
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
                            {},
                            {},
                            {}},
     PromoInfoSettings(PromoConfiguration{{}, MinMaxOrderPrice{150, 200}})}};

INSTANTIATE_TEST_SUITE_P(MaxOrderPriceData, MaxOrderPriceDataFull,
                         ::testing::ValuesIn(kMaxOrderPriceData));

TEST_P(MaxOrderPriceDataFull, check_max_order_price_feature) {
  auto param = GetParam();
  models::PromoSettings settings;
  settings.info.configuration = param.settings;
  auto min_order_price = MinOrderPrice(Validator(), settings, {}, param.data);

  min_order_price.UpdateResponse(param.response);
  ASSERT_EQ(param.response, param.expected_response);
  min_order_price.UpdateStoredData(param.stored_data);
  ASSERT_EQ(param.stored_data, param.expected_stored_data);
  min_order_price.UpdateDiscountData(param.discount_data);
  ASSERT_EQ(param.discount_data, param.expected_discount_data);
}

}  // namespace eats_restapp_promo::models::promo_features
