#include <userver/utest/utest.hpp>

#include <numeric>

#include <testing/taxi_config.hpp>
#include <userver/engine/run_in_coro.hpp>
#include <userver/utils/mock_now.hpp>

#include <candidates/configs/filters.hpp>
#include <candidates/filters/meta_factory.hpp>
#include <candidates/filters/self_diagnostics.hpp>
#include <candidates/filters/test/dummy.hpp>

namespace cf = candidates::filters;

namespace {

void SetStats(cf::Statistics::FilterStats& stats, const uint64_t total,
              uint8_t disallow_prc, uint64_t time = 0) {
  const uint64_t disallows = total * disallow_prc / 100;
  stats.results[static_cast<size_t>(cf::Result::kAllow)] += total - disallows;
  stats.results[static_cast<size_t>(cf::Result::kDisallow)] += disallows;
  stats.timings_percentile.GetCurrentCounter().Account(time);
}

void SetErrorStats(cf::Statistics::FilterStats& stats, const uint64_t total,
                   uint8_t errors_prc) {
  const uint64_t errors = total * errors_prc / 100;
  stats.results[static_cast<size_t>(cf::Result::kAllow)] += total - errors;
  stats.errors += errors / 2;
  stats.timeouts += errors / 2;
}

std::shared_ptr<cf::Factory> CreateFactory(const cf::FilterInfo& info) {
  return std::make_shared<cf::test::DummyFactory<cf::test::DisallowAll>>(info);
}

std::vector<uint32_t> ConvertScores(const std::vector<uint32_t>& config) {
  std::vector<size_t> idx(config.size());
  std::iota(idx.begin(), idx.end(), 0);
  std::stable_sort(idx.begin(), idx.end(), [&](const size_t a, const size_t b) {
    return config[a] < config[b];
  });
  std::vector<uint32_t> dynamic(config.size());
  for (size_t i = 0; i < idx.size(); ++i) {
    dynamic[idx[i]] = i + 1;
  }
  return dynamic;
}

}  // namespace

UTEST_MT(FiltersSelfDiagnostics, Sample, 2) {
  cf::FilterInfo sample1;
  sample1.name = "sample1";
  sample1.required = false;
  sample1.disallow_limit = 90;

  cf::FilterInfo sample2;
  sample2.name = "sample2";
  sample2.required = true;
  sample2.disallow_limit = 90;

  cf::Statistics statistics;
  cf::MetaFactory meta_factory(
      {
          CreateFactory(sample1),
          CreateFactory(sample2),
      },
      []() { return cf::SelfDiagnosticsData{}; }, statistics);
  candidates::configs::Filters filters_configs(meta_factory, {});

  const auto sample1_idx = meta_factory.GetIdxDict().GetIdx(sample1.name);

  auto& sample1_stats = statistics.data[sample1.name];
  auto& sample2_stats = statistics.data[sample2.name];

  cf::SelfDiagnostics::Config config;
  config.lock_duration = std::chrono::seconds(300);
  config.min_total = 1000;
  config.min_factory_total = 100;
  config.max_factory_errors_prc = 30;
  config.max_errors_prc = 30;

  cf::SelfDiagnostics diag(meta_factory, statistics);
  EXPECT_TRUE(diag.Get().blocked.empty());
  diag.Monitor(config, filters_configs);
  EXPECT_TRUE(diag.Get().blocked.empty());

  SetStats(sample1_stats, config.min_total, 95);
  SetStats(sample2_stats, config.min_total, 93);
  diag.Monitor(config, filters_configs);
  auto data = diag.Get();
  ASSERT_EQ(data.blocked.size(), 1);
  EXPECT_TRUE(data.blocked.count(sample1_idx));
  EXPECT_TRUE(data.ignore_on_factory_errors.empty());

  utils::datetime::MockNowSet(utils::datetime::Now() + config.lock_duration);
  diag.Monitor(config, filters_configs);
  EXPECT_TRUE(diag.Get().blocked.empty());

  SetErrorStats(sample1_stats, config.min_total, 25);
  SetErrorStats(sample2_stats, config.min_total, 26);
  diag.Monitor(config, filters_configs);
  data = diag.Get();
  EXPECT_TRUE(diag.Get().blocked.empty());

  SetErrorStats(sample1_stats, config.min_total, 42);
  SetErrorStats(sample2_stats, config.min_total, 41);
  diag.Monitor(config, filters_configs);
  data = diag.Get();
  ASSERT_EQ(data.blocked.size(), 1);
  EXPECT_TRUE(data.blocked.count(sample1_idx));
  EXPECT_TRUE(data.ignore_on_factory_errors.empty());

  sample1_stats.created += 100;
  sample1_stats.factory_errors += 50;
  sample2_stats.created += 100;
  sample2_stats.factory_errors += 30;
  diag.Monitor(config, filters_configs);
  data = diag.Get();
  ASSERT_EQ(data.ignore_on_factory_errors.size(), 1);
  EXPECT_TRUE(data.ignore_on_factory_errors.count(sample1_idx));

  sample1_stats.created += 100;
  sample1_stats.factory_errors += 30;
  sample2_stats.created += 100;
  sample2_stats.factory_errors += 50;
  diag.Monitor(config, filters_configs);
  data = diag.Get();
  EXPECT_TRUE(data.ignore_on_factory_errors.empty());

  config.min_factory_total = 0;
  sample1_stats.created += 100;
  sample1_stats.factory_errors += 50;
  sample2_stats.created += 100;
  sample2_stats.factory_errors += 30;
  diag.Monitor(config, filters_configs);
  data = diag.Get();
  EXPECT_TRUE(data.ignore_on_factory_errors.empty());

  {
    SetErrorStats(sample1_stats, config.min_total, 42);
    diag.Monitor(config, filters_configs);
    data = diag.Get();
    ASSERT_EQ(data.blocked.size(), 1);
    EXPECT_TRUE(data.blocked.count(sample1_idx));
    EXPECT_TRUE(data.ignore_on_factory_errors.empty());

    candidates::models::FilterConfigs configs;
    configs["sample1"].required = true;
    SetErrorStats(sample1_stats, config.min_total, 42);
    diag.Monitor(config, {meta_factory, configs});
    data = diag.Get();
    EXPECT_TRUE(diag.Get().blocked.empty());
    EXPECT_TRUE(data.ignore_on_factory_errors.empty());
  }
}

UTEST_MT(FiltersSelfDiagnostics, Scores, 2) {
  cf::FilterInfo f1_info{"f1", {}, {}, false, {}, 30, 1, 5};
  cf::FilterInfo f2_info{"f2", {"f1"}, {}, false, {}, 30, 1, 3};
  cf::FilterInfo f3_info{"f3", {}, {"f1"}, false, {}, 30, 1, 4};
  cf::FilterInfo f4_info{"f4", {"f2", "f3"}, {}, false, {}, 30, 3, 5};

  cf::Statistics statistics;
  cf::MetaFactory meta_factory(
      {
          CreateFactory(f1_info),
          CreateFactory(f2_info),
          CreateFactory(f3_info),
          CreateFactory(f4_info),
      },
      []() { return cf::SelfDiagnosticsData{}; }, statistics);
  candidates::configs::Filters filters_configs(meta_factory, {});
  cf::SelfDiagnostics::Config config;
  config.min_total = 1000;

  cf::SelfDiagnostics diag(meta_factory, statistics);
  EXPECT_TRUE(diag.Get().scores.empty());

  config.enable_scoring = false;
  diag.CalcScores(config, filters_configs);
  EXPECT_TRUE(diag.Get().scores.empty());

  config.enable_scoring = true;
  diag.CalcScores(config, filters_configs);
  // Should be f4 f1 f3 f2
  EXPECT_EQ(diag.Get().scores, ConvertScores(filters_configs.GetScores()));

  auto& f1_stats = statistics.data["f1"];
  SetStats(f1_stats, 1000, 20, 2);
  diag.CalcScores(config, filters_configs);
  EXPECT_EQ(diag.Get().scores, ConvertScores(filters_configs.GetScores()));

  // Should be f4 f2 f1 f3
  auto& f2_stats = statistics.data["f2"];
  SetStats(f1_stats, 1000, 20, 2);
  SetStats(f2_stats, 800, 15, 1);
  diag.CalcScores(config, filters_configs);
  EXPECT_EQ(diag.Get().scores, (std::vector<uint32_t>{2, 3, 1, 4}));

  // Should be f4 f2 f1 f3
  auto& f3_stats = statistics.data["f3"];
  SetStats(f3_stats, 1000, 20, 2);
  SetStats(f2_stats, 1000, 25, 2);
  diag.CalcScores(config, filters_configs);
  EXPECT_EQ(diag.Get().scores, (std::vector<uint32_t>{2, 3, 1, 4}));

  // Should be f4 f1 f3 f2
  SetStats(f2_stats, 1000, 10, 2);
  diag.CalcScores(config, filters_configs);
  EXPECT_EQ(diag.Get().scores, (std::vector<uint32_t>{3, 1, 2, 4}));
}
