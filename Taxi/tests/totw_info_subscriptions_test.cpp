#include <experiments3/models/cache_manager.hpp>
#include <helpers/config_helper.hpp>
#include <modules/totw_info/subscriptions/subscription.hpp>

#include <set>

#include <testing/taxi_config.hpp>
#include <userver/utest/utest.hpp>

namespace internal_totw::info::subscriptions {

using CountrySettings =
    taxi_config::plus_summary_promotion_setting::CountrySettings;
using Decimal = decimal64::Decimal<4>;
using SubscriptionFeatures =
    taxi_config::plus_subscription_features::SubscriptionObj;
namespace exp3 = experiments3::models;

struct TotwPromotion {
  std::string id;
  std::string currency;
};

bool ShouldPromoteOrder(const OrderInfo& order_info,
                        const plus::PromotionSettings& settings);

decimal64::Decimal<4> CalcDiscount(const OrderInfo& order_info,
                                   const plus::PromotionSettings& settings);

std::optional<TotwPromotion> GetUserPromotion(
    const UserInfo& user_info, const taxi_config::TaxiConfig& config);

TEST(ShouldPromoteOrder, ShouldPromote) {
  const plus::PromotionSettings settings{
      {"business", "vip", "comfortplus"}, Decimal{"0.1"}, Decimal{900}};
  OrderInfo order_info = {Decimal(1000), "vip"};
  auto should = ShouldPromoteOrder(order_info, settings);
  ASSERT_TRUE(should);
}

TEST(ShouldPromoteOrder, TooLowCost) {
  const plus::PromotionSettings settings{
      {"business", "vip", "comfortplus"}, Decimal{"0.1"}, Decimal{900}};
  OrderInfo order_info = {Decimal(350), "vip"};
  auto should = ShouldPromoteOrder(order_info, settings);
  ASSERT_FALSE(should);
}

TEST(ShouldPromoteOrder, CategoryNotAllowed) {
  const plus::PromotionSettings settings{
      {"business", "vip", "comfortplus"}, Decimal{"0.1"}, Decimal{900}};
  OrderInfo order_info = {Decimal{1000}, "econom"};
  auto should = ShouldPromoteOrder(order_info, settings);
  ASSERT_FALSE(should);
}

TEST(CalcDiscount, HappyPath) {
  const plus::PromotionSettings settings{
      {"business", "vip", "comfortplus"}, Decimal{"0.1"}, Decimal{900}};
  OrderInfo order_info = {Decimal{1234}, "econom"};
  auto discount = CalcDiscount(order_info, settings);
  ASSERT_EQ(discount, Decimal{"123.4"});
}

auto build_config(
    const std::optional<std::vector<std::string>>& subs = std::nullopt) {
  auto config =
      dynamic_config::GetDefaultSnapshot().Get<taxi_config::TaxiConfig>();

  std::unordered_map<std::string, std::vector<std::string>> by_country;
  by_country["ru"] = subs.value_or(
      std::vector<std::string>{"ya_plus_rus", "ya_plus_trial_rus"});
  config.plus_allowed_subscriptions_by_countries.extra = by_country;

  std::set<std::string> categories{"business", "vip", "comfortplus"};
  CountrySettings settings{100, 0.1, categories};
  std::unordered_map<std::string, CountrySettings> promotion_settings;
  promotion_settings["ru"] = settings;
  config.plus_summary_promotion_setting.extra = promotion_settings;

  SubscriptionFeatures features{};
  features.price = {"169", "RUB"};
  std::unordered_map<std::string, SubscriptionFeatures> features_settings;
  features_settings["ya_plus_rus"] = features;
  config.plus_subscription_features.extra = features_settings;

  return config;
}

auto build_exp_data(
    const std::optional<std::vector<std::string>>& exps = std::nullopt) {
  exp3::ClientsCache::MappedData exp_data{};
  for (const auto& item : exps.value_or(std::vector<std::string>{})) {
    exp_data.insert({item, exp3::ExperimentResult{}});
  }
  return exp_data;
}

TEST(GetUserPromotion, NoCountry) {
  UserInfo user_info{"by", false};
  auto result = GetUserPromotion(user_info, build_config());
  ASSERT_EQ(result, std::nullopt);
}

TEST(GetUserPromotion, TrialOnly) {
  UserInfo user_info{"ru", false};
  auto result = GetUserPromotion(
      user_info, build_config(std::vector<std::string>{"ya_plus_trial_rus"}));
  ASSERT_EQ(result, std::nullopt);
}

TEST(GetUserPromotion, HasYaPlus) {
  UserInfo user_info{"ru", true};
  auto result = GetUserPromotion(user_info, build_config());
  ASSERT_EQ(result, std::nullopt);
}

TEST(GetUserPromotion, GetOne) {
  UserInfo user_info{"ru", false};
  auto result = GetUserPromotion(user_info, build_config());
  ASSERT_EQ(result->id, "ya_plus_rus");
  ASSERT_EQ(result->currency, "RUB");
}

TEST(BuildSubscriptions, PromotionInTotwOff) {
  SubscriptionDeps deps{build_config(), build_exp_data()};
  SubscriptionInput input{UserInfo{"ru", false},
                          OrderInfo{Decimal(1000), "vip"}};
  auto result = BuildSubscriptions(deps, input);
  ASSERT_TRUE(result.empty());
}

TEST(BuildSubscriptions, NoSettings) {
  SubscriptionDeps deps{
      build_config(),
      build_exp_data(std::vector<std::string>{"plus_promote_in_totw"})};
  SubscriptionInput input{UserInfo{"by", false},
                          OrderInfo{Decimal(1000), "vip"}};
  auto result = BuildSubscriptions(deps, input);
  ASSERT_TRUE(result.empty());
}

TEST(BuildSubscriptions, ShouldNotPromote) {
  SubscriptionDeps deps{
      build_config(),
      build_exp_data(std::vector<std::string>{"plus_promote_in_totw"})};
  SubscriptionInput input{UserInfo{"ru", false},
                          OrderInfo{Decimal(1000), "econom"}};
  auto result = BuildSubscriptions(deps, input);
  ASSERT_TRUE(result.empty());
}

TEST(BuildSubscriptions, NoPromotions) {
  SubscriptionDeps deps{
      build_config(),
      build_exp_data(std::vector<std::string>{"plus_promote_in_totw"})};
  SubscriptionInput input{UserInfo{"ru", true},
                          OrderInfo{Decimal(1000), "vip"}};
  auto result = BuildSubscriptions(deps, input);
  ASSERT_TRUE(result.empty());
}

TEST(BuildSubscriptions, HappyPath) {
  SubscriptionDeps deps{
      build_config(),
      build_exp_data(std::vector<std::string>{"plus_promote_in_totw"})};
  SubscriptionInput input{UserInfo{"ru", false},
                          OrderInfo{Decimal(1000), "vip"}};
  auto result = BuildSubscriptions(deps, input);
  ASSERT_EQ(result.size(), 1);
  ASSERT_EQ(result.front().id, "ya_plus_rus");
  ASSERT_EQ(result.front().currency, "RUB");
  ASSERT_EQ(result.front().discount, Decimal(100));
  ASSERT_EQ(result.front().banner.image_tag, "plus_banner_image");
  ASSERT_EQ(result.front().banner.title_key,
            "plus.promoted_subscriptions.yandex_plus.banner.title");
  ASSERT_EQ(result.front().banner.subtitle_key,
            "plus.promoted_subscriptions.yandex_plus.banner.subtitle");
  ASSERT_EQ(result.front().button.image_tag, "plus_button_image");
  ASSERT_EQ(result.front().button.title_key,
            "plus.promoted_subscriptions.yandex_plus.button.title");
}

}  // namespace internal_totw::info::subscriptions
