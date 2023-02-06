#include "models/places_units.hpp"

#include <gtest/gtest.h>
#include <clients/eats-core/client_gmock.hpp>

namespace eats_report_storage::models {

using namespace ::testing;

struct PlaceUnitsTest : public Test {
  StrictMock<clients::eats_core::ClientGMock> core_mock;

  clients::eats_core::Place MakePlace(int64_t place_id,
                                      const std::string& currency) {
    clients::eats_core::Place place;
    place.id = place_id;
    place.currency.sign = currency;
    return place;
  }
};

TEST_F(PlaceUnitsTest, should_return_nullopt_for_empty_place_ids_model) {
  PlacesUnits units(core_mock, types::PlaceIds{});
  const auto res = units.Get("currency");
  ASSERT_FALSE(res.has_value());
}

TEST_F(PlaceUnitsTest,
       should_request_core_on_first_call_and_return_value_from_place_info) {
  PlacesUnits units(core_mock, types::PlaceIds{types::PlaceId{1}});
  clients::eats_core::v1_places_info::post::Response response;
  response.payload = {MakePlace(1, "$$")};
  EXPECT_CALL(core_mock, V1PlacesInfo(_, _)).WillOnce(Return(response));
  units.Get("currency");
  const auto res = units.Get("currency");
  ASSERT_EQ(res, "$$");
}

TEST_F(PlaceUnitsTest, should_not_request_core_on_second_call) {
  PlacesUnits units(core_mock, types::PlaceIds{types::PlaceId{1}});
  clients::eats_core::v1_places_info::post::Response response;
  response.payload = {MakePlace(1, "$$")};
  EXPECT_CALL(core_mock, V1PlacesInfo(_, _)).WillOnce(Return(response));
  units.Get("currency");
  units.Get("currency");
}

TEST_F(PlaceUnitsTest, should_return_common_value_for_multiple_places) {
  PlacesUnits units(core_mock,
                    types::PlaceIds{types::PlaceId{1}, types::PlaceId{2}});
  clients::eats_core::v1_places_info::post::Response response;
  response.payload = {MakePlace(1, "$$"), MakePlace(2, "$$")};
  EXPECT_CALL(core_mock, V1PlacesInfo(_, _)).WillOnce(Return(response));
  const auto res = units.Get("currency");
  ASSERT_EQ(res, "$$");
}

TEST_F(PlaceUnitsTest, should_return_nullopt_for_different_places) {
  PlacesUnits units(core_mock,
                    types::PlaceIds{types::PlaceId{1}, types::PlaceId{2}});
  clients::eats_core::v1_places_info::post::Response response;
  response.payload = {MakePlace(1, "$$"), MakePlace(2, "¥¥")};
  EXPECT_CALL(core_mock, V1PlacesInfo(_, _)).WillOnce(Return(response));
  const auto res = units.Get("currency");
  ASSERT_FALSE(res.has_value());
}

TEST_F(PlaceUnitsTest, should_return_nullopt_for_unknown_unit) {
  PlacesUnits units(core_mock, types::PlaceIds{types::PlaceId{1}});
  const auto res = units.Get("unknown");
  ASSERT_FALSE(res.has_value());
}

}  // namespace eats_report_storage::models
