#include "types.hpp"

#include <gtest/gtest.h>

using geobus::internal::PackDriverId;
using geobus::internal::UnpackDriverId;

// DriverIdPack
struct PackDriverIdData {
  std::string dbid;
  std::string clid;
  std::string uuid;
  std::string packed;
  bool expect_error;
};

class DriverIdFull : public ::testing::TestWithParam<PackDriverIdData> {};

TEST_P(DriverIdFull, One) {
  const auto& param = GetParam();
  std::string packed;
  models::DriverId driver_id;

  if (!param.expect_error) {
    EXPECT_NO_THROW(packed = PackDriverId(
                        models::DriverId(param.dbid, param.clid, param.uuid)));
    EXPECT_EQ(param.packed, packed);
    EXPECT_NO_THROW(driver_id = UnpackDriverId(packed));
    if (!driver_id.dbid.empty())
      EXPECT_EQ(param.dbid, driver_id.dbid);
    else
      EXPECT_EQ(param.clid, driver_id.clid);
    EXPECT_EQ(param.uuid, driver_id.uuid);
  } else {
    EXPECT_ANY_THROW(
        PackDriverId(models::DriverId(param.dbid, param.clid, param.uuid)));
  }
}

const std::vector<PackDriverIdData> kPackDriverIdFullDataTestCases({
    // empty uuid
    {"ab", "ab", "", "", true},

    // empty dbid
    {"", "", "ab", "", true},

    // raw dbid_uuid (non-hex uuid)
    {"ab", "", "abc",
     ""
     "ab_abc",
     false},

    // raw dbid_uuid (non-hex dbid)
    {"abc", "", "ab",
     ""
     "abc_ab",
     false},

    // raw dbid_uuid (dbid too long)
    {"1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
     "1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
     "1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
     "1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
     "1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
     "1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
     "1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
     "1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
     "", "ab",
     ""
     "1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
     "1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
     "1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
     "1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
     "1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
     "1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
     "1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
     "1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
     "_ab",
     false},

    // packed dbid_uuid
    {"ab", "", "ab",
     "\x01\x01"
     "\xab\xab",
     false},
});

INSTANTIATE_TEST_CASE_P(Geobus, DriverIdFull,
                        ::testing::ValuesIn(kPackDriverIdFullDataTestCases), );

// DriverIdUnpack
struct UnpackDriverIdData {
  std::string packed;
  bool expect_error;
};

class DriverIdUnpack : public ::testing::TestWithParam<UnpackDriverIdData> {};

TEST_P(DriverIdUnpack, One) {
  const auto& param = GetParam();
  if (param.expect_error) {
    EXPECT_ANY_THROW(UnpackDriverId(param.packed));
  } else {
    EXPECT_NO_THROW(UnpackDriverId(param.packed));
  }
}

const std::vector<UnpackDriverIdData> kPackDriverIdUnpackDataTestCases({
    // empty value
    {"", true},

    // raw dbid_uuid
    {"", true},
    {"abab", true},
    {"ab_ab", false},

    // packed dbid_uuid
    {"\x01", true},
    {"\x01\x02", true},
    {"\x01\x02\xab", true},
    {"\x01\x02\xab\xab", true},
    {"\x01\x02\xab\xab\xab", false},
});

INSTANTIATE_TEST_CASE_P(
    Geobus, DriverIdUnpack,
    ::testing::ValuesIn(kPackDriverIdUnpackDataTestCases), );
