#include <userver/utest/utest.hpp>

#include <defs/api/promo.hpp>
#include <defs/definitions.hpp>
#include <experiments3/eats_restapp_promo_settings.hpp>

#include <models/promo_features/place_ids.hpp>
#include <types/discount_data.hpp>
#include <types/places.hpp>
#include <types/stored_data.hpp>

namespace eats_restapp_promo::models::promo_features {

namespace {

struct Validator {
  void ValidatePlaceIds(const models::PromoSettings&, types::Places&) const {
    return;
  }
};

const std::vector<int64_t> kOldPlaceIds = {1, 2, 3};

const std::vector<int64_t> kNewPlaceIds = {4, 5};

}  // namespace

struct PlaceIdsData {
  handlers::PromoRequest data;

  handlers::Promo response;
  handlers::Promo expected_response;
  types::StoredDataRaw stored_data;
  types::StoredDataRaw expected_stored_data;
  types::DiscountDataRaw discount_data;
  types::DiscountDataRaw expected_discount_data;
};

class PlaceIdsDataFull : public ::testing::TestWithParam<PlaceIdsData> {};

const std::vector<PlaceIdsData> kPlaceIdsData{
    {handlers::PromoRequest(), handlers::Promo(), handlers::Promo(),
     types::StoredDataRaw(), types::StoredDataRaw(), types::DiscountDataRaw(),
     types::DiscountDataRaw()},
    {handlers::PromoRequest(),
     handlers::Promo{1, {}, "name", {}, kOldPlaceIds, {}, {}, {}, {}, {}, {}},
     handlers::Promo{1, {}, "name", {}, {}, {}, {}, {}, {}, {}, {}},
     types::StoredDataRaw{kOldPlaceIds, {}, {}, {}, {}, {}},
     types::StoredDataRaw{{}, {}, {}, {}, {}, {}},
     types::DiscountDataRaw{{},
                            kOldPlaceIds,
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
     types::DiscountDataRaw{
         {}, {}, {}, {}, {}, 1, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}}},
    {handlers::PromoRequest{{}, kNewPlaceIds, {}, {}, {}, {}},
     handlers::Promo(),
     handlers::Promo{{}, {}, {}, {}, kNewPlaceIds, {}, {}, {}, {}, {}, {}},
     types::StoredDataRaw(),
     types::StoredDataRaw{kNewPlaceIds, {}, {}, {}, {}, {}},
     types::DiscountDataRaw(),
     types::DiscountDataRaw{{},
                            kNewPlaceIds,
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
                            {}}},
    {handlers::PromoRequest{{}, kNewPlaceIds, {}, {}, {}, {}},
     handlers::Promo{1, {}, "name", {}, kOldPlaceIds, {}, {}, {}, {}, {}, {}},
     handlers::Promo{1, {}, "name", {}, kNewPlaceIds, {}, {}, {}, {}, {}, {}},
     types::StoredDataRaw{kOldPlaceIds, {}, {}, {}, {}, {}},
     types::StoredDataRaw{kNewPlaceIds, {}, {}, {}, {}, {}},
     types::DiscountDataRaw{{},
                            kOldPlaceIds,
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
     types::DiscountDataRaw{{},
                            kNewPlaceIds,
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
                            {}}}};

INSTANTIATE_TEST_SUITE_P(PlaceIdsData, PlaceIdsDataFull,
                         ::testing::ValuesIn(kPlaceIdsData));

TEST_P(PlaceIdsDataFull, check_itm_ids_feature) {
  auto param = GetParam();
  models::PromoSettings settings;
  auto place_ids = PlaceIds(Validator(), settings, {}, param.data);

  place_ids.UpdateResponse(param.response);
  ASSERT_EQ(param.response, param.expected_response);

  place_ids.UpdateStoredData(param.stored_data);
  ASSERT_EQ(param.stored_data, param.expected_stored_data);

  place_ids.UpdateDiscountData(param.discount_data);
  ASSERT_EQ(param.discount_data, param.expected_discount_data);
}

}  // namespace eats_restapp_promo::models::promo_features
