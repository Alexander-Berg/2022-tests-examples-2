#include <gtest/gtest.h>

#include <candidates/filters/meta_factory.hpp>
#include <candidates/filters/self_diagnostics.hpp>
#include <candidates/filters/test/dummy.hpp>

namespace cf = candidates::filters;

namespace {

std::shared_ptr<cf::Factory> CreateFactory(const cf::FilterInfo& info) {
  return std::make_shared<cf::test::DummyFactory<cf::test::DisallowAll>>(info);
}

}  // namespace

TEST(FilterStatistics, Sample) {
  cf::FilterInfo sample1;
  sample1.name = "sample1";
  cf::FilterInfo sample2;
  sample2.name = "sample2";

  cf::Statistics statistics;
  cf::MetaFactory meta_factory(
      {
          CreateFactory(sample1),
          CreateFactory(sample2),
      },
      []() { return cf::SelfDiagnosticsData{}; }, statistics);
  const auto& idx_dict = meta_factory.GetIdxDict();

  statistics.AccountCreateAttempt(sample1.name);
  statistics.AccountCreateAttempt(sample2.name);

  cf::SelfDiagnosticsStats diag_stats;
  diag_stats.filters_stats.resize(idx_dict.size());
  diag_stats.filters_stats[idx_dict.GetIdx(sample1.name)].blocked = true;
  diag_stats.filters_stats[idx_dict.GetIdx(sample2.name)]
      .ignore_on_factory_errors = true;

  formats::json::Value json;
  ASSERT_NO_THROW(json = cf::StatisticsToJson(statistics, diag_stats,
                                              meta_factory.GetIdxDict())
                             .ExtractValue());
  ASSERT_TRUE(json.HasMember(sample1.name));
  ASSERT_TRUE(json.HasMember(sample2.name));

  const auto& json_sample1 = json[sample1.name];
  EXPECT_EQ(json_sample1["create_attempts"].As<int>(), 1);
  EXPECT_EQ(json_sample1["blocked"].As<int>(), 1);

  const auto& json_sample2 = json[sample2.name];
  EXPECT_EQ(json_sample2["create_attempts"].As<int>(), 1);
  EXPECT_EQ(json_sample2["ignore_on_factory_errors"].As<int>(), 1);
}
