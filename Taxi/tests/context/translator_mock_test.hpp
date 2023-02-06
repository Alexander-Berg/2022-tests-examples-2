#pragma once

#include <core/context/localizations.hpp>

#include <functional>

namespace routestats::test {

using Translation = core::Translation;

using TranslationHandler = std::function<std::optional<std::string>(
    const Translation&, const std::string&)>;

class TranslatorMock : public core::Translator {
 public:
  TranslatorMock(const TranslationHandler& handler) : handler_(handler){};

  std::optional<std::string> Translate(const Translation& translation,
                                       const std::string& locale) override {
    return handler_(translation, locale);
  }

 private:
  TranslationHandler handler_;
};

}  // namespace routestats::test
