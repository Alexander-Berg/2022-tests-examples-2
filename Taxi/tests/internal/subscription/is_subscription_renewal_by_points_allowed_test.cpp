#include <gtest/gtest.h>

#include "internal/subscription/subscription.hpp"

#include "tests/core/models_test.hpp"
#include "tests/internal/models_test.hpp"
#include "tests/mocks/subscription_service.hpp"

namespace sweet_home::subscription {

namespace {

const std::string kDefaultYandexUid = "default_yandex_uid";

auto get_subscription_info_default = [](const std::string&) {
  core::SubscriptionInfo subscription_info;
  subscription_info.type = "native-auto-subscription";
  subscription_info.end_time = std::chrono::system_clock::now();
  subscription_info.is_renewal_by_points_allowed = true;
  return subscription_info;
};

SubscriptionDeps PrepareDeps(
    const mocks::GetSubscriptionInfoHandler& get_subscription_info_handler =
        get_subscription_info_default) {
  SubscriptionDeps deps{
      std::make_shared<mocks::SubscriptionServiceMock>(
          nullptr, nullptr, nullptr, get_subscription_info_handler),
      tests::MakeExperiments()};

  return deps;
}

UserInfo MakeUserInfo(bool has_plus, bool has_cashback_plus = true) {
  return {kDefaultYandexUid, has_plus, has_cashback_plus};
}

}  // namespace

TEST(CanRenewalSubForPoints, TestSuccessAbilityForRenewalSub) {
  const auto deps = PrepareDeps();

  // Checking for has_plus == true
  auto user_info = MakeUserInfo(true);
  auto ans = GetSubscriptionInfo(deps, user_info);
  ASSERT_EQ(ans->is_renewal_by_points_allowed, true);

  user_info = MakeUserInfo(true, false);
  ans = GetSubscriptionInfo(deps, user_info);
  ASSERT_EQ(ans->is_renewal_by_points_allowed, true);

  // Checking for has_plus == false
  user_info = MakeUserInfo(false, false);
  ans = GetSubscriptionInfo(deps, user_info);
  ASSERT_EQ(ans->is_renewal_by_points_allowed, true);

  user_info = MakeUserInfo(false, true);
  ans = GetSubscriptionInfo(deps, user_info);
  ASSERT_EQ(ans->is_renewal_by_points_allowed, true);
}

TEST(CanRenewalSubForPoints, TestMediabillingError) {
  auto get_subscription_info_handler =
      [](const std::string&) -> core::SubscriptionInfo {
    throw core::MediabillingError("i am error");
  };
  const auto deps = PrepareDeps(get_subscription_info_handler);

  // Checking for has_plus == true
  auto user_info = MakeUserInfo(true);
  auto ans = GetSubscriptionInfo(deps, user_info);
  ASSERT_EQ(ans ? ans->is_renewal_by_points_allowed : false, false);

  user_info = MakeUserInfo(true, false);
  ans = GetSubscriptionInfo(deps, user_info);
  ASSERT_EQ(ans ? ans->is_renewal_by_points_allowed : false, false);

  // Checking for has_plus == false
  user_info = MakeUserInfo(false);
  ans = GetSubscriptionInfo(deps, user_info);
  ASSERT_EQ(ans ? ans->is_renewal_by_points_allowed : false, true);

  user_info = MakeUserInfo(false, false);
  ans = GetSubscriptionInfo(deps, user_info);
  ASSERT_EQ(ans ? ans->is_renewal_by_points_allowed : false, true);
}

TEST(CanRenewalSubForPoints, TestMediabillingReturnFalse) {
  auto get_subscription_info_handler = [](const std::string&) {
    core::SubscriptionInfo subscription_info;
    subscription_info.type = "native-auto-subscription";
    subscription_info.end_time = std::chrono::system_clock::now();
    subscription_info.is_renewal_by_points_allowed = false;
    return subscription_info;
  };
  const auto deps = PrepareDeps(get_subscription_info_handler);

  // Checking for has_plus == true
  auto user_info = MakeUserInfo(true);
  auto ans = GetSubscriptionInfo(deps, user_info);
  ASSERT_EQ(ans->is_renewal_by_points_allowed, false);

  user_info = MakeUserInfo(true, false);
  ans = GetSubscriptionInfo(deps, user_info);
  ASSERT_EQ(ans->is_renewal_by_points_allowed, false);

  // Checking for has_plus == false
  user_info = MakeUserInfo(false);
  ans = GetSubscriptionInfo(deps, user_info);
  ASSERT_EQ(ans->is_renewal_by_points_allowed, true);

  user_info = MakeUserInfo(false, false);
  ans = GetSubscriptionInfo(deps, user_info);
  ASSERT_EQ(ans->is_renewal_by_points_allowed, true);
}

}  // namespace sweet_home::subscription
