#include <gtest/gtest.h>

#include <filters/efficiency/fetch_reposition_status/fetch_reposition_status.hpp>
#include "inactive_reposition.hpp"

using candidates::GeoMember;
using candidates::filters::Context;
using candidates::filters::Result;
using candidates::filters::efficiency::FetchRepositionStatus;
using candidates::filters::efficiency::InactiveReposition;

const candidates::filters::FilterInfo kEmptyInfo;

TEST(InactiveReposition, NoStatus) {
  InactiveReposition filter(kEmptyInfo);
  Context context;
  GeoMember member;
  EXPECT_EQ(filter.Process(member, context), Result::kIgnore);
}

class InactiveRepositionParametric
    : public ::testing::TestWithParam<clients::reposition::IndexEntry> {};

TEST_P(InactiveRepositionParametric, Test) {
  InactiveReposition filter(kEmptyInfo);
  auto status = GetParam();
  Context context;
  FetchRepositionStatus::Set(context, status);
  GeoMember member;
  EXPECT_EQ(filter.Process(member, context),
            status.exclude ? Result::kDisallow : Result::kAllow);
}

INSTANTIATE_TEST_SUITE_P(
    InactiveReposition, InactiveRepositionParametric,
    ::testing::Values(clients::reposition::IndexEntry{false, false, false},
                      clients::reposition::IndexEntry{false, false, true},
                      clients::reposition::IndexEntry{false, true, false},
                      clients::reposition::IndexEntry{false, true, true},
                      clients::reposition::IndexEntry{true, false, false},
                      clients::reposition::IndexEntry{true, false, true},
                      clients::reposition::IndexEntry{true, true, false},
                      clients::reposition::IndexEntry{true, true, true}));
