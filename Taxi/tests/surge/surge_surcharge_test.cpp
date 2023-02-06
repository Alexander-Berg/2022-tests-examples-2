#include <algorithm>
#include <random>
#include <vector>

#include <gtest/gtest.h>

#include <surge/conventions.hpp>

void CheckCalculation(const surge::Surcharge& sc, double surge, double cost0,
                      double cost_expected) {
  const double cost_manual =
      sc.alpha * surge * cost0 + sc.beta * (cost0 + sc.surcharge);
  EXPECT_NEAR(cost_expected, cost_manual, 1e-6);

  const double cost = sc.Apply(surge, cost0);
  EXPECT_NEAR(cost_expected, cost, 1e-6);

  EXPECT_NEAR(cost0, sc.OriginalCost(surge, cost), 1e-6);
}

TEST(SurgeSurcharge, PureSurge) {
  surge::Surcharge surcharge = surge::conventions::kPureSurge;

  std::vector<double> surges(40);
  {
    double surge = 1.0;
    std::generate(surges.begin(), surges.end(), [&surge] {
      double r = surge;
      surge += 0.1;
      return r;
    });
  }

  std::uniform_real_distribution<double> urd(49., 2000.);
  std::default_random_engine re;

  for (double surge : surges) {
    double cost = urd(re);
    CheckCalculation(surcharge, surge, cost, surge * cost);
  }
}

TEST(SurgeSurcharge, PureSurcharge) {
  const double cost_surcharge = 39.;
  surge::Surcharge surcharge =
      surge::conventions::PureSurcharge(cost_surcharge);

  std::vector<double> costs(40);
  {
    double cost = 49;
    std::generate(costs.begin(), costs.end(), [&cost] {
      double r = cost;
      cost += 39;
      return r;
    });
  }

  // we really should ignore surge in this case
  std::uniform_real_distribution<double> urd(1.0, 9.0);
  std::default_random_engine re;

  for (double cost : costs) {
    CheckCalculation(surcharge, urd(re), cost, cost + cost_surcharge);
  }
}

TEST(SurgeSurcharge, CostCalculation) {
  surge::Surcharge surcharge(0.7, 0.3, 100.);

  EXPECT_NEAR(30., surcharge.CostSurcharge(), 1e-6);
  EXPECT_NEAR(1., surcharge.CostMultiplier(1.), 1e-6);
  EXPECT_NEAR(1.42, surcharge.CostMultiplier(1.6), 1e-6);
  EXPECT_NEAR(1.98, surcharge.CostMultiplier(2.4), 1e-6);

  const double cost = 99.;
  CheckCalculation(surcharge, 1.0, cost, 129.);
  CheckCalculation(surcharge, 1.6, cost, 170.58);
  CheckCalculation(surcharge, 2.4, cost, 226.02);
}
