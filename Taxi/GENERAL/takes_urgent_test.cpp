#include <gtest/gtest.h>

#include <filters/infrastructure/fetch_park/fetch_park.hpp>
#include "takes_urgent.hpp"

namespace cf = candidates::filters;

const cf::FilterInfo kEmptyInfo;

TEST(TakesUrgentTest, NoPark) {
  candidates::GeoMember member;
  cf::Context context;
  cf::partners::TakesUrgent filter(kEmptyInfo);
  EXPECT_ANY_THROW(filter.Process(member, context));
}

TEST(TakesUrgentTest, Sample) {
  candidates::GeoMember member;
  cf::Context context;
  cf::partners::TakesUrgent filter(kEmptyInfo);
  auto park = std::make_shared<models::Park>();

  park->takes_urgent = true;
  cf::infrastructure::FetchPark::Set(context, park);
  EXPECT_EQ(filter.Process(member, context), cf::Result::kAllow);

  park->takes_urgent = false;
  cf::infrastructure::FetchPark::Set(context, park);
  EXPECT_EQ(filter.Process(member, context), cf::Result::kDisallow);
}
