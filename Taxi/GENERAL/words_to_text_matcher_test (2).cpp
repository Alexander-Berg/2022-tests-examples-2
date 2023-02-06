#include "utils/words_to_text_matcher.hpp"

#include <gtest/gtest.h>

using utils::WordMatch;

namespace {

utils::Words MakeWords(std::initializer_list<const char*> words) {
  std::size_t index = 0;
  utils::Words result;
  for (auto& word : words) {
    result.emplace_back(word, index++);
  }
  return result;
}

}  // namespace

TEST(MatchWordToText, All) {
  using utils::MatchWordToText;

  EXPECT_EQ(WordMatch::Empty, MatchWordToText("todua", "tod"));
  EXPECT_EQ(WordMatch::Prefix, MatchWordToText("tod", "todua"));
  EXPECT_EQ(WordMatch::Substring, MatchWordToText("odu", "todua"));
  EXPECT_EQ(WordMatch::Substring, MatchWordToText("ua", "todua"));
  EXPECT_EQ(WordMatch::Exact, MatchWordToText("todua", "todua"));
}

TEST(WordsToTextMatcher, SingleWord) {
  const auto& words = MakeWords({"anto"});
  utils::WordIndices matched_words;
  utils::WordsToTextMatcher matcher{words, matched_words};

  EXPECT_EQ(WordMatch::Empty, matcher.GetMatch());

  matcher.MatchWords("ant");
  EXPECT_EQ(WordMatch::Empty, matcher.GetMatch());

  matcher.MatchWords("manton");
  EXPECT_EQ(WordMatch::Substring, matcher.GetMatch());

  matcher.MatchWords("abra");
  EXPECT_EQ(WordMatch::Substring, matcher.GetMatch());

  matcher.MatchWords("anton");
  EXPECT_EQ(WordMatch::Prefix, matcher.GetMatch());

  matcher.MatchWords("manton");
  EXPECT_EQ(WordMatch::Prefix, matcher.GetMatch());

  matcher.MatchWords("anto");
  EXPECT_EQ(WordMatch::Exact, matcher.GetMatch());

  matcher.MatchWords("kadabra");
  EXPECT_EQ(WordMatch::Exact, matcher.GetMatch());

  matcher.Reset(WordMatch::Exact);

  matcher.MatchWords("ant");
  EXPECT_EQ(WordMatch::Empty, matcher.GetMatch());

  matcher.MatchWords("manton");
  EXPECT_EQ(WordMatch::Empty, matcher.GetMatch());

  matcher.MatchWords("abra");
  EXPECT_EQ(WordMatch::Empty, matcher.GetMatch());

  matcher.MatchWords("anton");
  EXPECT_EQ(WordMatch::Empty, matcher.GetMatch());

  matcher.MatchWords("manton");
  EXPECT_EQ(WordMatch::Empty, matcher.GetMatch());

  matcher.MatchWords("anto");
  EXPECT_EQ(WordMatch::Exact, matcher.GetMatch());

  matcher.MatchWords("kadabra");
  EXPECT_EQ(WordMatch::Exact, matcher.GetMatch());
}

TEST(WordsToTextMatcher, BestMatch) {
  {
    const auto& words = MakeWords({"vwx", "xyz"});
    utils::WordIndices matched_words;
    utils::WordsToTextMatcher matcher{words, matched_words};
    matcher.MatchWords("vwxyz");
    EXPECT_EQ(WordMatch::Prefix, matcher.GetMatch());
  }

  {
    const auto& words = MakeWords({"vwxyz", "xyz"});
    utils::WordIndices matched_words;
    utils::WordsToTextMatcher matcher{words, matched_words};
    matcher.MatchWords("vwxyz");
    EXPECT_EQ(WordMatch::Exact, matcher.GetMatch());
  }

  {
    const auto& words = MakeWords({"vwxyz", "vwx"});
    utils::WordIndices matched_words;
    utils::WordsToTextMatcher matcher{words, matched_words};
    matcher.MatchWords("vwxyz");
    EXPECT_EQ(WordMatch::Exact, matcher.GetMatch());
  }
}

TEST(WordsToTextMatcher, MatchBestWord) {
  const auto& words = MakeWords({"ant", "anton", "dua"});
  utils::WordIndices matched_words;
  utils::WordsToTextMatcher matcher{words, matched_words,
                                    utils::WordMatchMode::BestWord};

  matcher.MatchWords("anton");
  EXPECT_EQ(WordMatch::Exact, matcher.GetMatch());
  EXPECT_EQ(1u, matched_words.size());
  EXPECT_TRUE(matched_words.count(1) > 0);

  matcher.Reset();
  matcher.MatchWords("todua");
  EXPECT_EQ(WordMatch::Substring, matcher.GetMatch());
  EXPECT_EQ(2u, matched_words.size());
  EXPECT_TRUE(matched_words.count(2) > 0);
}
