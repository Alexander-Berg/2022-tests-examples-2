#include <gmock/gmock.h>
#include <gtest/gtest.h>

#include "utils/algorithms.hpp"

TEST(gps_archive, TestMedian) {
  std::vector<double> data = {10, 1, 2, 3, 4, 18, 6, 7, 8, 9, 10, 25};
  utils::median_filter::Filter(data, [](double* z) { return z; }, 3);
  std::vector<double> diffs;
  ASSERT_EQ(*(--data.end()), 25);  // do nothing on borders
  data.erase(--data.end());
  boost::adjacent_difference(data, std::back_inserter(diffs));
  ASSERT_LE(boost::accumulate(diffs, 0u), data.size());
}

TEST(gps_archive, TestMedianSmall) {
  std::vector<double> data = {1, 200, 3};
  utils::median_filter::Filter(data, [](double* z) { return z; }, 5);
  ASSERT_THAT(data, testing::ElementsAre(1, 200, 3));
}

TEST(gps_archive, TestMedianNoWindow) {
  std::vector<double> data = {1, 200, 3, 4, 5};
  utils::median_filter::Filter(data, [](double* z) { return z; }, 0);
  ASSERT_THAT(data, testing::ElementsAre(1, 200, 3, 4, 5));
}

TEST(gps_archive, TestForEachGroup) {
  using Item = std::pair<std::string, int>;
  std::vector<std::pair<std::string, int>> data = {
      {"a", 1}, {"b", 1}, {"c", 2}, {"d", 3}, {"e", 3}, {"f", 1}};
  using It = utils::ForEachGroupIterator<std::vector<Item>>::type;
  std::vector<std::pair<It, It>> res;
  utils::ForEachGroup(data, [](Item l, Item r) { return l.second == r.second; },
                      [&res](It t1, It t2) {
                        res.push_back({t1, t2});
                      });

  ASSERT_EQ(res.size(), 4u);
  const auto check = [](const std::pair<It, It>& p) {
    It it = p.first;
    auto v = (*it).second;
    while (it != p.second) {
      ASSERT_EQ(it->second, v);
      ++it;
    }
  };

  for (const auto& r : res) {
    check(r);
  }
}

TEST(gps_archive, TestForEachGroup2) {
  using Item = std::pair<std::string, int>;
  std::vector<Item> data = {{"a", 42}};
  using It = utils::ForEachGroupIterator<std::vector<Item>>::type;
  std::vector<std::pair<It, It>> res;
  utils::ForEachGroup(data, [](Item l, Item r) { return l == r; },
                      [&res](It t1, It t2) {
                        res.push_back({t1, t2});
                      });

  ASSERT_EQ(res.size(), 1u);
  ASSERT_EQ(data[0].second, 42);
}

TEST(gps_archive, TestForEachGroupEmpty) {
  using Item = std::pair<std::string, int>;
  std::vector<Item> data = {};
  using It = utils::ForEachGroupIterator<std::vector<Item>>::type;
  std::vector<std::pair<It, It>> res;
  utils::ForEachGroup(
      data, [](Item l, Item r) { return l == r; },
      [](It, It) { ADD_FAILURE() << "ForEachGroup should not call callback"; });

  ASSERT_EQ(res.size(), 0u);
}

TEST(gps_archive, TestForEachGroupNoCmp) {
  using Item = int;
  std::vector<Item> data = {42, -1};
  using It = utils::ForEachGroupIterator<std::vector<Item>>::type;
  std::vector<std::pair<It, It>> res;
  utils::ForEachGroup(data, [&res](It t1, It t2) { res.push_back({t1, t2}); });

  ASSERT_EQ(res.size(), 2u);
  ASSERT_EQ(data[0], 42);
  ASSERT_EQ(data[1], -1);
}
