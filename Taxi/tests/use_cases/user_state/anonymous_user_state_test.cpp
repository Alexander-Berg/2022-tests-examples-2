#include <userver/utest/utest.hpp>

#include <testing/taxi_config.hpp>

#include "use_cases/user_state/anonymous_user_state.hpp"

#include "tests/core/models_test.hpp"
#include "tests/internal/models_test.hpp"
#include "tests/use_cases/user_state/output_models_test.hpp"

namespace sweet_home::user_state {

namespace {

AnonymousStateContext PrepareContext(bool has_cashback = false) {
  auto subscription = tests::MakePlusSubscription(
      "", subscription::PurchaseStatus::kNotAvailable, has_cashback);

  auto experiments = tests::MakeExperiments();

  return {subscription, kDefaultSdkClient, experiments,
          dynamic_config::GetDefaultSnapshot(),
          tests::defaults::kDefaultLocale};
}

}  // namespace

TEST(TestAnonymousState, HappyPath) {
  auto result = GetStateOfAnonymousUser(PrepareContext(), kDefaultServiceId);

  auto expected_subscription = tests::output_models::MakeSubscription(
      "", subscription::PurchaseStatus::kNotAvailable, false);

  ASSERT_EQ(result.subscription, expected_subscription);
  auto expected_notifications = tests::output_models::MakeNotifications(1);
  ASSERT_EQ(result.notifications, expected_notifications);

  ASSERT_TRUE(result.settings.settings.empty());
  ASSERT_TRUE(result.wallets.empty());
}

}  // namespace sweet_home::user_state
