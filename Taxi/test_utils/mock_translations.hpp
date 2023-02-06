#pragma once

#include <helpers/impl/legacy_translation_impl.hpp>
#include <helpers/translations.hpp>
#include <l10n/l10n.hpp>

#include <functional>

#include <userver/utest/utest.hpp>

namespace zoneinfo {

using TranslateHandler = std::function<std::optional<std::string>(
    const std::string&, const std::string&, const std::string&)>;

class TestTranslations : public l10n::Translations {
 public:
  TestTranslations(TranslateHandler handler)
      : handler_(std::move(handler)),
        template_ptr_(
            std::make_shared<simple_template::TextTemplate>("template")) {}

  ~TestTranslations() {}

  std::string GetWithArgs([[maybe_unused]] const std::string& keyset,
                          [[maybe_unused]] const std::string& key,
                          [[maybe_unused]] const std::string& locale,
                          [[maybe_unused]] const l10n::ArgsList& args,
                          [[maybe_unused]] int count = 1,
                          [[maybe_unused]] const std::string& fallback_locale =
                              l10n::locales::kRussian) const final {
    auto result = GetOptional(keyset, key, locale, count, fallback_locale);
    if (result) return *result;
    throw TranslationNotFound("test");
  }

  std::string Get([[maybe_unused]] const std::string& keyset,
                  [[maybe_unused]] const std::string& key,
                  [[maybe_unused]] const std::string& locale,
                  [[maybe_unused]] const int count = 1,
                  [[maybe_unused]] const std::string& fallback_locale =
                      l10n::locales::kRussian) const final {
    auto result = GetOptional(keyset, key, locale, count, fallback_locale);
    if (result) return *result;
    throw TranslationNotFound("test");
  }
  const simple_template::TextTemplate& GetTemplate(
      [[maybe_unused]] const std::string& keyset,
      [[maybe_unused]] const std::string& key,
      [[maybe_unused]] const std::string& locale,
      [[maybe_unused]] const int count = 1,
      [[maybe_unused]] const std::string& fallback_locale =
          l10n::locales::kRussian) const final {
    return *template_ptr_;
  }
  std::optional<std::string> GetOptional(
      [[maybe_unused]] const std::string& keyset,
      [[maybe_unused]] const std::string& key,
      [[maybe_unused]] const std::string& locale,
      [[maybe_unused]] int count = 1,
      [[maybe_unused]] const std::string& fallback_locale =
          l10n::locales::kRussian) const final {
    return handler_(keyset, key, locale);
  }
  const simple_template::TextTemplate* GetTemplateOptional(
      [[maybe_unused]] const std::string& keyset,
      [[maybe_unused]] const std::string& key,
      [[maybe_unused]] const std::string& locale,
      [[maybe_unused]] int count = 1,
      [[maybe_unused]] const std::string& fallback_locale =
          l10n::locales::kRussian) const final {
    return nullptr;
  }
  std::unordered_map<std::string, std::string> GetAllMappings(
      [[maybe_unused]] const std::string& keyset,
      [[maybe_unused]] const std::string& locale,
      [[maybe_unused]] const std::vector<std::string>& fallback_locales,
      [[maybe_unused]] bool use_all_fallbacks) const final {
    return {};
  };

  std::optional<l10n::KeysetWrapper> GetKeysetOptional(
      const std::string& keyset, const std::string& fallback_locale =
                                     l10n::locales::kDefault) const final {
    return l10n::KeysetWrapper(keyset, fallback_locale, *this);
  }

  size_t GetSize() const { return 1; }

 private:
  TranslateHandler handler_;
  std::shared_ptr<simple_template::TextTemplate> template_ptr_;
};

}  // namespace zoneinfo
