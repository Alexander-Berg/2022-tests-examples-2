#include <gtest/gtest.h>

#include <optional>
#include <string>
#include <vector>

#include <clients/billing_subventions/client.hpp>
#include <clients/subvention-order-context/client.hpp>

#include <views/internal/subvention-admin/v1/nmfg/orders/match/post/view.hpp>

namespace {
namespace bs = clients::billing_subventions;
namespace soc = clients::subvention_order_context;
namespace view = handlers::internal_subvention_admin_v1_nmfg_orders_match::post;
}  // namespace

constexpr soc::Branding kNoBranding{false, false};
constexpr soc::Branding kLightbox{true, false};
constexpr soc::Branding kSticker{false, true};
constexpr soc::Branding kFullBranding{true, true};

handlers::OrderProperty CreateBrandingProperty(const soc::Branding& branding,
                                               bool is_satisfied) {
  handlers::BrandingProperty prop;

  prop.type = handlers::BrandingPropertyType::kBranding;
  prop.value.lightbox = branding.has_lightbox;
  prop.value.sticker = branding.has_sticker;
  prop.is_satisfied = is_satisfied;

  return handlers::OrderProperty(prop);
}

struct BrandingData {
  soc::Branding driver_branding;
  std::optional<bs::AnyRuleBrandingtype> subvention_branding;
  std::optional<bool> is_satisfied;
};

struct BrandingValidatorFixtureParametrized
    : public ::testing::TestWithParam<BrandingData> {};

TEST_P(BrandingValidatorFixtureParametrized, CheckBrandingValidator) {
  view::NmfgRule rule;
  view::Order order;

  rule.branding_type = GetParam().subvention_branding;
  order.context.branding = GetParam().driver_branding;

  const auto prop =
      view::MapOptional(GetParam().is_satisfied, [](auto is_satisfied) {
        return CreateBrandingProperty(GetParam().driver_branding, is_satisfied);
      });

  ASSERT_EQ(prop, view::BrandingValidator().Validate(rule, order));
}

static const std::vector<BrandingData> kBrandingVariants{
    {kFullBranding, std::nullopt, std::nullopt},
    {kSticker, std::nullopt, std::nullopt},
    {kLightbox, std::nullopt, std::nullopt},
    {kNoBranding, std::nullopt, std::nullopt},

    {kFullBranding, bs::AnyRuleBrandingtype::kFullBranding, true},
    {kSticker, bs::AnyRuleBrandingtype::kFullBranding, false},
    {kLightbox, bs::AnyRuleBrandingtype::kFullBranding, false},
    {kNoBranding, bs::AnyRuleBrandingtype::kFullBranding, false},

    {kFullBranding, bs::AnyRuleBrandingtype::kSticker, true},
    {kSticker, bs::AnyRuleBrandingtype::kSticker, true},
    {kLightbox, bs::AnyRuleBrandingtype::kSticker, false},
    {kNoBranding, bs::AnyRuleBrandingtype::kSticker, false},

    {kFullBranding, bs::AnyRuleBrandingtype::kNoFullBranding, false},
    {kSticker, bs::AnyRuleBrandingtype::kNoFullBranding, true},
    {kLightbox, bs::AnyRuleBrandingtype::kNoFullBranding, true},
    {kNoBranding, bs::AnyRuleBrandingtype::kNoFullBranding, true},

    {kFullBranding, bs::AnyRuleBrandingtype::kNoBranding, false},
    {kSticker, bs::AnyRuleBrandingtype::kNoBranding, false},
    {kLightbox, bs::AnyRuleBrandingtype::kNoBranding, false},
    {kNoBranding, bs::AnyRuleBrandingtype::kNoBranding, true},
};

INSTANTIATE_TEST_SUITE_P(CheckBrandingValidator,
                         BrandingValidatorFixtureParametrized,
                         ::testing::ValuesIn(kBrandingVariants));

namespace {
using Tags = std::vector<std::string>;
}

handlers::OrderProperty CreateTagProperty(bool is_satisfied) {
  handlers::NMFGTagProperty prop;

  prop.type = handlers::NMFGTagPropertyType::kNmfgTag;
  prop.value = is_satisfied;
  prop.is_satisfied = is_satisfied;

  return handlers::OrderProperty(prop);
}

struct TagData {
  Tags driver_tags;
  Tags subvention_tags;
  bool is_satisfied;
};

struct TagValidatorFixtureParametrized
    : public ::testing::TestWithParam<TagData> {};

TEST_P(TagValidatorFixtureParametrized, CheckTagValidator) {
  view::NmfgRule rule;
  view::Order order;

  auto [driver_tags, subvention_tags, is_satisfied] = GetParam();
  rule.tags = std::move(subvention_tags);
  order.context.tags = std::move(driver_tags);

  const auto prop = CreateTagProperty(is_satisfied);

  ASSERT_EQ(prop, view::TagValidator().Validate(rule, order));
}

static const std::vector<TagData> kTagVariants{
    {{}, {}, true},
    {{"tag_1"}, {}, true},
    {{}, {"tag_1"}, false},
    {{"tag_1"}, {"tag_1"}, true},
    {{"tag_1", "tag_2"}, {"tag_1", "tag_2"}, true},
    {{"tag_1", "tag_2", "tag_3"}, {"tag_1", "tag_2"}, true},
};

INSTANTIATE_TEST_SUITE_P(CheckTagValidator, TagValidatorFixtureParametrized,
                         ::testing::ValuesIn(kTagVariants));
