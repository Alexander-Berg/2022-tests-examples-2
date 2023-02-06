#include "mock_legacy_translator.hpp"

namespace zoneinfo {

LegacyTranslator MockLegacyTranslator(std::optional<TranslateHandler> handler) {
  if (!handler) {
    handler = [](const std::string& keyset, const std::string& key,
                 const std::string& locale) {
      return keyset + "_" + key + "_legacy_tr_" + locale;
    };
  }
  return std::make_shared<LegacyTestTranslator>(*handler);
}

}  // namespace zoneinfo
