#include "translations_test.hpp"

#include <userver/utils/assert.hpp>

namespace eats_orders_tracking::tests {

const std::string Translations::kDefaultLocale = "ru";

std::string Translations::GetTestTranslation(const std::string& key,
                                             const std::string& locale) {
  if (locale == "en") {
    return "Testing translation for " + key;
  } else {
    return "Тестовый перевод для " + key;
  }
}

std::string Translations::Get(const std::string& /*keyset*/,
                              const std::string& key, const std::string& locale,
                              const int /*count*/,
                              const std::string& /*fallback_locale*/) const {
  return GetTestTranslation(key, locale);
}

const simple_template::TextTemplate& Translations::GetTemplate(
    const std::string& /*keyset*/, const std::string& /*key*/,
    const std::string& /*locale*/, const int /*count*/,
    const std::string& /*fallback_locale*/) const {
  UINVARIANT(false, "Not implemented");
  static simple_template::TextTemplate test("test");
  return test;
}

std::string Translations::GetWithArgs(
    const std::string& keyset, const std::string& key,
    const std::string& locale, const l10n::ArgsList& /*args*/, int count,
    const std::string& fallback_locale) const {
  return Get(keyset, key, locale, count, fallback_locale);
}

std::optional<std::string> Translations::GetOptional(
    const std::string& keyset, const std::string& key,
    const std::string& locale, int count,
    const std::string& fallback_locale) const {
  return Get(keyset, key, locale, count, fallback_locale);
}

const simple_template::TextTemplate* Translations::GetTemplateOptional(
    const std::string& /*keyset*/, const std::string& /*key*/,
    const std::string& /*locale*/, int /*count*/,
    const std::string& /*fallback_locale*/) const {
  UINVARIANT(false, "Not implemented");
  return nullptr;
}

std::unordered_map<std::string, std::string> Translations::GetAllMappings(
    const std::string& /*keyset*/, const std::string& /*locale*/,
    const std::vector<std::string>& /*fallback_locales*/,
    bool /*use_all_fallbacks*/) const {
  return {};
}

std::optional<l10n::KeysetWrapper> Translations::GetKeysetOptional(
    const std::string& keyset, const std::string& fallback_locale) const {
  return l10n::KeysetWrapper(keyset, fallback_locale, *this);
}

size_t Translations::GetSize() const { return 1; }

}  // namespace eats_orders_tracking::tests
