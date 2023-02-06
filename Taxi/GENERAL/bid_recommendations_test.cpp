#include <models/bid_recommendations.hpp>

#include <models/place.hpp>
#include <unordered_map>
#include <userver/dump/test_helpers.hpp>

#include <gtest/gtest.h>

namespace eats_restapp_marketing::models {

TEST(BidRecommendationContainerDump, TestReadWriteSimple) {
  PercentRecommendationRow row1{1, 1, 1, 1}, row2{2, 2, 2, 2}, row3{3, 3, 3, 3};
  std::vector<PercentRecommendationRow> source{row1, row2, row3};

  const auto container = BidRecommendationContainer(std::move(source), 1);
  dump::TestWriteReadCycle(container);
}

TEST(BidRecommendationContainerDump, TestGetPlaceRecommendationParameters) {
  models::PlaceId place_id{1};
  PercentRecommendationRow first_row_with_place_id{place_id.GetUnderlying(), 10,
                                                   1, 1},
      second_row_with_place_id{place_id.GetUnderlying(), 20, 2, 2};
  ASSERT_EQ(first_row_with_place_id.place_id,
            second_row_with_place_id.place_id);

  std::vector<PercentRecommendationRow> source{first_row_with_place_id,
                                               second_row_with_place_id};

  const auto container = BidRecommendationContainer(std::move(source), 1);
  auto recommendations = container.GetRecommendations(place_id);

  auto res_it = recommendations.find(
      models::Percent(first_row_with_place_id.wins_percent));
  ASSERT_FALSE(res_it == recommendations.end());
  auto res = res_it->second;
  ASSERT_EQ(res.average_cpc.ToInteger(), first_row_with_place_id.average_cpc);
  ASSERT_EQ(res.weekly_spend_limit.ToInteger(),
            first_row_with_place_id.weekly_spend_limit);

  res_it = recommendations.find(
      models::Percent(second_row_with_place_id.wins_percent));
  ASSERT_FALSE(res_it == recommendations.end());
  res = res_it->second;
  ASSERT_EQ(res.average_cpc.ToInteger(), second_row_with_place_id.average_cpc);
  ASSERT_EQ(res.weekly_spend_limit.ToInteger(),
            second_row_with_place_id.weekly_spend_limit);
}

TEST(BidRecommendationContainerDump, TestGetPlacesRecommendationCount) {
  models::PlaceId place_id1{1}, place_id2{2}, place_id3{3};
  PercentRecommendationRow first_row_with_place_id1{place_id1.GetUnderlying(),
                                                    10, 1, 1},
      second_row_with_place_id1{place_id1.GetUnderlying(), 20, 2, 2},
      row_with_place_id2{place_id2.GetUnderlying(), 2, 2, 2},
      row_with_place_id3{place_id3.GetUnderlying(), 3, 3, 3};
  std::vector<PercentRecommendationRow> source{
      first_row_with_place_id1, second_row_with_place_id1, row_with_place_id2,
      row_with_place_id3};

  std::unordered_map<models::PlaceId, int64_t> repeated_places_count;
  for (const auto& row : source) {
    auto [_, is_not_contains] =
        repeated_places_count.try_emplace(models::PlaceId{row.place_id}, 1);
    if (!is_not_contains) {
      repeated_places_count[models::PlaceId{row.place_id}]++;
    }
  }

  const auto container = BidRecommendationContainer(std::move(source), 1);
  for (const auto& place : source) {
    auto recommendations =
        container.GetRecommendations(models::PlaceId(place.place_id));
    ASSERT_EQ(recommendations.size(),
              repeated_places_count[models::PlaceId(place.place_id)]);
  }
}

}  // namespace eats_restapp_marketing::models
