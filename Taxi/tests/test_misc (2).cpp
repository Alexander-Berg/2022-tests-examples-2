#include <gtest/gtest.h>

#include <boost/uuid/uuid_io.hpp>

#include "models/misc.hpp"

#include <set>

namespace routehistory::test::models {
using namespace ::routehistory::models;

TEST(PgUuid, MakePgUuid) {
  EXPECT_EQ(boost::uuids::to_string(PgUuid("6c35cd7d05453ed7b58f6c45572b0921")),
            "6c35cd7d-0545-3ed7-b58f-6c45572b0921");
  EXPECT_EQ(boost::uuids::to_string(PgUuid("5e663654e344a249db330a66")),
            "00000000-5e66-3654-e344-a249db330a66");
}

TEST(PgUuid, MakePgUuidBad) {
  EXPECT_ANY_THROW(PgUuid("a000000000000000000000000000001"));
  EXPECT_ANY_THROW(PgUuid("a00000000000000000000000000000123"));
  EXPECT_ANY_THROW(PgUuid("b0000000000000000000001"));
  EXPECT_ANY_THROW(PgUuid("b000000000000000000000123"));
  EXPECT_ANY_THROW(PgUuid("string with nonhex chars"));
}

TEST(PgUuid, ToString) {
  EXPECT_EQ(PgUuid("6c35cd7d05453ed7b58f6c45572b0921").ToString(),
            "6c35cd7d05453ed7b58f6c45572b0921");
  EXPECT_EQ(PgUuid("0000cd7d05453ed7b58f6c45572b0921").ToString(),
            "0000cd7d05453ed7b58f6c45572b0921");
  EXPECT_EQ(PgUuid("0000000005453ed7b58f6c45572b0921").ToString(),
            "05453ed7b58f6c45572b0921");
  EXPECT_EQ(PgUuid("0000000000003ed7b58f6c45572b0921").ToString(),
            "00003ed7b58f6c45572b0921");
}

using PgUuidPair = std::pair<PgUuid, PgUuid>;
struct CompareTest : testing::TestWithParam<PgUuidPair> {};

TEST_P(CompareTest, Compare) {
  const auto [uuid1, uuid2] = GetParam();
  EXPECT_LT(uuid1, uuid2);
  EXPECT_LE(uuid1, uuid2);
  EXPECT_NE(uuid1, uuid2);
  EXPECT_GT(uuid2, uuid1);
  EXPECT_GE(uuid2, uuid1);
  EXPECT_EQ(uuid1, uuid1);
  EXPECT_EQ(uuid2, uuid2);
  std::set<PgUuid> uuids;
  uuids.insert(uuid1);
  uuids.insert(uuid2);
  EXPECT_EQ(uuids.size(), 2);
}

const PgUuidPair kPairsToCompare[] = {
    {PgUuid("000000000000000000000001"), PgUuid("000000000000000000000002")},
    {PgUuid("100000000000000000000001"), PgUuid("100000000000000000000002")},
    {PgUuid("200000000000000000000001"), PgUuid("200000000000000000000002")},
    {PgUuid("100000000000000000000000"), PgUuid("200000000000000000000000")},
    {PgUuid("000000000000000000000000"), PgUuid("000000000000000000000001")},
    {PgUuid("000000000000000000000000"), PgUuid("100000000000000000000000")},
    {PgUuid("00003ed7b58f6c45572b0921"), PgUuid("00004ed7b58f6c45572b0921")},
    {PgUuid("00003ed7b58f6c45572b0921"), PgUuid("00003ed7b58f6c45572b0922")},
};

INSTANTIATE_TEST_SUITE_P(PgUuid, CompareTest,
                         testing::ValuesIn(kPairsToCompare));

}  // namespace routehistory::test::models
