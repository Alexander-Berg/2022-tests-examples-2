#pragma once

#include <helpers/impl/legacy_translation_impl.hpp>
#include <helpers/translations.hpp>
#include <l10n/l10n.hpp>
#include <userver/utest/utest.hpp>

#include "mock_translations.hpp"

namespace zoneinfo {

class TestTranslator : public TankerTranslator {
 public:
  TestTranslator(TranslateHandler handler)
      : mock_translations_({std::move(handler)}) {}
  virtual ~TestTranslator() = default;

  std::optional<std::string> Translate(const Translation& translation,
                                       const std::string& locale) override {
    return mock_translations_.GetOptional(translation->GetKey().keyset,
                                          translation->GetKey().key, locale);
  }

  std::string TranslateThrows(const Translation& translation,
                              const std::string& locale) override {
    auto result = Translate(translation, locale);
    if (result) return *result;
    throw TranslationNotFound("test");
  }

 private:
  TestTranslations mock_translations_;
};

Translator MockTranslator(
    std::optional<TranslateHandler> handler = std::nullopt);

void AssertTankerKey(const TankerKey& left, const TankerKey& right);

}  // namespace zoneinfo
