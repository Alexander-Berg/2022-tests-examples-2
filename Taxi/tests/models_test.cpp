#include <gtest/gtest.h>

#include <userver/cache/statistics_mock.hpp>
#include <userver/formats/json.hpp>
#include <userver/utils/datetime.hpp>
#include <userver/utils/mock_now.hpp>

#include <models/park_activation.hpp>

TEST(TestParksActivation, TestParseFromString) {
  std::string data_str = R"(
  {
      "revision": 2,
      "last_modified": "1970-01-15T03:56:07.000",
      "park_id": "park1",
      "city_id": "city",
      "data": {
          "deactivated": false,
          "can_cash": false,
          "can_card": false,
          "can_coupon": true,
          "can_corp": false,
          "can_logistic": true
      }
  })";
  auto json = formats::json::FromString(data_str);
  parks_activation::models::Park data{json};
  EXPECT_EQ(2, data.update_info.revision);
  EXPECT_EQ("park1", data.park_id);
  EXPECT_EQ(false, data.can_cash);
  EXPECT_EQ(false, data.can_card);
  EXPECT_EQ(true, data.can_coupon);
  EXPECT_EQ(false, data.can_corp);
  EXPECT_EQ(false, data.deactivated);
  EXPECT_EQ(true, data.can_logistic);
  EXPECT_EQ(false, data.can_corp_without_vat);
  EXPECT_EQ(false, data.has_corp_without_vat_contract);
  data_str = R"(
  {
      "revision": 3,
      "last_modified": "1970-01-15T03:56:07.000",
      "park_id": "park2",
      "city_id": "city",
      "data": {
          "deactivated": true,
          "deactivated_reason": "test_reason",
          "can_cash": false,
          "can_card": false,
          "can_coupon": true,
          "can_corp": false,
          "can_logistic": true,
          "can_corp_without_vat": true,
          "has_corp_without_vat_contract": true
      }
  })";
  json = formats::json::FromString(data_str);
  data = parks_activation::models::Park(json);
  EXPECT_EQ(3, data.update_info.revision);
  EXPECT_EQ("park2", data.park_id);
  EXPECT_EQ(false, data.can_cash);
  EXPECT_EQ(false, data.can_card);
  EXPECT_EQ(true, data.can_coupon);
  EXPECT_EQ(false, data.can_corp);
  EXPECT_EQ(true, data.deactivated);
  EXPECT_EQ(true, data.can_logistic);
  EXPECT_EQ(true, data.can_corp_without_vat);
  EXPECT_EQ(true, data.has_corp_without_vat_contract);
  EXPECT_EQ("test_reason", data.deactivated_reason);
}

TEST(TestParksActivation, TestHoleStorage) {
  using Revision = parks_activation::models::Revision;
  parks_activation::models::MissedRevisionStorage hs;

  auto tp1 = utils::datetime::Stringtime("2019-02-28 21:00:00", "UTC",
                                         "%Y-%m-%d %H:%M:%S");
  auto tp2 = utils::datetime::Stringtime("2019-02-28 22:00:00", "UTC",
                                         "%Y-%m-%d %H:%M:%S");
  auto tp3 = utils::datetime::Stringtime("2019-02-28 23:00:00", "UTC",
                                         "%Y-%m-%d %H:%M:%S");

  hs.Add(1, tp1);
  EXPECT_TRUE(hs.Contains(1));
  EXPECT_EQ(std::unordered_set<Revision>{1}, hs.GetAll());

  hs.Add(3, tp3);
  EXPECT_EQ(2, hs.Count());
  EXPECT_TRUE(hs.Contains(3));
  auto expected_holes = std::unordered_set<Revision>{1, 3};
  EXPECT_EQ(expected_holes, hs.GetAll());

  hs.RemoveOld(tp2);
  EXPECT_FALSE(hs.Contains(1));
  EXPECT_TRUE(hs.Contains(3));
  EXPECT_EQ(1, hs.Count());
  EXPECT_EQ(std::unordered_set<Revision>{3}, hs.GetAll());

  hs.Erase(3);
  EXPECT_FALSE(hs.Contains(3));
  EXPECT_EQ(0, hs.Count());
  EXPECT_EQ(std::unordered_set<Revision>{}, hs.GetAll());
}

parks_activation::models::Park MakeTestItem(
    long revision, std::chrono::system_clock::time_point time_point =
                       ::utils::datetime::Now()) {
  parks_activation::models::Park test_item;
  test_item.park_id = std::to_string(revision);
  test_item.update_info.revision = revision;
  test_item.update_info.last_modified = time_point;
  return test_item;
}

TEST(TestParksActivation, TestCachedParks) {
  parks_activation::models::CachedParks cached_parks;
  using Revision = parks_activation::models::Revision;
  auto ttl = std::chrono::seconds(600);
  auto tp1 = utils::datetime::Stringtime("2019-02-28 21:00:00", "UTC",
                                         "%Y-%m-%d %H:%M:%S");
  auto tp2 = utils::datetime::Stringtime("2019-02-28 22:00:00", "UTC",
                                         "%Y-%m-%d %H:%M:%S");
  auto tp3 = utils::datetime::Stringtime("2019-02-28 23:00:00", "UTC",
                                         "%Y-%m-%d %H:%M:%S");
  auto tp4 = utils::datetime::Stringtime("2019-02-28 23:00:01", "UTC",
                                         "%Y-%m-%d %H:%M:%S");

  auto tp5 = utils::datetime::Stringtime("2019-02-28 23:00:01", "UTC",
                                         "%Y-%m-%d %H:%M:%S");

  ::cache::UpdateStatisticsScopeMock scope(::cache::UpdateType::kFull);
  ::utils::datetime::MockNowSet(tp1);
  cached_parks.UpsertItems({MakeTestItem(1, tp1)}, scope.GetScope(), ttl);
  EXPECT_EQ(1, cached_parks.Size());
  EXPECT_EQ(1, cached_parks.Cursor());
  ::utils::datetime::MockNowSet(tp2);
  cached_parks.UpsertItems({MakeTestItem(4, tp2)}, scope.GetScope(), ttl);
  EXPECT_EQ(2, cached_parks.Size());
  EXPECT_EQ(4, cached_parks.Cursor());
  auto expected_holes = std::unordered_set<Revision>{2, 3};
  EXPECT_EQ(expected_holes, cached_parks.GetMissedRevisions());

  cached_parks.RemoveOldMissedRevisions(tp1);

  EXPECT_EQ(expected_holes, cached_parks.GetMissedRevisions());
  EXPECT_EQ(2, cached_parks.Size());
  EXPECT_EQ(4, cached_parks.Cursor());

  ::utils::datetime::MockNowSet(tp4);
  cached_parks.UpsertItems(
      {MakeTestItem(6, tp4), MakeTestItem(7, tp4), MakeTestItem(9, tp4)},
      scope.GetScope(), ttl);
  expected_holes = std::unordered_set<Revision>{2, 3, 5, 8};
  EXPECT_EQ(expected_holes, cached_parks.GetMissedRevisions());
  EXPECT_EQ(5, cached_parks.Size());
  EXPECT_EQ(9, cached_parks.Cursor());

  cached_parks.RemoveOldMissedRevisions(tp2);
  expected_holes = std::unordered_set<Revision>{2, 3, 5, 8};
  EXPECT_EQ(expected_holes, cached_parks.GetMissedRevisions());
  EXPECT_EQ(5, cached_parks.Size());
  EXPECT_EQ(9, cached_parks.Cursor());

  cached_parks.RemoveOldMissedRevisions(tp3);
  expected_holes = std::unordered_set<Revision>{5, 8};
  EXPECT_EQ(expected_holes, cached_parks.GetMissedRevisions());
  EXPECT_EQ(5, cached_parks.Size());
  EXPECT_EQ(9, cached_parks.Cursor());

  cached_parks.UpsertItems({MakeTestItem(5, tp5)}, scope.GetScope(), ttl);
  expected_holes = std::unordered_set<Revision>{8};
  EXPECT_EQ(expected_holes, cached_parks.GetMissedRevisions());
  EXPECT_EQ(6, cached_parks.Size());
  EXPECT_EQ(9, cached_parks.Cursor());
}

TEST(TestParksActivation, TestCachedParksMissedRevision) {
  parks_activation::models::CachedParks cached_parks;
  using Revision = parks_activation::models::Revision;
  auto tp1 = utils::datetime::Stringtime("2019-02-28 21:00:00", "UTC",
                                         "%Y-%m-%d %H:%M:%S");
  ::cache::UpdateStatisticsScopeMock scope(::cache::UpdateType::kFull);
  ::utils::datetime::MockNowSet(tp1);
  cached_parks.UpsertItems({MakeTestItem(1, tp1), MakeTestItem(3, tp1)},
                           scope.GetScope(), std::chrono::seconds(1));
  auto expected_missed_revisions = std::unordered_set<Revision>{2};
  EXPECT_EQ(expected_missed_revisions, cached_parks.GetMissedRevisions());
}

TEST(TestParksActivation, TestCachedParksOldMissedRevision) {
  parks_activation::models::CachedParks cached_parks;
  using Revision = parks_activation::models::Revision;
  auto tp1 = utils::datetime::Stringtime("2019-02-28 21:00:00", "UTC",
                                         "%Y-%m-%d %H:%M:%S");
  auto ttl = std::chrono::seconds(10);
  ::cache::UpdateStatisticsScopeMock scope(::cache::UpdateType::kFull);
  ::utils::datetime::MockNowSet(tp1 + ttl + std::chrono::seconds(1));
  cached_parks.UpsertItems({MakeTestItem(100, tp1), MakeTestItem(300, tp1)},
                           scope.GetScope(), ttl);
  auto expected_missed_revisions = std::unordered_set<Revision>{};
  EXPECT_EQ(expected_missed_revisions, cached_parks.GetMissedRevisions());
}
