#include <endpoints/full/plugins/brandings/summary_scenarios/detectors/coupon_detector.hpp>

#include <tests/endpoints/full/plugins/brandings/summary_scenarios/utils_test.hpp>

#include <userver/utest/utest.hpp>

namespace routestats::full::brandings {
static const core::Coupon limit_coupon{core::CouponAppliedType::kLimit,
                                       core::Decimal::FromBiased(100, 1)};
static const core::Coupon value_coupon{core::CouponAppliedType::kValue,
                                       core::Decimal::FromBiased(100, 1)};
static const core::Coupon percent_coupon{core::CouponAppliedType::kPercent,
                                         core::Decimal::FromBiased(100, 1)};

TEST(TestCouponDetector, HappyPath) {
  const auto infos = ClassesInfo<core::Coupon>{
      {"econom", limit_coupon},
      {"business", value_coupon},
      {"vip", percent_coupon},
  };

  const auto service_levels = PrepareServiceLevels(infos);
  const auto exp_wrapper = MakeExpWrapper("coupon");

  ASSERT_FALSE(exp_wrapper.IsEmpty());

  auto coupon_detector = CouponDetector(exp_wrapper);
  RunDetector(coupon_detector, service_levels);
  ASSERT_TRUE(coupon_detector.HasDetectedScenarios());

  const auto scenarios = coupon_detector.GetDetectedScenarios();
  ASSERT_EQ(scenarios.size(), 3);
  ASSERT_TRUE(scenarios.count("econom"));
  ASSERT_TRUE(scenarios.count("business"));
  ASSERT_TRUE(scenarios.count("vip"));

  {
    const auto scenario = scenarios.at("econom");
    ASSERT_EQ(scenario.args.size(), 2);
    ASSERT_TRUE(scenario.args.count("final_price"));
    ASSERT_TRUE(scenario.args.count("coupon_discount_limit"));
  }
  {
    const auto scenario = scenarios.at("business");
    ASSERT_EQ(scenario.args.size(), 2);
    ASSERT_TRUE(scenario.args.count("final_price"));
    ASSERT_TRUE(scenario.args.count("coupon_discount_limit"));
  }
  {
    const auto scenario = scenarios.at("vip");
    ASSERT_EQ(scenario.args.size(), 2);
    ASSERT_TRUE(scenario.args.count("final_price"));
    ASSERT_TRUE(scenario.args.count("coupon_discount_percent"));
  }
}

TEST(TestCouponDetector, SupportedClasses) {
  const auto infos = ClassesInfo<core::Coupon>{
      {"econom", limit_coupon},
      {"business", std::nullopt},
      {"vip", limit_coupon},
  };

  const auto service_levels = PrepareServiceLevels(infos);
  const auto exp_wrapper = MakeExpWrapper("coupon", {"vip"});

  ASSERT_FALSE(exp_wrapper.IsEmpty());

  auto coupon_detector = CouponDetector(exp_wrapper);
  RunDetector(coupon_detector, service_levels);
  ASSERT_TRUE(coupon_detector.HasDetectedScenarios());

  const auto scenarios = coupon_detector.GetDetectedScenarios();
  ASSERT_EQ(scenarios.size(), 1);
  ASSERT_TRUE(scenarios.count("vip"));

  const auto scenario = scenarios.at("vip");
  ASSERT_EQ(scenario.args.size(), 2);
  ASSERT_TRUE(scenario.args.count("final_price"));
  ASSERT_TRUE(scenario.args.count("coupon_discount_limit"));
}

}  // namespace routestats::full::brandings
