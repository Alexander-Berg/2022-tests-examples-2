#include <impl/transliteration/transliterator.hpp>

#include <userver/utest/utest.hpp>

namespace {

constexpr char kTestString[] = "БВГбвг;&amp;& бБ0+_-0&amp123шЩ";

const std::unordered_map<std::string, std::string> kTestReplaceRules{
    {"б", "b"},  {"в", "v"},    {"г", "g"}, {"0", "0"}, {" ", "-"},
    {"ш", "sh"}, {"щ", "shch"}, {"_", "-"}, {"-", "-"}, {"&amp;", "&"},
};

}  // namespace

namespace eats_retail_seo::transliteration::tests {

UTEST(TestTransliterator, TestBaseTransliteration) {
  Transliterator transliterator{kTestReplaceRules,
                                Transliterator::Settings{false, false}};
  const std::string expected_str = "БВГbvg;&&-bБ0+--0&amp123shЩ";
  const auto test_str = transliterator.Transliterate(kTestString);
  EXPECT_EQ(expected_str, test_str);
}

UTEST(TestTransliterator, TestWithLower) {
  Transliterator transliterator{kTestReplaceRules,
                                Transliterator::Settings{true, false}};
  const std::string expected_str = "bvgbvg;&&-bb0+--0&amp123shshch";
  const auto test_str = transliterator.Transliterate(kTestString);
  EXPECT_EQ(expected_str, test_str);
}

UTEST(TestTransliterator, TestWithLowerAndRemove) {
  Transliterator transliterator{kTestReplaceRules,
                                Transliterator::Settings{true, true}};
  const std::string expected_str = "bvgbvg&&-bb0--0&shshch";
  const auto test_str = transliterator.Transliterate(kTestString);
  EXPECT_EQ(expected_str, test_str);
}

}  // namespace eats_retail_seo::transliteration::tests
