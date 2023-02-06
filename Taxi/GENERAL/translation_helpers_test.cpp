#include <userver/utest/utest.hpp>

#include <testing/taxi_config.hpp>

#include <memory>
#include <optional>
#include <string>

#include <boost/algorithm/string/replace.hpp>
#include <boost/regex.hpp>
#include <boost/regex/icu.hpp>

#include <userver/formats/json.hpp>

#include <l10n/l10n.hpp>
#include <price-format/currency.hpp>

#include <userver/dynamic_config/snapshot.hpp>

#include <utils/localizer.hpp>
#include <utils/translation_helpers.hpp>

namespace {

// copypaste from convert_to_template.cpp
std::string ConvertToTemplate(std::string str) {
  boost::replace_all(str, "{", "{{");
  boost::replace_all(str, "}", "}}");

  static const boost::u32regex e1 = boost::make_u32regex("%\\(([^)]+)\\)[sdf]");
  str = boost::u32regex_replace(str, e1, std::string("{$1}"));

  static const boost::u32regex e2 =
      boost::make_u32regex("%\\(([^)]+)\\)(\\.\\d+f)");
  str = boost::u32regex_replace(str, e2, std::string("{$1:$2}"));

  // there are templates "... %s ... %d ..." in project taximetre
  // FIXME: Bad code, either delete it or construct new string
  static const boost::u32regex e3 = boost::make_u32regex("(?<!%)%[sdf]");
  boost::smatch result;
  size_t count = 0;
  while (boost::u32regex_search(str.cbegin(), str.cend(), result, e3)) {
    ++count;
    const std::string named = "{" + std::to_string(count) + "}";
    str.replace(result[0].first - str.cbegin(),
                result[0].second - result[0].first, named);
  }

  boost::replace_all(str, "%%", "%");

  // there are tempaltes "... {0} ... {14} ..." in taximeter messages
  // FIXME: Bad code, either delete it or construct new string
  static const boost::u32regex e4 = boost::make_u32regex("\\{\\{\\d+\\}\\}");
  while (boost::u32regex_search(str.cbegin(), str.cend(), result, e4)) {
    std::string item(result[0].first, result[0].second);
    item = item.substr(1, item.size() - 2);
    str.replace(result[0].first - str.cbegin(),
                result[0].second - result[0].first, item);
  }
  return str;
}

class MockTranslations final : public l10n::Translations {
 public:
  MockTranslations()
      : ptr_(std::make_shared<simple_template::TextTemplate>("template")) {}

  ~MockTranslations() {}

  std::string GetWithArgs([[maybe_unused]] const std::string& keyset,
                          const std::string& key,
                          [[maybe_unused]] const std::string& locale,
                          const l10n::ArgsList& args,
                          [[maybe_unused]] int count = 1,
                          [[maybe_unused]] const std::string& fallback_locale =
                              l10n::locales::kRussian) const final {
    return GetTemplate(keyset, key, locale, count, fallback_locale)
        .SubstituteArgs(args);
  }

  std::string Get([[maybe_unused]] const std::string& keyset,
                  const std::string& key,
                  [[maybe_unused]] const std::string& locale,
                  [[maybe_unused]] const int count = 1,
                  [[maybe_unused]] const std::string& fallback_locale =
                      l10n::locales::kRussian) const final {
    if (key == "round.few_meters") return "10 m";
    return "TRANSLATED";
  }

  const simple_template::TextTemplate& GetTemplate(
      [[maybe_unused]] const std::string& keyset,
      [[maybe_unused]] const std::string& key,
      [[maybe_unused]] const std::string& locale,
      [[maybe_unused]] const int count = 1,
      [[maybe_unused]] const std::string& fallback_locale =
          l10n::locales::kRussian) const final {
    auto conv = [](const std::string& str) {
      return simple_template::TextTemplate(ConvertToTemplate(str));
    };
    static const std::map<std::string, simple_template::TextTemplate> kMap{
        {"round.tens_meters", conv("%(value).0f m")},
        {"round.hundreds_meters", conv("%(value).0f m")},
        {"round.kilometers", conv("%(value).0f km")},
        {"detailed.kilometers", conv("%(value).0f km")},
        {"", simple_template::TextTemplate("")},
    };

    const auto it = kMap.find(key);
    if (it != std::end(kMap)) {
      return it->second;
    }

    return kMap.at("");
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

TEST(TestUtils, RoundDistance) {
  auto translations = std::make_shared<MockTranslations>();
  const utils::Localizer localizer(*translations, "ru", /*country_id*/ "rus",
                                   price_format::Currency{"rub"},
                                   dynamic_config::GetDefaultSnapshot());

  // always ceil-like
  EXPECT_EQ(utils::RoundDistance(1, localizer), "10 m");
  EXPECT_EQ(utils::RoundDistance(8, localizer), "10 m");
  EXPECT_EQ(utils::RoundDistance(12, localizer), "20 m");
  EXPECT_EQ(utils::RoundDistance(56, localizer), "60 m");
  EXPECT_EQ(utils::RoundDistance(123, localizer), "200 m");
  EXPECT_EQ(utils::RoundDistance(456, localizer), "500 m");
  EXPECT_EQ(utils::RoundDistance(1234, localizer), "1.3 km");
  EXPECT_EQ(utils::RoundDistance(5678, localizer), "5.7 km");
  EXPECT_EQ(utils::RoundDistance(8951, localizer), "9 km");
  EXPECT_EQ(utils::RoundDistance(12345, localizer), "13 km");
}
