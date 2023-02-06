#include <endpoints/full/plugins/brandings/summary_scenarios/detectors/surge_detector.hpp>

#include <tests/endpoints/full/plugins/brandings/summary_scenarios/utils_test.hpp>

#include <userver/utest/utest.hpp>

namespace routestats::full::brandings {

TEST(TestSurgeDetector, HappyPath) {
  const auto infos = ClassesInfo<core::Surge>{
      {"econom", core::Surge{core::Decimal::FromBiased(130, 2)}},
      {"business", core::Surge{core::Decimal::FromBiased(100, 2)}},
      {"vip", core::Surge{core::Decimal::FromBiased(110, 2)}},
  };

  const auto service_levels = PrepareServiceLevels<core::Surge>(infos);
  const auto exp_wrapper = MakeExpWrapper("surge");

  ASSERT_FALSE(exp_wrapper.IsEmpty());

  auto surge_detector = SurgeDetector(exp_wrapper);
  RunDetector(surge_detector, service_levels);
  ASSERT_TRUE(surge_detector.HasDetectedScenarios());

  const auto scenarios = surge_detector.GetDetectedScenarios();
  ASSERT_EQ(scenarios.size(), 2);
  ASSERT_TRUE(scenarios.count("econom"));
  ASSERT_TRUE(scenarios.count("vip"));
}

TEST(TestSurgeDetector, Threshold) {
  const auto infos = ClassesInfo<core::Surge>{
      {"econom", core::Surge{core::Decimal::FromBiased(130, 2)}},
      {"business", core::Surge{core::Decimal::FromBiased(100, 2)}},
      {"vip", core::Surge{core::Decimal::FromBiased(110, 2)}},
  };

  {
    const auto threshold = 1.1;
    const auto service_levels = PrepareServiceLevels<core::Surge>(infos);

    const auto exp_wrapper = MakeExpWrapper("surge", {}, threshold);

    ASSERT_FALSE(exp_wrapper.IsEmpty());

    auto surge_detector = SurgeDetector(exp_wrapper);
    RunDetector(surge_detector, service_levels);
    ASSERT_TRUE(surge_detector.HasDetectedScenarios());

    const auto scenarios = surge_detector.GetDetectedScenarios();
    ASSERT_EQ(scenarios.size(), 1);
    ASSERT_TRUE(scenarios.count("econom"));
  }
  {
    const auto threshold = 1.3;
    const auto service_levels = PrepareServiceLevels<core::Surge>(infos);

    const auto exp_wrapper = MakeExpWrapper("surge", {}, threshold);

    ASSERT_FALSE(exp_wrapper.IsEmpty());

    auto surge_detector = SurgeDetector(exp_wrapper);
    RunDetector(surge_detector, service_levels);
    ASSERT_FALSE(surge_detector.HasDetectedScenarios());
  }
}

}  // namespace routestats::full::brandings
