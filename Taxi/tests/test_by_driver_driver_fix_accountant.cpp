#include <userver/utest/utest.hpp>

#include <iostream>
#include <memory>
#include <string>
#include <vector>

#include "by_driver/accountants/driver_fix.hpp"
#include "by_driver/entities.hpp"
#include "common/utils/types.hpp"

namespace bsx = billing_subventions_x;
using BalanceChange = bsx::by_driver::BalanceChange;
using DfAccountingData = bsx::by_driver::driver_fix::AccountingData;
using DfReport = bsx::by_driver::driver_fix::Report;
using DfAccountant = bsx::by_driver::accountants::DriverFixAccountant;
using Numeric = bsx::types::Numeric;

class DriverFixAccountantTest : public ::testing::Test {
  void SetUp() override {
    DfAccountingData data{{}, "RUB", "6", "28", "496", "8128"};
    accountant_ = std::make_unique<DfAccountant>(std::move(data));
  }

 protected:
  std::unique_ptr<DfAccountant> accountant_;
};

namespace billing_subventions_x::by_driver::driver_fix {
bool operator==(const Report& lhs, const Report& rhs) {
  return lhs.currency == rhs.currency && lhs.payoff == rhs.payoff &&
         lhs.online_minutes == rhs.online_minutes &&
         lhs.cash_commission == rhs.cash_commission && lhs.cash == rhs.cash &&
         lhs.guarantee == rhs.guarantee && lhs.total_income == rhs.total_income;
}
}  // namespace billing_subventions_x::by_driver::driver_fix

namespace std {
std::ostream& operator<<(
    std::ostream& os,
    const billing_subventions_x::by_driver::driver_fix::Report& r) {
  return os << r.currency << ", " << r.payoff << r.online_minutes
            << r.cash_commission << r.cash << r.guarantee << r.total_income;
}

}  // namespace std

TEST_F(DriverFixAccountantTest, ZerosWhenNoBalances) {
  auto actual = std::get<DfReport>(accountant_->MakeReport({}));
  auto expected = DfReport{"RUB"};
  EXPECT_EQ(actual, expected);
}

TEST_F(DriverFixAccountantTest, PayoffIsZeroIfIncomeGreaterGuarantee) {
  std::vector<BalanceChange> balances{
      BalanceChange{"guarantee", "RUB", Numeric{1}},
      BalanceChange{"income", "RUB", Numeric{2}}};
  auto actual = std::get<DfReport>(accountant_->MakeReport(balances));
  EXPECT_EQ(actual.payoff, Numeric{0});
}

TEST_F(DriverFixAccountantTest,
       CashCommissionIsZeroIfGuaranteeGreaterThanCashIncome) {
  std::vector<BalanceChange> balances{
      BalanceChange{"guarantee", "RUB", Numeric{2}},
      BalanceChange{"income/cash", "RUB", Numeric{1}}};
  auto actual = std::get<DfReport>(accountant_->MakeReport(balances));
  EXPECT_EQ(actual.cash_commission, Numeric{0});
}

TEST_F(DriverFixAccountantTest, DifferencesPassedToReport) {
  std::vector<BalanceChange> balances{
      BalanceChange{"income", "RUB", Numeric{1}},
      BalanceChange{"guarantee", "RUB", Numeric{2}},
      BalanceChange{"guarantee/on_order", "RUB", Numeric{3}},
      BalanceChange{"time/free_minutes", "XXX", Numeric{4}},
      BalanceChange{"time/on_order_minutes", "XXX", Numeric{5}},
      BalanceChange{"income/cash", "RUB", Numeric{6}},
      BalanceChange{"discounts", "RUB", Numeric{7}},
      BalanceChange{"promocodes/marketing", "RUB", Numeric{8}},
      BalanceChange{"promocodes/support", "RUB", Numeric{9}}};

  auto actual = std::get<DfReport>(accountant_->MakeReport(balances));
  EXPECT_EQ(actual.online_minutes, Numeric{4 + 5});
  EXPECT_EQ(actual.cash, Numeric{6});
  EXPECT_EQ(actual.guarantee, Numeric{2});
  EXPECT_EQ(actual.total_income, Numeric{1 + 7 + 8 + 9});
}
