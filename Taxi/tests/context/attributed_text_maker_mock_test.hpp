#pragma once

#include <core/context/localizations.hpp>
#include <extended-template/extended-template.hpp>

#include <functional>

namespace routestats::test {

using Translation = core::Translation;

using AttributedTextHandler =
    std::function<std::optional<extended_template::AttributedText>(
        const Translation&, const std::string&)>;

class AttributedTextMakerMock : public core::AttributedTextMaker {
 public:
  AttributedTextMakerMock(const AttributedTextHandler& handler)
      : handler_(handler) {}

  virtual std::optional<extended_template::AttributedText> Translate(
      const Translation& translation, const std::string& locale) override {
    return handler_(translation, locale);
  }

  virtual std::optional<std::string> TranslateToString(
      const Translation& translation, const std::string& locale) override {
    return translation->main_key.key + "##" + locale;
  }

  std::optional<extended_template::AttributedText> TranslateAttributedText(
      const extended_template::AttributedText& attributed_text,
      const std::string& locale,
      [[maybe_unused]] const l10n::ArgsList& args) const override {
    std::vector<extended_template::ATUnit> items;
    for (const auto& item : attributed_text.items) {
      if (std::holds_alternative<extended_template::ATTextProperty>(item)) {
        // need to translate only text fields
        const auto text_item =
            std::get<extended_template::ATTextProperty>(item);
        const auto translated = TranslateATText(text_item, locale);
        if (!translated) {
          return std::nullopt;
        }

        items.push_back(translated.value());
      } else {
        items.push_back(item);
      }
    }
    return extended_template::AttributedText{items};
  }

 private:
  AttributedTextHandler handler_;

  std::optional<extended_template::ATTextProperty> TranslateATText(
      const extended_template::ATTextProperty& item,
      const std::string& locale) const {
    return extended_template::ATTextProperty{
        handlers::libraries::extended_template::ATTextPropertyType::kText,
        item.text + "##" + locale,
        item.font_size,
        item.font_weight,
        item.font_style,
        item.color,
        std::nullopt,
        std::nullopt};
  };
};

}  // namespace routestats::test
