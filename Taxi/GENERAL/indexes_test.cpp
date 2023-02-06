#include <type_traits>

#include "place_indexes.hpp"
#include "zone_indexes.hpp"

#include <userver/utest/utest.hpp>

namespace eats_catalog_storage::indexes {

namespace {

template <typename Item>
Item CreateItem(int64_t id, int64_t revision_id) {
  Item item;
  item.id = id;
  item.revision_id = revision_id;
  if constexpr (std::is_same_v<Item, models::DeliveryZone>) {
    item.place_id = 0;
  }
  return item;
}

template <typename Item>
std::unordered_map<int64_t, Item> CreateItemCache(
    std::vector<std::pair<int64_t, int64_t>>&& id_revision) {
  std::unordered_map<int64_t, Item> cache;
  for (auto p : id_revision)
    cache.emplace(p.first, CreateItem<Item>(p.first, p.second));
  return cache;
}

template <typename Item, typename Index>
Index CreateIndexes(std::vector<std::pair<int64_t, int64_t>>&& id_revision) {
  auto cache_ptr = std::make_shared<const std::unordered_map<int64_t, Item>>(
      CreateItemCache<Item>(std::move(id_revision)));
  return Index(cache_ptr);
}

}  // namespace

template <typename T>
class IndexesTest : public ::testing::Test {};

struct ZonesTest {
  using DataType = models::DeliveryZone;
  using IndexType = ZoneIndexes;
};

struct PlacesTest {
  using DataType = models::PlaceCacheItem;
  using IndexType = PlaceIndexes;
};

using TestTypes = ::testing::Types<ZonesTest, PlacesTest>;
TYPED_TEST_SUITE(IndexesTest, TestTypes);

TYPED_TEST(IndexesTest, FindStartingWithRevisionId_EmptyCache) {
  RunInCoro([] {
    auto indexes = CreateIndexes<typename TypeParam::DataType,
                                 typename TypeParam::IndexType>({});
    auto result = indexes.FindStartingWithRevisionId(100, 10);
    ASSERT_TRUE(result.empty());
  });
}

TYPED_TEST(IndexesTest, FindStartingWithRevisionId_ZeroLimit) {
  RunInCoro([] {
    auto indexes = CreateIndexes<typename TypeParam::DataType,
                                 typename TypeParam::IndexType>({});
    auto result = indexes.FindStartingWithRevisionId(100, 0);
    ASSERT_TRUE(result.empty());
  });
}

TYPED_TEST(IndexesTest, FindStartingWithRevisionId_GreaterRevisionId) {
  RunInCoro([] {
    auto indexes =
        CreateIndexes<typename TypeParam::DataType,
                      typename TypeParam::IndexType>({{1, 10}, {2, 11}});
    auto result = indexes.FindStartingWithRevisionId(12, 10);
    ASSERT_TRUE(result.empty());
  });
}

TYPED_TEST(IndexesTest, FindStartingWithRevisionId_GetByLimit) {
  RunInCoro([] {
    std::vector<std::pair<int64_t, int64_t>> id_revision{
        {1, 10}, {2, 11}, {3, 13}};
    auto indexes =
        CreateIndexes<typename TypeParam::DataType,
                      typename TypeParam::IndexType>(std::move(id_revision));
    auto limit = 2;
    auto result = indexes.FindStartingWithRevisionId(1, limit);
    ASSERT_EQ(result.size(), limit);
    for (int i = 0; i < limit; i++) ASSERT_EQ(result[i], id_revision[i].first);
  });
}

TYPED_TEST(IndexesTest, FindStartingWithRevisionId_GetToLastRevision) {
  RunInCoro([] {
    std::vector<std::pair<int64_t, int64_t>> id_revision{
        {1, 10}, {2, 11}, {3, 13}};
    auto indexes =
        CreateIndexes<typename TypeParam::DataType,
                      typename TypeParam::IndexType>(std::move(id_revision));
    auto result = indexes.FindStartingWithRevisionId(11, 5);
    ASSERT_EQ(result.size(), 2);
    ASSERT_EQ(result[0], 2);
    ASSERT_EQ(result[1], 3);
  });
}

TYPED_TEST(IndexesTest, GetByRevisionId_NoExistRevisionId) {
  RunInCoro([] {
    auto indexes =
        CreateIndexes<typename TypeParam::DataType,
                      typename TypeParam::IndexType>({{1, 10}, {2, 11}});
    auto result = indexes.GetByRevisionId(12);
    ASSERT_FALSE(result.has_value());
  });
}

TYPED_TEST(IndexesTest, GetByRevisionId_ExistRevisionId) {
  RunInCoro([] {
    auto indexes =
        CreateIndexes<typename TypeParam::DataType,
                      typename TypeParam::IndexType>({{1, 10}, {2, 11}});
    auto result = indexes.GetByRevisionId(11);
    ASSERT_TRUE(result.has_value());
    ASSERT_EQ(result.value().id, 2);
  });
}

TYPED_TEST(IndexesTest, GetLastRevisionId_EmptyCache) {
  RunInCoro([] {
    auto indexes = CreateIndexes<typename TypeParam::DataType,
                                 typename TypeParam::IndexType>({});
    auto last_revision = indexes.GetLastRevisionId();
    ASSERT_EQ(last_revision, 0);
  });
}

TYPED_TEST(IndexesTest, GetLastRevisionId) {
  RunInCoro([] {
    auto indexes =
        CreateIndexes<typename TypeParam::DataType,
                      typename TypeParam::IndexType>({{1, 10}, {2, 11}});
    auto last_revision = indexes.GetLastRevisionId();
    ASSERT_EQ(last_revision, 11);
  });
}

}  // namespace eats_catalog_storage::indexes
