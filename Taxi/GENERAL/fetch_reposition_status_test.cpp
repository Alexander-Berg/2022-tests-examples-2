#include <gtest/gtest.h>

#include "fetch_reposition_status.hpp"

using candidates::GeoMember;
using candidates::filters::Context;
using candidates::filters::Result;
using candidates::filters::efficiency::FetchRepositionStatus;
const candidates::filters::FilterInfo kEmptyInfo;

TEST(FetchRepositionStatus, NoStatus) {
  auto statuses = std::make_shared<clients::reposition::Index>();
  FetchRepositionStatus filter(kEmptyInfo, statuses);
  Context context;
  GeoMember member;
  EXPECT_EQ(filter.Process(member, context), Result::kAllow);
  EXPECT_FALSE(FetchRepositionStatus::Get(context, {}).override_busy);
  EXPECT_FALSE(FetchRepositionStatus::Get(context, {}).exclude);
  EXPECT_FALSE(
      FetchRepositionStatus::Get(context, {}).reposition_check_required);
}

class FetchRepositionStatusParametric
    : public ::testing::TestWithParam<clients::reposition::IndexEntry> {};

TEST_P(FetchRepositionStatusParametric, Test) {
  auto statuses = std::make_shared<clients::reposition::Index>();
  auto status = GetParam();
  statuses->data["dbid_uuid"] = status;
  FetchRepositionStatus filter(kEmptyInfo, statuses);
  Context context;
  GeoMember member;
  member.id = "dbid_uuid";
  EXPECT_EQ(filter.Process(member, context), Result::kAllow);
  EXPECT_EQ(FetchRepositionStatus::Get(context, {}).override_busy,
            status.override_busy);
  EXPECT_EQ(FetchRepositionStatus::Get(context, {}).exclude, status.exclude);
  EXPECT_EQ(FetchRepositionStatus::Get(context, {}).reposition_check_required,
            status.reposition_check_required);
  if (status.reposition_check_required) {
    EXPECT_EQ(context.meta[FetchRepositionStatus::kCheckRequired],
              formats::json::ValueBuilder(true).ExtractValue());
  }
}

INSTANTIATE_TEST_SUITE_P(
    FetchRepositionStatus, FetchRepositionStatusParametric,
    ::testing::Values(clients::reposition::IndexEntry{false, false, false},
                      clients::reposition::IndexEntry{false, false, true},
                      clients::reposition::IndexEntry{false, true, false},
                      clients::reposition::IndexEntry{false, true, true},
                      clients::reposition::IndexEntry{true, false, false},
                      clients::reposition::IndexEntry{true, false, true},
                      clients::reposition::IndexEntry{true, true, false},
                      clients::reposition::IndexEntry{true, true, true}));
