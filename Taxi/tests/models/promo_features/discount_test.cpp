#include <userver/utest/utest.hpp>

#include <defs/api/promo.hpp>
#include <defs/definitions.hpp>
#include <defs/internal/stored_data.hpp>
#include <experiments3/eats_restapp_promo_settings.hpp>

#include <models/promo_features/discount.hpp>
#include <types/discount_data.hpp>
#include <types/stored_data.hpp>

namespace eats_restapp_promo::models::promo_features {

namespace {

struct Validator {};

const std::vector<handlers::PromoBonus> kOldResponseBonuses = {
    handlers::PromoBonus{"1", 5, std::vector<double>{1, 2}, {}, {}},
    handlers::PromoBonus{"3", {}, std::vector<double>{1}, {}, {}}};

const std::vector<handlers::PromoBonus> kNewResponseBonuses = {
    handlers::PromoBonus{{}, 6, {}, {}, {}}};

const std::vector<handlers::PromoBonus> kMergeredResponseBonuses = {
    kOldResponseBonuses[0], kOldResponseBonuses[1], kNewResponseBonuses[0]};

const std::vector<handlers::PromoBonus> kNewResponseBonusesWithMaximumDiscount =
    {handlers::PromoBonus{{}, 6, {}, {}, 1000.0}};

const std::vector<handlers::PromoBonus>
    kMergeredResponseBonusesWithMaximumDiscount = {
        kOldResponseBonuses[0], kOldResponseBonuses[1],
        kNewResponseBonusesWithMaximumDiscount[0]};

const std::vector<::defs::internal::stored_data::StoredPromoBonus>
    kOldStoredBonuses = {::defs::internal::stored_data::StoredPromoBonus{
                             "1", 5, std::vector<double>{1, 2}, {}, {}, {}},
                         ::defs::internal::stored_data::StoredPromoBonus{
                             "3", {}, std::vector<double>{1}, {}, {}, {}}};

const std::vector<::defs::internal::stored_data::StoredPromoBonus>
    kNewStoredBonuses = {::defs::internal::stored_data::StoredPromoBonus{
        {}, 6, {}, {}, {}, "fraction"}};

const std::vector<::defs::internal::stored_data::StoredPromoBonus>
    kMergeredStoredBonuses = {kOldStoredBonuses[0], kOldStoredBonuses[1],
                              kNewStoredBonuses[0]};

const std::vector<::defs::internal::stored_data::StoredPromoBonus>
    kNewStoredBonusesWithMaximumDiscount = {
        ::defs::internal::stored_data::StoredPromoBonus{
            {}, 6, {}, {}, 1000.0, "fraction"}};

const std::vector<::defs::internal::stored_data::StoredPromoBonus>
    kMergeredStoredBonusesWithMaximumDiscount = {
        kOldStoredBonuses[0], kOldStoredBonuses[1],
        kNewStoredBonusesWithMaximumDiscount[0]};

formats::json::ValueBuilder MakeStorageBonuses(
    const std::vector<::defs::internal::stored_data::StoredPromoBonus>& res) {
  formats::json::ValueBuilder kStorageBonuses;
  kStorageBonuses["bonuses"] = res;
  return kStorageBonuses;
}

}  // namespace

struct DiscountData {
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

class DiscountDataFull : public ::testing::TestWithParam<DiscountData> {};

const std::vector<DiscountData> kDiscountData{
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
    {handlers::PromoRequest{
         {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, 1000.0},
     handlers::Promo(),
     handlers::Promo(),
     types::StoredDataRaw(),
     types::StoredDataRaw(),
     types::DiscountDataRaw(),
     types::DiscountDataRaw(),
     {},
     {}},
    {handlers::PromoRequest{
         {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, 1000.0},
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
    {handlers::PromoRequest{{}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, 6},
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
                            handlers::Discount{6, {}},
                            {},
                            {},
                            {},
                            {},
                            {}},
     {},
     {{"discount", "6"}}},
    {handlers::PromoRequest{{}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, 6},
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
                            handlers::Discount{6, {}},
                            {},
                            {},
                            {},
                            {},
                            {}},
     {},
     {{"discount", "6"}}},
    {handlers::PromoRequest{
         {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, 6, {}, 1000.0},
     handlers::Promo(),
     handlers::Promo{{},
                     {},
                     {},
                     {},
                     {},
                     {},
                     {},
                     {},
                     {},
                     {},
                     kNewResponseBonusesWithMaximumDiscount},
     types::StoredDataRaw(),
     types::StoredDataRaw{
         {},
         {},
         {},
         {},
         MakeStorageBonuses(kNewStoredBonusesWithMaximumDiscount),
         {}},
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
                            handlers::Discount{6, 1000.0},
                            {},
                            {},
                            {},
                            {},
                            {}},
     {},
     {{"discount", "6"}}},
    {handlers::PromoRequest{
         {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, 6, {}, 1000.0},
     handlers::Promo{
         1, {}, "name", {}, {}, {}, {}, {}, {}, {}, kOldResponseBonuses},
     handlers::Promo{1,
                     {},
                     "name",
                     {},
                     {},
                     {},
                     {},
                     {},
                     {},
                     {},
                     kMergeredResponseBonusesWithMaximumDiscount},
     types::StoredDataRaw{
         {1, 2}, {}, {}, {}, MakeStorageBonuses(kOldStoredBonuses), {}},
     types::StoredDataRaw{
         {1, 2},
         {},
         {},
         {},
         MakeStorageBonuses(kMergeredStoredBonusesWithMaximumDiscount),
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
                            {},
                            handlers::Discount{6, 1000.0},
                            {},
                            {},
                            {},
                            {},
                            {}},
     {},
     {{"discount", "6"}}}};

INSTANTIATE_TEST_SUITE_P(DiscountData, DiscountDataFull,
                         ::testing::ValuesIn(kDiscountData));

TEST_P(DiscountDataFull, check_discount_feature) {
  auto param = GetParam();
  models::PromoSettings settings;
  auto discount = Discount(Validator(), settings, {}, param.data);

  discount.UpdateResponse(param.response);
  ASSERT_EQ(param.response.bonuses.size(),
            param.expected_response.bonuses.size());

  discount.UpdateStoredData(param.stored_data);
  ASSERT_EQ(param.stored_data, param.expected_stored_data);

  discount.UpdateDiscountData(param.discount_data);
  ASSERT_EQ(param.discount_data, param.expected_discount_data);

  discount.UpdateTranslationArgs(param.tr_args);
  ASSERT_EQ(param.tr_args, param.expected_tr_args);
}

}  // namespace eats_restapp_promo::models::promo_features
