#pragma once

#include "core/translator.hpp"

#include <functional>

namespace sweet_home::mocks {

using HandlerTranslate = std::function<std::optional<std::string>(
    const core::TranslationData&, const std::string&)>;
using HandlerTranslateThrow = std::function<std::string(
    const core::TranslationData&, const std::string&)>;

class TranslatorServiceMock : public core::TranslatorService {
 private:
  HandlerTranslate handler_;
  HandlerTranslateThrow handler_throw_;

 public:
  TranslatorServiceMock(const HandlerTranslate& handler = nullptr,
                        const HandlerTranslateThrow& handler_throw = nullptr)
      : handler_(handler), handler_throw_(handler_throw){};

  std::optional<std::string> Translate(
      const core::TranslationData& translation, const std::string& locale,
      const std::string& /* fallback_locale */ =
          l10n::locales::kDefault) const override {
    if (!handler_) {
      return translation.main_key->key;
    }
    return handler_(translation, locale);
  }

  std::string TranslateThrows(const core::TranslationData& translation,
                              const std::string& locale,
                              const std::string& /* fallback_locale */ =
                                  l10n::locales::kDefault) const override {
    if (!handler_throw_) {
      return translation.main_key->key;
    }
    return handler_throw_(translation, locale);
  }
};

}  // namespace sweet_home::mocks
