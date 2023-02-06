#include <gtest/gtest.h>

#include "search_text.hpp"

using eats_full_text_search::models::SearchAttrsCondition;
using eats_full_text_search::models::SearchTextCondition;
using eats_full_text_search::models::Serialize;

using eats_full_text_search::models::ExtendTextWithStar;

TEST(SearchTextCondition, SerializeEmpty) {
  SearchTextCondition text;
  ASSERT_EQ(Serialize(text), "");
}

TEST(SearchTextCondition, SerializeOnlyText) {
  SearchTextCondition text;
  text.text = "My Text";
  ASSERT_EQ(Serialize(text), "My Text");
}

TEST(SearchTextCondition, SerializeTextWithAll) {
  SearchTextCondition text;
  text.text = "My Text";
  text.conjunction.emplace_back("key", "value");
  ASSERT_EQ(Serialize(text), "My Text && key:value");
}

TEST(SearchTextCondition, SerializeTextWithMultiAll) {
  SearchTextCondition text;
  text.text = "My Text";
  text.conjunction.emplace_back("k1", "v1");
  text.conjunction.emplace_back("k2", "v2");
  ASSERT_EQ(Serialize(text), "My Text && (k1:v1 && k2:v2)");
}

TEST(SearchTextCondition, SerializeTextWithAny) {
  SearchTextCondition text;
  text.text = "My Text";
  text.disjunction.emplace_back("key", "value");
  ASSERT_EQ(Serialize(text), "My Text && key:value");
}

TEST(SearchTextCondition, SerializeTextWithMultiAny) {
  SearchTextCondition text;
  text.text = "My Text";
  text.disjunction.emplace_back("k1", "v1");
  text.disjunction.emplace_back("k2", "v2");
  ASSERT_EQ(Serialize(text), "My Text && (k1:v1 | k2:v2)");
}

TEST(SearchTextCondition, SerializeTextWithMultiAllAny) {
  SearchTextCondition text;
  text.text = "My Text";

  text.conjunction.emplace_back("k1", "v1");
  text.conjunction.emplace_back("k2", "v2");

  text.disjunction.emplace_back("k3", "v3");
  text.disjunction.emplace_back("k4", "v4");

  ASSERT_EQ(Serialize(text),
            "My Text && ((k1:v1 && k2:v2) && (k3:v3 | k4:v4))");
}

TEST(SearchAttrsCondition, SerializeWithOneCondExtra) {
  std::vector<SearchAttrsCondition> conds;
  auto& cond = conds.emplace_back();
  cond.conjunction.emplace_back("key", "value");

  ASSERT_EQ(Serialize(conds), "key:value");
}

TEST(SearchAttrsCondition, SerializeWithOneCondAny) {
  std::vector<SearchAttrsCondition> conds;
  auto& cond = conds.emplace_back();

  cond.disjunction.emplace_back("k1", "v1");
  cond.disjunction.emplace_back("k2", "v2");

  ASSERT_EQ(Serialize(conds), "(k1:v1 | k2:v2)");
}

TEST(SearchAttrsCondition, SerializeWithTwoConds) {
  std::vector<SearchAttrsCondition> conds;
  auto& cond = conds.emplace_back();

  cond.conjunction.emplace_back("k1", "v1");
  cond.disjunction.emplace_back("k2", "v2");

  auto& cond2 = conds.emplace_back();
  cond2.conjunction.emplace_back("k3", "v3");
  cond2.conjunction.emplace_back("k4", "v4");

  ASSERT_EQ(Serialize(conds), "(k1:v1 && k2:v2) | (k3:v3 && k4:v4)");
}

// Тесты ниже описывают случаи, которые реально сейчас
// используются в коде
TEST(SearchTextReal, SerializeInPlaceSerch) {
  SearchTextCondition text;
  text.text = "My Text";
  text.conjunction.emplace_back("place_slug", "my_slug");
  ASSERT_EQ(Serialize(text), "My Text && place_slug:my_slug");
}

TEST(SearchTextReal, SerializePlaces) {
  SearchTextCondition text;
  text.text = "My Text";
  text.disjunction.emplace_back("place_id", "1");
  text.disjunction.emplace_back("place_id", "2");
  text.disjunction.emplace_back("place_id", "3");
  ASSERT_EQ(Serialize(text),
            "My Text && (place_id:1 | place_id:2 | place_id:3)");
}

TEST(SearchTextReal, SerializeCategory) {
  std::vector<SearchAttrsCondition> conds;
  auto& cond = conds.emplace_back();

  cond.conjunction.emplace_back("i_type", "2");
  cond.conjunction.emplace_back("i_core_category_id", "100");

  ASSERT_EQ(Serialize(conds), "(i_type:2 && i_core_category_id:100)");
}
