#include <gtest/gtest.h>

#include <testing/source_path.hpp>
#include <userver/fs/blocking/read.hpp>

#include <l10n/l10n.hpp>

#include <views/translations.hpp>

namespace {

std::string ReadFile(const std::string& name) {
  return fs::blocking::ReadFileContents(
      utils::CurrentSourcePath("tests/static/" + name));
}

class TestTranslations : public l10n::Translations {
 public:
  TestTranslations()
      : ptr_(std::make_shared<simple_template::TextTemplate>("template")) {}

  ~TestTranslations() {}

  std::string GetWithArgs([[maybe_unused]] const std::string& keyset,
                          [[maybe_unused]] const std::string& key,
                          [[maybe_unused]] const std::string& locale,
                          [[maybe_unused]] const l10n::ArgsList& args,
                          [[maybe_unused]] int count = 1,
                          [[maybe_unused]] const std::string& fallback_locale =
                              l10n::locales::kRussian) const final {
    return "TRANSLATED";
  }

  std::string Get([[maybe_unused]] const std::string& keyset,
                  [[maybe_unused]] const std::string& key,
                  [[maybe_unused]] const std::string& locale,
                  [[maybe_unused]] const int count = 1,
                  [[maybe_unused]] const std::string& fallback_locale =
                      l10n::locales::kRussian) const final {
    return "TRANSLATED";
  }
  const simple_template::TextTemplate& GetTemplate(
      [[maybe_unused]] const std::string& keyset,
      [[maybe_unused]] const std::string& key,
      [[maybe_unused]] const std::string& locale,
      [[maybe_unused]] const int count = 1,
      [[maybe_unused]] const std::string& fallback_locale =
          l10n::locales::kRussian) const final {
    return *ptr_;
  }
  std::optional<std::string> GetOptional(
      [[maybe_unused]] const std::string& keyset,
      [[maybe_unused]] const std::string& key,
      [[maybe_unused]] const std::string& locale,
      [[maybe_unused]] int count = 1,
      [[maybe_unused]] const std::string& fallback_locale =
          l10n::locales::kRussian) const final {
    return std::nullopt;
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
  std::shared_ptr<simple_template::TextTemplate> ptr_;
};

}  // namespace

TEST(TestLocalizeMembers, LocalizeMembers) {
  auto translations = std::make_shared<TestTranslations>();
  formats::json::Value data = formats::json::FromString(ReadFile("data.json"));
  formats::json::Value expected =
      formats::json::FromString(ReadFile("expected.json"));
  const auto& localized =
      views::translations::LocalizeMembers(data, *translations, "ru");
  ASSERT_EQ(expected, localized);
}
