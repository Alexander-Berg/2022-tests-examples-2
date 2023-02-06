#include <userver/utest/utest.hpp>

#include <utils/entrypoints.hpp>

const std::string kDefaultIconTag{"default_icon_tag"};
const std::string kRtlIconTag{"rtl_icon_tag"};
const std::string kRtlMulticolorEnabledTag{"rtl_multicolor_enabled_tag"};
const std::string kRtlMulticolorDisabledTag{"rtl_multicolor_disabled_tag"};
const std::string kDefaultMulticolorEnabledTag{
    "default_multicolor_enabled_tag"};
const std::string kDefaultMulticolorDisabledTag{
    "default_multicolor_disabled_tag"};

const bool MULTICOLOR_SUPPORTED{true};
const bool MULTICOLOR_NOT_SUPPORTED{false};
const bool SERVICE_AVAILABLE{true};
const bool SERVICE_NOT_AVAILABLE{false};
const bool USE_RTL_ICON{true};
const bool USE_DEFAULT_ICON{false};

struct IconTagCtx {
  bool multicolor_icons_supported;
  bool service_available;
  bool use_rtl_icon;
};

struct TestCase {
  IconTagCtx ctx;
  std::string expected_tag;
};

shortcuts::experiments::ButtonAppearance GetDefaultAppearance(
    const bool add_rtl_icons = true) {
  shortcuts::experiments::ButtonAppearance appearance{};
  appearance.icon_tag = kDefaultIconTag;
  appearance.multicolor_icon = {kDefaultMulticolorEnabledTag,
                                kDefaultMulticolorDisabledTag};

  if (!add_rtl_icons) {
    return appearance;
  }
  appearance.icon_tag_rtl = kRtlIconTag;
  appearance.multicolor_icon_rtl = {kRtlMulticolorEnabledTag,
                                    kRtlMulticolorDisabledTag};
  return appearance;
}

TEST(TestRtlIcons, FullAppearance) {
  const auto appearance = GetDefaultAppearance();

  std::vector<TestCase> test_cases{
      {
          {MULTICOLOR_SUPPORTED, SERVICE_AVAILABLE, USE_RTL_ICON},
          kRtlMulticolorEnabledTag,
      },
      {
          {MULTICOLOR_SUPPORTED, SERVICE_AVAILABLE, USE_DEFAULT_ICON},
          kDefaultMulticolorEnabledTag,
      },
      {
          {MULTICOLOR_SUPPORTED, SERVICE_NOT_AVAILABLE, USE_RTL_ICON},
          kRtlMulticolorDisabledTag,
      },
      {
          {MULTICOLOR_SUPPORTED, SERVICE_NOT_AVAILABLE, USE_DEFAULT_ICON},
          kDefaultMulticolorDisabledTag,
      },
      {
          {MULTICOLOR_NOT_SUPPORTED, SERVICE_AVAILABLE, USE_RTL_ICON},
          kRtlIconTag,
      },
      {
          {MULTICOLOR_NOT_SUPPORTED, SERVICE_AVAILABLE, USE_DEFAULT_ICON},
          kDefaultIconTag,
      },
      {
          {MULTICOLOR_NOT_SUPPORTED, SERVICE_NOT_AVAILABLE, USE_RTL_ICON},
          kRtlIconTag,
      },
      {
          {MULTICOLOR_NOT_SUPPORTED, SERVICE_NOT_AVAILABLE, USE_DEFAULT_ICON},
          kDefaultIconTag,
      },
  };

  for (const auto& [ctx, expected_tag] : test_cases) {
    const auto& icon_tag = utils::entrypoints::GetIconTag(
        appearance, {}, ctx.multicolor_icons_supported, ctx.service_available,
        ctx.use_rtl_icon, std::nullopt);
    EXPECT_EQ(icon_tag, expected_tag);
  }
}

TEST(TestRtlIcons, AppearanceWithoutRtlIcons) {
  const auto appearance = GetDefaultAppearance(false);

  std::vector<TestCase> test_cases{
      {
          {MULTICOLOR_SUPPORTED, SERVICE_AVAILABLE, USE_RTL_ICON},
          kDefaultMulticolorEnabledTag,
      },
      {
          {MULTICOLOR_SUPPORTED, SERVICE_NOT_AVAILABLE, USE_RTL_ICON},
          kDefaultMulticolorDisabledTag,
      },
      {
          {MULTICOLOR_NOT_SUPPORTED, SERVICE_AVAILABLE, USE_RTL_ICON},
          kDefaultIconTag,
      },
      {
          {MULTICOLOR_NOT_SUPPORTED, SERVICE_NOT_AVAILABLE, USE_RTL_ICON},
          kDefaultIconTag,
      },
  };

  for (const auto& [ctx, expected_tag] : test_cases) {
    const auto& icon_tag = utils::entrypoints::GetIconTag(
        appearance, {}, ctx.multicolor_icons_supported, ctx.service_available,
        ctx.use_rtl_icon, std::nullopt);
    EXPECT_EQ(icon_tag, expected_tag);
  }
}
