#include "orders_restriction.hpp"

#include <defs/all_definitions.hpp>
#include <userver/utest/utest.hpp>

UTEST(OrdersRestriction, Size) {
  std::vector<handlers::libraries::discounts_match::OrdersRestriction> items{
      {{0, 5}, "android", "card"}};

  models::OrdersRestriction orders_restriction(items);
  EXPECT_EQ(orders_restriction.GetSize(), 1);
}

UTEST(OrdersRestriction, SelectOnEmptyRestrictions) {
  models::OrdersCounter counter{
      std::vector<handlers::OrdersCount>{{1, "android", "card"}}};

  models::OrdersRestriction orders_restriction(
      std::vector<handlers::libraries::discounts_match::OrdersRestriction>{});
  EXPECT_EQ(
      orders_restriction.Select(counter),
      std::vector<handlers::libraries::discounts_match::OrdersRestriction>{});
}

UTEST(OrdersRestriction, SelectOk) {
  models::OrdersCounter counter{std::vector<handlers::OrdersCount>{
      {4, "android", "card"},
      {7, "android", "cash"},
  }};

  models::OrdersRestriction orders_restriction({
      {{0, 3}, "android", "card"},
      {{1, 4}, std::nullopt, "card"},
      {{0, 10}, "android", std::nullopt},
      {{11, 15}, "android", std::nullopt},
  });
  std::vector<handlers::libraries::discounts_match::OrdersRestriction> expected{
      {{1, 4}, std::nullopt, "card"}, {{11, 15}, "android", std::nullopt}};
  EXPECT_EQ(orders_restriction.Select(counter), expected);
}

UTEST(OrdersRestriction, GetConditionOk) {
  models::OrdersCounter counter{std::vector<handlers::OrdersCount>{
      {4, "android", "card"},
      {7, "android", "cash"},
  }};

  models::OrdersRestriction orders_restriction({
      {{0, 3}, "android", "card"},
      {{1, 4}, std::nullopt, "card"},
      {{0, 10}, "android", std::nullopt},
      {{11, 15}, "android", std::nullopt},
  });
  std::vector<handlers::libraries::discounts_match::OrdersRestriction>
      expected_values{{{1, 4}, std::nullopt, "card"},
                      {{11, 15}, "android", std::nullopt}};
  handlers::libraries::discounts_match::MatchCondition expected{
      "orders_restriction", expected_values};
  EXPECT_EQ(orders_restriction.GetCondition(counter), expected);
}
