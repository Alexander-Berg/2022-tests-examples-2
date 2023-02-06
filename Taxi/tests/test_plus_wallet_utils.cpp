#include <userver/utest/utest.hpp>

#include <utils/plus_wallet.hpp>

TEST(TestExperimentsPlusStatus, TestNoPlus) {
  passenger_authorizer::models::AuthContext auth_context;
  auth_context.flags.has_plus_cashback = false;
  auth_context.flags.has_ya_plus = false;
  ASSERT_EQ(utils::plus_wallet::GetExperimentsPlusStatus(auth_context),
            "no_plus");
}

TEST(TestExperimentsPlusStatus, TestPlusDiscount) {
  passenger_authorizer::models::AuthContext auth_context;
  auth_context.flags.has_plus_cashback = false;
  auth_context.flags.has_ya_plus = true;
  ASSERT_EQ(utils::plus_wallet::GetExperimentsPlusStatus(auth_context),
            "plus_discount");
}

TEST(TestExperimentsPlusStatus, TestPlusCashback) {
  passenger_authorizer::models::AuthContext auth_context;
  auth_context.flags.has_plus_cashback = true;
  auth_context.flags.has_ya_plus = true;
  ASSERT_EQ(utils::plus_wallet::GetExperimentsPlusStatus(auth_context),
            "plus_cashback");
}
