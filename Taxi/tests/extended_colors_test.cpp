#include <fmt/format.h>

#include <testing/taxi_config.hpp>
#include <userver/utest/utest.hpp>

#include <extended-colors/extended_colors.hpp>
#include <taxi_config/variables/EXTENDED_COLORS_SETTINGS.hpp>

namespace {

using OptString = ::extended_colors::OptString;

}  // namespace

UTEST(ExtendedColorsTest, TestSimpleColor) {
  ::extended_colors::ExtendedColors colors{dynamic_config::GetDefaultSource()};

  auto color = "#FAFAFA";
  EXPECT_EQ(color, colors.BuildSupportedColor(color, ::std::nullopt));
  EXPECT_EQ(color, colors.BuildSupportedColor(color, "1"));
}

UTEST(ExtendedColorsTest, TestSimpleColorOpt) {
  ::extended_colors::ExtendedColors colors{dynamic_config::GetDefaultSource()};

  auto color_opt = ::std::optional<::std::string>("#FAFAFA");
  EXPECT_EQ(color_opt,
            colors.BuildSupportedColorOpt(color_opt, ::std::nullopt));
  EXPECT_EQ(::std::nullopt, colors.BuildSupportedColorOpt(::std::nullopt, "2"));
}

UTEST(ExtendedColorsTest, TestMultihexColor) {
  ::extended_colors::ExtendedColors colors{dynamic_config::GetDefaultSource()};

  ::std::string multihex;

  multihex = "l:#AABBCC;d:#FFEEDD";
  EXPECT_EQ("#AABBCC", colors.BuildSupportedColor(multihex, ::std::nullopt));
  EXPECT_EQ("#AABBCC", colors.BuildSupportedColor(multihex, "1"));
  EXPECT_EQ("#AABBCC", colors.BuildSupportedColor(multihex, "true"));
  EXPECT_EQ(multihex, colors.BuildSupportedColor(multihex, "2"));
  EXPECT_EQ(multihex, colors.BuildSupportedColor(multihex, "3"));
  EXPECT_EQ(multihex, colors.BuildSupportedColor(multihex, "12"));

  multihex = "al:#112233;l:#AABBCC;d:#FFEEDD";
  EXPECT_EQ("#AABBCC", colors.BuildSupportedColor(multihex, ::std::nullopt));
  EXPECT_EQ("#AABBCC", colors.BuildSupportedColor(multihex, "1"));
  EXPECT_EQ(multihex, colors.BuildSupportedColor(multihex, "2"));

  // invalid multihex without light theme
  multihex = "a:#112233;d:#FFEEDD";
  EXPECT_EQ(multihex, colors.BuildSupportedColor(multihex, ::std::nullopt));
  EXPECT_EQ(multihex, colors.BuildSupportedColor(multihex, "1"));
  EXPECT_EQ(multihex, colors.BuildSupportedColor(multihex, "2"));
}

UTEST(ExtendedColorsTest, TestSemanticColors) {
  const auto& keyvalue = dynamic_config::KeyValue(
      taxi_config::EXTENDED_COLORS_SETTINGS,
      taxi_config::extended_colors_settings::VariableType{
          {{{"background",
             {{"__default__", "#FFFFFF"},
              {"ultima", "#000000"}}}}} /* semantic_colors_mapping */
      });
  const auto& storage = dynamic_config::MakeDefaultStorage({keyvalue});
  ::extended_colors::ExtendedColors colors{storage.GetSource()};

  ::std::string semantic;

  semantic = "background";
  EXPECT_EQ("#FFFFFF", colors.BuildSupportedColor(semantic, ::std::nullopt));
  EXPECT_EQ("#FFFFFF", colors.BuildSupportedColor(semantic, "0"));
  EXPECT_EQ("#FFFFFF", colors.BuildSupportedColor(semantic, "true"));
  EXPECT_EQ("#000000",
            colors.BuildSupportedColor(semantic, ::std::nullopt, "ultima"));
  EXPECT_EQ("#000000", colors.BuildSupportedColor(semantic, "0", "ultima"));
  EXPECT_EQ(semantic, colors.BuildSupportedColor(semantic, "1"));
  EXPECT_EQ(semantic, colors.BuildSupportedColor(semantic, "2"));
  EXPECT_EQ(semantic, colors.BuildSupportedColor(semantic, "3"));
  EXPECT_EQ(semantic, colors.BuildSupportedColor(semantic, "12"));

  // unknown semantic color
  semantic = "unknown";
  EXPECT_EQ(semantic, colors.BuildSupportedColor(semantic, ::std::nullopt));
  EXPECT_EQ(semantic, colors.BuildSupportedColor(semantic, "1"));
  EXPECT_EQ(semantic, colors.BuildSupportedColor(semantic, "2"));
}
