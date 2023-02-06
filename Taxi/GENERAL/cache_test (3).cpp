#include <data_provider/cache.hpp>

#include <gtest/gtest.h>

namespace {

class TestCache final : public data_provider::Cache<std::string> {
 public:
  using data_provider::Cache<std::string>::Cache;

  void Update(
      [[maybe_unused]] UpdateType type,
      [[maybe_unused]] const std::chrono::system_clock::time_point& last_update,
      [[maybe_unused]] const std::chrono::system_clock::time_point& now,
      [[maybe_unused]] UpdateStatisticsScope& stats_scope) final {}
};

}  // namespace

// just test of compilation
TEST(DataProvider, Cache) {
  [[maybe_unused]] std::unique_ptr<TestCache> ptr;
  const bool res =
      std::is_same<decltype(std::declval<TestCache>().Get()),
                   decltype(
                       std::declval<data_provider::DataProvider<std::string>>()
                           .Get())>::value;
  EXPECT_TRUE(res);
}
