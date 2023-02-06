#include "payment_system.hpp"

#include <defs/all_definitions.hpp>
#include <discounts/models/error.hpp>
#include <userver/utest/utest.hpp>

UTEST(GetPaymentSystem, Ok) {
  EXPECT_EQ(
      utils::GetPaymentSystem(std::nullopt, {"220000", "220001", "220010"}),
      utils::PaymentSystem::kMir);
  EXPECT_EQ(utils::GetPaymentSystem(std::nullopt, {"609998", "652110"}),
            utils::PaymentSystem::kRupay);
  EXPECT_EQ(utils::GetPaymentSystem(std::nullopt, {"639999", "670004"}),
            utils::PaymentSystem::kMaestro);
  EXPECT_EQ(utils::GetPaymentSystem(std::nullopt, {"272099", "510000"}),
            utils::PaymentSystem::kMastercard);
  EXPECT_EQ(utils::GetPaymentSystem(std::nullopt, {"400000"}),
            utils::PaymentSystem::kVisa);
  EXPECT_EQ(
      utils::GetPaymentSystem(utils::PaymentSystem::kMir, {"639999", "510000"}),
      utils::PaymentSystem::kMir);
}

UTEST(GetPaymentSystem, Errors) {
  using Error = discounts::models::Error;
  EXPECT_THROW(utils::GetPaymentSystem(std::nullopt, {}), Error)
      << "Empty bins";
  EXPECT_THROW(utils::GetPaymentSystem(std::nullopt, {"220000f"}), Error)
      << "Invalid bin";
  EXPECT_THROW(utils::GetPaymentSystem(utils::PaymentSystem::kMir, {"220000f"}),
               Error)
      << "Invalid bin";
  EXPECT_THROW(utils::GetPaymentSystem(std::nullopt, {"Invalid"}), Error)
      << "Invalid bin";
  EXPECT_THROW(utils::GetPaymentSystem(std::nullopt, {"000000"}), Error)
      << "Invalid bin";
  EXPECT_THROW(utils::GetPaymentSystem(std::nullopt, {"220000", "652110"}),
               Error)
      << "From different payment systems";
}
