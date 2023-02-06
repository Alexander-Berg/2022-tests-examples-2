#include <userver/utest/utest.hpp>

#include <fmt/format.h>

#include <models/finstmt.hpp>

namespace models {

//
// FinStmtCalcPayTest

struct FinStmtCalcPayTestParam {
  std::string balance_amount{};
  std::string balance_limit{};
  std::string pay_mult_of{};
  std::string pay_minimum{};
  std::string pay_maximum{};
  std::string pay_amount{};
};

std::ostream& operator<<(std::ostream& os,
                         const FinStmtCalcPayTestParam& param) {
  return os << fmt::format(
             FMT_STRING(R"fmt(("{}", "{}", "{}", "{}", "{}", "{}"))fmt"),
             param.balance_amount, param.balance_limit, param.pay_mult_of,
             param.pay_minimum, param.pay_maximum, param.pay_amount);
}

class FinStmtCalcPayTest
    : public ::testing::TestWithParam<FinStmtCalcPayTestParam> {};

const FinStmtCalcPayTestParam FinStmtCalcPayTest_Calculate[] = {
    // clang-format off
    {"-99", "100",  "3", "250", "750",   "0"},
    {  "0", "100",  "3", "250", "750",   "0"},
    {"100", "100",  "3", "250", "750",   "0"},
    {"500", "100",  "3", "250", "750", "399"},
    {"500", "-99",  "3", "250", "750", "498"},
    {"500",   "0",  "3", "250", "750", "498"},
    {"500", "501",  "3", "250", "750",   "0"},
    {"500", "100",  "3", "-99", "750", "399"},
    {"500", "100",  "3",   "0", "750", "399"},
    {"500", "100",  "3", "399", "750", "399"},
    {"500", "100",  "3", "400", "750",   "0"},
    {"500", "100",  "3", "250", "-99",   "0"},
    {"500", "100",  "3", "250",   "0",   "0"},
    {"500", "100",  "3", "250", "254", "252"},
    {"500", "100",  "3", "250", "255", "255"},
    {"500", "100", "-3", "250", "750", "400"},
    {"500", "100",  "0", "250", "750", "400"},
    // check 1'000'000 limit
    {"2000000", "0",        "0",       "0", "5000000", "1000000"},
    {"2000000", "0",  "1000000",  "999999", "5000000", "1000000"},
    {"2000000", "0",  "1000001",       "0", "5000000",       "0"},
    {"2000000", "0",        "3",  "999999", "5000000",  "999999"},
    {"2000000", "0",        "3", "1000000", "5000000",       "0"},
    {"2000000", "0",        "0", "1000000", "5000000", "1000000"},
    {"2000000", "0",        "0", "1000001", "5000000",       "0"},
    // clang-format on
};

TEST_P(FinStmtCalcPayTest, Calculate) {
  const auto& param = GetParam();

  Decimal4 balance_amount{param.balance_amount};
  Decimal4 balance_limit{param.balance_limit};
  Decimal4 pay_mult_of{param.pay_mult_of};
  Decimal4 pay_minimum{param.pay_minimum};
  Decimal4 pay_maximum{param.pay_maximum};
  Decimal4 pay_amount{param.pay_amount};

  FinStmtCalcPay calc_pay{balance_limit, pay_mult_of, pay_minimum, pay_maximum};
  ASSERT_EQ(calc_pay(balance_amount), pay_amount);
}

INSTANTIATE_TEST_SUITE_P(TestValues, FinStmtCalcPayTest,
                         ::testing::ValuesIn(FinStmtCalcPayTest_Calculate));

//
// FinStmtCalcBcmTest

struct FinStmtCalcBcmTestParam {
  std::string pay_amount{};
  std::string bcm_percent{};
  std::string bcm_minimum{};
  std::string bcm_amount{};
};

std::ostream& operator<<(std::ostream& os,
                         const FinStmtCalcBcmTestParam& param) {
  return os << fmt::format(FMT_STRING(R"fmt(("{}", "{}", "{}", "{}"))fmt"),
                           param.pay_amount, param.bcm_percent,
                           param.bcm_minimum, param.bcm_amount);
}

class FinStmtCalcBcmTest
    : public ::testing::TestWithParam<FinStmtCalcBcmTestParam> {};

TEST_P(FinStmtCalcBcmTest, Calculate) {
  const auto& param = GetParam();

  Decimal4 pay_amount{param.pay_amount};
  Decimal4 bcm_percent{param.bcm_percent};
  Decimal4 bcm_minimum{param.bcm_minimum};
  Decimal4 bcm_amount{param.bcm_amount};

  FinStmtCalcBcm calc_bcm{bcm_percent, bcm_minimum};
  ASSERT_EQ(calc_bcm(pay_amount), bcm_amount);
}

const FinStmtCalcBcmTestParam FinStmtCalcBcmTest_Calculate[] = {
    // clang-format off
    {"-99.0000",  "1.0000",  "1.0000",   "0.0000"},
    {"100.0000", "-1.0000",  "0.0000",   "0.0000"},
    {"100.0000", "-1.0000",  "1.0000",   "1.0000"},
    {"100.0000",  "0.0000", "-1.0000",   "0.0000"},
    {"100.0000",  "1.0000", "-1.0000",  "50.0000"},
    {  "0.0000",  "0.0000",  "3.0000",   "0.0000"},
    {  "0.0000",  "0.0500",  "0.0000",   "0.0000"},
    {  "0.0000",  "0.0500",  "3.0000",   "0.0000"},
    {  "1.0000",  "0.0000",  "3.0000",   "1.0000"},
    {  "1.0000",  "0.0500",  "0.0000",   "0.0476"},
    {  "1.0000",  "0.0500",  "3.0000",   "1.0000"},
    {"100.0000",  "0.0000",  "3.0000",   "3.0000"},
    {"100.0000",  "0.0500",  "0.0000",   "4.7619"},
    {"100.0000",  "0.0500",  "3.0000",   "4.7619"},
    // rounding
    {  "1.0026",  "0.1000",  "0.0000",   "0.0911"},  // 0.091145454545455
    {  "1.0027",  "0.1000",  "0.0000",   "0.0912"},  // 0.091154545454545
    {  "1.0028",  "0.1000",  "0.0000",   "0.0912"},  // 0.091163636363636
    // clang-format on
};

INSTANTIATE_TEST_SUITE_P(TestValues, FinStmtCalcBcmTest,
                         ::testing::ValuesIn(FinStmtCalcBcmTest_Calculate));

}  // namespace models
