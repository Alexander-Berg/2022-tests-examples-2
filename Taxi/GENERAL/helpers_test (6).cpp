#include "helpers.hpp"

#include <vector>

#include <userver/utest/utest.hpp>

UTEST(HelpersTest, MergeSearchResults) {
  using identification::helpers::MergeSearchResults;
  using SearchResult = identification::SignatureIndex::SearchResultItem;

  {
    std::vector<SearchResult> result1;
    result1.reserve(5);
    for (int i = 1; i <= 10; i += 2) {
      result1.push_back({std::to_string(i), float(i)});
    }

    std::vector<SearchResult> result2;
    result2.reserve(5);
    for (int i = 2; i <= 10; i += 2) {
      result2.push_back({std::to_string(i), float(i)});
    }

    const auto result =
        MergeSearchResults(std::move(result1), std::move(result2), 10);

    EXPECT_EQ(result.size(), 10);
    for (int i = 1; i <= 10; ++i) {
      const auto& item = result[i - 1];
      EXPECT_EQ(item.name, std::to_string(i));
    }
  }
  {
    std::vector<SearchResult> result1;
    result1.reserve(5);
    for (int i = 1; i <= 10; i += 2) {
      result1.push_back({std::to_string(i), float(i)});
    }

    std::vector<SearchResult> result2;
    result2.reserve(5);
    for (int i = 2; i <= 10; i += 2) {
      result2.push_back({std::to_string(i), float(i)});
    }

    const auto result =
        MergeSearchResults(std::move(result1), std::move(result2), 4);

    EXPECT_EQ(result.size(), 4);
    for (int i = 1; i <= 4; ++i) {
      const auto& item = result[i - 1];
      EXPECT_EQ(item.name, std::to_string(i));
    }
  }
  {
    std::vector<SearchResult> result1;
    result1.reserve(3);
    for (int i = 0; i < 3; ++i) {
      result1.push_back({std::to_string(i), float(i)});
    }

    std::vector<SearchResult> result2;
    result2.reserve(7);
    for (int i = 3; i < 10; ++i) {
      result2.push_back({std::to_string(i), float(i)});
    }

    const auto result =
        MergeSearchResults(std::move(result1), std::move(result2), 10);

    EXPECT_EQ(result.size(), 10);
    for (int i = 0; i < 10; ++i) {
      const auto& item = result[i];
      EXPECT_EQ(item.name, std::to_string(i));
    }
  }
}
