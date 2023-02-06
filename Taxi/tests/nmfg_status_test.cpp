#include <gtest/gtest.h>

#include <common_handlers/nmfg_summary/common.hpp>
#include <views/v1/nmfg/status/post/types.hpp>

#include "common.hpp"

using clients::billing_subventions::AnyRuleBrandingtype;
using models::DriverBranding;

struct BrandingData {
  DriverBranding driver_branding;
  std::optional<AnyRuleBrandingtype> subvention_branding;
  bool is_satisfy;
};

struct CompareBrandingFixtureParametrized
    : public ::testing::TestWithParam<BrandingData> {};

TEST_P(CompareBrandingFixtureParametrized, CompareBranding) {
  ASSERT_EQ(GetParam().is_satisfy,
            handlers::IsDriverSatisfiesSubventionBranding(
                GetParam().driver_branding, GetParam().subvention_branding));
}

static const std::vector<BrandingData> kBrandingVariants{
    {DriverBranding::kFullBranding, std::nullopt, true},
    {DriverBranding::kSticker, std::nullopt, true},
    {DriverBranding::kLightbox, std::nullopt, true},
    {DriverBranding::kNoBranding, std::nullopt, true},

    {DriverBranding::kFullBranding, AnyRuleBrandingtype::kFullBranding, true},
    {DriverBranding::kSticker, AnyRuleBrandingtype::kFullBranding, false},
    {DriverBranding::kLightbox, AnyRuleBrandingtype::kFullBranding, false},
    {DriverBranding::kNoBranding, AnyRuleBrandingtype::kFullBranding, false},

    {DriverBranding::kFullBranding, AnyRuleBrandingtype::kSticker, true},
    {DriverBranding::kSticker, AnyRuleBrandingtype::kSticker, true},
    {DriverBranding::kLightbox, AnyRuleBrandingtype::kSticker, false},
    {DriverBranding::kNoBranding, AnyRuleBrandingtype::kSticker, false},

    {DriverBranding::kFullBranding, AnyRuleBrandingtype::kNoFullBranding,
     false},
    {DriverBranding::kSticker, AnyRuleBrandingtype::kNoFullBranding, true},
    {DriverBranding::kLightbox, AnyRuleBrandingtype::kNoFullBranding, true},
    {DriverBranding::kNoBranding, AnyRuleBrandingtype::kNoFullBranding, true},

    {DriverBranding::kFullBranding, AnyRuleBrandingtype::kNoBranding, false},
    {DriverBranding::kSticker, AnyRuleBrandingtype::kNoBranding, false},
    {DriverBranding::kLightbox, AnyRuleBrandingtype::kNoBranding, false},
    {DriverBranding::kNoBranding, AnyRuleBrandingtype::kNoBranding, true},
};

INSTANTIATE_TEST_SUITE_P(CompareBranding, CompareBrandingFixtureParametrized,
                         ::testing::ValuesIn(kBrandingVariants));

struct TariffClassesData {
  std::set<std::string> driver_classes;
  std::vector<std::string> rule_classes;
  bool is_satisfy;
};

struct TariffClassesDataParametrized
    : public ::testing::TestWithParam<TariffClassesData> {};

TEST_P(TariffClassesDataParametrized, CheckTariffClasses) {
  ASSERT_EQ(GetParam().is_satisfy,
            handlers::v1_nmfg_status::post::AreTariffClassesSatisfied(
                GetParam().rule_classes, GetParam().driver_classes));
}

static const std::vector<TariffClassesData> kTariffClassesVariants{
    {{"econom"}, {"econom", "comfort"}, true},
    {{"econom"}, {"comfort_plus", "comfort"}, false},
    {{"econom"}, {"econom"}, true}};

INSTANTIATE_TEST_SUITE_P(CheckTariffClasses, TariffClassesDataParametrized,
                         ::testing::ValuesIn(kTariffClassesVariants));
