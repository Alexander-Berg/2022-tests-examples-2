#include <endpoints/full/plugins/brandings/summary_scenarios/detectors/cheapest_detector.hpp>
#include <tests/endpoints/full/plugins/brandings/summary_scenarios/utils_test.hpp>
#include <userver/utest/utest.hpp>

namespace routestats::full::brandings {
const auto infos = ClassesInfo<core::Decimal>{
    {"econom", core::Decimal::FromBiased(1100, 1)},
    {"business", core::Decimal::FromBiased(2100, 1)},
    {"vip", core::Decimal::FromBiased(3100, 1)},
};

TEST(TestCheapestDetector, HappyPath) {
  const auto service_levels = PrepareServiceLevels(infos);
  const auto exp_wrapper = MakeExpWrapper("cheapest");

  ASSERT_FALSE(exp_wrapper.IsEmpty());

  auto cheapest_detector = CheapestDetector(exp_wrapper);
  RunDetector(cheapest_detector, service_levels);
  ASSERT_TRUE(cheapest_detector.HasDetectedScenarios());

  const auto scenarios = cheapest_detector.GetDetectedScenarios();
  ASSERT_EQ(scenarios.size(), 1);
  ASSERT_TRUE(scenarios.count("econom"));

  const auto scenario = scenarios.at("econom");
  ASSERT_EQ(scenario.args.size(), 1);
  ASSERT_TRUE(scenario.args.count("final_price"));
}

TEST(TestCheapestDetector, SupportedClasses) {
  const auto service_levels = PrepareServiceLevels(infos);
  const auto exp_wrapper = MakeExpWrapper("cheapest", {"business", "vips"});

  ASSERT_FALSE(exp_wrapper.IsEmpty());

  auto cheapest_detector = CheapestDetector(exp_wrapper);
  RunDetector(cheapest_detector, service_levels);
  ASSERT_TRUE(cheapest_detector.HasDetectedScenarios());

  const auto scenarios = cheapest_detector.GetDetectedScenarios();
  ASSERT_EQ(scenarios.size(), 1);
  ASSERT_TRUE(scenarios.count("business"));

  const auto scenario = scenarios.at("business");
  ASSERT_EQ(scenario.args.size(), 1);
  ASSERT_TRUE(scenario.args.count("final_price"));
}

}  // namespace routestats::full::brandings
