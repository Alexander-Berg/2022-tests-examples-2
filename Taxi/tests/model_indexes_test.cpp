#include <gtest/gtest.h>

#include <userver/utest/utest.hpp>

#include <api_base/bucket_locked_model_indexes.hpp>

formats::bson::Timestamp GetNextRevision(size_t& cur_increment) {
  ++cur_increment;
  return formats::bson::Timestamp(0, cur_increment);
}

struct IndexItem {
  IndexItem(const std::string& driver_id, const std::string& car_id,
            const std::string& license, formats::bson::Timestamp revision,
            bool is_deleted = false)
      : driver_id_(driver_id),
        car_id_(car_id),
        license_(license),
        revision_(revision),
        is_deleted_(is_deleted) {}

  std::string GetId() const { return driver_id_; }

  bool IsDeleted() const { return is_deleted_; }

  formats::bson::Timestamp GetTimestamp() const { return revision_; }

  std::string driver_id_;
  std::string car_id_;
  std::string license_;
  formats::bson::Timestamp revision_;
  const bool is_deleted_;
};

UTEST(PrimaryIndex, TestPrimaryIndex) {
  api_over_db::PrimaryIndex<IndexItem, formats::bson::Timestamp, 10> index;
  size_t increment = 0;

  auto driver1 = std::make_shared<const IndexItem>("id1", "car1", "license1",
                                                   GetNextRevision(increment));
  index.Upsert(driver1);
  ASSERT_EQ(index.Size(), 1);
  ASSERT_NE(index.Get(driver1->GetId()), nullptr);
  ASSERT_EQ(index.GetLastTimestamp(), formats::bson::Timestamp(0, 1));

  auto updated_driver = std::make_shared<const IndexItem>(
      "id1", "car42", "license1", GetNextRevision(increment));
  index.Upsert(updated_driver);
  ASSERT_EQ(index.Size(), 1);
  ASSERT_NE(index.Get(driver1->GetId()), nullptr);
  ASSERT_EQ(index.Get(driver1->GetId())->car_id_, "car42");
  ASSERT_EQ(index.GetLastTimestamp(), formats::bson::Timestamp(0, 2));

  index.Upsert(driver1);
  ASSERT_EQ(index.Size(), 1);

  auto driver2 = std::make_shared<const IndexItem>("id2", "car2", "license1",
                                                   GetNextRevision(increment));
  index.Upsert(driver2);
  ASSERT_EQ(index.Size(), 2);
  ASSERT_NE(index.Get(driver2->GetId()), nullptr);
  ASSERT_EQ(index.GetLastTimestamp(), formats::bson::Timestamp(0, 3));

  ASSERT_EQ(index.Erase(driver2->GetId()), true);
  ASSERT_EQ(index.Size(), 1);
  ASSERT_EQ(index.Get(driver2->GetId()), nullptr);

  ASSERT_EQ(index.Erase(driver1->GetId()), true);
  ASSERT_EQ(index.Size(), 0);
  ASSERT_EQ(index.Get(driver1->GetId()), nullptr);
}

struct IndexParameters {
  const size_t elements_count;
  const size_t limit;
};

bool CheckOrder(
    const std::map<formats::bson::Timestamp,
                   std::pair<std::shared_ptr<const IndexItem>, size_t>>&
        items) {
  if (items.empty()) return true;
  auto it = items.begin();
  ++it;
  for (; it != items.end(); ++it) {
    auto anothe_it = it;
    --anothe_it;
    if (it->second.first->GetTimestamp() <=
        anothe_it->second.first->GetTimestamp())
      return false;
  }
  return true;
}

TEST(PrimaryIndex, TestBuildItemsMapByTimestamp) {
  std::vector<IndexParameters> tests{
      {10, 5}, {5, 10}, {20, 10}, {20, 20}, {50, 5}};

  // 1 bucket
  for (const auto& test : tests) {
    api_over_db::PrimaryIndex<IndexItem, formats::bson::Timestamp, 1> index;

    RunInCoro([&test, &index] {
      size_t increment = 0;

      for (size_t i = 0; i < test.elements_count; ++i) {
        auto driver = std::make_shared<const IndexItem>(
            "id" + std::to_string(i), "car", "license",
            GetNextRevision(increment));
        index.Upsert(driver);
      }

      ASSERT_EQ(index.Size(), test.elements_count);
      auto resp1 = index.BuildItemsMapByTimestamp(
          formats::bson::Timestamp(0, 0), formats::bson::Timestamp(0, 100),
          test.limit);
      ASSERT_EQ(resp1.size(), std::min(test.limit, test.elements_count));
      ASSERT_EQ(CheckOrder(resp1), true);

      auto resp2 = index.BuildItemsMapByTimestamp(
          formats::bson::Timestamp(0, test.elements_count - 1),
          formats::bson::Timestamp(0, 100), test.limit);
      ASSERT_EQ(resp2.size(), 1);
      ASSERT_EQ(CheckOrder(resp2), true);

      auto resp3 = index.BuildItemsMapByTimestamp(
          formats::bson::Timestamp(0, 2), formats::bson::Timestamp(0, 100),
          test.limit);
      ASSERT_EQ(resp3.size(), std::min(test.limit, test.elements_count - 2));
      const auto& element = resp3.begin()->second.first;
      ASSERT_EQ(element->GetTimestamp(), formats::bson::Timestamp(0, 3));
      ASSERT_EQ(CheckOrder(resp3), true);

      auto resp4 = index.BuildItemsMapByTimestamp(
          formats::bson::Timestamp(0, 3), formats::bson::Timestamp(0, 4),
          test.limit);
      ASSERT_EQ(resp4.size(), 1);
    });
  }

  // 5 buckets
  for (const auto& test : tests) {
    api_over_db::PrimaryIndex<IndexItem, formats::bson::Timestamp, 5> index;

    RunInCoro([&test, &index] {
      size_t increment = 0;

      for (size_t i = 0; i < test.elements_count; ++i) {
        auto driver = std::make_shared<const IndexItem>(
            "id" + std::to_string(i), "car", "license",
            GetNextRevision(increment));
        index.Upsert(driver);
      }

      ASSERT_EQ(index.Size(), test.elements_count);
      auto resp1 = index.BuildItemsMapByTimestamp(
          formats::bson::Timestamp(0, 0), formats::bson::Timestamp(0, 100),
          test.limit);
      ASSERT_EQ(resp1.size(), std::min(test.limit, test.elements_count));
      ASSERT_EQ(CheckOrder(resp1), true);

      auto resp2 = index.BuildItemsMapByTimestamp(
          formats::bson::Timestamp(0, test.elements_count - 1),
          formats::bson::Timestamp(0, 100), test.limit);
      ASSERT_EQ(resp2.size(), 1);
      ASSERT_EQ(CheckOrder(resp2), true);

      auto resp3 = index.BuildItemsMapByTimestamp(
          formats::bson::Timestamp(0, 2), formats::bson::Timestamp(0, 100),
          test.limit);
      ASSERT_EQ(resp3.size(), std::min(test.limit, test.elements_count - 2));
      const auto& element = resp3.begin()->second.first;
      ASSERT_EQ(element->GetTimestamp(), formats::bson::Timestamp(0, 3));
      ASSERT_EQ(CheckOrder(resp3), true);

      auto resp4 = index.BuildItemsMapByTimestamp(
          formats::bson::Timestamp(0, 3), formats::bson::Timestamp(0, 4),
          test.limit);
      ASSERT_EQ(resp4.size(), 1);
    });
  }

  // Check left > right
  {
    api_over_db::PrimaryIndex<IndexItem, formats::bson::Timestamp, 5> index;
    RunInCoro([&index] {
      size_t increment = 0;

      for (size_t i = 0; i < 5; ++i) {
        auto driver = std::make_shared<const IndexItem>(
            "id" + std::to_string(i), "car", "license",
            GetNextRevision(increment));
        index.Upsert(driver);
      }

      ASSERT_EQ(index.Size(), 5);
      auto resp1 = index.BuildItemsMapByTimestamp(
          formats::bson::Timestamp(0, 100), formats::bson::Timestamp(0, 0), 10);
      ASSERT_EQ(resp1.size(), 0);
    });
  }
}

UTEST(PrimaryIndex, TestEraseDeletedOlderThan) {
  api_over_db::PrimaryIndex<IndexItem, formats::bson::Timestamp, 10> index;
  size_t increment = 0;

  auto driver1 = std::make_shared<const IndexItem>(
      "id1", "car1", "license1", GetNextRevision(increment), true);
  auto driver2 = std::make_shared<const IndexItem>(
      "id2", "car1", "license2", GetNextRevision(increment), true);
  auto driver3 = std::make_shared<const IndexItem>(
      "id3", "car1", "license3", GetNextRevision(increment), true);
  auto driver4 = std::make_shared<const IndexItem>(
      "id4", "car1", "license4", GetNextRevision(increment), true);
  index.Upsert(driver1);
  index.Upsert(driver2);
  index.Upsert(driver3);
  index.Upsert(driver4);
  ASSERT_EQ(index.Size(), 4);

  auto deleted = index.EraseDeletedOlderThan(formats::bson::Timestamp(0, 3));
  ASSERT_EQ(deleted.size(), 2);
  ASSERT_EQ(index.Size(), 2);
  auto res = index.Get(driver4->GetId());
  ASSERT_NE(res, nullptr);
  ASSERT_EQ(index.Get(driver2->GetId()), nullptr);
}

UTEST(SecondaryIndex, TestSecondaryIndex) {
  api_over_db::SecondaryIndex<IndexItem, formats::bson::Timestamp, 10> index;
  size_t increment = 0;

  auto driver1 = std::make_shared<const IndexItem>("id1", "car1", "license1",
                                                   GetNextRevision(increment));
  index.Upsert(driver1->car_id_, driver1);
  ASSERT_EQ(index.Size(), 1);
  ASSERT_EQ(index.Count(driver1->car_id_), 1);
  auto result1 = index.Get(driver1->car_id_);
  ASSERT_TRUE(result1);
  ASSERT_EQ(result1->size(), 1);

  driver1 = std::make_shared<const IndexItem>("id1", "car1", "license2",
                                              GetNextRevision(increment));
  index.Upsert(driver1->car_id_, driver1);
  ASSERT_EQ(index.Size(), 1);
  auto update_result = index.Get(driver1->car_id_);
  ASSERT_TRUE(update_result);
  ASSERT_EQ(update_result->size(), 1);
  ASSERT_EQ(update_result->at("id1")->license_, "license2");

  auto driver2 = std::make_shared<const IndexItem>("id2", "car1", "license1",
                                                   GetNextRevision(increment));
  index.Upsert(driver2->car_id_, driver2);
  ASSERT_EQ(index.Size(), 2);
  ASSERT_EQ(index.Count(driver2->car_id_), 2);
  auto result2 = index.Get(driver2->car_id_);
  ASSERT_TRUE(result2);
  ASSERT_EQ(result2->size(), 2);

  ASSERT_EQ(index.Erase(driver2->car_id_, driver2->driver_id_), true);
  ASSERT_EQ(index.Size(), 1);

  ASSERT_EQ(index.Erase(driver1->car_id_, driver1->driver_id_), true);
  ASSERT_EQ(index.Size(), 0);

  auto result3 = index.Get(driver2->car_id_);
  ASSERT_FALSE(result3);
  ASSERT_EQ(index.Count(driver2->car_id_), 0);
}
