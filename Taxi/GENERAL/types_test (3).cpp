#include "types.hpp"

#include <gtest/gtest.h>

#include <driver-id/test/print_to.hpp>
#include <geobus/test/print_to.hpp>

using geobus::lowlevel::PackDriverId;
using geobus::lowlevel::UnpackDriverId;

using namespace ::driver_id::literals;

// DriverIdPack
struct PackDriverIdData {
  ::driver_id::DriverDbid dbid;
  ::driver_id::DriverUuid uuid;
  std::string packed;
  bool expect_error;
  const auto& GetDbid() const { return dbid; }
  const auto& GetUuid() const { return uuid; }
};

class DriverIdFull : public ::testing::TestWithParam<PackDriverIdData> {};

TEST_P(DriverIdFull, One) {
  const auto& param = GetParam();
  std::string packed;
  geobus::types::DriverId driver_id;

  if (!param.expect_error) {
    EXPECT_NO_THROW(packed = PackDriverId(geobus::types::DriverId(
                        param.GetDbid(), param.GetUuid())));
    EXPECT_EQ(param.packed, packed);
    EXPECT_NO_THROW(driver_id = UnpackDriverId(std::string(packed)));
    EXPECT_EQ(param.GetDbid(), driver_id.GetDbid());
    EXPECT_EQ(param.GetUuid(), driver_id.GetUuid());
  } else {
    EXPECT_ANY_THROW(PackDriverId(
        geobus::types::DriverId(param.GetDbid(), param.GetUuid())));
  }
}

const std::vector<PackDriverIdData> kPackDriverIdFullDataTestCases({
    // empty GetUuid()
    {"ab"_dbid, ""_uuid, "", true},

    // empty GetDbid()
    {""_dbid, "ab"_uuid, "", true},

    // raw dbid_uuid (non-hex GetUuid())
    {"ab"_dbid, "abc"_uuid,
     ""
     "ab_abc",
     false},

    // raw dbid_uuid (non-hex GetDbid())
    {"abc"_dbid, "ab"_uuid,
     ""
     "abc_ab",
     false},

    // raw dbid_uuid (GetDbid() too long)
    {"1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
     "1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
     "1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
     "1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
     "1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
     "1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
     "1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
     "1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"_dbid,
     "ab"_uuid,
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
    {"ab"_dbid, "ab"_uuid,
     "\x01\x01"
     "\xab\xab",
     false},
});

INSTANTIATE_TEST_SUITE_P(Geobus, DriverIdFull,
                         ::testing::ValuesIn(kPackDriverIdFullDataTestCases));

// DriverIdUnpack
struct UnpackDriverIdData {
  std::string packed;
  bool expect_error;
};

class DriverIdUnpack : public ::testing::TestWithParam<UnpackDriverIdData> {};

TEST_P(DriverIdUnpack, One) {
  const auto& param = GetParam();
  if (param.expect_error) {
    EXPECT_FALSE(UnpackDriverId(std::string(param.packed)).IsValid());
  } else {
    geobus::types::DriverId data;
    EXPECT_NO_THROW(data = UnpackDriverId(std::string(param.packed)));
    EXPECT_TRUE(data.IsValid());
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

INSTANTIATE_TEST_SUITE_P(Geobus, DriverIdUnpack,
                         ::testing::ValuesIn(kPackDriverIdUnpackDataTestCases));
