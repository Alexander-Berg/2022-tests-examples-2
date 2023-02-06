#include "random.hpp"

#include <gtest/gtest.h>

#include <map>

namespace routehistory::utils {
inline namespace {
const size_t kNumIterations = 200000;
const double kPrecision = 0.002;

void TestGroup(const std::vector<int>& groups,
               const std::map<size_t, double>& expected_probabilities) {
  std::map<size_t, size_t> result;
  for (size_t i = 0; i < kNumIterations; ++i) {
    ++result[RandomSelectGroup(groups)];
  }
  ASSERT_EQ(result.size(), expected_probabilities.size());
  for (const auto& [group, count] : result) {
    auto probability = (double)count / kNumIterations;
    auto difference = probability - expected_probabilities.at(group);
    ASSERT_LE(std::abs(difference), kPrecision);
  }
}

TEST(Random, RandomSelectGroup) {
  //
  GetRandomEngineThreadLocal().seed(1337);
  TestGroup({30, 40, 50}, {{0, 30.0 / 120}, {1, 40.0 / 120}, {2, 50.0 / 120}});
  TestGroup({30, 0, 50}, {{0, 30.0 / 80}, {2, 50.0 / 80}});
  TestGroup({30, 0, 0}, {{0, 1.0}});
  TestGroup({30}, {{0, 1.0}});
  TestGroup({0, 0, 1}, {{2, 1.0}});
  TestGroup({0, 1, 1}, {{1, 0.5}, {2, 0.5}});
}

}  // namespace
}  // namespace routehistory::utils
