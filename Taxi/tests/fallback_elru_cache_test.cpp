#include <gtest/gtest.h>

#include <fallback-cache/fallback_elru_cache.hpp>

#include <clients/statistics.hpp>
#include <clients/statistics/client_mock_base.hpp>
#include <userver/utils/mock_now.hpp>

namespace {
namespace cs = clients::statistics;
}  // namespace

class MockStatClient : public clients::StatisticsReachInterface {
 public:
  void Send(const std::string& /*metric*/, unsigned /*value*/) const noexcept {}
  bool FallbackFired(const std::string& fallback) const noexcept {
    return std::find(fallback_fired_.begin(), fallback_fired_.end(),
                     fallback) != fallback_fired_.end();
  }
  unsigned GetMetric(const std::string& /*metric*/) const noexcept { return 0; }

  void SetFallbacks(const std::vector<std::string>& fallbacks) {
    fallback_fired_ = fallbacks;
  }

 private:
  std::vector<std::string> fallback_fired_;
};

static std::unordered_map<std::string, int> update_calls;
static std::unordered_map<std::string, int> fallback_update_calls;

const auto UpdateFunc0 = [](const std::string& key) {
  update_calls[key] += 1;
  return 0;
};
const auto UpdateFunc1 = [](const std::string& key) {
  update_calls[key] += 1;
  return 1;
};

const auto FallbackUpdateFunc2 = [](const std::string& key) {
  fallback_update_calls[key] += 1;
  return 2;
};
const auto FallbackUpdateFunc3 = [](const std::string& key) {
  fallback_update_calls[key] += 1;
  return 3;
};
const auto FallbackUpdateFuncThrowing = [](const std::string&) {
  throw std::exception();
  return 4;
};

void SetUpKey(const std::string& key) {
  update_calls[key] = 0;
  fallback_update_calls[key] = 0;
}

std::string fallback_name = "subvention_view.driver-tags-dmp.fallback";
auto tp1 = utils::datetime::Stringtime("2020-09-01 12:00:00", "UTC",
                                       "%Y-%m-%d %H:%M:%S");
auto tp2 = utils::datetime::Stringtime("2020-09-01 12:00:02", "UTC",
                                       "%Y-%m-%d %H:%M:%S");
auto tp3 = utils::datetime::Stringtime("2020-09-01 12:00:05", "UTC",
                                       "%Y-%m-%d %H:%M:%S");

UTEST(FallbackELRUCacheTests, NoFallback) {
  MockStatClient stat_client;

  fallback_cache::FallbackELruCache<std::string, int> fallback_cache(
      1, 5000, "fallback_name", stat_client);
  fallback_cache.SetMaxLifetime(std::chrono::seconds(1));

  SetUpKey("key1");

  ASSERT_EQ(fallback_cache.Get("key1", UpdateFunc0, FallbackUpdateFunc2), 0);
  ASSERT_EQ(update_calls["key1"], 1);
  ASSERT_EQ(fallback_cache.Get("key1", UpdateFunc1, FallbackUpdateFunc2), 0);

  ASSERT_EQ(update_calls["key1"], 1);
  ASSERT_EQ(fallback_update_calls["key1"], 0);
}

UTEST(FallbackELRUCacheTests, WithFallback) {
  MockStatClient stat_client;
  stat_client.SetFallbacks({fallback_name});
  ASSERT_EQ(stat_client.FallbackFired(fallback_name), true);

  fallback_cache::FallbackELruCache<std::string, int> fallback_cache(
      1, 5000, fallback_name, stat_client);
  fallback_cache.SetMaxLifetime(std::chrono::seconds(1));

  SetUpKey("key1");

  ASSERT_EQ(fallback_cache.Get("key1", UpdateFunc0, FallbackUpdateFunc2), 2);
  ASSERT_EQ(fallback_update_calls["key1"], 1);
  ASSERT_EQ(fallback_cache.Get("key1", UpdateFunc0, FallbackUpdateFunc3), 2);

  ASSERT_EQ(update_calls["key1"], 0);
  ASSERT_EQ(fallback_update_calls["key1"], 1);
}

UTEST(FallbackELRUCacheTests, Expiry) {
  MockStatClient stat_client;

  ::utils::datetime::MockNowSet(tp1);

  fallback_cache::FallbackELruCache<std::string, int> fallback_cache(
      1, 5000, fallback_name, stat_client);
  fallback_cache.SetMaxLifetime(std::chrono::seconds(1));

  SetUpKey("key1");

  ASSERT_EQ(fallback_cache.Get("key1", UpdateFunc0, FallbackUpdateFunc2), 0);
  ::utils::datetime::MockNowSet(tp2);
  ASSERT_EQ(update_calls["key1"], 1);
  ASSERT_EQ(fallback_cache.Get("key1", UpdateFunc1, FallbackUpdateFunc2), 1);

  ASSERT_EQ(update_calls["key1"], 2);
  ASSERT_EQ(fallback_update_calls["key1"], 0);

  ::utils::datetime::MockNowSet(tp3);
  stat_client.SetFallbacks({fallback_name});
  ASSERT_EQ(fallback_cache.Get("key1", UpdateFunc0, FallbackUpdateFunc2), 1);
  ASSERT_EQ(fallback_update_calls["key1"], 0);
}

UTEST(FallbackELRUCacheTests, Throws) {
  MockStatClient stat_client;
  stat_client.SetFallbacks({fallback_name});

  fallback_cache::FallbackELruCache<std::string, int> fallback_cache(
      1, 5000, fallback_name, stat_client);
  fallback_cache.SetMaxLifetime(std::chrono::seconds(1));

  SetUpKey("key1");

  EXPECT_THROW(
      fallback_cache.Get("key1", UpdateFunc0, FallbackUpdateFuncThrowing),
      std::exception);
}
