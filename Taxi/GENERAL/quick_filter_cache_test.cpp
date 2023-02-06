#include "quick_filter_cache.hpp"

#include <gtest/gtest.h>

#include <userver/dump/test_helpers.hpp>

#include <models/quick_filter.hpp>

namespace eats_places::models {

constexpr bool operator==(const QuickFilter& lhs, const QuickFilter& rhs) {
  return lhs.id == rhs.id && lhs.slug == rhs.slug && lhs.name == rhs.name &&
         lhs.priority == rhs.priority && lhs.category_id == rhs.category_id;
}

}  // namespace eats_places::models

namespace eats_catalog::components {

TEST(QuickFilterCache, ReadWrite) {
  QuickFilters quick_filters{
      {
          models::QuickFilterId(1),
          {
              models::QuickFilterId(1),      // id
              models::QuickFilterSlug("1"),  // slug
              "First",                       // name
              10,                            // priority
              std::nullopt,                  // category_id
              std::nullopt,                  // genitive
              std::nullopt,                  // photo_uri
              std::nullopt,                  // picture_uri
              std::nullopt,                  // promo_photo_uri
              true,                          // is_enabled
              true,                          // is_wizard_enabled
          },
      },
      {
          models::QuickFilterId(2),
          {
              models::QuickFilterId(2),      // id
              models::QuickFilterSlug("2"),  // slug
              "Second",                      // name
              12,                            // priority
              1324,                          // category_id
              std::nullopt,                  // genitive
              std::nullopt,                  // photo_uri
              std::nullopt,                  // picture_uri
              std::nullopt,                  // promo_photo_uri
              true,                          // is_enabled
              true,                          // is_wizard_enabled
          },
      },
      {
          models::QuickFilterId(3),
          {
              models::QuickFilterId(3),      // id
              models::QuickFilterSlug("3"),  // slug
              "Third",                       // name
              1023,                          // priority
              12,                            // category_id
              std::nullopt,                  // genitive
              std::nullopt,                  // photo_uri
              std::nullopt,                  // picture_uri
              std::nullopt,                  // promo_photo_uri
              true,                          // is_enabled
              true,                          // is_wizard_enabled
          },
      },
  };

  const auto binary = dump::ToBinary(quick_filters);
  const auto actual = dump::FromBinary<QuickFilters>(binary);

  ASSERT_EQ(quick_filters.size(), actual.size())
      << "unexpected size of quick filter map from binary";

  for (const auto& [id, quick_filter] : quick_filters) {
    const auto it = actual.find(id);
    ASSERT_NE(it, actual.end())
        << "missing quick filter with id " << id.GetUnderlying();
    ASSERT_EQ(quick_filter, it->second) << "unexpected quick filter value";
  }
}

}  // namespace eats_catalog::components
