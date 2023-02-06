#include <gtest/gtest.h>

#include <filters/infrastructure/fetch_park/fetch_park.hpp>
#include "fetch_city.hpp"

namespace cf = candidates::filters;

const cf::FilterInfo kEmptyInfo;

TEST(FetchCityTest, NoPark) {
  candidates::GeoMember member;
  cf::Context context;
  auto cities = std::make_shared<models::Cities>();
  cf::infrastructure::FetchCity filter(kEmptyInfo, cities);
  EXPECT_ANY_THROW(filter.Process(member, context));
}

TEST(FetchCityTest, Sample) {
  candidates::GeoMember member;
  cf::Context context;

  auto cities = std::make_shared<models::Cities>();
  cities->emplace("city", std::make_shared<models::City>());

  cf::infrastructure::FetchCity filter(kEmptyInfo, cities);

  auto park = std::make_shared<models::Park>();

  // Park with empty city name
  park->city = std::string();
  cf::infrastructure::FetchPark::Set(context, park);
  EXPECT_EQ(filter.Process(member, context), cf::Result::kAllow);

  // Park city does not found in cities
  park->city = "wrong_city";
  cf::infrastructure::FetchPark::Set(context, park);
  EXPECT_EQ(filter.Process(member, context), cf::Result::kDisallow);

  // Park city found in cities
  park->city = "city";
  cf::infrastructure::FetchPark::Set(context, park);
  EXPECT_EQ(filter.Process(member, context), cf::Result::kAllow);
}
