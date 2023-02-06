#include <gtest/gtest.h>
#include <functional>
#include <optional>
#include <set>
#include <string>
#include <unordered_set>

#include "api_base/model.hpp"
#include "api_base/utils.hpp"

#include <iostream>

namespace {
struct TestModelItem {
  std::string id;
  bool is_deleted{false};
  formats::bson::Timestamp mongo_timestamp;
  std::optional<std::string> field;

  using IdType = std::string;

  TestModelItem() = default;

  TestModelItem(const std::string& id, bool deleted,
                formats::bson::Timestamp ts,
                std::optional<std::string> field = std::nullopt)
      : id(id), is_deleted(deleted), mongo_timestamp(ts), field(field) {}

  void Save(std::ofstream&) {}
  void Load(std::ifstream&) {}

  formats::bson::Timestamp GetTimestamp() const { return mongo_timestamp; }
  IdType GetId() const { return id; }
  bool IsDeleted() const { return is_deleted; }

  bool operator==(const TestModelItem& other) const {
    return id == other.id && is_deleted == other.is_deleted &&
           mongo_timestamp == other.mongo_timestamp && field == other.field;
  }

  bool operator!=(const TestModelItem& other) const {
    return !(*this == other);
  }
};

struct TestCacheModelTraits {
  static constexpr const char* kLogPrefix = "test-cache : ";
  using ItemType = TestModelItem;
  using Timestamp = formats::bson::Timestamp;
  enum class IndicesEnum { kField, kCount };
  static const std::vector<
      std::function<std::set<std::optional<std::string>>(const ItemType& item)>>
      kKeysByIndex;
  static constexpr bool kEraseDeleted = false;
};

std::set<std::optional<std::string>> GetKeysForFieldIndex(
    const TestCacheModelTraits::ItemType& item) {
  std::set<std::optional<std::string>> result;
  result.insert(item.field);
  return result;
}

const std::vector<std::function<std::set<std::optional<std::string>>(
    const TestCacheModelTraits::ItemType& item)>>
    TestCacheModelTraits::kKeysByIndex{&GetKeysForFieldIndex};

using TestCacheModel = api_over_db::CacheModel<TestCacheModelTraits>;
using IndicesEnum = TestCacheModelTraits::IndicesEnum;

void TestIndexItems(const TestCacheModel::Index& index,
                    std::optional<std::string> key,
                    std::unordered_set<std::string> expected_ids) {
  std::unordered_set<std::string> ids;
  auto value = index.Get(key);
  ASSERT_TRUE(bool(value));
  for (auto it = value->begin(); it != value->end(); ++it) {
    ids.insert(it->second->GetId());
  }
  EXPECT_EQ(expected_ids, ids);
}
}  // namespace

TEST(ApiOverDbCacheModel, CacheInsertions) {
  TestCacheModel cache;
  {
    // first insert
    auto timestamp = formats::bson::Timestamp{0, 1};
    auto test_item = TestModelItem("testId1", false, timestamp, std::nullopt);

    EXPECT_TRUE(cache.Upsert(std::make_shared<TestModelItem>(test_item)));
    EXPECT_EQ((*cache.GetItemsById().at("testId1")), test_item);
    EXPECT_EQ((*cache.GetItemsByTimestamp().at(timestamp)), test_item);
    EXPECT_EQ(1u, cache.GetItemsByIndex<IndicesEnum::kField>().Size());
    EXPECT_EQ(1u,
              cache.GetItemsByIndex<IndicesEnum::kField>().Count(std::nullopt));
    TestIndexItems(cache.GetItemsByIndex<IndicesEnum::kField>(), std::nullopt,
                   {"testId1"});
  }
  {
    // insert same updated document
    auto timestamp = formats::bson::Timestamp{2, 1};
    auto test_item = TestModelItem("testId1", false, timestamp,
                                   std::string("new_field_value"));
    EXPECT_TRUE(cache.Upsert(std::make_shared<TestModelItem>(test_item)));
    EXPECT_EQ(cache.GetItemsById().size(), 1);
    EXPECT_EQ(cache.GetItemsByTimestamp().size(), 1);
    EXPECT_EQ((*cache.GetItemsById().at("testId1")), test_item);
    EXPECT_EQ((*cache.GetItemsByTimestamp().at(formats::bson::Timestamp{2, 1})),
              test_item);
    EXPECT_EQ(1u, cache.GetItemsByIndex<IndicesEnum::kField>().Size());
    EXPECT_EQ(1u, cache.GetItemsByIndex<IndicesEnum::kField>().Count(
                      std::string("new_field_value")));
    TestIndexItems(cache.GetItemsByIndex<IndicesEnum::kField>(),
                   std::string("new_field_value"), {"testId1"});
  }
  {
    // insert new document
    auto test_item_old =
        TestModelItem("testId1", false, formats::bson::Timestamp{2, 1},
                      std::string("new_field_value"));
    auto test_item_new =
        TestModelItem("testId2", false, formats::bson::Timestamp{3, 1},
                      std::string("new_field_value"));
    EXPECT_TRUE(cache.Upsert(std::make_shared<TestModelItem>(test_item_new)));
    EXPECT_EQ(cache.GetItemsById().size(), 2);
    EXPECT_EQ(cache.GetItemsByTimestamp().size(), 2);
    // check id1
    EXPECT_EQ((*cache.GetItemsById().at("testId1")), test_item_old);
    EXPECT_EQ((*cache.GetItemsByTimestamp().at(formats::bson::Timestamp{2, 1})),
              test_item_old);
    // check id2
    EXPECT_EQ((*cache.GetItemsById().at("testId2")), test_item_new);
    EXPECT_EQ((*cache.GetItemsByTimestamp().at(formats::bson::Timestamp{3, 1})),
              test_item_new);
    EXPECT_EQ(2u, cache.GetItemsByIndex<IndicesEnum::kField>().Size());
    EXPECT_EQ(2u, cache.GetItemsByIndex<IndicesEnum::kField>().Count(
                      std::string("new_field_value")));

    auto test_item_new_3 =
        TestModelItem("testId3", false, formats::bson::Timestamp{4, 1},
                      std::string("new_field_value_3"));
    EXPECT_TRUE(cache.Upsert(std::make_shared<TestModelItem>(test_item_new_3)));
    EXPECT_EQ(3u, cache.GetItemsByIndex<IndicesEnum::kField>().Size());
    EXPECT_EQ(2u, cache.GetItemsByIndex<IndicesEnum::kField>().Count(
                      std::string("new_field_value")));
    TestIndexItems(cache.GetItemsByIndex<IndicesEnum::kField>(),
                   std::string("new_field_value"), {"testId1", "testId2"});
    EXPECT_EQ(1u, cache.GetItemsByIndex<IndicesEnum::kField>().Count(
                      std::string("new_field_value_3")));
    TestIndexItems(cache.GetItemsByIndex<IndicesEnum::kField>(),
                   std::string("new_field_value_3"), {"testId3"});

    auto test_item_new_3_deleted =
        TestModelItem("testId3", true, formats::bson::Timestamp{5, 1},
                      std::string("new_field_value_3"));
    EXPECT_TRUE(
        cache.Upsert(std::make_shared<TestModelItem>(test_item_new_3_deleted)));
  }
}

TEST(ApiOverDbCacheModel, CacheDeletions) {
  TestCacheModel cache;
  for (uint32_t i = 1; i < 20; ++i) {
    cache.Upsert(std::make_shared<TestModelItem>(
        std::to_string(i), (i % 19 ? true : false),
        formats::bson::Timestamp{i, 1}, "field_" + std::to_string(i)));
  }
  EXPECT_EQ(cache.GetItemsById().size(), 19);
  EXPECT_EQ(cache.GetItemsByTimestamp().size(), 19);
  cache.EraseDeletedOlderThan(formats::bson::Timestamp{20, 1});
  EXPECT_EQ(cache.GetItemsById().size(), 1);
  EXPECT_EQ(cache.GetItemsByTimestamp().size(), 1);
  auto test_item = TestModelItem("19", false, formats::bson::Timestamp{19, 1},
                                 std::string("field_19"));
  EXPECT_EQ((*cache.GetItemsById().begin()->second.get()), test_item);
  EXPECT_EQ((*cache.GetItemsByTimestamp().begin()->second.get()), test_item);
  EXPECT_EQ(1u, cache.GetItemsByIndex<IndicesEnum::kField>().Size());
  TestIndexItems(cache.GetItemsByIndex<IndicesEnum::kField>(),
                 std::string("field_19"), {"19"});
}

TEST(ApiOverDbCacheModel, CacheUpdateDeleted) {
  TestCacheModel cache;
  for (uint32_t i = 1; i < 4; ++i) {
    cache.Upsert(std::make_shared<TestModelItem>(
        std::to_string(i), (i % 3 ? true : false),
        formats::bson::Timestamp{i, 1}));
  }
  EXPECT_FALSE(cache.Upsert(std::make_shared<TestModelItem>(
      "1", false, formats::bson::Timestamp{4, 1})));
  EXPECT_FALSE(cache.Upsert(std::make_shared<TestModelItem>(
      "2", false, formats::bson::Timestamp{5, 1})));
  EXPECT_TRUE(cache.Upsert(std::make_shared<TestModelItem>(
      "3", true, formats::bson::Timestamp{6, 1})));
}

namespace {
struct TestClientCacheModelTraits {
  static constexpr const char* kLogPrefix = "test-cache : ";
  using ItemType = TestModelItem;
  using Timestamp = formats::bson::Timestamp;
  enum class IndicesEnum { kField, kCount };
  static const std::vector<
      std::function<std::set<std::optional<std::string>>(const ItemType& item)>>
      kKeysByIndex;
  static constexpr bool kEraseDeleted = true;
};

std::set<std::optional<std::string>> GetClientKeysForFieldIndex(
    const TestClientCacheModelTraits::ItemType& item) {
  std::set<std::optional<std::string>> result;
  result.insert(item.field);
  return result;
}

const std::vector<std::function<std::set<std::optional<std::string>>(
    const TestClientCacheModelTraits::ItemType& item)>>
    TestClientCacheModelTraits::kKeysByIndex{&GetClientKeysForFieldIndex};

using TestClientCacheModel =
    api_over_db::CacheModel<TestClientCacheModelTraits>;
using ClientIndicesEnum = TestClientCacheModelTraits::IndicesEnum;
}  // namespace

TEST(ApiOverDbCacheModel, ClientCacheUpdateDeleted) {
  TestClientCacheModel cache;
  EXPECT_TRUE(cache.Upsert(std::make_shared<TestModelItem>(
      "testId1", false, formats::bson::Timestamp{0, 1},
      std::string("field_value_1"))));

  EXPECT_EQ(1u, cache.Size());
  EXPECT_EQ(1u, cache.GetItemsByIndex<ClientIndicesEnum::kField>().Size());

  EXPECT_TRUE(cache.Upsert(std::make_shared<TestModelItem>(
      "testId1", true, formats::bson::Timestamp{1, 1},
      std::string("field_value_2"))));

  EXPECT_EQ(0u, cache.Size());
  EXPECT_EQ(0u, cache.GetItemsByIndex<ClientIndicesEnum::kField>().Size());
}

TEST(ApiOverDbCacheModel, IndexTest) {
  api_over_db::Index<TestModelItem> index;
  auto index_key_1 = std::nullopt;
  auto index_key_23 = std::string("index_key");
  auto test_item_1 = std::make_shared<TestModelItem>(
      "testId1", false, formats::bson::Timestamp{2, 1}, std::nullopt);
  auto test_item_2 = std::make_shared<TestModelItem>(
      "testId2", false, formats::bson::Timestamp{2, 1}, index_key_23);
  auto test_item_3 = std::make_shared<TestModelItem>(
      "testId3", false, formats::bson::Timestamp{2, 1}, index_key_23);

  EXPECT_TRUE(index.Add(index_key_1, test_item_1));
  EXPECT_EQ(1u, index.Size());
  EXPECT_EQ(1u, index.Count(index_key_1));
  TestIndexItems(index, index_key_1, {"testId1"});

  EXPECT_FALSE(index.Add(index_key_1, test_item_1));
  EXPECT_EQ(1u, index.Size());
  EXPECT_EQ(1u, index.Count(index_key_1));
  TestIndexItems(index, index_key_1, {"testId1"});

  EXPECT_TRUE(index.Add(index_key_23, test_item_2));
  EXPECT_EQ(2u, index.Size());
  EXPECT_EQ(1u, index.Count(index_key_1));
  EXPECT_EQ(1u, index.Count(index_key_23));
  TestIndexItems(index, index_key_1, {"testId1"});
  TestIndexItems(index, index_key_23, {"testId2"});

  EXPECT_TRUE(index.Add(index_key_23, test_item_3));
  EXPECT_EQ(3u, index.Size());
  EXPECT_EQ(1u, index.Count(index_key_1));
  EXPECT_EQ(2u, index.Count(index_key_23));
  TestIndexItems(index, index_key_1, {"testId1"});
  TestIndexItems(index, index_key_23, {"testId2", "testId3"});

  EXPECT_TRUE(index.Erase(index_key_23, "testId3"));
  EXPECT_EQ(2u, index.Size());
  EXPECT_EQ(1u, index.Count(index_key_1));
  EXPECT_EQ(1u, index.Count(index_key_23));
  TestIndexItems(index, index_key_1, {"testId1"});
  TestIndexItems(index, index_key_23, {"testId2"});

  EXPECT_TRUE(index.Erase(index_key_1, "testId1"));
  EXPECT_EQ(1u, index.Size());
  EXPECT_EQ(0u, index.Count(index_key_1));
  EXPECT_EQ(1u, index.Count(index_key_23));
  EXPECT_FALSE(bool(index.Get(index_key_1)));
  TestIndexItems(index, index_key_23, {"testId2"});

  EXPECT_FALSE(index.Erase(index_key_1, "testId1"));
  EXPECT_EQ(1u, index.Size());
  EXPECT_EQ(0u, index.Count(index_key_1));
  EXPECT_EQ(1u, index.Count(index_key_23));
  EXPECT_FALSE(bool(index.Get(index_key_1)));
  TestIndexItems(index, index_key_23, {"testId2"});
}
