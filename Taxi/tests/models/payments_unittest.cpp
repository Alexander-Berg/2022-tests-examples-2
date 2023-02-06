#include "models/payments.hpp"

#include <gtest/gtest.h>

TEST(TestInnerCost, CostToInner) {
  EXPECT_EQ(models::payments::CostToInner(1234.5678), 12345678);
}

TEST(TestInnerCost, InnerToCost) {
  EXPECT_EQ(models::payments::InnerToCost(12345678), 1234.5678);
}

TEST(TestParsers, ParseRefundStatus) {
  EXPECT_EQ(models::payments::parser::ParseRefundStatus("refund_pending"),
            models::payments::RefundStatus::REFUND_PENDING);
  EXPECT_EQ(models::payments::parser::ParseRefundStatus("refund_success"),
            models::payments::RefundStatus::REFUND_SUCCESS);
  EXPECT_EQ(models::payments::parser::ParseRefundStatus("refund_fail"),
            models::payments::RefundStatus::REFUND_FAIL);
  EXPECT_EQ(models::payments::parser::ParseRefundStatus("unknown"),
            models::payments::RefundStatus::UNKNOWN);
}

TEST(TestParsers, ParseTransactionStatus) {
  EXPECT_EQ(models::payments::parser::ParseTransactionStatus("hold_init"),
            models::payments::TransactionStatus::HOLD_INIT);
  EXPECT_EQ(models::payments::parser::ParseTransactionStatus("hold_pending"),
            models::payments::TransactionStatus::HOLD_PENDING);
  EXPECT_EQ(models::payments::parser::ParseTransactionStatus("hold_success"),
            models::payments::TransactionStatus::HOLD_SUCCESS);
  EXPECT_EQ(models::payments::parser::ParseTransactionStatus("hold_resize"),
            models::payments::TransactionStatus::HOLD_RESIZE);
  EXPECT_EQ(models::payments::parser::ParseTransactionStatus("hold_fail"),
            models::payments::TransactionStatus::HOLD_FAIL);
  EXPECT_EQ(models::payments::parser::ParseTransactionStatus("clear_init"),
            models::payments::TransactionStatus::CLEAR_INIT);
  EXPECT_EQ(models::payments::parser::ParseTransactionStatus("clear_pending"),
            models::payments::TransactionStatus::CLEAR_PENDING);
  EXPECT_EQ(models::payments::parser::ParseTransactionStatus("clear_success"),
            models::payments::TransactionStatus::CLEAR_SUCCESS);
  EXPECT_EQ(models::payments::parser::ParseTransactionStatus("clear_fail"),
            models::payments::TransactionStatus::CLEAR_FAIL);
  EXPECT_EQ(models::payments::parser::ParseTransactionStatus("refund_pending"),
            models::payments::TransactionStatus::REFUND_PENDING);
  EXPECT_EQ(models::payments::parser::ParseTransactionStatus("refund_fail"),
            models::payments::TransactionStatus::REFUND_FAIL);
  EXPECT_EQ(models::payments::parser::ParseTransactionStatus("unknown"),
            models::payments::TransactionStatus::UNKNOWN);
}

TEST(TestParsers, ParseSum) {
  mongo::BSONObj doc =
      BSON("ride" << 12345678987654321ll << "tips" << 98765432123456789ll);
  auto result = models::payments::parser::ParseSum(doc);

  EXPECT_EQ(result.ride, 12345678987654321ll);
  EXPECT_EQ(result.tips, 98765432123456789ll);
}

TEST(TestParsers, ParseRefund) {
  mongo::BSONObj doc =
      BSON("sum" << BSON("ride" << 111 << "tips" << 222) << "status"
                 << "refund_success");

  auto result = models::payments::parser::ParseRefund(doc);
  EXPECT_TRUE(result.IsSuccess());
  EXPECT_EQ(result.sum.ride, 111);
  EXPECT_EQ(result.sum.tips, 222);
  EXPECT_EQ(result.status, models::payments::RefundStatus::REFUND_SUCCESS);
}

TEST(TestParsers, ParseTransaction) {
  mongo::BSONObj doc = BSON(
      "sum" << BSON("ride" << 111 << "tips" << 222) << "status"
            << "clear_success"
            << "refunds"
            << BSON_ARRAY(BSON("sum" << BSON("ride" << 333 << "tips" << 444)
                                     << "status"
                                     << "refund_fail")));

  auto result = models::payments::parser::ParseTransaction(doc);
  EXPECT_TRUE(result.IsSuccess());
  EXPECT_EQ(result.sum.ride, 111);
  EXPECT_EQ(result.sum.tips, 222);
  EXPECT_EQ(result.status, models::payments::TransactionStatus::CLEAR_SUCCESS);
  EXPECT_TRUE(result.refunds.size() == 1);
  EXPECT_EQ(result.refunds[0].sum.ride, 333);
  EXPECT_EQ(result.refunds[0].sum.tips, 444);
  EXPECT_EQ(result.refunds[0].status,
            models::payments::RefundStatus::REFUND_FAIL);
}

TEST(TestCalcHoldRefundOrResize, NoTransactions) {
  models::payments::Payable payable = {{10000000, 0}, {}};
  auto result = models::payments::CalcHoldRefundOrResize(payable);
  EXPECT_EQ(result.ride, 10000000);
  EXPECT_EQ(result.tips, 0);
}

TEST(TestCalcHoldRefundOrResize, Failure) {
  models::payments::Payable payable = {
      {10000000, 0},
      {models::payments::Transaction{
          models::payments::TransactionStatus::HOLD_FAIL,
          {10000000, 0},
          {},
          "",
          "",
          "",
          false,
          boost::none}}};
  auto result = models::payments::CalcHoldRefundOrResize(payable);
  EXPECT_EQ(result.ride, 10000000);
  EXPECT_EQ(result.tips, 0);
}

TEST(TestCalcHoldRefundOrResize, Success) {
  models::payments::Payable payable = {
      {10000000, 0},
      {models::payments::Transaction{
          models::payments::TransactionStatus::HOLD_SUCCESS,
          {10000000, 0},
          {},
          "",
          "",
          "",
          false,
          boost::none}}};
  auto result = models::payments::CalcHoldRefundOrResize(payable);
  EXPECT_EQ(result.ride, 0);
  EXPECT_EQ(result.tips, 0);
}

TEST(TestCalcHoldRefundOrResize, Fail) {
  models::payments::Payable payable = {
      {10000000, 0},
      {models::payments::Transaction{
          models::payments::TransactionStatus::HOLD_FAIL,
          {10000000, 0},
          {},
          "",
          "",
          "",
          false,
          boost::none}}};
  auto result = models::payments::CalcHoldRefundOrResize(payable);
  EXPECT_EQ(result.ride, 10000000);
  EXPECT_EQ(result.tips, 0);
}

TEST(TestCalcHoldRefundOrResize, FailThenSuccess) {
  models::payments::Payable payable = {
      {10000000, 0},
      {models::payments::Transaction{
           models::payments::TransactionStatus::HOLD_FAIL,
           {10000000, 0},
           {},
           "",
           "",
           "",
           false,
           boost::none},
       models::payments::Transaction{
           models::payments::TransactionStatus::HOLD_SUCCESS,
           {10000000, 0},
           {},
           "",
           "",
           "",
           false,
           boost::none}}};
  auto result = models::payments::CalcHoldRefundOrResize(payable);
  EXPECT_EQ(result.ride, 0);
  EXPECT_EQ(result.tips, 0);
}

TEST(TestCalcHoldRefundOrResize, SuccessRefund) {
  models::payments::Payable payable = {
      {10000000, 0},
      {models::payments::Transaction{
          models::payments::TransactionStatus::HOLD_SUCCESS,
          {10000000, 0},
          {models::payments::Refund{
              models::payments::RefundStatus::REFUND_SUCCESS, {5000000, 0}}},
          "",
          "",
          "",
          false,
          boost::none}}};
  auto result = models::payments::CalcHoldRefundOrResize(payable);
  EXPECT_EQ(result.ride, 5000000);
  EXPECT_EQ(result.tips, 0);
}

TEST(TestCalcHoldRefundOrResize, SuccessRefundFail) {
  models::payments::Payable payable = {
      {10000000, 0},
      {models::payments::Transaction{
          models::payments::TransactionStatus::HOLD_SUCCESS,
          {10000000, 0},
          {models::payments::Refund{models::payments::RefundStatus::REFUND_FAIL,
                                    {5000000, 0}}},
          "",
          "",
          "",
          false,
          boost::none}}};
  auto result = models::payments::CalcHoldRefundOrResize(payable);
  EXPECT_EQ(result.ride, 0);
  EXPECT_EQ(result.tips, 0);
}

TEST(TestCalcHoldRefundOrResize, SuccessResize) {
  models::payments::Payable payable = {
      {10000000, 0},
      {models::payments::Transaction{
          models::payments::TransactionStatus::HOLD_SUCCESS,
          {15000000, 0},
          {},
          "",
          "",
          "",
          false,
          boost::none}}};
  auto result = models::payments::CalcHoldRefundOrResize(payable);
  EXPECT_EQ(result.ride, -5000000);
  EXPECT_EQ(result.tips, 0);
}
