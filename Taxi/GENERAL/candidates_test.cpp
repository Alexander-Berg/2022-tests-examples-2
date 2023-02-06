#include "candidates.hpp"

#include <vector>

#include <defs/api/api.hpp>
#include <userver/utest/utest.hpp>

#include <constants/payment_methods.hpp>

namespace models::candidates {

TEST(IsPaymentMethodExistsTest, IsEmpty) {
  EXPECT_EQ(IsPaymentMethodExists(std::vector<handlers::DriverPaymentMethod>{},
                                  {constants::payment_methods::kCash}),
            false);
  EXPECT_EQ(IsPaymentMethodExists(
                std::vector<handlers::DriverPaymentMethod>{
                    handlers::DriverPaymentMethod::kCash,
                    handlers::DriverPaymentMethod::kCard},
                {}),
            false);
}

TEST(IsPaymentMethodExistsTest, IsCashOnly) {
  EXPECT_EQ(IsPaymentMethodExists(
                std::vector<handlers::DriverPaymentMethod>{
                    handlers::DriverPaymentMethod::kCash},
                {constants::payment_methods::kCash}),
            true);
  EXPECT_EQ(IsPaymentMethodExists(
                std::vector<handlers::DriverPaymentMethod>{
                    handlers::DriverPaymentMethod::kCash},
                {constants::payment_methods::kCard}),
            false);
  EXPECT_EQ(IsPaymentMethodExists(
                std::vector<handlers::DriverPaymentMethod>{
                    handlers::DriverPaymentMethod::kCash},
                {constants::payment_methods::kCard,
                 constants::payment_methods::kCash}),
            false);
}

TEST(IsPaymentMethodExistsTest, IsCardOnly) {
  EXPECT_EQ(IsPaymentMethodExists(
                std::vector<handlers::DriverPaymentMethod>{
                    handlers::DriverPaymentMethod::kCard},
                {constants::payment_methods::kCard}),
            true);

  EXPECT_EQ(IsPaymentMethodExists(
                std::vector<handlers::DriverPaymentMethod>{
                    handlers::DriverPaymentMethod::kCard},
                {constants::payment_methods::kCard,
                 constants::payment_methods::kCoupon}),
            true);

  EXPECT_EQ(IsPaymentMethodExists(
                std::vector<handlers::DriverPaymentMethod>{
                    handlers::DriverPaymentMethod::kCard},
                {constants::payment_methods::kCorp}),
            true);
  EXPECT_EQ(IsPaymentMethodExists(
                std::vector<handlers::DriverPaymentMethod>{
                    handlers::DriverPaymentMethod::kCard},
                {constants::payment_methods::kCash}),
            false);
  EXPECT_EQ(
      IsPaymentMethodExists(
          std::vector<handlers::DriverPaymentMethod>{
              handlers::DriverPaymentMethod::kCash},
          {constants::payment_methods::kCorp, constants::payment_methods::kCash,
           constants::payment_methods::kCard}),
      false);
}

TEST(IsPaymentMethodExistsTest, IsCashAndCard) {
  EXPECT_EQ(IsPaymentMethodExists(
                std::vector<handlers::DriverPaymentMethod>{
                    handlers::DriverPaymentMethod::kCash,
                    handlers::DriverPaymentMethod::kCard},
                {constants::payment_methods::kCash,
                 constants::payment_methods::kCard}),
            true);
  EXPECT_EQ(IsPaymentMethodExists(
                std::vector<handlers::DriverPaymentMethod>{
                    handlers::DriverPaymentMethod::kCash,
                    handlers::DriverPaymentMethod::kCard},
                {constants::payment_methods::kCard}),
            false);
  EXPECT_EQ(IsPaymentMethodExists(
                std::vector<handlers::DriverPaymentMethod>{
                    handlers::DriverPaymentMethod::kCash,
                    handlers::DriverPaymentMethod::kCard},
                {constants::payment_methods::kCash}),
            false);
}

}  // namespace models::candidates
