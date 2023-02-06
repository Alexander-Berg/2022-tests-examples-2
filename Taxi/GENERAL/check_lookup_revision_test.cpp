#include <gtest/gtest.h>

#include <lookup-dispatch/models/check_lookup_revision.hpp>

TEST(CheckLookupRevision, One) {
  using namespace lookup_dispatch::models;

  EXPECT_EQ(
      LookupStatus::kPresent,
      CheckLookupRevision(LookupRevision{1, 8, 5}, LookupRevision{1, 6, 3}));
  EXPECT_EQ(
      LookupStatus::kOutdated,
      CheckLookupRevision(LookupRevision{2, 1, 1}, LookupRevision{1, 1, 1}));
  EXPECT_EQ(
      LookupStatus::kOutdated,
      CheckLookupRevision(LookupRevision{1, 8, 5}, LookupRevision{1, 4, 2}));
}
