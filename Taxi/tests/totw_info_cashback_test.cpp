#include <testing/taxi_config.hpp>
#include <userver/utest/utest.hpp>

#include <experiments3/models/cache_manager.hpp>
#include <modules/totw_info/cashback_info/cashback_info.hpp>
#include "mock_cashback_test.hpp"

namespace internal_totw::info::cashback {

static const std::string kExpAttributedTextTotw = "plus_totw_attributed_text";

using Decimal = decimal64::Decimal<4>;
namespace exp3 = experiments3::models;

bool ShouldNotify(
    const decimal64::Decimal<4>& cashback,
    const experiments3::models::ClientsCache::MappedData& exp_data);
bool ShouldShowCashbackCost(
    const decimal64::Decimal<4>& cashback,
    const experiments3::models::ClientsCache::MappedData& exp_data);
CostDetails BuildCostDetails(const decimal64::Decimal<4>& cashback);
bool ShouldShowCostDetails(const decimal64::Decimal<4>& cashback,
                           const UserInfo& user_info,
                           const exp3::ClientsCache::MappedData& exp_data);

auto build_exp_data(
    const std::optional<std::vector<std::string>>& exps = std::nullopt) {
  exp3::ClientsCache::MappedData exp_data{};
  for (const auto& item : exps.value_or(std::vector<std::string>{})) {
    exp3::ExperimentResult expResult;
    if (item == kExpAttributedTextTotw) {
      formats::json::ValueBuilder valueBuilder;
      valueBuilder["items"] = std::vector<std::string>{};

      expResult = {"", valueBuilder.ExtractValue(), {}};
    }
    exp_data.insert({item, expResult});
  }
  return exp_data;
}

TEST(ShouldNotify, Should) {
  auto result = ShouldNotify(
      Decimal{10},
      build_exp_data(std::vector<std::string>{"plus_notifications_in_totw"}));
  ASSERT_TRUE(result);
}

TEST(ShouldNotify, NoCashback) {
  auto result = ShouldNotify(
      Decimal{0},
      build_exp_data(std::vector<std::string>{"plus_notifications_in_totw"}));
  ASSERT_FALSE(result);
}

TEST(ShouldNotify, ExpOff) {
  auto result = ShouldNotify(Decimal{10}, build_exp_data());
  ASSERT_FALSE(result);
}

TEST(ShouldShowCashbackCost, Should) {
  auto result = ShouldShowCashbackCost(
      Decimal{10},
      build_exp_data(std::vector<std::string>{"plus_cashback_in_totw"}));
  ASSERT_TRUE(result);
}

TEST(ShouldShowCashbackCost, NoCashback) {
  auto result = ShouldShowCashbackCost(
      Decimal{0},
      build_exp_data(std::vector<std::string>{"plus_cashback_in_totw"}));
  ASSERT_FALSE(result);
}

TEST(BuildCostDetails, WithCashback) {
  auto result = BuildCostDetails(Decimal{10});
  ASSERT_EQ(result.action, std::nullopt);
  ASSERT_EQ(result.text, "taxiontheway.cashback.title.with_cashback");
}

TEST(BuildCostDetails, NoCashback) {
  auto result = BuildCostDetails(Decimal{0});
  ASSERT_EQ(result.action, "buy_plus");
  ASSERT_EQ(result.text, "taxiontheway.cashback.title.without_cashback");
}

TEST(ShouldShowCashbackCost, HasCashbackPlus) {
  auto result = ShouldShowCostDetails(Decimal{42}, UserInfo{true, true},
                                      build_exp_data());
  ASSERT_TRUE(result);
}

TEST(ShouldShowCashbackCost, HasOnlyYaPlus) {
  auto result = ShouldShowCostDetails(Decimal{0}, UserInfo{true, false},
                                      build_exp_data());
  ASSERT_FALSE(result);
}

TEST(ShouldShowCashbackCost, HasOnlyCashback) {
  auto result = ShouldShowCostDetails(Decimal{0}, UserInfo{false, true},
                                      build_exp_data());
  ASSERT_FALSE(result);
}

TEST(ShouldShowCashbackCost, ExpOn) {
  auto result = ShouldShowCostDetails(Decimal{0}, UserInfo{false, false},
                                      build_exp_data(std::vector<std::string>{
                                          "plus_without_cashback_in_totw"}));
  ASSERT_TRUE(result);
}

TEST(ShouldShowCashbackCost, ExpOff) {
  auto result = ShouldShowCostDetails(Decimal{0}, UserInfo{false, false},
                                      build_exp_data());
  ASSERT_FALSE(result);
}

TEST(BuildCashbackInfo, HappyPath) {
  auto cashback_accessor =
      plus::MockCashbackAccessor(plus::Cashback{Decimal(34)});
  CashbackInfoDeps deps{
      dynamic_config::GetDefaultSnapshot(),
      build_exp_data(std::vector<std::string>{
          "plus_without_cashback_in_totw", "plus_cashback_in_totw",
          "plus_notifications_in_totw", "plus_totw_attributed_text"}),
      cashback_accessor};
  CashbackInfoInput input{};

  auto result = BuildCashbackInfo(deps, input);
  ASSERT_TRUE(result.show_cost_details_cashback);
  ASSERT_EQ(result.cashback, Decimal(34));
  ASSERT_TRUE(result.notifications.cashback.show_notification);
  ASSERT_EQ(result.notifications.cashback.type, "cashback");
  ASSERT_EQ(result.notifications.cashback.text_key,
            "taxiontheway.notifications.cashback.text");
  ASSERT_TRUE(result.show_cost_details);
  ASSERT_EQ(result.cost_details.action, std::nullopt);
  ASSERT_EQ(result.cost_details.text,
            "taxiontheway.cashback.title.with_cashback");
}

TEST(BuildCashbackInfo, NoExpsMatched) {
  auto cashback_accessor =
      plus::MockCashbackAccessor(plus::Cashback{Decimal(44)});
  CashbackInfoDeps deps{dynamic_config::GetDefaultSnapshot(), build_exp_data(),
                        cashback_accessor};
  CashbackInfoInput input{};

  auto result = BuildCashbackInfo(deps, input);
  ASSERT_FALSE(result.show_cost_details_cashback);
  ASSERT_FALSE(result.notifications.cashback.show_notification);
  ASSERT_FALSE(result.show_cost_details);
}

}  // namespace internal_totw::info::cashback
