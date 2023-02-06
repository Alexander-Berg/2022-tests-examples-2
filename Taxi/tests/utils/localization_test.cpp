#include <gmock/gmock.h>

#include <test_stubs/translations_test.hpp>
#include <utils/localization.hpp>

namespace {

namespace localization = eats_compensations_matrix::utils::localization;
namespace tests = eats_compensations_matrix::tests;

using localization::L10nTranslationsPtr;
using localization::Translation;
using localization::TranslationContext;

constexpr const char* kTestKey = "test_key";
constexpr const char* kTestKeyWithSpaceChars = " \t\n\rtest_key \t\n\r";

class TranslationsNotFound : public tests::Translations {
 public:
  virtual std::string Get(
      const std::string& /*keyset*/, const std::string& key,
      const std::string& /*locale*/, const int /*count*/,
      const std::string& /*fallback_locale*/) const override {
    throw l10n::NotFound(key);
  }
};

class TranslationsException : public tests::Translations {
 public:
  virtual std::string Get(
      const std::string& /*keyset*/, const std::string& key,
      const std::string& /*locale*/, const int /*count*/,
      const std::string& /*fallback_locale*/) const override {
    throw std::runtime_error(key);
  }
};

class TranslationsReturnKey : public tests::Translations {
 public:
  virtual std::string Get(
      const std::string& /*keyset*/, const std::string& key,
      const std::string& /*locale*/, const int /*count*/,
      const std::string& /*fallback_locale*/) const override {
    return key;
  }
};

}  // namespace

TEST(Translation, GreenFlow) {
  L10nTranslationsPtr translations =
      std::make_shared<const tests::Translations>();
  const auto expected_text = tests::Translations::GetTestTranslation(kTestKey);

  const Translation translation(translations);

  ASSERT_EQ(expected_text, translation.Translate(kTestKey));
  ASSERT_EQ(expected_text, translation.Translate(kTestKey, {}, 1));
  ASSERT_EQ(expected_text, translation.TranslateWithoutFallback(kTestKey));
  ASSERT_EQ(expected_text,
            translation.TranslateWithoutFallback(kTestKey, {}, 1));
}

TEST(Translation, NotFoundFallbackToKey) {
  L10nTranslationsPtr translations =
      std::make_shared<const TranslationsNotFound>();
  const Translation translation(translations);

  ASSERT_EQ(kTestKey, translation.Translate(kTestKey));
  ASSERT_EQ(kTestKey, translation.Translate(kTestKey, {}, 1));
}

TEST(Translation, NotFoundNoFallbackToKey) {
  L10nTranslationsPtr translations =
      std::make_shared<const TranslationsNotFound>();
  const Translation translation(translations);

  ASSERT_EQ(std::nullopt, translation.TranslateWithoutFallback(kTestKey));
  ASSERT_EQ(std::nullopt,
            translation.TranslateWithoutFallback(kTestKey, {}, 1));
}

TEST(Translation, ExceptionFallbackToKey) {
  L10nTranslationsPtr translations =
      std::make_shared<const TranslationsException>();
  const Translation translation(translations);

  ASSERT_EQ(kTestKey, translation.Translate(kTestKey));
  ASSERT_EQ(kTestKey, translation.Translate(kTestKey, {}, 1));
}

TEST(Translation, ExceptionNoFallbackToKey) {
  L10nTranslationsPtr translations =
      std::make_shared<const TranslationsException>();
  const Translation translation(translations);

  ASSERT_EQ(std::nullopt, translation.TranslateWithoutFallback(kTestKey));
  ASSERT_EQ(std::nullopt,
            translation.TranslateWithoutFallback(kTestKey, {}, 1));
}

TEST(Translation, TrimSpaces) {
  L10nTranslationsPtr translations =
      std::make_shared<const TranslationsReturnKey>();
  const Translation translation(translations);

  ASSERT_EQ(kTestKey, translation.Translate(kTestKeyWithSpaceChars, true));
  ASSERT_EQ(kTestKey,
            translation.Translate(kTestKeyWithSpaceChars, {}, 1, true));
  ASSERT_EQ(kTestKey,
            translation.TranslateWithoutFallback(kTestKeyWithSpaceChars, true));
  ASSERT_EQ(kTestKey, translation.TranslateWithoutFallback(
                          kTestKeyWithSpaceChars, {}, 1, true));
}
