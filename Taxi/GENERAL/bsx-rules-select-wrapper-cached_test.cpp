#include <gtest/gtest.h>

#include <bsx-rules-select-wrapper/bsx-rules-select-wrapper-cached.hpp>

namespace bsx = clients::billing_subventions_x;

TEST(RulesSelectCache, KeysTimeToleranceCommon) {
  using namespace bsx_rules_select_wrapper;

  auto begin = utils::datetime::Now();
  auto end = begin + std::chrono::hours(6);

  bsx::SelectRulesRequest body1;
  body1.time_range.start = begin;
  body1.time_range.end = end;
  body1.limit = 100;
  impl::Key key1;
  key1.body = body1;

  auto body2 = body1;
  body2.time_range.start = begin + std::chrono::seconds(10);
  body2.time_range.end = end + std::chrono::seconds(6);
  impl::Key key2;
  key2.body = std::move(body2);

  auto body3 = body1;
  body3.time_range.start = begin + std::chrono::seconds(15);
  body3.time_range.end = end + std::chrono::seconds(3);
  impl::Key key3;
  key3.body = std::move(body3);

  auto body4 = body1;
  body4.limit = 100500;
  impl::Key key4;
  key4.body = std::move(body4);

  impl::KeyComparator comparator{std::chrono::seconds{11}};

  ASSERT_TRUE(comparator(key1, key2));
  ASSERT_FALSE(comparator(key1, key3));

  impl::KeyHasher hasher;
  ASSERT_EQ(hasher(key1), hasher(key2));
  ASSERT_NE(hasher(key1), hasher(key4));
}

TEST(RulesSelectCache, KeysTimeToleranceRules) {
  using namespace bsx_rules_select_wrapper;

  auto begin = utils::datetime::Now();
  auto end = begin + std::chrono::hours(6);

  bsx::SelectRulesRequest body1;
  body1.time_range.start = begin;
  body1.time_range.end = end;
  body1.limit = 100;
  impl::Key key1;
  key1.body = body1;

  auto body2 = body1;
  body2.time_range.start = begin + std::chrono::seconds(10);
  body2.time_range.end = end + std::chrono::seconds(6);
  impl::Key key2;
  key2.body = std::move(body2);

  auto body3 = body1;
  body3.time_range.start = begin + std::chrono::seconds(15);
  body3.time_range.end = end + std::chrono::seconds(3);
  impl::Key key3;
  key3.body = std::move(body3);

  impl::KeyComparator comparator{std::chrono::seconds{11}};

  ASSERT_TRUE(comparator(key1, key2));
  ASSERT_FALSE(comparator(key1, key3));

  impl::KeyHasher hasher;
  ASSERT_EQ(hasher(key1), hasher(key2));
}

TEST(RulesSelectCache, KeysTimeToleranceMixed) {
  using namespace bsx_rules_select_wrapper;

  const auto begin = utils::datetime::Now();
  const auto end = begin + std::chrono::hours(6);

  bsx::SelectRulesRequest body1;
  body1.time_range.start = begin;
  body1.time_range.end = end;
  body1.limit = 100;
  impl::Key key1;
  key1.body = body1;

  bsx::SelectRulesRequest body2;
  body2.time_range.start = begin + std::chrono::seconds(10);
  body2.time_range.end = end + std::chrono::seconds(6);
  body2.limit = 100;
  impl::Key key2;
  key2.body = std::move(body2);

  auto body3 = body1;
  body3.time_range.start = begin + std::chrono::seconds(15);
  body3.time_range.end = end + std::chrono::seconds(3);
  impl::Key key3;
  key3.body = std::move(body3);

  impl::KeyComparator comparator{std::chrono::seconds{11}};

  ASSERT_TRUE(comparator(key1, key2));
  ASSERT_FALSE(comparator(key1, key3));

  impl::KeyHasher hasher;
  ASSERT_EQ(hasher(key1), hasher(key2));
}
