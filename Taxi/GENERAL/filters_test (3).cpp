#include "filters.hpp"

#include <models/place.hpp>

#include <gtest/gtest.h>

namespace handlers::internal_v1_catalog_for_layout::post::filters {

namespace {

using eats_catalog::models::Place;
using eats_catalog::models::PlaceInfo;

const std::unordered_map<eats_catalog::models::QuickFilterId,
                         eats_catalog::models::QuickFilter>
    kKnownFilters{};
const std::optional<std::unordered_map<eats_catalog::models::PlaceId, double>>
    kPlusCashback{};
const DeliveryTimeFilter kDeliveryTimeFilter{std::nullopt, false};
const eats_catalog::models::ShippingType kShippingType{};
const std::optional<std::unordered_map<eats_catalog::models::BrandId, Favorite>>
    kFavoriteBrands{};
const std::unordered_set<std::string> kKnownTags{};
const std::vector<FilterPtr> kFilters{};

FilterScrapper MakeFilterScrapper(const std::vector<const Place*>& places) {
  const auto context = eats_catalog::models::Context({});

  FilterScrapper scrapper(context, kKnownFilters, kPlusCashback, std::nullopt,
                          kFavoriteBrands, {});
  for (const auto* place : places) {
    scrapper.Fill(*place);
  }
  return scrapper;
}

Matcher MakeFilterMatcher(
    const std::optional<std::vector<RequestFilterGroup>>& groups,
    const std::optional<std::unordered_set<std::string>>& tags = std::nullopt) {
  const auto& known_tags = tags.has_value() ? tags.value() : kKnownTags;
  MatcherFactory factory(kShippingType, kKnownFilters, kPlusCashback,
                         kDeliveryTimeFilter, kFilters, kFavoriteBrands,
                         known_tags);
  return factory.GetMatcher(groups);
}

}  // namespace

TEST(ScrapperGetMatcher, any) {
  PlaceInfo info;
  Place p{info};
  const auto target = MakeFilterScrapper({&p});

  const auto matcher = MakeFilterMatcher({});

  ASSERT_TRUE(matcher.Match(p));
}

TEST(ScrapperGetMatcher, match_single_tag) {
  PlaceInfo info1;
  info1.tags.insert("foo");
  info1.tags.insert("bar");
  Place p1{info1};

  PlaceInfo info2;
  info2.tags.insert("baz");
  Place p2{info2};

  const std::unordered_set<std::string> known_tags{"foo", "bar", "baz"};

  const auto scrapper = MakeFilterScrapper({&p1, &p2});

  const std::vector<RequestFilter> filters = {
      {
          FilterType::kQuickfilter,  // type
          "baz",                     // slug
      },
  };

  const std::vector<RequestFilterGroup> filter_group = {{
      RequestFilterGroupType::kAnd,
      filters,
  }};
  const auto matcher = MakeFilterMatcher(filter_group, known_tags);

  ASSERT_FALSE(matcher.Match(p1));  // doesn't have baz tag
  ASSERT_TRUE(matcher.Match(p2));   // does have baz tag
}

TEST(ScrapperGetMatcher, match_or_group) {
  PlaceInfo info1;
  info1.tags.insert("foo");
  info1.tags.insert("bar");
  Place p1{info1};

  PlaceInfo info2;
  info2.tags.insert("baz");
  info2.tags.insert("quux");
  Place p2{info2};

  PlaceInfo info3;
  info3.tags.insert("baz");
  Place p3{info3};

  const std::unordered_set<std::string> known_tags{"foo", "bar", "baz", "quux"};

  const auto scrapper = MakeFilterScrapper({&p1, &p2, &p3});

  const std::vector<RequestFilter> match_foo_or_quux = {
      {
          FilterType::kQuickfilter,  // type
          "foo",                     // slug
      },
      {
          FilterType::kQuickfilter,  // type
          "quux",                    // slug
      },
  };

  const std::vector<RequestFilterGroup> filter_group = {{
      RequestFilterGroupType::kOr,
      match_foo_or_quux,
  }};
  const auto matcher = MakeFilterMatcher(filter_group, known_tags);

  ASSERT_TRUE(matcher.Match(p1));   // has foo
  ASSERT_TRUE(matcher.Match(p2));   // has quux
  ASSERT_FALSE(matcher.Match(p3));  // has no foo nor quux
}

TEST(ScrapperGetMatcher, match_multiple_group) {
  PlaceInfo info1;
  info1.tags.insert("foo");
  info1.tags.insert("bar");
  info1.tags.insert("baz");
  Place p1{info1};

  PlaceInfo info2;
  info2.tags.insert("baz");
  Place p2{info2};

  PlaceInfo info3;
  info3.tags.insert("quux");
  Place p3{info3};

  const std::unordered_set<std::string> known_tags{"foo", "bar", "baz", "quux"};

  const auto scrapper = MakeFilterScrapper({&p1, &p2, &p3});

  const std::vector<RequestFilter> match_baz = {
      {
          FilterType::kQuickfilter,  // type
          "baz",                     // slug
      },
  };

  const std::vector<RequestFilter> match_foo_or_quux = {
      {
          FilterType::kQuickfilter,  // type
          "foo",                     // slug
      },
      {
          FilterType::kQuickfilter,  // type
          "quux",                    // slug
      },
  };

  // match baz and (foo or quux)
  const std::vector<RequestFilterGroup> filter_group = {
      {
          RequestFilterGroupType::kAnd,
          match_baz,
      },
      {
          RequestFilterGroupType::kOr,
          match_foo_or_quux,
      }};
  const auto matcher = MakeFilterMatcher(filter_group, known_tags);

  ASSERT_TRUE(matcher.Match(p1));   // has baz and foo
  ASSERT_FALSE(matcher.Match(p2));  // has baz has no foo nor quux
  ASSERT_FALSE(matcher.Match(p3));  // has no baz
}

}  // namespace handlers::internal_v1_catalog_for_layout::post::filters
