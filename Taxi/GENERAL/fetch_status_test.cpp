#include <gtest/gtest.h>

#include "fetch_status.hpp"

using candidates::GeoMember;
using candidates::filters::Context;
using candidates::filters::Result;
using candidates::filters::infrastructure::FetchStatus;

const candidates::filters::FilterInfo kEmptyInfo;

TEST(FetchStatus, NoStatus) {
  auto statuses = std::make_shared<models::Statuses>();
  FetchStatus filter(kEmptyInfo, statuses);
  Context context;
  GeoMember member{{}, "id1"};
  EXPECT_EQ(filter.Process(member, context), Result::kDisallow);
  EXPECT_ANY_THROW(FetchStatus::Get(context));
}

TEST(FetchStatus, Sample) {
  auto statuses = std::make_shared<models::Statuses>();
  (*statuses)["id1"] = models::Status{};
  FetchStatus filter(kEmptyInfo, statuses);
  Context context;
  GeoMember member{{}, "id1"};
  EXPECT_EQ(filter.Process(member, context), Result::kAllow);
  EXPECT_NO_THROW(FetchStatus::Get(context));
}
