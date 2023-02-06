#include <userver/utest/utest.hpp>

#include <algorithm>
#include <atomic>
#include <stdexcept>
#include <vector>

#include <utils/parallel_for.hpp>

namespace utils {

constexpr std::size_t kIterations = 1000;

TEST(ParallelForTest, Return) {
  RunInCoro(
      [] {
        std::vector<std::atomic_bool> visited(kIterations);
        ParallelFor(kIterations, 8, [&visited](std::size_t i) {
          ASSERT_LT(i, kIterations);
          ASSERT_EQ(visited[i].exchange(true), false);
        });
        ASSERT_TRUE(std::all_of(visited.begin(), visited.end(),
                                [](const auto& x) { return x.load(); }));
      },
      2);
}

TEST(ParallelForTest, Exception) {
  RunInCoro(
      [] {
        ASSERT_THROW(
            {
              ParallelFor(kIterations, 8, [](std::size_t i) {
                if (i & 1) {
                  throw std::runtime_error{"test error message"};
                }
              });
            },
            std::runtime_error);
      },
      2);
}

}  // namespace utils
