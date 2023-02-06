#include <gtest/gtest.h>

#include <userver/cache/statistics_mock.hpp>

#include <filters/infrastructure/fetch_dbpark/fetch_dbpark_test.hpp>
#include "fetch_park_activation.hpp"

const candidates::filters::FilterInfo kEmptyInfo;

TEST(FetchParkActivation, NoClid) {
  candidates::GeoMember member{};
  candidates::filters::Context context;
  const auto parks = std::make_shared<parks_activation::models::CachedParks>();
  candidates::filters::infrastructure::FetchParkActivation filter(kEmptyInfo,
                                                                  parks);
  EXPECT_ANY_THROW(filter.Process(member, context));
}

TEST(FetchParkActivation, Sample) {
  candidates::GeoMember member{};
  candidates::filters::Context context;
  candidates::filters::infrastructure::test::SetClid(context, "clid");

  const auto parks = std::make_shared<parks_activation::models::CachedParks>();
  candidates::filters::infrastructure::FetchParkActivation filter(kEmptyInfo,
                                                                  parks);
  EXPECT_EQ(filter.Process(member, context),
            candidates::filters::Result::kDisallow);

  parks_activation::models::Park park;
  park.park_id = "clid";

  cache::UpdateStatisticsScopeMock stats(cache::UpdateType::kFull);
  parks->UpsertItems({park}, stats.GetScope(), std::chrono::seconds(1));
  EXPECT_EQ(filter.Process(member, context),
            candidates::filters::Result::kAllow);
  EXPECT_NO_THROW(
      candidates::filters::infrastructure::FetchParkActivation::Get(context));
}
