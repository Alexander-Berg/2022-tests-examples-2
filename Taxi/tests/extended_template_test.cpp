#include <gtest/gtest.h>

#include <extended-template/exceptions.hpp>
#include <extended-template/extended-template.hpp>

#include <array>
#include <optional>

namespace config_styles = taxi_config::extended_template_styles_map;
namespace extended_template_styles = handlers::libraries::extended_template;

using ImageType = handlers::libraries::extended_template::ATImagePropertyType;
using TextType = handlers::libraries::extended_template::ATTextPropertyType;

static const extended_template::ConfigAttributedTextStyle bold_style = {
    1,
    config_styles::StyleFontweight::kBold,
    config_styles::StyleFontstyle::kNormal,
    "black",
    "bold_color",
    config_styles::StyleMetastyle::kTitleBold,
    std::unordered_set<config_styles::StyleTextdecorationA>{
        config_styles::StyleTextdecorationA::kLineThrough}};
static const extended_template::ConfigAttributedTextStyle plus_style = {
    2,
    config_styles::StyleFontweight::kLight,
    config_styles::StyleFontstyle::kItalic,
    "plus_text",
    "plus_color",
    config_styles::StyleMetastyle::kCaptionBold,
    std::unordered_set<config_styles::StyleTextdecorationA>{
        config_styles::StyleTextdecorationA::kUnderline}};

static const extended_template::ConfigAttributedTextStyle image_style = {
    std::nullopt, std::nullopt,
    std::nullopt, std::nullopt,
    "plus_color", std::nullopt,
    std::nullopt, 10,
    10,           config_styles::StyleVerticalalignment::kCenter};

static const extended_template::ArgsList args = {{"arg", "zzz"},
                                                 {"points", "50"}};
static const extended_template::ConfigStyleMap styles = {
    {"bold", bold_style}, {"plus", plus_style}, {"image", image_style}};

template <typename T>
bool IsNullopt(const std::optional<T>& val) {
  return !val.has_value();
}

std::vector<extended_template::ATTextProperty> GetText(
    const extended_template::AttributedTextList& attrs) {
  std::vector<extended_template::ATTextProperty> text_attrs;
  for (const auto& attr : attrs) {
    text_attrs.push_back(std::get<extended_template::ATTextProperty>(attr));
  }
  return text_attrs;
}

TEST(TestExtendedTemplate, DefaultTest) {
  auto text_tpl = extended_template::TextTemplate("xxx{arg}yyy");
  EXPECT_EQ(text_tpl.GetArgNames().size(), 1u);
  EXPECT_EQ(text_tpl.GetOriginal(), "xxx{arg}yyy");
  EXPECT_EQ(text_tpl.GetOriginalTpl(), "");
  EXPECT_EQ(text_tpl.GetText(args), "xxxzzzyyy");
  EXPECT_EQ(text_tpl.SubstituteArgs(args), "xxxzzzyyy");

  text_tpl = extended_template::TextTemplate("xxx{arg}yyy{arg}");
  EXPECT_EQ(text_tpl.GetArgNames().size(), 1u);
  EXPECT_EQ(text_tpl.SubstituteArgs(args), "xxxzzzyyyzzz");
}

TEST(TestExtendedTemplate, EmptyTemplateTest) {
  const auto text_tpl = extended_template::TextTemplate("xxxyyy");
  EXPECT_EQ(text_tpl.GetArgNames().size(), 0u);
  EXPECT_EQ(text_tpl.SubstituteArgs(args), "xxxyyy");
}

TEST(TestExtendedTemplate, BrokenTemplateTest) {
  ASSERT_THROW(extended_template::TextTemplate("xxx{yyy"),
               extended_template::BracesImbalance);
  ASSERT_THROW(extended_template::TextTemplate("xxx{{arg}}yyy"),
               extended_template::BracesImbalance);
  ASSERT_THROW(extended_template::TextTemplate("{xxx{arg}yyy}"),
               extended_template::BracesImbalance);
  ASSERT_THROW(extended_template::TextTemplate("{}"),
               extended_template::BracesImbalance);
}

TEST(TestExtendedTemplate, AbsentTest) {
  auto text_tpl = extended_template::TextTemplate("xxx{undefined_arg}yyy");
  ASSERT_THROW(text_tpl.SubstituteArgs(args),
               extended_template::AbsentKeyError);
}

TEST(TestExtendedTemplate, DefaultStylishTest) {
  const auto text_tpl =
      extended_template::TextTemplate("xxx<bold>sss</bold>yyy<plus></plus>");
  EXPECT_EQ(text_tpl.GetText(), "xxxsssyyy");

  const auto attrs = text_tpl.GetAttributedText(styles);
  EXPECT_EQ(attrs.items.size(), 3u);

  const auto text_attrs = GetText(attrs.items);

  EXPECT_EQ(text_attrs[0].text, "xxx");
  ASSERT_TRUE(IsNullopt(text_attrs[0].meta_style));
  ASSERT_TRUE(IsNullopt(text_attrs[0].meta_color));

  EXPECT_EQ(text_attrs[1].text, "sss");
  ASSERT_FALSE(IsNullopt(text_attrs[1].meta_style));
  ASSERT_FALSE(IsNullopt(text_attrs[1].meta_color));
  EXPECT_EQ(*text_attrs[1].meta_style,
            extended_template_styles::ATTextPropertyMetastyle::kTitleBold);
  EXPECT_EQ(*text_attrs[1].meta_color, *bold_style.meta_color);

  EXPECT_EQ(text_attrs[2].text, "yyy");
  ASSERT_TRUE(IsNullopt(text_attrs[2].meta_style));
  ASSERT_TRUE(IsNullopt(text_attrs[2].meta_color));
}

TEST(TestExtendedTemplate, StylishAndTemplateTest) {
  constexpr size_t token_size = 2u;
  const auto text_tpl =
      extended_template::TextTemplate("<plus>arg: {arg}</plus>");
  EXPECT_EQ(text_tpl.GetText(args), "arg: zzz");
  const auto attrs = text_tpl.GetAttributedText(styles, args);
  const std::array<std::string, token_size> expected_tokes = {"arg: ", "zzz"};
  EXPECT_EQ(attrs.items.size(), token_size);

  const auto text_attrs = GetText(attrs.items);

  for (size_t i = 0; i < text_attrs.size(); ++i) {
    const auto& text_attr = text_attrs[i];

    EXPECT_EQ(text_attr.text, expected_tokes[i]);
    EXPECT_EQ(*text_attr.font_size, 2);
    EXPECT_EQ(*text_attr.font_weight,
              extended_template_styles::ATTextPropertyFontweight::kLight);
    EXPECT_EQ(*text_attr.font_style,
              extended_template_styles::ATTextPropertyFontstyle::kItalic);
    EXPECT_EQ(*text_attr.color, *plus_style.color);
    EXPECT_EQ(*text_attr.meta_style,
              extended_template_styles::ATTextPropertyMetastyle::kCaptionBold);
    EXPECT_EQ(*text_attr.meta_color, *plus_style.meta_color);
    EXPECT_EQ(text_attr.text_decoration->size(), 1);
    EXPECT_EQ(ToString(*text_attr.text_decoration->begin()),
              ToString(*plus_style.text_decoration->begin()));
  }
}

TEST(TestExtendedTemplate, BrokenStyleTest) {
  ASSERT_THROW(extended_template::TextTemplate("xxx<bold>sss</bold>yyy<"),
               extended_template::XmlParsingError);

  ASSERT_THROW(extended_template::TextTemplate("xxx<bold>sss</bold>yyy</"),
               extended_template::XmlParsingError);

  ASSERT_THROW(extended_template::TextTemplate("xxx<bold>sss</bold>yyy</>"),
               extended_template::XmlParsingError);

  ASSERT_THROW(extended_template::TextTemplate("xxx<bold>sss</bold>yyy<>"),
               extended_template::XmlParsingError);
}

TEST(TestExtendedTemplate, NoSuchTagError) {
  ASSERT_THROW(extended_template::TextTemplate("xxx<bold>sss</bold>yyy<<>>"),
               extended_template::XmlParsingError);
}

TEST(TestExtendedTemplate, DifferentUncloseTag) {
  ASSERT_THROW(extended_template::TextTemplate("xxx<bold>sss</hold>yyy"),
               extended_template::XmlParsingError);
}

TEST(TestExtendedTemplate, OverlappingTags) {
  ASSERT_THROW(
      extended_template::TextTemplate("xxx<bold>sss<hold>zzz</bold>yyy</hold>"),
      extended_template::XmlParsingError);
}

TEST(TestExtendedTemplate, NestedTags) {
  const auto text_tpl =
      extended_template::TextTemplate("xxx<bold>sss<plus>z</plus></bold>yyy");
  EXPECT_EQ(text_tpl.GetText(), "xxxssszyyy");
  const auto attrs = text_tpl.GetAttributedText(styles);

  EXPECT_EQ(attrs.items.size(), 4u);

  const auto text_attrs = GetText(attrs.items);

  EXPECT_EQ(text_attrs[1].color, *bold_style.color);
  EXPECT_EQ(text_attrs[2].color, *plus_style.color);
}

TEST(TestExtendedTemplate, AbsentStyleError) {
  const auto text_tpl = extended_template::TextTemplate("<pold>sss</pold>");
  EXPECT_EQ(text_tpl.GetText(), "sss");
  ASSERT_THROW(text_tpl.GetAttributedText(styles),
               extended_template::AbsentStyleError);
}

TEST(TestExtendedTemplate, StyleConversionError) {
  // We should broke config or connection between config and api
  extended_template::ConfigAttributedTextStyle broken_style;
  broken_style.font_weight =
      static_cast<::taxi_config::extended_template_styles_map::StyleFontweight>(
          -1);
  const extended_template::ConfigStyleMap broken_styles = {
      {"pold", broken_style}};
  const auto text_tpl = extended_template::TextTemplate("<pold>sss</pold>");
  ASSERT_THROW(text_tpl.GetAttributedText(broken_styles),
               extended_template::StyleConversionError);
}

TEST(TestExtendedTemplate, SimpleLink) {
  auto text_tpl =
      extended_template::TextTemplate("Hi <a href=\"hi.ru\">Yandex</a>");
  EXPECT_EQ(text_tpl.GetText(), "Hi hi.ru");

  const auto attrs = text_tpl.GetAttributedText(styles, args);
  EXPECT_EQ(attrs.items.size(), 2u);

  const auto& text_attr =
      std::get<extended_template::ATTextProperty>(attrs.items[0]);
  EXPECT_EQ(text_attr.text, "Hi ");

  const auto& link_attr =
      std::get<extended_template::ATLinkProperty>(attrs.items[1]);
  EXPECT_EQ(link_attr.link, "hi.ru");
  EXPECT_EQ(link_attr.text.text, "Yandex");
}

TEST(TestExtendedTemplate, ArgStylishLink) {
  auto text_tpl = extended_template::TextTemplate(
      "<bold><a href=\"hi.ru\">Yandex{arg}hello</a></bold>");
  EXPECT_EQ(text_tpl.GetText(), "hi.ru");

  const auto attrs = text_tpl.GetAttributedText(styles, args);
  EXPECT_EQ(attrs.items.size(), 1u);

  const auto& link_attr =
      std::get<extended_template::ATLinkProperty>(attrs.items[0]);
  EXPECT_EQ(link_attr.text.text, "Yandexzzzhello");
  ASSERT_FALSE(IsNullopt(link_attr.text.meta_style));
  ASSERT_FALSE(IsNullopt(link_attr.text.meta_color));
  EXPECT_EQ(*link_attr.text.meta_style,
            extended_template_styles::ATTextPropertyMetastyle::kTitleBold);
  EXPECT_EQ(*link_attr.text.meta_color, *bold_style.meta_color);
}

TEST(TestExtendedTemplate, ATagWithoutHref) {
  EXPECT_THROW(extended_template::TextTemplate("<a>Yandex</a>"),
               extended_template::ATagWithoutHrefError);
  EXPECT_THROW(extended_template::TextTemplate("<a hre=\"hi.ru\">Yandex</a>"),
               extended_template::ATagWithoutHrefError);
}

TEST(TestExtendedTemplate, ImgTagUnstylish) {
  auto text_tpl =
      extended_template::TextTemplate("<img src=\"plus_icon_tag\" />");
  const auto attrs = text_tpl.GetAttributedText(styles, args);
  const auto& image_attr =
      std::get<extended_template::ATImageProperty>(attrs.items[0]);

  EXPECT_EQ(image_attr.image_tag, "plus_icon_tag");
  EXPECT_EQ(image_attr.type, ImageType::kImage);
  ASSERT_TRUE(IsNullopt(image_attr.width));
  ASSERT_TRUE(IsNullopt(image_attr.vertical_alignment));
}

TEST(TestExtendedTemplate, ImgTag) {
  auto text_tpl = extended_template::TextTemplate(
      "<image><img src=\"plus_icon_tag\" /></image>");
  const auto attrs = text_tpl.GetAttributedText(styles, args);
  const auto& image_attr =
      std::get<extended_template::ATImageProperty>(attrs.items[0]);

  EXPECT_EQ(image_attr.image_tag, "plus_icon_tag");
  EXPECT_EQ(image_attr.type, ImageType::kImage);
  EXPECT_EQ(image_attr.width, 10);
  EXPECT_EQ(
      image_attr.vertical_alignment,
      extended_template_styles::ATImagePropertyVerticalalignment::kCenter);
}

TEST(TestExtendedTemplate, ImgTagWithArgs) {
  auto text_tpl = extended_template::TextTemplate(
      "<image><img src=\"plus_{arg}_tag\" /></image>");
  const auto attrs = text_tpl.GetAttributedText(styles, args);
  const auto& image_attr =
      std::get<extended_template::ATImageProperty>(attrs.items[0]);

  EXPECT_EQ(image_attr.image_tag, "plus_zzz_tag");
  EXPECT_EQ(image_attr.type, ImageType::kImage);
  EXPECT_EQ(image_attr.width, 10);
  EXPECT_EQ(
      image_attr.vertical_alignment,
      extended_template_styles::ATImagePropertyVerticalalignment::kCenter);
}

TEST(TestExtendedTemplate, ImgTagWithoutSrc) {
  EXPECT_THROW(extended_template::TextTemplate("<img>Yandex</img>"),
               extended_template::ImgTagWithoutSrcError);
  EXPECT_THROW(
      extended_template::TextTemplate("<img source=\"hi.ru\" />Yandex"),
      extended_template::ImgTagWithoutSrcError);
}

TEST(TestExtendedTemplate, ContainerHappyPathUnstylish) {
  auto text_tpl = extended_template::TextTemplate(
      "<container meta_color=\"plus_color\">"
      "<img src=\"plus_icon_tag\" />{points}</container>");
  const auto attrs = text_tpl.GetAttributedText(styles, args);
  ASSERT_TRUE(std::get_if<extended_template::ATContainer>(&attrs.items[0]));

  const extended_template::ATContainer& container =
      std::get<extended_template::ATContainer>(attrs.items[0]);
  const auto& container_attr = container.items;
  ASSERT_TRUE(container_attr.size() == 2);

  extended_template::ATContainerGroupattributes expected_group_attr = {
      "plus_color"};
  EXPECT_EQ(container.group_attributes.meta_color,
            expected_group_attr.meta_color);

  const auto& image_attr =
      std::get<extended_template::ATImageProperty>(container_attr[0]);
  const auto& text_attr =
      std::get<extended_template::ATTextProperty>(container_attr[1]);

  EXPECT_EQ(image_attr.image_tag, "plus_icon_tag");
  EXPECT_EQ(image_attr.type, ImageType::kImage);
  EXPECT_EQ(text_attr.text, "50");
  EXPECT_EQ(text_attr.type, TextType::kText);
}

TEST(TestExtendedTemplate, ContainerHappyPathStyled) {
  auto text_tpl = extended_template::TextTemplate(
      "<container meta_color=\"plus_color\" some_arg=\"some_val\">"
      "<image><img src=\"plus_icon_tag\" "
      "/></image><plus>{points}</plus></container>");
  const auto attrs = text_tpl.GetAttributedText(styles, args);
  ASSERT_TRUE(std::get_if<extended_template::ATContainer>(&attrs.items[0]));

  const extended_template::ATContainer& container =
      std::get<extended_template::ATContainer>(attrs.items[0]);

  const auto& container_attr = container.items;
  ASSERT_TRUE(container_attr.size() == 2);

  extended_template::ATContainerGroupattributes expected_group_attr = {
      "plus_color"};
  EXPECT_EQ(container.group_attributes.meta_color,
            expected_group_attr.meta_color);

  const auto& image_attr =
      std::get<extended_template::ATImageProperty>(container_attr[0]);
  const auto& text_attr =
      std::get<extended_template::ATTextProperty>(container_attr[1]);

  EXPECT_EQ(image_attr.image_tag, "plus_icon_tag");
  EXPECT_EQ(image_attr.type, ImageType::kImage);
  EXPECT_EQ(image_attr.width, 10);
  EXPECT_EQ(image_attr.height, 10);
  EXPECT_EQ(
      image_attr.vertical_alignment,
      extended_template_styles::ATImagePropertyVerticalalignment::kCenter);

  EXPECT_EQ(text_attr.text, "50");
  EXPECT_EQ(text_attr.type, TextType::kText);
  EXPECT_EQ(text_attr.font_size, 2);
  EXPECT_EQ(text_attr.font_weight,
            extended_template_styles::ATTextPropertyFontweight::kLight);
  EXPECT_EQ(text_attr.font_style,
            extended_template_styles::ATTextPropertyFontstyle::kItalic);
}

TEST(TestExtendedTemplate, ContainerEmptyPathsErrors) {
  EXPECT_THROW(
      extended_template::TextTemplate("<container meta_color=\"\"><image><img "
                                      "src=\"plus_icon_tag\"/></image>"
                                      "<plus>{points}</plus></container>"),
      extended_template::EmptyAttributesInContainerError);

  EXPECT_THROW(extended_template::TextTemplate(
                   "<container><image><img src=\"plus_icon_tag\"/></image>"
                   "<plus>{points}</plus></container>"),
               extended_template::EmptyAttributesInContainerError);

  EXPECT_THROW(extended_template::TextTemplate(
                   "<container meta_color=\"plus_color\"></container>"),
               extended_template::EmptyContainerError);
}

TEST(TestExtendedTemplate, ContainerNestedError) {
  EXPECT_THROW(extended_template::TextTemplate(
                   "<container meta_color=\"plus_color\" some_arg=\"some_val\">"
                   "<image><img src=\"plus_icon_tag\"/></image>"
                   "<container meta_color=\"plus_color\">"
                   "<image><img src=\"another_plus_icon_tag\"/></image>"
                   "</container>"
                   "<plus>{points}</plus>"
                   "</container>"),
               extended_template::NestedContainerError);
}

TEST(TestExtendedTemplate, RemoveDoubleBraces) {
  const auto& check_removing = [](std::string arg,
                                  const std::string& expected) {
    extended_template::RemoveDoubleBraces(arg);
    EXPECT_EQ(arg, expected);
  };

  check_removing("abc", "abc");
  check_removing("abc{", "abc{");
  check_removing("abc{}", "abc{}");
  check_removing("abc{{}}", "abc{}");
  check_removing("abc{{bb}", "abc{bb}");
  check_removing("abc{{{}}}", "abc{{}}");
  check_removing("{{}}", "{}");
}
