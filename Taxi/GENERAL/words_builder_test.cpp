#include <gtest/gtest.h>

#include <utils/text_preparation.hpp>

#include "words_builder.hpp"

namespace {

void CheckWords(utils::WordsBuilder& builder,
                const std::vector<std::string>& expected_words) {
  const auto& built_words = builder.Build();
  std::vector<std::string> text_words;
  text_words.reserve(built_words.size());
  for (const auto& word : built_words) {
    text_words.push_back(word.text);
  }
  ASSERT_EQ(expected_words, text_words);
}

}  // namespace

TEST(WordsBuilder, SingleWordWithoutPreprocessor) {
  utils::WordsBuilder builder{1u, 3u};
  builder.AddWord("a");
  builder.AddWord("ab");
  builder.AddWord("aBc");
  builder.AddWord("abcd");
  builder.AddWord("abcde");
  CheckWords(builder, {"aBc"});
}

TEST(WordsBuilder, FiveWordsWithoutPreprocessor) {
  utils::WordsBuilder builder{5u, 0u};
  builder.AddWord("a");
  builder.AddWord("aB");
  builder.AddWord("abC");
  builder.AddWord("ABcd");
  builder.AddWord("abCd");
  builder.AddWord("abcde");
  CheckWords(builder, {"a", "aB", "abC", "ABcd", "abCd"});
}

TEST(WordsBuilder, FourUpperWords) {
  utils::WordsBuilder builder{5u, 5u, utils::MakeUpper};
  builder.AddWord(u8"абвгдеёжзийклмнопрстуфхцчшщъыьэюя");
  builder.AddWord("abcdefghijklmnopqrstuvwxyz");
  builder.AddWord("ABCDEFGHIJKLMNOPQRSTUVWXYZ");
  builder.AddWord(u8"АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ");
  builder.AddWord("abcd");
  builder.AddWord("abcde");
  builder.AddWord("012  345");
  builder.AddWord("none");
  CheckWords(builder, {u8"АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ",
                       "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "ABCDE", "012  345"});
}
