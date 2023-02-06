#include "tables.hpp"

#include <userver/utest/utest.hpp>

#include <models/pgsql/consts.hpp>

TEST(TablesTest, TestPastToNowTablesIndexIterator) {
  using models::pgsql::kEventsTablesCount;

  for (std::size_t i = 0; i < kEventsTablesCount; ++i) {
    std::vector<int> expected;
    for (int j = 0, k = (i + 1) % kEventsTablesCount;
         j < kEventsTablesCount - 1; ++j, k = (k + 1) % kEventsTablesCount) {
      expected.push_back(k);
    }
    std::vector<int> result;
    for (models::pgsql::PastToNowTablesIndexIterator iter(i); !iter.IsEnd();
         ++iter) {
      result.push_back(*iter);
    }
    EXPECT_EQ(expected, result) << i;
  }
}
