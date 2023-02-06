#include <userver/utest/utest.hpp>

#include <models/promo_features.hpp>

namespace eats_restapp_promo::models {

struct TestValidator {};

struct BaseTestFeature : promo_features::Base {
  template <typename... Args>
  BaseTestFeature(Args&&...) {}

  virtual ~BaseTestFeature() = default;

  void UpdateStoredData(types::StoredDataRaw&) const override {}
  void UpdateDiscountData(types::DiscountDataRaw&) const override {}
  void UpdateResponse(models::PromoResponse&) const override {}
};

struct FirstTestFeature final : public BaseTestFeature {
  static constexpr const char* kName = "first";
  using BaseTestFeature::BaseTestFeature;
  void UpdateResponse(models::PromoResponse& response) const override {
    response.name = kName;
  }
};

struct SecondTestFeature final : public BaseTestFeature {
  static constexpr const char* kName = "second";
  using BaseTestFeature::BaseTestFeature;
  void UpdateResponse(models::PromoResponse& response) const override {
    response.name = kName;
  }
};

void CheckFeature(const PromoFeatures& features, const std::string& slug) {
  const auto feature = features.at(slug);
  ASSERT_TRUE(feature);
  models::PromoResponse response;
  feature->UpdateResponse(response);
  ASSERT_EQ(response.name, slug);
}

using TestRegistered = RegisterFeatures<FirstTestFeature, SecondTestFeature>;

TEST(MakePromoFeaturesTest, on_null_slugs_in_settings_returns_nothing) {
  PromoSettings settings;
  auto result =
      MakePromoFeatures<TestRegistered>(TestValidator{}, settings, {}, int());
  ASSERT_TRUE(result.empty());
}

TEST(MakePromoFeaturesTest, on_empty_slugs_in_settings_returns_nothing) {
  PromoSettings settings;
  settings.info.features = PromoFeatureSlugs{};
  auto result =
      MakePromoFeatures<TestRegistered>(TestValidator{}, settings, {}, int());
  ASSERT_TRUE(result.empty());
}

TEST(MakePromoFeaturesTest, on_first_slug_in_settings_returns_first_feature) {
  PromoSettings settings;
  settings.info.features = PromoFeatureSlugs{"first"};
  auto result =
      MakePromoFeatures<TestRegistered>(TestValidator{}, settings, {}, int());
  ASSERT_EQ(result.size(), 1);
  CheckFeature(result, "first");
}

TEST(MakePromoFeaturesTest, on_second_slug_in_settings_returns_second_feature) {
  PromoSettings settings;
  settings.info.features = PromoFeatureSlugs{"second"};
  auto result =
      MakePromoFeatures<TestRegistered>(TestValidator{}, settings, {}, int());
  ASSERT_EQ(result.size(), 1);
  CheckFeature(result, "second");
}

TEST(MakePromoFeaturesTest, on_both_slugs_in_settings_returns_both_features) {
  PromoSettings settings;
  settings.info.features = PromoFeatureSlugs{"second", "first"};
  auto result =
      MakePromoFeatures<TestRegistered>(TestValidator{}, settings, {}, int());
  ASSERT_EQ(result.size(), 2);
  CheckFeature(result, "first");
  CheckFeature(result, "second");
}

TEST(MakePromoFeaturesTest, on_unknown_slug_in_settings_throws_logic_error) {
  PromoSettings settings;
  settings.info.features = PromoFeatureSlugs{"first", "unknown"};
  ASSERT_THROW(
      MakePromoFeatures<TestRegistered>(TestValidator{}, settings, {}, int()),
      std::logic_error);
}

}  // namespace eats_restapp_promo::models
