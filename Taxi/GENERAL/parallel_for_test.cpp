#include <userver/utest/utest.hpp>

#include <algorithm>
#include <atomic>
#include <stdexcept>
#include <vector>

#include <utils/parallel_for.hpp>

namespace {

constexpr std::size_t kIterations = 10000;

TEST(ParallelForTest, ReturnsVoid) {
  RunInCoro(
      [] {
        std::vector<std::atomic_bool> visited(kIterations);
        utils::ParallelFor(kIterations, 8, [&visited](std::size_t i) {
          ASSERT_LT(i, kIterations);
          ASSERT_EQ(visited[i].exchange(true), false);
        });
        ASSERT_TRUE(std::all_of(visited.begin(), visited.end(),
                                [](const auto& x) { return x.load(); }));
      },
      2);
}

TEST(ParallelForTest, ThrowsException) {
  RunInCoro(
      [] {
        ASSERT_THROW(
            {
              utils::ParallelFor(kIterations, 8, [](std::size_t i) {
                if (i & 1) {
                  throw std::runtime_error{"test error message"};
                }
              });
            },
            std::runtime_error);
      },
      2);
}

}  // namespace
