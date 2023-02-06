#include <gtest/gtest.h>

#include "internal/subscription/subscription.hpp"

#include "tests/core/models_test.hpp"
#include "tests/internal/models_test.hpp"  // for function AssertPlusSubscription
#include "tests/mocks/subscription_service.hpp"

namespace sweet_home::subscription {

namespace {
const std::string kCountry = "some_country";
const int32_t kRegionId = 1;
const std::string kPlatform = "android";
const core::SDKPurchaseType kPurchaseType = core::SDKPurchaseType::kNative;
const std::string kTimeZone = "Europe/Moscow";
}  // namespace

namespace {

SubscriptionDeps PrepareDeps(
    const std::optional<mocks::GetAvailableSubscriptionsForUserHandler>&
        available_subscriptions_handler = std::nullopt,
    const std::optional<mocks::GetSubscriptionPriceHandler>&
        get_subscription_price_handler = std::nullopt) {
  SubscriptionDeps deps{
      std::make_shared<mocks::SubscriptionServiceMock>(nullptr, nullptr),
      tests::MakeExperiments()};
  if (available_subscriptions_handler && get_subscription_price_handler) {
    deps.subscription_service =
        std::make_shared<mocks::SubscriptionServiceMock>(
            *available_subscriptions_handler, *get_subscription_price_handler);
  }

  return deps;
}

UserInfo MakeUserInfo(bool has_plus, bool has_cashback_plus) {
  return {"some_id", has_plus, has_cashback_plus};
}

core::MediabillingSubscription MakeMediabillingSubscription(
    const std::string& subscription_id, bool is_trial,
    const core::SubscriptionType type) {
  core::MediabillingSubscription subscription;
  subscription.subscription_id = subscription_id;
  subscription.product_id = "product_" + subscription_id;
  subscription.is_trial = is_trial;
  subscription.type = type;
  return subscription;
}

core::PurchaseContext MakePurhaseContext(
    core::Region region = {kCountry, kRegionId, kTimeZone},
    std::string platform = kPlatform,
    core::SDKPurchaseType purchase_type = kPurchaseType) {
  return core::PurchaseContext{std::move(region), std::move(platform),
                               purchase_type};
}

}  // namespace

TEST(TestGetPlusSubscriptionForUser, HasPlus) {
  auto deps = PrepareDeps();
  auto user_info = MakeUserInfo(true, false);
  const core::PurchaseContext purchase_context = MakePurhaseContext();

  auto result = GetPlusSubscriptionForUser(deps, user_info, purchase_context);

  PlusSubscription expected{"", "", PurchaseStatus::kActive, std::nullopt,
                            false};
  AssertPlusSubscription(result, expected);
}

TEST(TestGetPlusSubscriptionForUser, NoPlusFindAvailableSubscriptions) {
  auto deps = PrepareDeps();
  auto user_info = MakeUserInfo(false, true);

  auto result = GetPlusSubscriptionForUser(deps, user_info, std::nullopt);

  PlusSubscription expected{"", "", PurchaseStatus::kNotAvailable, std::nullopt,
                            true};
  AssertPlusSubscription(result, expected);
}

TEST(TestGetPlusSubscriptionForUser, HasAvailableSubscription) {
  auto get_subscriptions_handler = [](const std::string&,
                                      const core::PurchaseContext&, bool) {
    return std::vector<core::MediabillingSubscription>{
        MakeMediabillingSubscription("plus", false,
                                     core::SubscriptionType::kPlus)};
  };

  auto get_subscription_price_handler = [](const std::string&) {
    return core::Price{decimal64::Decimal<4>{199}, "RUB"};
  };

  auto deps =
      PrepareDeps(get_subscriptions_handler, get_subscription_price_handler);
  auto user_info = MakeUserInfo(false, false);
  auto purchase_context = MakePurhaseContext();

  auto result1 = GetPlusSubscriptionForUser(deps, user_info, purchase_context);

  PlusSubscription expected1{"plus", "product_plus", PurchaseStatus::kAvailable,
                             tests::MakeSubscriptionPrice("199", "RUB"), false};
  AssertPlusSubscription(result1, expected1);

  user_info.has_cashback_plus = true;
  auto result2 = GetPlusSubscriptionForUser(deps, user_info, purchase_context);

  PlusSubscription expected2{"plus", "product_plus", PurchaseStatus::kAvailable,
                             tests::MakeSubscriptionPrice("199", "RUB"), true};
  AssertPlusSubscription(result2, expected2);
}

TEST(TestGetPlusSubscriptionForUser, EmptyAvailableSubscriptions) {
  auto get_subscriptions_handler = [](const std::string&,
                                      const core::PurchaseContext&, bool) {
    return std::vector<core::MediabillingSubscription>{};
  };

  mocks::GetSubscriptionPriceHandler get_subscription_price_handler =
      [](const std::string&) { return std::nullopt; };

  auto deps =
      PrepareDeps(get_subscriptions_handler, get_subscription_price_handler);
  auto user_info = MakeUserInfo(false, false);
  auto purchase_context = MakePurhaseContext();

  auto result = GetPlusSubscriptionForUser(deps, user_info, purchase_context);

  PlusSubscription expected{"", "", PurchaseStatus::kNotAvailable, std::nullopt,
                            false};
  AssertPlusSubscription(result, expected);
}

TEST(TestGetPlusSubscriptionForUser, ErrorInSubscriptionService) {
  auto get_subscriptions_handler = [](const std::string&,
                                      const core::PurchaseContext&, bool) {
    throw core::MediabillingError("i am error");
    return std::vector<core::MediabillingSubscription>{};
  };
  mocks::GetSubscriptionPriceHandler get_subscription_price_handler =
      [](const std::string&) { return std::nullopt; };

  auto deps =
      PrepareDeps(get_subscriptions_handler, get_subscription_price_handler);
  auto user_info = MakeUserInfo(false, false);
  auto purchase_context = MakePurhaseContext();

  auto result = GetPlusSubscriptionForUser(deps, user_info, purchase_context);

  PlusSubscription expected{"", "", PurchaseStatus::kNotAvailable, std::nullopt,
                            false};
  AssertPlusSubscription(result, expected);
}

}  // namespace sweet_home::subscription
