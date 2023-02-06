#include <gtest/gtest.h>

#include <functional>
#include <vector>

#include <common/async.hpp>
#include <logging/log_extra.hpp>
#include <threads/async.hpp>
#include <utils/prof.hpp>

namespace {

using DataLoader = std::function<int()>;

constexpr int kThreadCount{8};
constexpr int kLoadersCount{4};
constexpr int kLoopsCount{1000};

void SomeWork(){};

[[maybe_unused]] DataLoader MakeBadLoader(TimeStorage&& ts) {
  return [ts{std::make_shared<TimeStorage>(std::move(ts))}] {
    {
      ScopeTime perf_st{*ts, "data_loader"};

      SomeWork();
    }

    return 100;
  };
}

DataLoader MakeGoodLoader(TimeStorage&& ts) {
  return [ts{std::make_shared<TimeStorage>(std::move(ts))}]() mutable {
    {
      ScopeTime perf_st{*ts, "data_loader"};

      SomeWork();
    }

    ts.reset();

    return 100;
  };
}

template <typename F>
void LoadersTest(const utils::Async& pool, F f) {
  LogExtra log_extra{{"a", "b"}, {"c", "d"}};

  LoggingTimeStorage prof_ts{"load_data_timings", log_extra};

  std::vector<DataLoader> loaders;
  loaders.reserve(16);

  for (int i = 0; i < kLoadersCount; ++i) {
    loaders.push_back(f(prof_ts.CreateChild()));
  }

  auto [loaders_data] = async::CallAndWaitFor(
      pool, std::chrono::milliseconds{1}, std::move(loaders));

  for (const auto& data : loaders_data) {
    EXPECT_EQ(100, data.value_or(100));
  }
}

}  // namespace

TEST(AsyncTest, Base) {
  utils::Async pool{kThreadCount, "async_test"};

  for (int i = 0; i < kLoopsCount; ++i) {
    LoadersTest(pool, MakeGoodLoader);
    // LoadersTest(pool, MakeBadLoader);
  }
}
