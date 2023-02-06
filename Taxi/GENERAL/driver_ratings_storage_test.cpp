#include <gtest/gtest.h>

#include <userver/dump/test_helpers.hpp>
#include <userver/utils/datetime.hpp>

#include <models/driver_ratings_storage.hpp>

using models::driver_rating::RatingWithDetails;
using models::driver_rating::ScoreItem;
using models::driver_ratings_storage::Storage;

TEST(DriverRatingsModels, EmptyData) {
  dump::TestWriteReadCycle(ScoreItem{});
  dump::TestWriteReadCycle(RatingWithDetails{});
}

TEST(DriverRatingsModels, NonEmptyData) {
  using namespace std::chrono_literals;
  auto now = utils::datetime::Now();

  const ScoreItem item1{now - 10s, 5, 1.0};
  const ScoreItem item2{now - 20s, 4, 2.0};

  const RatingWithDetails rating{{"unique_driver_id", now, 4.5, 2},
                                 5,
                                 std::vector<ScoreItem>{item1, item2}};

  const Storage data{std::vector<RatingWithDetails>{rating}, "cursor"};

  dump::TestWriteReadCycle(item1);
  dump::TestWriteReadCycle(item2);
  dump::TestWriteReadCycle(rating);
  dump::TestWriteReadCycle(data);
}
