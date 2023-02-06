#include <memory>
#include <utility>

#include <gmock/gmock.h>
#include <userver/utest/utest.hpp>

#include <userver/utils/datetime.hpp>

#include "by_driver/accountants/goal.hpp"
#include "by_driver/entities.hpp"
#include "common/utils/types.hpp"
#include "smart_rules/types/goal/counter.hpp"

namespace bsx = billing_subventions_x;
using AccountsKey = bsx::by_driver::AccountsKey;
using BalanceChange = bsx::by_driver::BalanceChange;
using GoalAccountant = bsx::by_driver::accountants::GoalAccountant;
using GoalAccountantData = bsx::by_driver::goal::AccountingData;
using GoalStep = bsx::types::GoalStep;
using Numeric = bsx::types::Numeric;
using Report = bsx::by_driver::goal::Report;
using TimeInterval = bsx::by_driver::TimeInterval;

class AGoalAccountant : public ::testing::Test {
  void SetUp() override {
    interval_ = TimeInterval{
        utils::datetime::Stringtime("2021-01-01T12:00:00Z"),
        utils::datetime::Stringtime("2021-01-07T15:00:00Z"),
    };
    auto steps = std::vector<GoalStep>{GoalStep{10, "100.0000"}};
    auto data =
        GoalAccountantData{interval_, "<counter>", "RUB", "<udid>", steps};
    accountant_ = std::make_unique<GoalAccountant>(std::move(data));
  }

 protected:
  TimeInterval interval_;
  std::unique_ptr<GoalAccountant> accountant_;
};

namespace billing_subventions_x::by_driver::goal {
bool operator==(const Report& lhs, const Report& rhs) {
  return lhs.counter == rhs.counter && lhs.num_orders == rhs.num_orders &&
         lhs.currency == rhs.currency && lhs.payoff == rhs.payoff &&
         lhs.period == rhs.period;
}
}  // namespace billing_subventions_x::by_driver::goal

TEST_F(AGoalAccountant, HasAccountsKey) {
  auto expected =
      AccountsKey{"unique_driver_id/<udid>", "subvention/counter/<counter>"};
  ASSERT_THAT(accountant_->GetAccountsKey(), ::testing::Eq(expected));
}

TEST_F(AGoalAccountant, HasSubAccounts) {
  ASSERT_THAT(accountant_->GetSubAccounts(),
              ::testing::ElementsAre("num_orders"));
}

TEST_F(AGoalAccountant, HasPeriodSet) {
  ASSERT_THAT(accountant_->GetPeriod(), ::testing::Eq(interval_));
}

TEST_F(AGoalAccountant, ReturnsReportWithZeroPayoffWhenNoBalanceChanges) {
  auto report = accountant_->MakeReport({});
  auto expected = Report{"<counter>", 0, "RUB", Numeric{0}, interval_};
  ASSERT_THAT(std::get<Report>(report), ::testing::Eq(expected));
}

TEST_F(AGoalAccountant, ReturnsReportWithZeroPayoffWhenGoalNotFulfilled) {
  std::vector<BalanceChange> balances{
      BalanceChange{"num_orders", "RUB", Numeric{5}}};
  auto report = accountant_->MakeReport(balances);
  auto expected = Report{"<counter>", 5, "RUB", Numeric{0}, interval_};
  ASSERT_THAT(std::get<Report>(report), ::testing::Eq(expected));
}

TEST_F(AGoalAccountant, ReturnsReportWithNonZeroPayoffWhenGoalFulfilled) {
  std::vector<BalanceChange> balances{
      BalanceChange{"num_orders", "RUB", Numeric{10}}};
  auto report = accountant_->MakeReport(balances);
  auto expected = Report{"<counter>", 10, "RUB", Numeric{100}, interval_};
  ASSERT_THAT(std::get<Report>(report), ::testing::Eq(expected));
}

TEST_F(AGoalAccountant, ReturnsReportWithNonZeroPayoffWhenGoalExceeded) {
  std::vector<BalanceChange> balances{
      BalanceChange{"num_orders", "RUB", Numeric{11}}};
  auto report = accountant_->MakeReport(balances);
  auto expected = Report{"<counter>", 11, "RUB", Numeric{100}, interval_};
  ASSERT_THAT(std::get<Report>(report), ::testing::Eq(expected));
}
