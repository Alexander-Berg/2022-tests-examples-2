#include <endpoints/full/plugins/brandings/summary_scenarios/detectors/fastest_detector.hpp>

#include <tests/endpoints/full/plugins/brandings/summary_scenarios/utils_test.hpp>

#include <userver/utest/utest.hpp>

namespace routestats::full::brandings {

const auto infos = ClassesInfo<core::EstimatedWaiting>{
    {"econom", core::EstimatedWaiting{3, ""}},
    {"comfort", core::EstimatedWaiting{10, ""}},
    {"business", core::EstimatedWaiting{100, ""}},
};

TEST(TestFastestDetector, HappyPath) {
  const auto service_levels = PrepareServiceLevels(infos);
  const auto exp_wrapper = MakeExpWrapper("fastest");

  ASSERT_FALSE(exp_wrapper.IsEmpty());

  auto fastest_detector = FastestDetector(exp_wrapper);
  RunDetector(fastest_detector, service_levels);
  ASSERT_TRUE(fastest_detector.HasDetectedScenarios());

  const auto result = fastest_detector.GetDetectedScenarios();
  ASSERT_EQ(result.size(), 1);  // only one fastest class is possible

  const auto econom_it = result.find("econom");
  ASSERT_NE(econom_it, result.cend());
}

TEST(TestFastestDetector, SupportedClasses) {
  const auto service_levels = PrepareServiceLevels(infos);
  const auto exp_wrapper = MakeExpWrapper("fastest", {"comfort"});

  ASSERT_FALSE(exp_wrapper.IsEmpty());

  auto fastest_detector = FastestDetector(exp_wrapper);
  RunDetector(fastest_detector, service_levels);
  ASSERT_TRUE(fastest_detector.HasDetectedScenarios());

  const auto result = fastest_detector.GetDetectedScenarios();
  ASSERT_EQ(result.size(), 1);  // only one fastest class is possible

  const auto comfort_it = result.find("comfort");
  ASSERT_NE(comfort_it, result.cend());
}

TEST(TestFastestDetector, Threshold) {
  const auto service_levels = PrepareServiceLevels(infos);
  {
    auto exp_wrapper = MakeExpWrapper("fastest", {"comfort"}, std::nullopt, 9);

    ASSERT_FALSE(exp_wrapper.IsEmpty());

    auto fastest_detector = FastestDetector(exp_wrapper);
    RunDetector(fastest_detector, service_levels);
    ASSERT_FALSE(fastest_detector.HasDetectedScenarios());
  }
  {
    auto exp_wrapper = MakeExpWrapper("fastest", {"comfort"}, std::nullopt, 10);

    ASSERT_FALSE(exp_wrapper.IsEmpty());

    auto fastest_detector = FastestDetector(exp_wrapper);
    RunDetector(fastest_detector, service_levels);
    ASSERT_TRUE(fastest_detector.HasDetectedScenarios());

    const auto result = fastest_detector.GetDetectedScenarios();
    const auto comfort_it = result.find("comfort");
    ASSERT_NE(comfort_it, result.cend());
  }
}
}  // namespace routestats::full::brandings
