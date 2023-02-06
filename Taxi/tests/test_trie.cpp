#include <gtest/gtest.h>

#include <utils/trie.hpp>

namespace hejmdal {

TEST(TestTrie, TestDoubleInsert) {
  utils::Trie<int> t;
  t.Insert("abc", 123);
  EXPECT_THROW(t.Insert("abc", 123), std::logic_error);
}

TEST(TestTrie, TestFindAll) {
  utils::Trie<int> t;
  t.Insert("abcd", 1);
  t.Insert("abxy", 2);
  t.Insert("qwer", 3);
  ASSERT_EQ(t.Size(), 3);
  auto result = t.Find("", 10);
  ASSERT_EQ(result.size(), 3);
  EXPECT_EQ(result[0].word, "abcd");
  EXPECT_EQ(result[1].word, "abxy");
  EXPECT_EQ(result[2].word, "qwer");
  EXPECT_EQ(*result[0].data, 1);
  EXPECT_EQ(*result[1].data, 2);
  EXPECT_EQ(*result[2].data, 3);
}

TEST(TestTrie, TestEmptyFind) {
  utils::Trie<int> t;
  auto result = t.Find("a");
  EXPECT_TRUE(result.empty());
}

TEST(TestTrie, TestOkFind) {
  utils::Trie<int> t;
  t.Insert("abcd", 1);
  t.Insert("abqw", 2);
  t.Insert("abxy", 3);
  t.Insert("zxcv", 4);
  t.Insert("qwer", 5);
  t.Insert("asdf", 6);
  ASSERT_EQ(t.Size(), 6);
  auto result = t.Find("ab", 10);
  ASSERT_EQ(result.size(), 3);
  EXPECT_EQ(result[0].word, "abcd");
  EXPECT_EQ(result[1].word, "abqw");
  EXPECT_EQ(result[2].word, "abxy");
  EXPECT_EQ(*result[0].data, 1);
  EXPECT_EQ(*result[1].data, 2);
  EXPECT_EQ(*result[2].data, 3);
}

TEST(TestTrie, TestFindResponseSize) {
  utils::Trie<int> t;
  t.Insert("abcd", 1);
  t.Insert("abxy", 2);
  t.Insert("qwer", 3);
  ASSERT_EQ(t.Size(), 3);
  auto result = t.Find("", 2);
  ASSERT_EQ(result.size(), 2);
  EXPECT_EQ(result[0].word, "abcd");
  EXPECT_EQ(result[1].word, "abxy");
  EXPECT_EQ(*result[0].data, 1);
  EXPECT_EQ(*result[1].data, 2);
}

TEST(TestTrie, TestEraseEmptyTrie) {
  utils::Trie<int> t;
  std::string s("asdf");
  ASSERT_FALSE(t.Erase(s));
}

TEST(TestTrie, TestEraseEmptyWord) {
  utils::Trie<int> t;
  ASSERT_FALSE(t.Erase(""));
}

TEST(TestTrie, TetstOkErise) {
  utils::Trie<int> t;
  t.Insert("abcd", 1);
  t.Insert("abqw", 2);
  t.Insert("abxy", 3);
  t.Insert("zxcv", 4);
  t.Insert("qwer", 5);
  t.Insert("asdf", 6);
  ASSERT_EQ(t.Size(), 6);
  t.Erase("abqw");
  ASSERT_EQ(t.Size(), 5);
  auto result = t.Find("ab", 10);
  ASSERT_EQ(result.size(), 2);
  EXPECT_EQ(result[0].word, "abcd");
  EXPECT_EQ(result[1].word, "abxy");
  EXPECT_EQ(*result[0].data, 1);
  EXPECT_EQ(*result[1].data, 3);
}

TEST(TestTrie, TetstEraseDoesntExistWord) {
  utils::Trie<int> t;
  t.Insert("abcd", 1);
  t.Insert("abqw", 2);
  t.Insert("abxy", 3);
  ASSERT_EQ(t.Size(), 3);
  ASSERT_FALSE(t.Erase("zxcv"));
}

TEST(TestTrie, TestCopyConstructor) {
  utils::Trie<int> t_copy;
  {
    utils::Trie<int> t;
    t.Insert("abcd", 1);
    t.Insert("abqw", 2);
    t.Insert("abxy", 3);
    ASSERT_EQ(t.Size(), 3);
    t_copy = t;
  }
  ASSERT_EQ(t_copy.Size(), 3);
  auto result = t_copy.Find("ab", 10);
  ASSERT_EQ(result.size(), 3);
  EXPECT_EQ(result[0].word, "abcd");
  EXPECT_EQ(result[1].word, "abqw");
  EXPECT_EQ(result[2].word, "abxy");
  EXPECT_EQ(*result[0].data, 1);
  EXPECT_EQ(*result[1].data, 2);
  EXPECT_EQ(*result[2].data, 3);
}

TEST(TestTrie, TestEraseRoot) {
  utils::Trie<int> t;
  t.Insert("abcd", 1);
  t.Insert("ab", 2);
  t.Erase("ab");
  ASSERT_EQ(t.Size(), 1);
  auto result = t.Find("", 10);
  ASSERT_EQ(result.size(), 1);
  EXPECT_EQ(result[0].word, "abcd");
}

TEST(TestTrie, TestEraseChild) {
  utils::Trie<int> t;
  t.Insert("abcd", 1);
  t.Insert("ab", 2);
  t.Erase("abcd");
  ASSERT_EQ(t.Size(), 1);
  auto result = t.Find("ab");
  ASSERT_EQ(result.size(), 1);
  EXPECT_EQ(result[0].word, "ab");
}

TEST(TestTrie, TestEraseAll) {
  utils::Trie<int> t;
  t.Insert("abcd", 1);
  t.Insert("abxy", 2);
  t.Insert("qwer", 3);
  t.Erase("abcd");
  t.Erase("abxy");
  t.Erase("qwer");
  ASSERT_TRUE(t.IsEmpty());
  ASSERT_EQ(t.Size(), 0);
  auto result = t.Find("ab", 10);
  ASSERT_EQ(result.size(), 0);
}

TEST(TestTrie, TestClean) {
  utils::Trie<int> t;
  t.Insert("abcd", 1);
  t.Clear();
  ASSERT_TRUE(t.IsEmpty());
  ASSERT_EQ(t.Size(), 0);
  auto result = t.Find("", 10);
  ASSERT_EQ(result.size(), 0);
}

TEST(TestTrie, TestEraseDifferentRoot) {
  utils::Trie<int> t;
  t.Insert("abcd", 1);
  t.Insert("qwer", 2);
  t.Insert("zxcv", 3);
  t.Erase("qwer");
  ASSERT_EQ(t.Size(), 2);
  auto result = t.Find("", 10);
  ASSERT_EQ(result.size(), 2);
  EXPECT_EQ(result[0].word, "abcd");
  EXPECT_EQ(result[1].word, "zxcv");
  t.Erase("abcd");
  ASSERT_EQ(t.Size(), 1);
  auto result2 = t.Find("", 10);
  ASSERT_EQ(result2.size(), 1);
  EXPECT_EQ(result2[0].word, "zxcv");
}

TEST(TestTrie, TestEraseEndOfWordBranch) {
  utils::Trie<int> t;
  t.Insert("abcd", 1);
  t.Insert("abqw", 2);
  t.Insert("abzx", 3);
  t.Insert("ab", 4);
  ASSERT_EQ(t.Size(), 4);
  t.Erase("ab");
  ASSERT_EQ(t.Size(), 3);
  auto result = t.Find("", 10);
  ASSERT_EQ(result.size(), 3);
  EXPECT_EQ(result[0].word, "abcd");
  EXPECT_EQ(result[1].word, "abqw");
  EXPECT_EQ(result[2].word, "abzx");
}

TEST(TestTrie, TestInsertEmpty) {
  utils::Trie<int> t;
  t.Insert("", 1);
  ASSERT_EQ(t.Size(), 1);
  auto result = t.Find("", 10);
  ASSERT_EQ(result.size(), 1);
  EXPECT_EQ(*result[0].data, 1);
}

TEST(TestTrie, TestUpdData) {
  utils::Trie<int> t;
  t.Upsert("abc", 1);
  ASSERT_EQ(t.Size(), 1);
  auto result = t.Find("abc", 10);
  ASSERT_EQ(result.size(), 1);
  EXPECT_EQ(*result[0].data, 1);
  t.Upsert("abc", 123);
  ASSERT_EQ(t.Size(), 1);
  result = t.Find("abc", 10);
  ASSERT_EQ(result.size(), 1);
  EXPECT_EQ(*result[0].data, 123);
}

TEST(TestTrie, TestEraseEmpty) {
  utils::Trie<int> t;
  t.Insert("", 123);
  ASSERT_EQ(t.Size(), 1);
  auto result = t.Find("", 10);
  ASSERT_EQ(result.size(), 1);
  EXPECT_EQ(*result[0].data, 123);
  t.Erase("");
  ASSERT_TRUE(t.IsEmpty());
}

TEST(TestTrie, TestDoubleInsertVoid) {
  utils::Trie t;
  t.Insert("abc");
  EXPECT_THROW(t.Insert("abc"), std::logic_error);
}

TEST(TestTrie, TestFindAllVoid) {
  utils::Trie t;
  t.Insert("abcd");
  t.Insert("abxy");
  t.Insert("qwer");
  ASSERT_EQ(t.Size(), 3);
  auto result = t.Find("", 10);
  ASSERT_EQ(result.size(), 3);
  EXPECT_EQ(result[0], "abcd");
  EXPECT_EQ(result[1], "abxy");
  EXPECT_EQ(result[2], "qwer");
}

TEST(TestTrie, TestEmptyFindVoid) {
  utils::Trie<int> t;
  auto result = t.Find("a");
  EXPECT_TRUE(result.empty());
}

TEST(TestTrie, TestOkFindVoid) {
  utils::Trie t;
  t.Insert("abcd");
  t.Insert("abqw");
  t.Insert("abxy");
  t.Insert("zxcv");
  t.Insert("qwer");
  t.Insert("asdf");
  ASSERT_EQ(t.Size(), 6);
  auto result = t.Find("ab", 10);
  ASSERT_EQ(result.size(), 3);
  EXPECT_EQ(result[0], "abcd");
  EXPECT_EQ(result[1], "abqw");
  EXPECT_EQ(result[2], "abxy");
}

TEST(TestTrie, TestFindResponseSizeVoid) {
  utils::Trie t;
  t.Insert("abcd");
  t.Insert("abxy");
  t.Insert("qwer");
  ASSERT_EQ(t.Size(), 3);
  auto result = t.Find("", 2);
  ASSERT_EQ(result.size(), 2);
  EXPECT_EQ(result[0], "abcd");
  EXPECT_EQ(result[1], "abxy");
}

TEST(TestTrie, TestEraseEmptyTrieVoid) {
  utils::Trie t;
  std::string s("asdf");
  ASSERT_FALSE(t.Erase(s));
}

TEST(TestTrie, TetstOkEriseVoid) {
  utils::Trie t;
  t.Insert("abcd");
  t.Insert("abqw");
  t.Insert("abxy");
  t.Insert("zxcv");
  t.Insert("qwer");
  t.Insert("asdf");
  ASSERT_EQ(t.Size(), 6);
  t.Erase("abqw");
  ASSERT_EQ(t.Size(), 5);
  auto result = t.Find("ab", 10);
  ASSERT_EQ(result.size(), 2);
  EXPECT_EQ(result[0], "abcd");
  EXPECT_EQ(result[1], "abxy");
}

TEST(TestTrie, TetstEraseDoesntExistWordVoid) {
  utils::Trie t;
  t.Insert("abcd");
  t.Insert("abqw");
  t.Insert("abxy");
  ASSERT_EQ(t.Size(), 3);
  ASSERT_FALSE(t.Erase("zxcv"));
}

TEST(TestTrie, TestCopyConstructorVoid) {
  utils::Trie t_copy;
  {
    utils::Trie t;
    t.Insert("abcd");
    t.Insert("abqw");
    t.Insert("abxy");
    ASSERT_EQ(t.Size(), 3);
    t_copy = t;
  }
  ASSERT_EQ(t_copy.Size(), 3);
  auto result = t_copy.Find("ab", 10);
  ASSERT_EQ(result.size(), 3);
  EXPECT_EQ(result[0], "abcd");
  EXPECT_EQ(result[1], "abqw");
  EXPECT_EQ(result[2], "abxy");
}

}  // namespace hejmdal
