#include <gtest/gtest.h>

#include <filters/infrastructure/fetch_dbpark/fetch_dbpark_test.hpp>
#include "fetch_park.hpp"

const candidates::filters::FilterInfo kEmptyInfo;

TEST(FetchPark, NoClid) {
  candidates::GeoMember member;
  candidates::filters::Context context;
  const auto parks = std::make_shared<models::Parks>();
  candidates::filters::infrastructure::FetchPark filter(kEmptyInfo, parks);
  EXPECT_ANY_THROW(filter.Process(member, context));
}

TEST(FetchPark, Sample) {
  candidates::GeoMember member;
  candidates::filters::Context context;
  candidates::filters::infrastructure::test::SetClid(context, "clid");

  auto parks = std::make_shared<models::Parks>();
  candidates::filters::infrastructure::FetchPark filter(kEmptyInfo, parks);
  EXPECT_EQ(filter.Process(member, context),
            candidates::filters::Result::kDisallow);

  parks->emplace("clid", std::make_shared<models::Park>());
  EXPECT_EQ(filter.Process(member, context),
            candidates::filters::Result::kAllow);
  EXPECT_NO_THROW(candidates::filters::infrastructure::FetchPark::Get(context));
}
