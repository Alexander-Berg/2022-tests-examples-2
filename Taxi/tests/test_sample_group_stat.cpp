#include <gtest/gtest.h>

#include <utils/sample_group_stat.hpp>

namespace hejmdal::utils::stat {

TEST(TestSampleGroupStat, SampleByGroup) {
  SampleByGroup samples1;
  samples1.Append("label1", 1);
  samples1.Append("label1", 2);
  samples1.Append("label1", 3);

  samples1.Append("label2", 2);
  samples1.Append("label2", 3);
  samples1.Append("label2", 4);

  SampleByGroup samples2;

  samples2.Append("label2", 3);
  samples2.Append("label2", 4);
  samples2.Append("label2", 5);

  samples2.Append("label3", 4);
  samples2.Append("label3", 5);
  samples2.Append("label3", 6);

  SampleByGroup result_samples;
  result_samples.Merge(std::move(samples1));
  result_samples.Merge(std::move(samples2));

  auto raw = result_samples.ExtractLags();
  SampleByGroupContainer expected{{"label1", {1, 2, 3}},
                                  {"label2", {2, 3, 4, 3, 4, 5}},
                                  {"label3", {4, 5, 6}}};
  EXPECT_EQ(expected, raw);
}

}  // namespace hejmdal::utils::stat
