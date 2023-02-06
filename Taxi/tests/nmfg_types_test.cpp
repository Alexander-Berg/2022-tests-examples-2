#include <optional>

#include <gtest/gtest.h>

#include <views/v1/nmfg/status/post/types.hpp>

#include "common.hpp"

using namespace handlers::v1_nmfg_status::post;

struct GetSubventionCommissionData {
  std::optional<bool> is_net;
  std::optional<bool> has_commission;

  Commission expected;
};

struct GetSubventionCommissionParametrized
    : public ::testing::TestWithParam<GetSubventionCommissionData> {};

TEST_P(GetSubventionCommissionParametrized, CheckCommissions) {
  bs::DailyGuaranteeRule rule;
  rule.is_net = GetParam().is_net;
  rule.has_commission = GetParam().has_commission;

  ASSERT_EQ(GetParam().expected, GetSubventionCommission(rule));
}

static const std::vector<GetSubventionCommissionData> kCommissionData{
    // is_net, has_commission, expected
    {std::nullopt, std::nullopt, Commission::kNoCommission},
    {std::nullopt, true, Commission::kWithCommission},
    {std::nullopt, false, Commission::kNoCommission},

    {false, std::nullopt, Commission::kNoCommission},
    {false, true, Commission::kWithCommission},
    {false, false, Commission::kNoCommission},

    {true, std::nullopt, Commission::kNoCommission},
    {true, true, Commission::kNoCommission},
    {true, false, Commission::kNoCommission},
};

INSTANTIATE_TEST_SUITE_P(CheckCommissions, GetSubventionCommissionParametrized,
                         ::testing::ValuesIn(kCommissionData));
