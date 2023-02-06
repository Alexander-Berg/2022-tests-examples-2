#include <endpoints/full/plugins/brandings/summary_scenarios/detectors/discount_detector.hpp>

#include <tests/endpoints/full/plugins/brandings/summary_scenarios/utils_test.hpp>

#include <userver/utest/utest.hpp>

namespace routestats::full::brandings {

TEST(TestDiscountDetector, RoundValue) {
  const auto exp_wrapper = MakeExpWrapper("discount");
  ASSERT_FALSE(exp_wrapper.IsEmpty());
  {
    // expected discount: round((1 - 0.876) * 100) = round(12.4) = 12
    const auto infos = ClassesInfo<core::Discount>{
        {"econom", core::Discount{core::Decimal::FromBiased(876, 3), ""}},
    };

    const auto service_levels = PrepareServiceLevels(infos);

    auto discount_detector = DiscountDetector(exp_wrapper);
    RunDetector(discount_detector, service_levels);

    const auto scenarios = discount_detector.GetDetectedScenarios();
    ASSERT_EQ(scenarios.size(), 1);
    const auto it = scenarios.begin()->second.args.find("discount_percent");
    ASSERT_NE(it, scenarios.begin()->second.args.end());
    ASSERT_EQ(it->second, "12");
  }
  {
    // expected discount: round((1 - 0.875) * 100) = round(12.5) = 13
    const auto infos = ClassesInfo<core::Discount>{
        {"econom", core::Discount{core::Decimal::FromBiased(875, 3), ""}},
    };

    const auto service_levels = PrepareServiceLevels(infos);

    auto discount_detector = DiscountDetector(exp_wrapper);
    RunDetector(discount_detector, service_levels);

    const auto scenarios = discount_detector.GetDetectedScenarios();
    ASSERT_EQ(scenarios.size(), 1);
    const auto it = scenarios.begin()->second.args.find("discount_percent");
    ASSERT_NE(it, scenarios.begin()->second.args.end());
    ASSERT_EQ(it->second, "13");
  }
}

TEST(TestDiscountDetector, DiscountValue) {
  const auto exp_wrapper = MakeExpWrapper("discount");
  ASSERT_FALSE(exp_wrapper.IsEmpty());
  const auto infos = ClassesInfo<core::Discount>{
      {"econom", core::Discount{core::Decimal::FromBiased(87, 2), ""}},
  };
  auto service_levels = PrepareServiceLevels(infos);
  for (auto& service_level : service_levels) {
    service_level.final_price = core::Decimal::FromBiased(870, 1);
    service_level.internal_original_price = core::Decimal::FromBiased(1000, 1);
  }

  auto discount_detector = DiscountDetector(exp_wrapper);
  RunDetector(discount_detector, service_levels);

  const auto scenarios = discount_detector.GetDetectedScenarios();
  ASSERT_EQ(scenarios.size(), 1);
  {
    const auto it = scenarios.begin()->second.args.find("discount_percent");
    ASSERT_NE(it, scenarios.begin()->second.args.end());
    ASSERT_EQ(it->second, "13");  // round((1 - 0.87) * 100)
  }
  {
    const auto it = scenarios.begin()->second.args.find("discount_value");
    ASSERT_NE(it, scenarios.begin()->second.args.end());
    ASSERT_EQ(it->second, "13");  // 100 - 87
  }
}

TEST(TestDiscountDetector, NegativeDiscountValue) {
  // Usually it mustn't happen but we check it anyway
  const auto exp_wrapper = MakeExpWrapper("discount");
  ASSERT_FALSE(exp_wrapper.IsEmpty());
  const auto infos = ClassesInfo<core::Discount>{
      {"econom", core::Discount{core::Decimal::FromBiased(87, 2), ""}},
  };
  auto service_levels = PrepareServiceLevels(infos);
  for (auto& service_level : service_levels) {
    service_level.final_price = core::Decimal::FromBiased(870, 1);
    service_level.internal_original_price = core::Decimal::FromBiased(870, 1);
  }

  {
    auto discount_detector = DiscountDetector(exp_wrapper);
    RunDetector(discount_detector, service_levels);

    const auto scenarios = discount_detector.GetDetectedScenarios();
    ASSERT_EQ(scenarios.size(), 1);
    {
      const auto it = scenarios.begin()->second.args.find("discount_percent");
      ASSERT_NE(it, scenarios.begin()->second.args.end());
      ASSERT_EQ(it->second, "13");  // round((1 - 0.87) * 100)
    }
    {
      const auto it = scenarios.begin()->second.args.find("discount_value");
      ASSERT_EQ(it, scenarios.begin()->second.args.end());  // 87 - 87 = 0
    }
  }

  for (auto& service_level : service_levels) {
    service_level.final_price = core::Decimal::FromBiased(970, 1);
    service_level.internal_original_price = core::Decimal::FromBiased(870, 1);
  }

  {
    auto discount_detector = DiscountDetector(exp_wrapper);
    RunDetector(discount_detector, service_levels);

    const auto scenarios = discount_detector.GetDetectedScenarios();
    ASSERT_EQ(scenarios.size(), 1);
    {
      const auto it = scenarios.begin()->second.args.find("discount_percent");
      ASSERT_NE(it, scenarios.begin()->second.args.end());
      ASSERT_EQ(it->second, "13");  // round((1 - 0.87) * 100)
    }
    {
      const auto it = scenarios.begin()->second.args.find("discount_value");
      ASSERT_EQ(it, scenarios.begin()->second.args.end());  // 97 - 87 = -10
    }
  }
}

TEST(TestDiscountDetector, NegativeDiscount) {
  const auto exp_wrapper = MakeExpWrapper("discount");
  ASSERT_FALSE(exp_wrapper.IsEmpty());
  const auto infos = ClassesInfo<core::Discount>{
      {"econom", core::Discount{core::Decimal::FromBiased(879, 2), ""}},
  };

  const auto service_levels = PrepareServiceLevels(infos);

  auto discount_detector = DiscountDetector(exp_wrapper);
  RunDetector(discount_detector, service_levels);

  ASSERT_FALSE(discount_detector.HasDetectedScenarios());
}
}  // namespace routestats::full::brandings
