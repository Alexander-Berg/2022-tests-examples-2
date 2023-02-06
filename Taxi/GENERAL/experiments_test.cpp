#include <gtest/gtest.h>
#include <userver/utils/mock_now.hpp>

#include "experiments.hpp"
#include "internal/unittest_utils/test_utils.hpp"

TEST(experiment, cached) {
  using driver_route_watcher::models::DriverId;
  driver_route_watcher::test_utils::TestExperiments exp;
  const auto now = utils::datetime::Now();
  utils::datetime::MockNowSet(now);

  exp.SetResult(driver_route_watcher::internal::ExperimentsBase::Values{
      std::chrono::seconds(42), std::nullopt});

  driver_route_watcher::internal::ExperimentsCached exp_cached(exp);
  {
    /// First request, original exp must be called
    EXPECT_EQ(0ull, exp.GetRequestCount());
    auto res = exp_cached.GetRebuildOldRouteMinEta(DriverId());
    EXPECT_EQ(std::chrono::seconds(42), res);
    EXPECT_EQ(1ull, exp.GetRequestCount());
  }
  {
    /// Second request, original exp must not be called (must return cached
    /// result)
    auto res = exp_cached.GetRebuildOldRouteMinEta(DriverId());
    EXPECT_EQ(std::chrono::seconds(42), res);
    EXPECT_EQ(1ull, exp.GetRequestCount());
  }
  utils::datetime::MockNowSet(now + std::chrono::minutes(31));
  {
    /// original exp must be called cause enough time has passed
    auto res = exp_cached.GetRebuildOldRouteMinEta(DriverId());
    EXPECT_EQ(std::chrono::seconds(42), res);
    EXPECT_EQ(2ull, exp.GetRequestCount());
  }
}
