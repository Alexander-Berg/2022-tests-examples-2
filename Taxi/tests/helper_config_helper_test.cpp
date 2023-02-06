#include <helpers/config_helper.hpp>

#include <set>

#include <testing/taxi_config.hpp>
#include <userver/utest/utest.hpp>

using CountrySettings =
    taxi_config::plus_summary_promotion_setting::CountrySettings;
using Decimal = decimal64::Decimal<4>;
using SubscriptionFeatures =
    taxi_config::plus_subscription_features::SubscriptionObj;
using SubscriptionType = taxi_config::plus_subscription_price::SubscriptionType;
using SubscriptionTypeV2 =
    taxi_config::plus_subscription_features_v2::SubscriptionType;

const std::vector<std::string> config_list{"value", "another_value", "another"};

TEST(ConfigListFilter, FilterOne) {
  auto filtered = plus::ConfigListFilter(config_list, "another_value");
  std::vector<std::string> expected = {"value", "another"};
  ASSERT_EQ(filtered.size(), expected.size());
  for (size_t i = 0; i < filtered.size(); ++i)
    EXPECT_EQ(filtered[i], expected[i]);
}

TEST(ConfigListFilter, FilterSeveral) {
  auto filtered = plus::ConfigListFilter(config_list, "value");
  std::vector<std::string> expected = {"another"};
  ASSERT_EQ(filtered.size(), expected.size());
  for (size_t i = 0; i < filtered.size(); ++i)
    EXPECT_EQ(filtered[i], expected[i]);
}

TEST(ConfigListFilter, FilterNothing) {
  auto filtered = plus::ConfigListFilter(config_list, "nothing");
  std::vector<std::string> expected = {"value", "another_value", "another"};
  ASSERT_EQ(filtered.size(), expected.size());
  for (size_t i = 0; i < filtered.size(); ++i)
    EXPECT_EQ(filtered[i], expected[i]);
}

TEST(ConfigListFilter, FilterAll) {
  auto filtered = plus::ConfigListFilter(config_list, "a");
  std::vector<std::string> expected = {};
  ASSERT_TRUE(filtered.empty());
}

auto build_config() {
  auto config =
      dynamic_config::GetDefaultSnapshot().Get<taxi_config::TaxiConfig>();

  std::vector<std::string> subs{"ya_plus_rus", "ya_plus_trial_rus"};
  std::unordered_map<std::string, std::vector<std::string>> by_country;
  by_country["ru"] = subs;
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

  std::unordered_map<std::string, SubscriptionType> sub_price_by_type{};
  SubscriptionType sub_price_by_sub_id{};
  sub_price_by_sub_id.extra["sub_id"] = {"100", "RUB"};
  sub_price_by_type["type_sub"] = sub_price_by_sub_id;
  config.plus_subscription_price.extra = sub_price_by_type;

  taxi_config::plus_subscription_features_v2::Action action{"buy_plus"};
  taxi_config::plus_subscription_features_v2::Feature feature_v2{
      "feature_type", "feature_title", "feature_subtitle", "feature_icon",
      "feature_value"};

  SubscriptionTypeV2 sub_features_by_id{};
  sub_features_by_id.extra["sub_id"] = {
      "title", "subtitle", {feature_v2}, action};

  std::unordered_map<std::string, SubscriptionTypeV2> sub_v2{};
  sub_v2["type_sub"] = sub_features_by_id;

  config.plus_subscription_features_v2.extra = sub_v2;

  return config;
}

auto build_empty_config() {
  auto config =
      dynamic_config::GetDefaultSnapshot().Get<taxi_config::TaxiConfig>();
  config.plus_allowed_subscriptions_by_countries.extra = {};
  config.plus_subscription_features.extra = {};
  config.plus_summary_promotion_setting.extra = {};
  config.plus_subscription_features_v2.extra = {};
  config.plus_subscription_price.extra = {};
  return config;
}

TEST(GetAllowedSubscriptions, EmptyConfig) {
  auto result = plus::GetAllowedSubscriptions(build_empty_config(), "ru");
  ASSERT_EQ(result, std::nullopt);
}

TEST(GetAllowedSubscriptions, GetOne) {
  std::vector<std::string> expected{"ya_plus_rus", "ya_plus_trial_rus"};
  auto result = plus::GetAllowedSubscriptions(build_config(), "ru");
  ASSERT_NE(result, std::nullopt);
  ASSERT_EQ(result->size(), expected.size());
  for (size_t i = 0; i < result->size(); ++i)
    EXPECT_EQ(result->data()[i], expected[i]);
}

TEST(GetAllowedSubscriptions, NoOne) {
  auto result = plus::GetAllowedSubscriptions(build_config(), "by");
  ASSERT_EQ(result, std::nullopt);
}

TEST(GetSubscriptionFeaturesPrice, EmptyConfig) {
  auto result =
      plus::GetAllowedSubscriptions(build_empty_config(), "ya_plus_rus");
  ASSERT_EQ(result, std::nullopt);
}

TEST(GetSubscriptionFeaturesPrice, GetOne) {
  auto result =
      plus::GetSubscriptionFeaturesPrice(build_config(), "ya_plus_rus");
  ASSERT_NE(result, std::nullopt);
  ASSERT_EQ(result->currency, "RUB");
}

TEST(GetSubscriptionFeaturesPrice, NoOne) {
  auto result =
      plus::GetSubscriptionFeaturesPrice(build_config(), "ya_plus_eur");
  ASSERT_EQ(result, std::nullopt);
}

TEST(GetPromotionSettings, EmptyConfig) {
  auto result = plus::GetPromotionSetting(build_empty_config(), "ru");
  ASSERT_EQ(result, std::nullopt);
}

TEST(GetPromotionSettings, GetOne) {
  std::set<std::string> categories{"business", "vip", "comfortplus"};
  plus::PromotionSettings expected{categories, Decimal{"0.1"}, Decimal{100}};
  auto result = plus::GetPromotionSetting(build_config(), "ru");
  ASSERT_NE(result, std::nullopt);
  EXPECT_EQ(result->categories, expected.categories);
  EXPECT_EQ(result->discount, expected.discount);
  EXPECT_EQ(result->min_price, expected.min_price);
}

TEST(GetPromotionSettings, NoOne) {
  auto result = plus::GetPromotionSetting(build_config(), "by");
  ASSERT_EQ(result, std::nullopt);
}

TEST(GetSubscriptionInfoConfig, EmptyPriceAndConfifuration) {
  auto result = plus::GetSubscriptionInfoConfig("type_sub", "sub_id",
                                                build_empty_config());
  ASSERT_EQ(result, std::nullopt);
}

TEST(GetSubscriptionInfoConfig, ExistPriceAndConfiguration) {
  auto result =
      plus::GetSubscriptionInfoConfig("type_sub", "sub_id", build_config());
  ASSERT_NE(result, std::nullopt);
  EXPECT_EQ(result->title, "title");
  EXPECT_EQ(result->subtitle, "subtitle");
  EXPECT_EQ(result->price.currency, "RUB");
  EXPECT_EQ(result->price.value, "100");
  EXPECT_EQ(result->action, "buy_plus");
  EXPECT_EQ(result->features.size(), 1);
  EXPECT_EQ(result->features[0].icon, "feature_icon");
  EXPECT_EQ(result->features[0].title, "feature_title");
  EXPECT_EQ(result->features[0].type, "feature_type");
  EXPECT_EQ(result->features[0].subtitle, "feature_subtitle");
  EXPECT_EQ(result->features[0].value, "feature_value");
}

TEST(GetSubscriptionInfoConfig, ExistPriceAndEmptyConfiguration) {
  auto builded_config = build_config();
  builded_config.plus_subscription_features_v2.extra = {};
  auto result =
      plus::GetSubscriptionInfoConfig("type_sub", "sub_id", builded_config);
  ASSERT_EQ(result, std::nullopt);
}

TEST(GetSubscriptionInfoConfig, ExistConfigurationAndEmptyPrice) {
  auto builded_config = build_config();
  builded_config.plus_subscription_price.extra = {};
  auto result =
      plus::GetSubscriptionInfoConfig("type_sub", "sub_id", builded_config);
  ASSERT_EQ(result, std::nullopt);
}
