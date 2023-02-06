#include <gtest/gtest.h>

#include <filters/infrastructure/fetch_city/fetch_city.hpp>
#include "country.hpp"

namespace cf = candidates::filters;

const cf::FilterInfo kEmptyInfo;

TEST(CountryTest, Sample) {
  candidates::GeoMember member;
  cf::Context context;
  cf::infrastructure::Country filter(kEmptyInfo, "country");

  // City was not found
  EXPECT_EQ(filter.Process(member, context), cf::Result::kAllow);

  auto city = std::make_shared<models::City>();

  // City country is match zone country
  city->country = "country";
  cf::infrastructure::FetchCity::Set(context, city);

  EXPECT_EQ(filter.Process(member, context), cf::Result::kAllow);

  // City country does not match zone country
  city->country = "wrong_country";
  cf::infrastructure::FetchCity::Set(context, city);
  EXPECT_EQ(filter.Process(member, context), cf::Result::kDisallow);
}
