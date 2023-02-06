#include <userver/utest/utest.hpp>

#include <defs/api/promo.hpp>
#include <defs/definitions.hpp>
#include <defs/internal/stored_data.hpp>
#include <experiments3/eats_restapp_promo_settings.hpp>

#include <models/promo_features/shipping_types.hpp>
#include <types/discount_data.hpp>
#include <types/stored_data.hpp>

namespace eats_restapp_promo::models::promo_features {

namespace {

struct Validator {
  void ValidateShippingTypes(
      const models::PromoSettings&,
      const std::optional<std::vector<std::string>>&) const {
    return;
  }
};

const std::vector<handlers::PromoRequirement> kOldResponseRequirement = {
    handlers::PromoRequirement{1.1,
                               {},
                               {},
                               {},
                               {},
                               {},
                               std::vector<std::string>{"method1", "method2"}},
    handlers::PromoRequirement{
        0.1, {}, {}, {}, {}, {}, std::vector<std::string>{"method3"}}};

const std::vector<handlers::PromoRequirement> kNewResponseRequirement = {
    handlers::PromoRequirement{{},
                               {},
                               {},
                               {},
                               {},
                               {},
                               std::vector<std::string>{"method4", "method5"}}};

const std::vector<handlers::PromoRequirement> kMergeredResponseRequirement{
    kOldResponseRequirement[0], kOldResponseRequirement[1],
    kNewResponseRequirement[0]};

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
            {},
            {},
            std::vector<std::string>{"method1", "method2"}},
        ::defs::internal::stored_data::StoredPromoRequirement{
            0.1,
            {},
            {},
            {},
            {},
            {},
            0,
            {},
            {},
            std::vector<std::string>{"method3"}}};

const std::vector<::defs::internal::stored_data::StoredPromoRequirement>
    kNewStoredRequirement = {
        ::defs::internal::stored_data::StoredPromoRequirement{
            {},
            {},
            {},
            {},
            {},
            {},
            {},
            {},
            {},
            std::vector<std::string>{"method4", "method5"}}};

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

const std::vector<std::string> kOldRequestShihppingTypes = {
    "method1", "method2", "method3"};

const std::vector<std::string> kNewRequestShihppingTypes = {"method4",
                                                            "method5"};

const std::vector<std::string> kMergeredRequestShihppingTypes = {
    "method1", "method2", "method3", "method4", "method5"};

}  // namespace

struct ShippingTypesData {
  handlers::PromoRequest data;

  handlers::Promo response;
  handlers::Promo expected_response;
  types::StoredDataRaw stored_data;
  types::StoredDataRaw expected_stored_data;
  types::DiscountDataRaw discount_data;
  types::DiscountDataRaw expected_discount_data;
};

class ShippingTypesDataFull
    : public ::testing::TestWithParam<ShippingTypesData> {};

const std::vector<ShippingTypesData> kShippingTypesData{
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
                            {},
                            {},
                            {},
                            kOldRequestShihppingTypes},
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
                            {},
                            {},
                            kOldRequestShihppingTypes}},
    {handlers::PromoRequest{{},
                            {},
                            {},
                            {},
                            {},
                            {},
                            {},
                            std::vector<std::string>{"method4", "method5"}},
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
                            {},
                            {},
                            {},
                            kOldRequestShihppingTypes},
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
                            {},
                            {},
                            kMergeredRequestShihppingTypes}},
    {handlers::PromoRequest{{},
                            {},
                            {},
                            {},
                            {},
                            {},
                            {},
                            std::vector<std::string>{"method4", "method5"}},
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
                            kNewRequestShihppingTypes}}};

INSTANTIATE_TEST_SUITE_P(ShippingTypesData, ShippingTypesDataFull,
                         ::testing::ValuesIn(kShippingTypesData));

TEST_P(ShippingTypesDataFull, check_delivery_methods_feature) {
  auto param = GetParam();
  models::PromoSettings settings;
  auto shipping_types = ShippingTypes(Validator(), settings, {}, param.data);

  shipping_types.UpdateResponse(param.response);
  ASSERT_EQ(param.response, param.expected_response);

  shipping_types.UpdateStoredData(param.stored_data);
  ASSERT_EQ(param.stored_data, param.expected_stored_data);

  shipping_types.UpdateDiscountData(param.discount_data);
  ASSERT_EQ(param.discount_data, param.expected_discount_data);
}

}  // namespace eats_restapp_promo::models::promo_features
