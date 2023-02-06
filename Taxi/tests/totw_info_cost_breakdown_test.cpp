#include <userver/utest/utest.hpp>

#include <experiments3/models/cache_manager.hpp>
#include <modules/totw_info/cost_breakdown/cost_breakdown.hpp>
#include "mock_complements_test.hpp"

namespace internal_totw::info::cost_breakdown {

using Decimal = decimal64::Decimal<4>;
namespace exp3 = experiments3::models;

auto build_exp_data(
    const std::optional<std::vector<std::string>>& exps = std::nullopt) {
  exp3::ClientsCache::MappedData exp_data{};
  for (const auto& item : exps.value_or(std::vector<std::string>{})) {
    exp_data.insert({item, exp3::ExperimentResult{}});
  }
  return exp_data;
}

TEST(BuildCostBreakdown, HappyPath) {
  auto complements = plus::Complements{Decimal{150}, Decimal{900}};
  auto complemets_accessor = plus::MockComplementsAccessor(complements);
  CostBreakdownInput input{};
  input.wallet_in_complements = true;
  auto result = BuildCostBreakdown(
      CostBreakDownDeps{
          complemets_accessor,
          build_exp_data(std::vector<std::string>{"plus_complements_in_totw"})},
      input);
  ASSERT_EQ(result.size(), 2);
  ASSERT_EQ(result[0].amount, Decimal{150});
  ASSERT_EQ(result[0].with_currency, false);
  ASSERT_EQ(result[0].name_key,
            "taxiontheway.cost_breakdown.paid_by_wallet.name");
  ASSERT_EQ(result[1].amount, Decimal{900});
  ASSERT_EQ(result[1].with_currency, true);
  ASSERT_EQ(result[1].name_key,
            "taxiontheway.cost_breakdown.paid_by_card.name");
}

TEST(BuildCostBreakdown, ComplementsInTotwOff) {
  auto complements = plus::Complements{Decimal{0}, Decimal{900}};
  CostBreakdownInput input{};
  input.wallet_in_complements = false;
  auto complemets_accessor = plus::MockComplementsAccessor(complements);
  auto result = BuildCostBreakdown(
      CostBreakDownDeps{complemets_accessor, build_exp_data()}, input);
  ASSERT_EQ(result.size(), 0);
}

TEST(BuildCostBreakdown, NoWalletInComplements) {
  auto complements = plus::Complements{Decimal{0}, Decimal{900}};
  CostBreakdownInput input{};
  input.wallet_in_complements = false;
  auto complemets_accessor = plus::MockComplementsAccessor(complements);
  auto result = BuildCostBreakdown(
      CostBreakDownDeps{
          complemets_accessor,
          build_exp_data(std::vector<std::string>{"plus_complements_in_totw"})},
      input);
  ASSERT_EQ(result.size(), 0);
}

TEST(BuildCostBreakdown, EmptyWallet) {
  auto complements = plus::Complements{Decimal{0}, Decimal{900}};
  auto complemets_accessor = plus::MockComplementsAccessor(complements);
  CostBreakdownInput input{};
  input.wallet_in_complements = true;
  auto result = BuildCostBreakdown(
      CostBreakDownDeps{
          complemets_accessor,
          build_exp_data(std::vector<std::string>{"plus_complements_in_totw"})},
      input);
  ASSERT_EQ(result.size(), 0);
}

}  // namespace internal_totw::info::cost_breakdown
