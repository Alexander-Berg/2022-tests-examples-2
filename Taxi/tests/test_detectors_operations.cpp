#include <gtest/gtest.h>

#include "tools/testutils.hpp"

#include <models/models_fwd.hpp>
#include <utils/timeseries_operations.hpp>

namespace hejmdal {

TEST(TestDetectorsOperations, TestStandardDeviation) {
  std::vector<double> raw_data = {1, 5, 2, -8, 3, 6, 4, 12, 5, 10};
  auto view = testutils::BuildView(raw_data);
  {
    auto res = utils::timeseries_operations::StandardDeviation(view.begin(),
                                                               view.begin());
    EXPECT_DOUBLE_EQ(res, 0.);
  }
  {
    auto res = utils::timeseries_operations::StandardDeviation(view.begin(),
                                                               view.end());
    EXPECT_DOUBLE_EQ(res, 5.1380930314660516);
  }
  {
    auto res = utils::timeseries_operations::StandardDeviation(view.begin(),
                                                               view.end() - 1);
    EXPECT_DOUBLE_EQ(res, 4.9888765156985881);
  }
}

TEST(TestDetectorsOperations, TestMean) {
  std::vector<double> raw_data = {1, 5, 2, -8, 3, 6, 4, 12, 5, 10};
  auto view = testutils::BuildView(raw_data);
  {
    auto res = utils::timeseries_operations::Mean(view.begin(), view.begin());
    EXPECT_DOUBLE_EQ(res, 0.);
  }
  {
    auto res = utils::timeseries_operations::Mean(view.begin(), view.end());
    EXPECT_DOUBLE_EQ(res, 4.);
  }
  {
    auto res = utils::timeseries_operations::Mean(view.begin(), view.end() - 2);
    EXPECT_DOUBLE_EQ(res, 3.125);
  }
}

}  // namespace hejmdal
