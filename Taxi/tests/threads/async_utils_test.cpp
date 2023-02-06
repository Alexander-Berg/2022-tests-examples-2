#include "threads/async_utils.hpp"
#include <gmock/gmock.h>
#include <gtest/gtest.h>

int f(int x) { return x * x; }

std::future<int> g(int x) {
  std::promise<int> p;
  p.set_value(x * x);
  return p.get_future();
}

TEST(TestAsyncUtils, TestAsyncExecBatch) {
  utils::Async async{4, "test_pool", false};
  utils::AsyncExecuter executer{async};
  const std::vector<int> data = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9};

  const auto results = utils::ProcessInBatches(data, f, executer, 4);
  ASSERT_EQ(results.size(), 10u);
  ASSERT_THAT(results,
              testing::ElementsAre(0, 1, 4, 9, 16, 25, 36, 49, 64, 81));

  const auto results2 = utils::ProcessInBatches(data, g, 4);
  ASSERT_EQ(results.size(), 10u);
  ASSERT_THAT(results,
              testing::ElementsAre(0, 1, 4, 9, 16, 25, 36, 49, 64, 81));
}
