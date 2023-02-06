#include "matcher.hpp"
#include "place.hpp"

#include <gtest/gtest.h>

namespace eats_catalog::models {

TEST(GetTagMatcherFunc, no_match_missing) {
  PlaceInfo info;
  info.tags.insert("best");
  Place p{info};

  const auto matcher = GetTagMatcherFunc("test");
  ASSERT_FALSE(matcher(p));
}

TEST(GetTagMatcherFunc, no_match_empty) {
  PlaceInfo info;
  info.tags = {};
  Place p{info};

  const auto matcher = GetTagMatcherFunc("test");
  ASSERT_FALSE(matcher(p));
}

TEST(GetTagMatcherFunc, match) {
  PlaceInfo info;
  info.tags.insert("test");
  Place p{info};

  const auto matcher = GetTagMatcherFunc("test");
  ASSERT_TRUE(matcher(p));
}

TEST(IsMatchingAll, tags) {
  PlaceInfo info;
  info.tags.insert("foo");
  info.tags.insert("bar");
  Place p{info};

  std::vector<MatcherFunc> matchers;
  matchers.push_back(GetTagMatcherFunc("foo"));
  matchers.push_back(GetTagMatcherFunc("bar"));

  const auto matcher = GetAllOfMatcherFunc(matchers);
  ASSERT_TRUE(matcher(p));
}

TEST(GetQuickFilterMatcherFunc, no_match_empty) {
  PlaceInfo info;
  info.quick_filters = {};
  Place p{info};

  const auto matcher = GetQuickFilterMatcherFunc(QuickFilterId(1));
  ASSERT_FALSE(matcher(p));
}

TEST(GetQuickFilterMatcherFunc, no_match_missing) {
  PlaceInfo info;
  info.quick_filters.insert(QuickFilterId(2));
  Place p{info};

  const auto matcher = GetQuickFilterMatcherFunc(QuickFilterId(1));
  ASSERT_FALSE(matcher(p));
}

TEST(GetQuickFilterMatcherFunc, match) {
  PlaceInfo info;
  info.quick_filters.insert(QuickFilterId(1));
  info.quick_filters.insert(QuickFilterId(2));
  Place p{info};

  const auto matcher = GetQuickFilterMatcherFunc(QuickFilterId(1));
  ASSERT_TRUE(matcher(p));
}

TEST(GetFavoriteMatcherFunc, match) {
  PlaceInfo info;
  info.brand.id = BrandId(1);
  Place p{info};

  const auto matcher = GetFavoriteMatcherFunc({BrandId(1)});
  ASSERT_TRUE(matcher(p));
}

TEST(GetFavoriteMatcherFunc, no_match) {
  PlaceInfo info;
  info.brand.id = BrandId(2);
  Place p{info};

  const auto matcher = GetFavoriteMatcherFunc({BrandId(1)});
  ASSERT_FALSE(matcher(p));
}

TEST(IsMatchingAll, match_many) {
  PlaceInfo info;
  info.quick_filters.insert(QuickFilterId(1));
  info.tags.insert("test");
  Place p{info};

  std::vector<MatcherFunc> matchers;
  matchers.push_back(GetQuickFilterMatcherFunc(QuickFilterId(1)));
  matchers.push_back(GetTagMatcherFunc("test"));

  const auto matcher = GetAllOfMatcherFunc(matchers);
  ASSERT_TRUE(matcher(p));
}

TEST(IsMatchingAll, not_match_first) {
  PlaceInfo info;
  info.quick_filters.insert(QuickFilterId(2));
  info.tags.insert("test");
  Place p{info};

  std::vector<MatcherFunc> matchers;
  matchers.push_back(GetQuickFilterMatcherFunc(QuickFilterId(1)));
  matchers.push_back(GetTagMatcherFunc("test"));

  const auto matcher = GetAllOfMatcherFunc(matchers);

  ASSERT_FALSE(matcher(p));
}

TEST(IsMatchingAll, not_match_second) {
  PlaceInfo info;
  info.quick_filters.insert(QuickFilterId(1));
  info.tags.insert("unit-test");
  Place p{info};

  std::vector<MatcherFunc> matchers;
  matchers.push_back(GetQuickFilterMatcherFunc(QuickFilterId(1)));
  matchers.push_back(GetTagMatcherFunc("test"));

  const auto matcher = GetAllOfMatcherFunc(matchers);

  ASSERT_FALSE(matcher(p));
}

}  // namespace eats_catalog::models
