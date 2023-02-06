#include <gtest/gtest.h>
#include <clients/eats-place-rating/client_gmock.hpp>
#include <taxi_config/variables/EATS_RESTAPP_MARKETING_PROMO_START.hpp>
#include <userver/dynamic_config/test_helpers.hpp>
#include <userver/utest/utest.hpp>
#include "promo/checker.hpp"

namespace testing {
using Config = ::taxi_config::eats_restapp_marketing_promo_start::
    EatsRestappMarketingPromoStart;
using eats_restapp_marketing::promo::checker::CheckerResults;
using eats_restapp_marketing::promo::checker::CheckRating;

struct PromoCheckerTest : public Test {
  std::shared_ptr<StrictMock<clients::eats_place_rating::ClientGMock>>
      rating_mock = std::make_shared<
          StrictMock<clients::eats_place_rating::ClientGMock>>();

  clients::eats_place_rating::PlaceRatingInfo BuildRatingInfo(
      std::int64_t id, double rating, double cancel_rating,
      std::optional<int> feedbacks_count) {
    clients::eats_place_rating::PlaceRatingInfo info;
    info.place_id = id;
    info.average_rating = rating;
    info.cancel_rating = cancel_rating;
    info.feedbacks_count = feedbacks_count;
    return info;
  }
};

TEST_F(PromoCheckerTest, BadAverageRating) {
  std::vector<std::int64_t> place_ids{111111};
  {
    namespace rating_client = clients::eats_place_rating::
        eats_v1_eats_place_rating_v1_places_rating_info::get;
    rating_client::Request rating_request;
    rating_request.place_ids = place_ids;
    rating_client::Response200 rating_response200;
    rating_response200.places_rating_info = {
        BuildRatingInfo(111111, 4.0, 3.5, 11)};
    EXPECT_CALL(*rating_mock,
                EatsV1EatsPlaceRatingV1PlacesRatingInfo(rating_request, _))
        .WillOnce(Return(rating_response200));
  }
  const auto source = dynamic_config::GetDefaultSource().GetSnapshot();
  auto result = CheckRating(
      place_ids, source[taxi_config::EATS_RESTAPP_MARKETING_PROMO_START],
      *rating_mock);
  ASSERT_EQ(result.size(), 1);
  ASSERT_EQ(result[111111]->result, CheckerResults::kBadRating);
  ASSERT_EQ(result[111111]->rating, 4.0);
  ASSERT_EQ(result[111111]->cancel_rating, 3.5);
}
TEST_F(PromoCheckerTest, BadCancelRating) {
  std::vector<std::int64_t> place_ids{111111};
  {
    namespace rating_client = clients::eats_place_rating::
        eats_v1_eats_place_rating_v1_places_rating_info::get;
    rating_client::Request rating_request;
    rating_request.place_ids = place_ids;
    rating_client::Response200 rating_response200;
    rating_response200.places_rating_info = {
        BuildRatingInfo(111111, 4.0, 3.5, 9)};
    EXPECT_CALL(*rating_mock,
                EatsV1EatsPlaceRatingV1PlacesRatingInfo(rating_request, _))
        .WillOnce(Return(rating_response200));
  }
  const auto source = dynamic_config::GetDefaultSource().GetSnapshot();
  auto result = CheckRating(
      place_ids, source[taxi_config::EATS_RESTAPP_MARKETING_PROMO_START],
      *rating_mock);
  ASSERT_EQ(result.size(), 1);
  ASSERT_EQ(result[111111]->result, CheckerResults::kBadCancelRating);
  ASSERT_EQ(result[111111]->rating, 4.0);
  ASSERT_EQ(result[111111]->cancel_rating, 3.5);
}
TEST_F(PromoCheckerTest, OkRatingMoreThanThreshold) {
  std::vector<std::int64_t> place_ids{111111};
  {
    namespace rating_client = clients::eats_place_rating::
        eats_v1_eats_place_rating_v1_places_rating_info::get;
    rating_client::Request rating_request;
    rating_request.place_ids = place_ids;
    rating_client::Response200 rating_response200;
    rating_response200.places_rating_info = {
        BuildRatingInfo(111111, 4.2, 5.0, 10)};
    EXPECT_CALL(*rating_mock,
                EatsV1EatsPlaceRatingV1PlacesRatingInfo(rating_request, _))
        .WillOnce(Return(rating_response200));
  }
  const auto source = dynamic_config::GetDefaultSource().GetSnapshot();
  auto result = CheckRating(
      place_ids, source[taxi_config::EATS_RESTAPP_MARKETING_PROMO_START],
      *rating_mock);
  ASSERT_EQ(result.size(), 1);
  ASSERT_EQ(result[111111]->result, CheckerResults::kOkRating);
}
TEST_F(PromoCheckerTest, OkRatingLessThanThreshold) {
  std::vector<std::int64_t> place_ids{111111};
  {
    namespace rating_client = clients::eats_place_rating::
        eats_v1_eats_place_rating_v1_places_rating_info::get;
    rating_client::Request rating_request;
    rating_request.place_ids = place_ids;
    rating_client::Response200 rating_response200;
    rating_response200.places_rating_info = {
        BuildRatingInfo(111111, 5.0, 3.9, 9)};
    EXPECT_CALL(*rating_mock,
                EatsV1EatsPlaceRatingV1PlacesRatingInfo(rating_request, _))
        .WillOnce(Return(rating_response200));
  }
  const auto source = dynamic_config::GetDefaultSource().GetSnapshot();
  auto result = CheckRating(
      place_ids, source[taxi_config::EATS_RESTAPP_MARKETING_PROMO_START],
      *rating_mock);
  ASSERT_EQ(result.size(), 1);
  ASSERT_EQ(result[111111]->result, CheckerResults::kOkCancelRating);
}

TEST_F(PromoCheckerTest, ManyPlaces) {
  std::vector<std::int64_t> place_ids{1, 2, 3, 4, 5};
  {
    namespace rating_client = clients::eats_place_rating::
        eats_v1_eats_place_rating_v1_places_rating_info::get;
    rating_client::Request rating_request;
    rating_request.place_ids = place_ids;
    rating_client::Response200 rating_response200;
    rating_response200.places_rating_info = {
        BuildRatingInfo(1, 5.0, 3.9, 1), BuildRatingInfo(2, 5.0, 3.9, 1),
        BuildRatingInfo(3, 5.0, 3.9, 1),
        BuildRatingInfo(4, 5.0, 3.9, std::nullopt),
        BuildRatingInfo(5, 5.0, 3.9, 1)};
    EXPECT_CALL(*rating_mock,
                EatsV1EatsPlaceRatingV1PlacesRatingInfo(rating_request, _))
        .WillOnce(Return(rating_response200));
  }
  const auto source = dynamic_config::GetDefaultSource().GetSnapshot();
  CheckRating(place_ids,
              source[taxi_config::EATS_RESTAPP_MARKETING_PROMO_START],
              *rating_mock);
}

}  // namespace testing

namespace clients::eats_place_rating {
namespace eats_v1_eats_place_rating_v1_places_rating_info::get {
inline bool operator==(const Request& lhs, const Request& rhs) {
  return lhs.place_ids.size() == rhs.place_ids.size();
}
}  // namespace eats_v1_eats_place_rating_v1_places_rating_info::get
}  // namespace clients::eats_place_rating
