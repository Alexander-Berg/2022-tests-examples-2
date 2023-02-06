#include <handlers/text_filter.hpp>

#include <gtest/gtest.h>

namespace {

using handlers::TextFilter;

void AssertWords(const std::vector<std::string>& expected_words,
                 const TextFilter& text_filter) {
  ASSERT_EQ(expected_words, text_filter.GetWords());
}

models::Client BuildClient(std::string&& client_id, std::string&& name) {
  models::Client result;
  result.client_id = std::move(client_id);
  result.name = std::move(name);
  return result;
}

}  // namespace

TEST(TextFilter, GetWords) {
  AssertWords({}, TextFilter{std::string(65, 'a')});
  AssertWords({std::string(64, 'a')}, TextFilter{std::string(64, 'a')});
  AssertWords({}, TextFilter{""});
  AssertWords({}, TextFilter{"     "});
  AssertWords({}, TextFilter{"a"});
  AssertWords({}, TextFilter{"ab"});
  AssertWords({}, TextFilter{"ab"});
  AssertWords({}, TextFilter{"й"});
  AssertWords({}, TextFilter{"йц"});
  AssertWords({"abc"}, TextFilter{"AbC"});
  AssertWords({"abc"}, TextFilter{" aBc"});
  AssertWords({"abc"}, TextFilter{"aBC "});
  AssertWords({"abc"}, TextFilter{" abc "});
  AssertWords({"йцщ"}, TextFilter{" йцщ     "});
  AssertWords({"abc"}, TextFilter{"abc abc"});
  AssertWords({"xyz", "+7910"}, TextFilter{"xYz +7910 xyZ"});
  AssertWords({"w_1", "w_2", "w_3", "w_4", "w_5"},
              TextFilter{"w_1 W_2 W_3  W_4 w_5 "});
  AssertWords({"w_1", "w_2", "w_3", "w_4", "w_5"},
              TextFilter{"w_1 W_2 W_3 w_3 w_3 w_2  W_4 w_5 "});
  AssertWords({"w_1", "w_2", "w_3", "w_4", "w_6"},
              TextFilter{"w_1 W_2 W_3 w_3 w_4 w_6 W_5 "});
}

TEST(TextFilter, Check) {
  TextFilter text_filter{"АнТон тОД Ton tODua"};
  AssertWords({"антон", "тод", "ton", "todua"}, text_filter);
  ASSERT_FALSE(text_filter.Check(BuildClient("ivanov", "Иванов")));
  ASSERT_TRUE(text_filter.Check(BuildClient("anton", "")));
  ASSERT_TRUE(text_filter.Check(BuildClient("todua", "")));
  ASSERT_TRUE(text_filter.Check(BuildClient("", "Антон")));
  ASSERT_TRUE(text_filter.Check(BuildClient("Anton", "Тодуа")));
  ASSERT_TRUE(text_filter.Check(BuildClient("todua", "Антон")));
}
