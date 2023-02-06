#include <gtest/gtest.h>

#include <ctime>
#include <random>

#include <models/billing/payment_billing.hpp>

namespace models::billing {

namespace {

std::mt19937 mt_rand(std::time(0));

TimePoint RandomTimePoint() {
  return TimePoint{std::chrono::seconds(mt_rand() % 1000000)};
}

double RandomDouble(const double scale) {
  double d = (double)rand() / RAND_MAX;
  return d * scale;
}

BillingTransaction RandomTransaction() {
  BillingTransaction transaction;
  transaction.payment_time = RandomTimePoint();
  transaction.handling_time = RandomTimePoint();
  transaction.sum = RandomDouble(10000);
  return transaction;
}

}  // namespace

TEST(PaymentBillingTest, Sort) {
  std::vector<BillingTransaction> transactions(10000);
  for (std::size_t i = 0; i < transactions.size(); ++i) {
    transactions[i] = RandomTransaction();
  }
  std::sort(transactions.begin(), transactions.end(),
            CompareBillingTransactions);
}

}  // namespace models::billing
