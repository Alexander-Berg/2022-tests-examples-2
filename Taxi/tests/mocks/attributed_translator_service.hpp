#pragma once

#include "core/translator.hpp"

#include <functional>

namespace plus_plaque::mocks {

using HandlerAttributedTranslate =
    std::function<std::optional<extended_template::AttributedText>(
        const core::AttributedTranslationData&, const std::string&,
        const std::string&)>;
using HandlerAttributedTranslateThrow =
    std::function<extended_template::AttributedText(
        const core::AttributedTranslationData&, const std::string&,
        const std::string&)>;

class AttributedTranslatorServiceMock
    : public core::AttributedTranslatorService {
 private:
  HandlerAttributedTranslate handler_;
  HandlerAttributedTranslateThrow handler_throw_;

 public:
  AttributedTranslatorServiceMock(
      HandlerAttributedTranslate handler = nullptr,
      HandlerAttributedTranslateThrow handler_throw = nullptr)
      : handler_(std::move(handler)),
        handler_throw_(std::move(handler_throw)){};

  std::optional<extended_template::AttributedText> Translate(
      const core::AttributedTranslationData& translation,
      const std::string& locale,
      const std::string& fallback_locale =
          l10n::locales::kDefault) const override {
    return handler_(translation, locale, fallback_locale);
  }

  extended_template::AttributedText TranslateThrows(
      const core::AttributedTranslationData& translation,
      const std::string& locale,
      const std::string& fallback_locale =
          l10n::locales::kDefault) const override {
    return handler_throw_(translation, locale, fallback_locale);
  }
};

}  // namespace plus_plaque::mocks
