#include <gtest/gtest.h>

#include <ctime>
#include <random>

#include <models/billing/payment_oebs.hpp>

namespace models::billing {

namespace {

std::mt19937 mt_rand(std::time(0));

std::string RandomString() {
  if (mt_rand() == 0) {
    return "YA_NETTING";
  }

  static const char alphabet[] = "abcdefgh";
  std::string s;
  for (std::size_t i = 0; i < 4; ++i) {
    s += alphabet[mt_rand() % (sizeof(alphabet) - 1)];
  }
  return s;
}

std::optional<std::string> RandomOptionalString() {
  if (mt_rand() == 0) {
    return std::nullopt;
  }

  return RandomString();
}

TimePoint RandomTimePoint() {
  return TimePoint{std::chrono::seconds(mt_rand() % 1000000)};
}

std::optional<TimePoint> RandomOptionalTimePoint() {
  if (mt_rand() == 0) {
    return std::nullopt;
  }
  return RandomTimePoint();
}

OebsPaymentDetail CreateDetail(std::optional<std::string> order_id,
                               std::optional<TimePoint> payment_time,
                               std::string product) {
  OebsPaymentDetail detail;
  detail.order_id = std::move(order_id);
  detail.payment_time = std::move(payment_time);
  detail.product = std::move(product);
  return detail;
}

OebsPaymentDetail RandomDetails() {
  return CreateDetail(RandomOptionalString(), RandomOptionalTimePoint(),
                      RandomString());
}

}  // namespace

TEST(PaymentOebsTest, SortRandom) {
  std::vector<OebsPaymentDetail> details(10000);
  for (std::size_t i = 0; i < details.size(); ++i) {
    details[i] = RandomDetails();
  }
  std::sort(details.begin(), details.end(), CompareOebsTransactions);
}

TEST(PaymentOebsTest, Compare1) {
  OebsPaymentDetail details1 = CreateDetail(
      "105", TimePoint{std::chrono::seconds(10003000)}, "orders_cost");
  OebsPaymentDetail details2 = CreateDetail(
      std::nullopt, TimePoint{std::chrono::seconds(10003000)}, "orders_cost");
  ASSERT_EQ(CompareOebsTransactions(details1, details2), true);
  ASSERT_EQ(CompareOebsTransactions(details2, details1), false);
}

TEST(PaymentOebsTest, Compare2) {
  OebsPaymentDetail details1 = CreateDetail(
      std::nullopt, TimePoint{std::chrono::seconds(10003000)}, "orders_cost");
  OebsPaymentDetail details2 = CreateDetail(
      std::nullopt, TimePoint{std::chrono::seconds(10003000)}, "orders_cost");
  ASSERT_EQ(CompareOebsTransactions(details1, details2), false);
}

TEST(PaymentOebsTest, Compare3) {
  OebsPaymentDetail details1 = CreateDetail(
      std::nullopt, TimePoint{std::chrono::seconds(10003000)}, "orders_cost");
  OebsPaymentDetail details2 = CreateDetail(
      std::nullopt, TimePoint{std::chrono::seconds(10003000)}, "commission");
  ASSERT_EQ(CompareOebsTransactions(details1, details2), false);
}

TEST(PaymentOebsTest, Compare4) {
  OebsPaymentDetail details1 = CreateDetail(
      std::nullopt, TimePoint{std::chrono::seconds(10003000)}, "YA_NETTING");
  OebsPaymentDetail details2 = CreateDetail(
      std::nullopt, TimePoint{std::chrono::seconds(10003000)}, "commission");
  ASSERT_EQ(CompareOebsTransactions(details1, details2), true);
}

TEST(PaymentOebsTest, Compare5) {
  OebsPaymentDetail details1 = CreateDetail(
      std::nullopt, TimePoint{std::chrono::seconds(10003000)}, "orders_cost");
  OebsPaymentDetail details2 = CreateDetail(
      std::nullopt, TimePoint{std::chrono::seconds(10003000)}, "details_other");
  ASSERT_EQ(CompareOebsTransactions(details1, details2), true);
}

TEST(PaymentOebsTest, Compare6) {
  OebsPaymentDetail details1 = CreateDetail(
      "105", TimePoint{std::chrono::seconds(10003000)}, "orders_cost");
  OebsPaymentDetail details2 = CreateDetail("105", std::nullopt, "commission");
  ASSERT_EQ(CompareOebsTransactions(details1, details2), true);
  ASSERT_EQ(CompareOebsTransactions(details2, details1), false);
  ASSERT_EQ(CompareOebsTransactions(details2, details2), false);
}

TEST(PaymentOebsTest, Compare7) {
  OebsPaymentDetail details1 = CreateDetail(
      "102", TimePoint{std::chrono::seconds(10005000)}, "orders_cost");
  OebsPaymentDetail details2 = CreateDetail(
      "104", TimePoint{std::chrono::seconds(10003000)}, "orders_cost");
  ASSERT_EQ(CompareOebsTransactions(details1, details2), true);
  ASSERT_EQ(CompareOebsTransactions(details2, details1), false);
}

TEST(PaymentOebsTest, Compare8) {
  OebsPaymentDetail details1 = CreateDetail(
      "104", TimePoint{std::chrono::seconds(10003000)}, "orders_cost");
  OebsPaymentDetail details2 = CreateDetail(
      "102", TimePoint{std::chrono::seconds(10003000)}, "orders_cost");
  ASSERT_EQ(CompareOebsTransactions(details1, details2), true);
  ASSERT_EQ(CompareOebsTransactions(details2, details1), false);
}

}  // namespace models::billing
