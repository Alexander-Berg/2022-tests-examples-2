#include <gtest/gtest.h>

#include <chrono>
#include <list>
#include <vector>

#include <userver/utils/datetime.hpp>
#include <userver/utils/mock_now.hpp>

#include <models/cached_park_activation.hpp>
#include <models/park_activation.hpp>

std::vector<parks_activation::models::ParkActivation> MockParkUpdates() {
  return std::vector<parks_activation::models::ParkActivation>{{
                                                                   "park1",
                                                                   "moscow",
                                                                   false,
                                                                   std::nullopt,
                                                                   false,
                                                                   false,
                                                                   false,
                                                                   false,
                                                                   false,
                                                                   false,
                                                                   false,
                                                                   false,
                                                                   {},
                                                                   1,
                                                                   false,
                                                                   std::nullopt,
                                                                   false,
                                                                   false,
                                                               },
                                                               {
                                                                   "park2",
                                                                   "moscow",
                                                                   false,
                                                                   std::nullopt,
                                                                   false,
                                                                   false,
                                                                   false,
                                                                   false,
                                                                   false,
                                                                   false,
                                                                   false,
                                                                   false,
                                                                   {},
                                                                   4,
                                                                   false,
                                                                   std::nullopt,
                                                                   false,
                                                                   false,
                                                               },
                                                               {
                                                                   "park6",
                                                                   "moscow",
                                                                   false,
                                                                   std::nullopt,
                                                                   false,
                                                                   false,
                                                                   false,
                                                                   false,
                                                                   false,
                                                                   false,
                                                                   false,
                                                                   false,
                                                                   {},
                                                                   7,
                                                                   false,
                                                                   std::nullopt,
                                                                   false,
                                                                   false,
                                                               }};
}

TEST(ParksActivationCache, TestCachedParksMissedRevisionsCalculating) {
  std::chrono::seconds ttl{100};
  auto tp1 = utils::datetime::Stringtime("2019-09-03 19:09:00", "UTC",
                                         "%Y-%m-%d %H:%M:%S");
  auto tp2 = tp1 + std::chrono::seconds(1);
  auto tp3 = tp2 + ttl + std::chrono::seconds(1);
  auto parks = MockParkUpdates();
  auto park = parks.begin();
  park->updated = tp1;
  park++;
  park->updated = tp2;
  park++;
  park->updated = tp3;
  ::utils::datetime::MockNowSet(tp3);
  parks_activation::models::CachedParkActivation park_activation;
  park_activation.UpsertItems(std::move(parks), ttl);
  std::unordered_set<std::int64_t> missed_revisions{5, 6};  // 2, 3 - ttl
  ASSERT_EQ(missed_revisions, park_activation.GetMissedRevisions());
}

TEST(ParksActivationCache, TestCachedParksRemoOld) {
  std::chrono::seconds ttl{100};
  auto tp1 = utils::datetime::Stringtime("2019-09-03 19:09:00", "UTC",
                                         "%Y-%m-%d %H:%M:%S");
  auto tp2 = tp1 + std::chrono::seconds(1);
  auto tp3 = tp2 + ttl + std::chrono::seconds(1);
  auto parks = MockParkUpdates();
  auto park = parks.begin();
  park->updated = tp1;
  park++;
  park->updated = tp2;
  park++;
  park->updated = tp3;
  ::utils::datetime::MockNowSet(tp3);
  parks_activation::models::CachedParkActivation park_activation;
  park_activation.UpsertItems(std::move(parks), ttl);
  auto tp4 = tp3 + std::chrono::seconds(1);
  park_activation.RemoveOldMissedRevisions(tp4);
  ASSERT_EQ(std::unordered_set<std::int64_t>{},
            park_activation.GetMissedRevisions());
}

TEST(ParksActivationCache, TestCachedParksGetWithRevisionGreater) {
  std::chrono::seconds ttl{100};
  auto parks = MockParkUpdates();
  parks_activation::models::CachedParkActivation park_activation;
  park_activation.UpsertItems(std::move(parks), ttl);
  std::vector<parks_activation::models::ParkActivation> expected_parks1{
      {
          "park1",
          "moscow",
          false,
          std::nullopt,
          false,
          false,
          false,
          false,
          false,
          false,
          false,
          false,
          {},
          1,
          false,
          std::nullopt,
          false,
          false,
      },
      {
          "park2",
          "moscow",
          false,
          std::nullopt,
          false,
          false,
          false,
          false,
          false,
          false,
          false,
          false,
          {},
          4,
          false,
          std::nullopt,
          false,
          false,
      },
      {
          "park6",
          "moscow",
          false,
          std::nullopt,
          false,
          false,
          false,
          false,
          false,
          false,
          false,
          false,
          {},
          7,
          false,
          std::nullopt,
          false,
          false,
      }};
  ASSERT_EQ(expected_parks1, park_activation.GetWithRevisionGreater(0, 3));

  std::vector<parks_activation::models::ParkActivation> expected_parks2{{
      "park1",
      "moscow",
      false,
      std::nullopt,
      false,
      false,
      false,
      false,
      false,
      false,
      false,
      false,
      {},
      1,
      false,
      std::nullopt,
      false,
      false,
  }};
  ASSERT_EQ(expected_parks2, park_activation.GetWithRevisionGreater(0, 1));

  std::vector<parks_activation::models::ParkActivation> expected_parks3{
      {
          "park2",
          "moscow",
          false,
          std::nullopt,
          false,
          false,
          false,
          false,
          false,
          false,
          false,
          false,
          {},
          4,
          false,
          std::nullopt,
          false,
          false,
      },
      {
          "park6",
          "moscow",
          false,
          std::nullopt,
          false,
          false,
          false,
          false,
          false,
          false,
          false,
          false,
          {},
          7,
          false,
          std::nullopt,
          false,
          false,
      }};
  ASSERT_EQ(expected_parks3, park_activation.GetWithRevisionGreater(1, 2));
}

TEST(ParksActivationCache, TestCachedParksGetByRevision) {
  std::chrono::seconds ttl{100};
  auto parks = MockParkUpdates();
  parks_activation::models::CachedParkActivation park_activation;
  park_activation.UpsertItems(std::move(parks), ttl);
  std::vector<parks_activation::models::ParkActivation> expected_parks1{
      {
          "park1",
          "moscow",
          false,
          std::nullopt,
          false,
          false,
          false,
          false,
          false,
          false,
          false,
          false,
          {},
          1,
          false,
          std::nullopt,
          false,
          false,
      },
      {
          "park2",
          "moscow",
          false,
          std::nullopt,
          false,
          false,
          false,
          false,
          false,
          false,
          false,
          false,
          {},
          4,
          false,
          std::nullopt,
          false,
          false,
      },
      {
          "park6",
          "moscow",
          false,
          std::nullopt,
          false,
          false,
          false,
          false,
          false,
          false,
          false,
          false,
          {},
          7,
          false,
          std::nullopt,
          false,
          false,
      }};
  ASSERT_EQ(expected_parks1, park_activation.GetByRevision({1, 4, 7}));

  std::vector<parks_activation::models::ParkActivation> expected_parks2{{
      "park1",
      "moscow",
      false,
      std::nullopt,
      false,
      false,
      false,
      false,
      false,
      false,
      false,
      false,
      {},
      1,
      false,
      std::nullopt,
      false,
      false,
  }};
  ASSERT_EQ(expected_parks2, park_activation.GetByRevision({1}));

  std::vector<parks_activation::models::ParkActivation> expected_parks3{
      {
          "park2",
          "moscow",
          false,
          std::nullopt,
          false,
          false,
          false,
          false,
          false,
          false,
          false,
          false,
          {},
          4,
          false,
          std::nullopt,
          false,
          false,
      },
      {
          "park6",
          "moscow",
          false,
          std::nullopt,
          false,
          false,
          false,
          false,
          false,
          false,
          false,
          false,
          {},
          7,
          false,
          std::nullopt,
          false,
          false,
      }};
  ASSERT_EQ(expected_parks3, park_activation.GetByRevision({4, 7, 10}));
}

TEST(ParksActivationCache, TestCachedParksGetById) {
  std::chrono::seconds ttl{100};
  auto parks = MockParkUpdates();
  parks_activation::models::CachedParkActivation park_activation;
  park_activation.UpsertItems(std::move(parks), ttl);
  std::vector<parks_activation::models::ParkActivation> expected_parks1{
      {
          "park1",
          "moscow",
          false,
          std::nullopt,
          false,
          false,
          false,
          false,
          false,
          false,
          false,
          false,
          {},
          1,
          false,
          std::nullopt,
          false,
          false,
      },
      {
          "park2",
          "moscow",
          false,
          std::nullopt,
          false,
          false,
          false,
          false,
          false,
          false,
          false,
          false,
          {},
          4,
          false,
          std::nullopt,
          false,
          false,
      },
      {
          "park6",
          "moscow",
          false,
          std::nullopt,
          false,
          false,
          false,
          false,
          false,
          false,
          false,
          false,
          {},
          7,
          false,
          std::nullopt,
          false,
          false,
      }};
  std::vector<std::string> park_ids1{"park1", "park2", "park6"};
  ASSERT_EQ(expected_parks1, park_activation.GetById(park_ids1));
  std::vector<parks_activation::models::ParkActivation> expected_parks2{
      {
          "park1",
          "moscow",
          false,
          std::nullopt,
          false,
          false,
          false,
          false,
          false,
          false,
          false,
          false,
          {},
          1,
          false,
          std::nullopt,
          false,
          false,
      },
      {
          "park2",
          "moscow",
          false,
          std::nullopt,
          false,
          false,
          false,
          false,
          false,
          false,
          false,
          false,
          {},
          4,
          false,
          std::nullopt,
          false,
          false,
      }};
  std::vector<std::string> park_ids2{"park1", "park2", "unknown_id"};
  ASSERT_EQ(expected_parks2, park_activation.GetById(park_ids2));
}
