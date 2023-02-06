#include <gtest/gtest.h>

#include "ancestors.hpp"

using eats_full_text_search_models::ParentCategory;
using namespace eats_full_text_search_indexer::models;

TEST(BuildAncestors, Empty) {
  // Tree 1: empty
  std::vector<ParentCategory> categories;
  const auto ancestors = BuildAncestors(categories, 1, true);
  ASSERT_EQ(ancestors.empty(), true);
}

TEST(BuildAncestors, NotFound) {
  // Tree: "name1" -> "name2" -> "name3"
  std::vector<ParentCategory> categories = {
      {1, std::nullopt, "name1"}, {2, 1, "name2"}, {3, 2, "name3"}};
  const auto ancestors = BuildAncestors(categories, 4, true);
  ASSERT_EQ(ancestors.empty(), true);
}

TEST(BuildAncestors, EmptyWithoutLower) {
  // Tree: "name1" -> "name2" -> "name3"
  std::vector<ParentCategory> categories = {
      {1, std::nullopt, "name1"}, {2, 1, "name2"}, {3, 2, "name3"}};
  const auto ancestors = BuildAncestors(categories, 1, false);
  ASSERT_EQ(ancestors.empty(), true);
}

TEST(BuildAncestors, Higer) {
  // Tree: "name1" -> "name2" -> "name3"
  std::vector<ParentCategory> categories = {
      {1, std::nullopt, "name1"}, {2, 1, "name2"}, {3, 2, "name3"}};
  const auto ancestors = BuildAncestors(categories, 1, true);
  ASSERT_EQ(ancestors.size(), 1);
  for (size_t i = 0; i < ancestors.size(); ++i) {
    ASSERT_EQ(ancestors[i].id, categories[i].id);
    ASSERT_EQ(ancestors[i].parent_id, categories[i].parent_id);
    ASSERT_EQ(ancestors[i].title, categories[i].title);
  }
}

TEST(BuildAncestors, All) {
  // Tree: "name1" -> "name2" -> "name3"
  std::vector<ParentCategory> categories = {
      {1, std::nullopt, "name1"}, {2, 1, "name2"}, {3, 2, "name3"}};
  const auto ancestors = BuildAncestors(categories, 3, true);
  ASSERT_EQ(ancestors.size(), 3);
  for (size_t i = 0; i < ancestors.size(); ++i) {
    ASSERT_EQ(ancestors[i].id, categories[i].id);
    ASSERT_EQ(ancestors[i].parent_id, categories[i].parent_id);
    ASSERT_EQ(ancestors[i].title, categories[i].title);
  }
}

TEST(BuildAncestors, Multi) {
  // Tree 1: "name1" -> "name2" -> "name3"
  // Tree 2: "name4" -> "name5"
  std::vector<ParentCategory> categories = {{1, std::nullopt, "name1"},
                                            {2, 1, "name2"},
                                            {3, 2, "name3"},
                                            {4, std::nullopt, "name4"},
                                            {5, 4, "name5"}};
  size_t first_tree_size = 3, second_tree_size = 2;
  // Build first tree
  {
    const auto ancestors = BuildAncestors(categories, 3, true);
    ASSERT_EQ(ancestors.size(), first_tree_size);
    for (size_t i = 0; i < ancestors.size(); ++i) {
      ASSERT_EQ(ancestors[i].id, categories[i].id);
      ASSERT_EQ(ancestors[i].parent_id, categories[i].parent_id);
      ASSERT_EQ(ancestors[i].title, categories[i].title);
    }
  }
  // Build second tree
  {
    const auto ancestors = BuildAncestors(categories, 5, true);
    ASSERT_EQ(ancestors.size(), second_tree_size);
    for (size_t i = 0; i < ancestors.size(); ++i) {
      ASSERT_EQ(ancestors[i].id, categories[i + first_tree_size].id);
      ASSERT_EQ(ancestors[i].parent_id,
                categories[i + first_tree_size].parent_id);
      ASSERT_EQ(ancestors[i].title, categories[i + first_tree_size].title);
    }
  }
}
