#include <gtest/gtest.h>

#include <userver/utils/text.hpp>

#include <eats-adverts-goods/auction/adverts_auction.hpp>
#include <eats-adverts-goods/models/adverts.hpp>
#include <eats-adverts-goods/utils/tests.hpp>

namespace eats_adverts_goods::auction {

namespace {

/// @brief абстрактный товар/блюдо для тестирования сортировки аукционом
using ItemId =
    ::utils::StrongTypedef<class ItemIdTag, std::string,
                           ::utils::StrongTypedefOps::kCompareStrong>;
struct Item {
  ItemId item_id{};
  bool is_promo{};
};

bool operator==(const Item& lhs, const Item& rhs) {
  return lhs.item_id == rhs.item_id && lhs.is_promo == rhs.is_promo;
}

log::AuctionContext GetEmptyContext() {
  return log::AuctionContext{
      nullptr,  // logger_ptr
      false,    // is_logging_enabled
      false,    // is_tracing_enabled
      {},       // tags
  };
}

std::vector<Item> BuildItems(const size_t count) {
  std::vector<Item> items{};
  items.reserve(count);
  for (size_t i = 1; i <= count; i++) {
    items.push_back(Item{
        ItemId{std::to_string(i)},  // item_id
        false,                      // is_Advert
    });
  }
  return items;
}

std::vector<Item> BuildItems(const std::vector<int> item_ids) {
  std::vector<Item> items{};
  items.reserve(item_ids.size());
  for (const auto& id : item_ids) {
    items.push_back(Item{
        ItemId{std::to_string(id)},  // item_id
        false,                       // is_Advert
    });
  }
  return items;
}

std::vector<Item> BuildItems(
    const std::vector<std::pair<int, bool>>& ids_and_adverts) {
  std::vector<Item> items{};
  items.reserve(ids_and_adverts.size());
  for (const auto& [id, is_advert] : ids_and_adverts) {
    items.push_back(Item{
        ItemId{std::to_string(id)},  // item_id
        is_advert,                   // is_Advert
    });
  }
  return items;
}

std::string ItemsToString(const std::vector<Item>& items) {
  std::vector<std::string> string_items{};
  string_items.reserve(items.size());
  std::transform(items.begin(), items.end(), std::back_inserter(string_items),
                 [](const auto& item) {
                   std::stringstream ss{};
                   ss << "{id:" << item.item_id.GetUnderlying()
                      << ", is_promo:" << (item.is_promo ? "true" : "false")
                      << "}";
                   return ss.str();
                 });
  return ::utils::text::Join(string_items, " ");
}

struct TestAuctionSortCase final {
  std::string name{};
  std::vector<Item> items{};
  std::vector<ItemId> promoted_items_ids{};
  std::vector<size_t> promo_positions{};
  std::vector<Item> expected_items{};
};

struct TestAuctionMarkPromoCase final {
  std::string name{};
  std::vector<Item> items{};
  std::vector<ItemId> promoted_items_ids{};
  std::vector<Item> expected_items{};
};

}  // namespace

class TestAuctionSort : public ::testing::TestWithParam<TestAuctionSortCase> {};

TEST_P(TestAuctionSort, Test) {
  auto param = GetParam();

  Auction<ItemId> auction(std::move(param.promoted_items_ids),
                          param.promo_positions, GetEmptyContext());
  auction.SortItems<Item>(param.items,
                          [](const auto& item) { return item.item_id; });

  ASSERT_EQ(param.expected_items, param.items)
      << "[" << param.name
      << "] expected: " << ItemsToString(param.expected_items)
      << "; actual: " << ItemsToString(param.items) << ".";
}

std::vector<TestAuctionSortCase> MakeTestAuctionSortCases();

INSTANTIATE_TEST_SUITE_P(AdvertsAuction, TestAuctionSort,
                         ::testing::ValuesIn(MakeTestAuctionSortCases()),
                         [](const auto& test_case) -> std::string {
                           return utils::tests::GetName(test_case.param);
                         });

std::vector<TestAuctionSortCase> MakeTestAuctionSortCases() {
  return std::vector<TestAuctionSortCase>{
      TestAuctionSortCase{
          "sort no promos",             // name
          BuildItems(5),                // items
          {},                           // promoted_items_ids
          {},                           // promo_positions
          BuildItems({1, 2, 3, 4, 5}),  // expected_items
      },
      TestAuctionSortCase{
          "sort with promos",           // name
          BuildItems(5),                // items
          {ItemId{"4"}, ItemId{"5"}},   // promoted_items_ids
          {},                           // promo_positions
          BuildItems({4, 5, 1, 2, 3}),  // expected_items
      },
      TestAuctionSortCase{
          "sort with organically placed promos",  // name
          BuildItems(5),                          // items
          {ItemId{"1"}, ItemId{"3"}},             // promoted_items_ids
          {},                                     // promo_positions
          BuildItems({1, 3, 2, 4, 5}),            // expected_items
      },
      TestAuctionSortCase{
          "sort with positions",        // name
          BuildItems(5),                // items
          {ItemId{"4"}, ItemId{"5"}},   // promoted_items_ids
          {0, 2},                       // promo_positions
          BuildItems({4, 1, 5, 2, 3}),  // expected_items
      },
      TestAuctionSortCase{
          "sort with mixed positions",              // name
          BuildItems(5),                            // items
          {ItemId{"3"}, ItemId{"4"}, ItemId{"5"}},  // promoted_items_ids
          {4, 0, 2},                                // promo_positions
          BuildItems({3, 1, 4, 2, 5}),              // expected_items
      },
      TestAuctionSortCase{
          "sort with less positions than promos",  // name
          BuildItems(5),                           // items
          {ItemId{"4"}, ItemId{"5"}},              // promoted_items_ids
          {0},                                     // promo_positions
          BuildItems({4, 1, 2, 3, 5}),             // expected_items
      },
      TestAuctionSortCase{
          "sort with less promos than positions",  // name
          BuildItems(5),                           // items
          {ItemId{"4"}},                           // promoted_items_ids
          {0, 2, 4},                               // promo_positions
          BuildItems({4, 1, 2, 3, 5}),             // expected_items
      },
      TestAuctionSortCase{
          "sort with positions and "
          "organically placed promos",  // name
          BuildItems(5),                // items
          {ItemId{"1"}, ItemId{"2"}},   // promoted_items_ids
          {0, 2},                       // promo_positions
          BuildItems({1, 2, 3, 4, 5}),  // expected_items
      },
      TestAuctionSortCase{
          "sort with positions further "
          "than organically placed promos",  // name
          BuildItems(5),                     // items
          {ItemId{"1"}},                     // promoted_items_ids
          {4},                               // promo_positions
          BuildItems({1, 2, 3, 4, 5}),       // expected_items
      },
      TestAuctionSortCase{
          "sort with extra promo items",              // name
          BuildItems({2, 3, 4, 5}),                   // items
          {ItemId{"1"}, ItemId{"5"}, {ItemId{"6"}}},  // promoted_items_ids
          {},                                         // promo_positions
          BuildItems({5, 2, 3, 4}),                   // expected_items
      },
      TestAuctionSortCase{
          "sort with extra promo items "
          "and positions",                          // name
          BuildItems({2, 3, 4, 5}),                 // items
          {ItemId{"1"}, ItemId{"5"}, ItemId{"6"}},  // promoted_items_ids
          {1, 2},                                   // promo_positions
          BuildItems({2, 5, 3, 4}),                 // expected_items
      },
  };
}

class TestAuctionMarkPromo
    : public ::testing::TestWithParam<TestAuctionMarkPromoCase> {};

TEST_P(TestAuctionMarkPromo, Test) {
  auto param = GetParam();

  Auction<ItemId> auction(std::move(param.promoted_items_ids),
                          /*promo_positions*/ {}, GetEmptyContext());
  const auto to_item_id = [](const auto& item) { return item.item_id; };
  const auto mark_promo = [](auto& item, bool is_promo) {
    item.is_promo = is_promo;
  };
  auction.SortItems<Item>(param.items, to_item_id, mark_promo);

  ASSERT_EQ(param.expected_items, param.items)
      << "[" << param.name
      << "] expected: " << ItemsToString(param.expected_items)
      << "; actual: " << ItemsToString(param.items) << ".";
}

std::vector<TestAuctionMarkPromoCase> MakeTestAuctionMarkPromoCases();

INSTANTIATE_TEST_SUITE_P(AdvertsAuction, TestAuctionMarkPromo,
                         ::testing::ValuesIn(MakeTestAuctionMarkPromoCases()),
                         [](const auto& test_case) -> std::string {
                           return utils::tests::GetName(test_case.param);
                         });

std::vector<TestAuctionMarkPromoCase> MakeTestAuctionMarkPromoCases() {
  return std::vector<TestAuctionMarkPromoCase>{
      TestAuctionMarkPromoCase{
          "no promos",    // name
          BuildItems(3),  // items
          {},             // promoted_items_ids
          BuildItems({
              {1, false},
              {2, false},
              {3, false},
          }),  // expected_items
      },
      TestAuctionMarkPromoCase{
          "with promos",               // name
          BuildItems(3),               // items
          {ItemId{"1"}, ItemId{"3"}},  // promoted_items_ids
          BuildItems({
              {1, true},
              {3, true},
              {2, false},
          }),  // expected_items
      },
  };
}

}  // namespace eats_adverts_goods::auction
