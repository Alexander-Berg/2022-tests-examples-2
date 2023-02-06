#include <gtest/gtest.h>

#include <search_rules/response_rules/items_availability_rule/items_preview_batcher.hpp>

namespace eats_full_text_search {

namespace search_rules::response_rules::items_availability_rule {

namespace tests {

namespace {

ItemPreviewBatcher::PlacesItemsRequest MakeRequest(size_t places_num,
                                                   size_t items_num) {
  ItemPreviewBatcher::PlacesItemsRequest result;
  for (size_t i = 0; i < places_num; i++) {
    auto& place = result.emplace_back();
    place.place_id = fmt::format("place_{}", i);
    for (size_t j = 0; j < items_num; j++) {
      place.items.push_back(fmt::format("item_{}_{}", i, j));
    }
  }
  return result;
}

}  // namespace

TEST(ItemPreviewBatcher, Empty) {
  ItemPreviewBatcher batcher{{}, 10};
  ASSERT_FALSE(batcher.HasMore());
  // Вызов Next при HasMore() == false не должен приводить к UB
  ASSERT_TRUE(batcher.Next().empty());
}

TEST(ItemPreviewBatcher, OneBatch) {
  constexpr static size_t kPlacesSize = 10;
  constexpr static size_t kItemsSize = 100;
  constexpr static size_t kBatchSize = 1000;

  ItemPreviewBatcher batcher{MakeRequest(kPlacesSize, kItemsSize), kBatchSize};
  ASSERT_TRUE(batcher.HasMore());

  auto batch = batcher.Next();
  ASSERT_EQ(batch.size(), kPlacesSize);
  for (const auto& items : batch) {
    ASSERT_EQ(items.items.size(), kItemsSize);
  }
}

TEST(ItemPreviewBatcher, ManyBatches) {
  constexpr static size_t kPlacesSize = 4;
  constexpr static size_t kItemsSize = 10;
  constexpr static size_t kBatchSize = 15;

  ItemPreviewBatcher batcher{MakeRequest(kPlacesSize, kItemsSize), kBatchSize};

  // Первый батч 2 реста, в первом 15, во втором 5
  {
    ASSERT_TRUE(batcher.HasMore());
    auto batch = batcher.Next();
    ASSERT_EQ(batch.size(), 2);
    auto first = batch.front();
    ASSERT_EQ(first.place_id, "place_0");
    ASSERT_EQ(first.items.size(), 10);
    auto second = batch.back();
    ASSERT_EQ(second.place_id, "place_1");
    ASSERT_EQ(second.items.size(), 5);
  }

  // Второй батч 2 реста, в первом 5 (остаток с предыдущего), во втором 10
  {
    ASSERT_TRUE(batcher.HasMore());
    auto batch = batcher.Next();
    ASSERT_EQ(batch.size(), 2);
    auto first = batch.front();
    ASSERT_EQ(first.place_id, "place_1");
    ASSERT_EQ(first.items.size(), 5);
    auto second = batch.back();
    ASSERT_EQ(second.place_id, "place_2");
    ASSERT_EQ(second.items.size(), 10);
  }

  // Третий батч 1 рест, все 10 айтемов
  {
    ASSERT_TRUE(batcher.HasMore());
    auto batch = batcher.Next();
    ASSERT_EQ(batch.size(), 1);
    auto first = batch.front();
    ASSERT_EQ(first.place_id, "place_3");
    ASSERT_EQ(first.items.size(), 10);
  }

  // Больше батчей нет
  ASSERT_FALSE(batcher.HasMore());
}

}  // namespace tests
}  // namespace search_rules::response_rules::items_availability_rule
}  // namespace eats_full_text_search
