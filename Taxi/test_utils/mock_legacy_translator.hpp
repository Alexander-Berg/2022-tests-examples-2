#pragma once

#include <userver/utest/utest.hpp>
#include "mock_translations.hpp"

namespace zoneinfo {

class LegacyTestTranslator : public LegacyTankerTranslator {
 public:
  LegacyTestTranslator(TranslateHandler handler)
      : mock_translations_({std::move(handler)}) {}
  virtual ~LegacyTestTranslator() = default;

  const l10n::Translations& GetRawL10nTranslations() override {
    return mock_translations_;
  }

 private:
  TestTranslations mock_translations_;
};

LegacyTranslator MockLegacyTranslator(
    std::optional<TranslateHandler> handler = std::nullopt);

}  // namespace zoneinfo
