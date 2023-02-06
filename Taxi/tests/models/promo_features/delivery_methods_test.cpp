#include <userver/utest/utest.hpp>

#include <defs/api/promo.hpp>
#include <defs/definitions.hpp>
#include <defs/internal/stored_data.hpp>
#include <experiments3/eats_restapp_promo_settings.hpp>

#include <models/promo_features/delivery_methods.hpp>
#include <types/discount_data.hpp>
#include <types/stored_data.hpp>

namespace eats_restapp_promo::models::promo_features {

namespace {

struct Validator {};

const std::vector<handlers::PromoRequirement> kResponseRequirements = {
    handlers::PromoRequirement{1.1, {}, {}, {}, {}, {}, {}},
    handlers::PromoRequirement{0.1, {}, {}, {}, {}, {}, {}}};

const std::vector<::defs::internal::stored_data::StoredPromoRequirement>
    kOldStoredRequirement = {
        ::defs::internal::stored_data::StoredPromoRequirement{
            1.1,
            {},
            {},
            {},
            {},
            std::vector<std::string>{"method1", "method2"},
            1,
            {},
            {},
            {}},
        ::defs::internal::stored_data::StoredPromoRequirement{
            0.1,
            {},
            {},
            {},
            {},
            std::vector<std::string>{"metohd3"},
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
            {},
            std::vector<std::string>{"pedestrian"},
            {},
            {},
            {},
            {}}};

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

const std::vector<std::string> kOldRequestDeliveryMethod = {"metohd1",
                                                            "metohd2"};

const std::vector<std::string> kNewRequestDeliveryMethod = {"pedestrian"};

const std::vector<std::string> kMergeredRequestDeliveryMethod = {
    kOldRequestDeliveryMethod[0], kOldRequestDeliveryMethod[1],
    kNewRequestDeliveryMethod[0]};

}  // namespace

struct DeliveryMethodsData {
  handlers::PromoRequest data;

  handlers::Promo response;
  handlers::Promo expected_response;
  types::StoredDataRaw stored_data;
  types::StoredDataRaw expected_stored_data;
  types::DiscountDataRaw discount_data;
  types::DiscountDataRaw expected_discount_data;
};

class DeliveryMethodsDataFull
    : public ::testing::TestWithParam<DeliveryMethodsData> {};

const std::vector<DeliveryMethodsData> kDeliveryMethodsData{
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
     types::DiscountDataRaw{{},
                            {1, 2},
                            {},
                            {},
                            kOldRequestDeliveryMethod,
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
                            {},
                            kOldRequestDeliveryMethod,
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
    {handlers::PromoRequest{handlers::TypeOfPromo::kFreeDelivery},
     handlers::Promo(), handlers::Promo(), types::StoredDataRaw(),
     types::StoredDataRaw{
         {}, {}, {}, MakeStorageRequirements(kNewStoredRequirement), {}, {}},
     types::DiscountDataRaw(),
     types::DiscountDataRaw{{},
                            {},
                            {},
                            {},
                            kNewRequestDeliveryMethod,
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
    {handlers::PromoRequest{handlers::TypeOfPromo::kFreeDelivery},
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
     types::DiscountDataRaw{{},
                            {1, 2},
                            {},
                            {},
                            kOldRequestDeliveryMethod,
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
                            {},
                            kMergeredRequestDeliveryMethod,
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

INSTANTIATE_TEST_SUITE_P(DeliveryMethodsData, DeliveryMethodsDataFull,
                         ::testing::ValuesIn(kDeliveryMethodsData));

TEST_P(DeliveryMethodsDataFull, check_delivery_metohds_feature) {
  auto param = GetParam();
  models::PromoSettings settings;
  auto delivery_methods =
      DeliveryMethods(Validator(), settings, {}, param.data);

  delivery_methods.UpdateResponse(param.response);
  ASSERT_EQ(param.response, param.expected_response);

  delivery_methods.UpdateStoredData(param.stored_data);
  ASSERT_EQ(param.stored_data, param.expected_stored_data);

  delivery_methods.UpdateDiscountData(param.discount_data);
  ASSERT_EQ(param.discount_data, param.expected_discount_data);
}

}  // namespace eats_restapp_promo::models::promo_features
