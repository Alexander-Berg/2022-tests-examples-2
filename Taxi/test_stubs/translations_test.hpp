#pragma once

#include <l10n/l10n.hpp>

namespace eats_compensations_matrix::tests {

class Translations : public l10n::Translations {
 public:
  static std::string GetTestTranslation(const std::string& key);

  virtual std::string Get(const std::string& keyset, const std::string& key,
                          const std::string& locale, const int count,
                          const std::string& fallback_locale) const override;

  virtual const simple_template::TextTemplate& GetTemplate(
      const std::string& keyset, const std::string& key,
      const std::string& locale, const int count,
      const std::string& fallback_locale) const override;

  virtual std::string GetWithArgs(
      const std::string& keyset, const std::string& key,
      const std::string& locale, const l10n::ArgsList& args, int count,
      const std::string& fallback_locale) const override;

  virtual std::optional<std::string> GetOptional(
      const std::string& keyset, const std::string& key,
      const std::string& locale, int count,
      const std::string& fallback_locale) const override;

  virtual const simple_template::TextTemplate* GetTemplateOptional(
      const std::string& keyset, const std::string& key,
      const std::string& locale, int count,
      const std::string& fallback_locale) const override;

  virtual std::unordered_map<std::string, std::string> GetAllMappings(
      const std::string& keyset, const std::string& locale,
      const std::vector<std::string>& fallback_locales,
      bool use_all_fallbacks) const override;

  virtual std::optional<l10n::KeysetWrapper> GetKeysetOptional(
      const std::string& keyset,
      const std::string& fallback_locale) const override;

  virtual size_t GetSize() const override;
};

}  // namespace eats_compensations_matrix::tests
