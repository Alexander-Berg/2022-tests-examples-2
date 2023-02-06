#include <chrono>
#include <string>

#include <gtest/gtest.h>
#include <geobase/exceptions.hpp>
#include <geobase/utils/city.hpp>
#include <geobase/utils/country.hpp>
#include <geobase/utils/ip.hpp>
#include <geobase/utils/timezone.hpp>
#include <userver/utils/assert.hpp>
#include <userver/utils/datetime.hpp>

#ifdef ARCADIA_ROOT
#include <library/cpp/testing/common/env.h>
#endif

namespace {

const std::string kMoscowIp = "81.195.17.222";
const std::string kInvalidIp = "invalid ip";

constexpr double kMoscowLat = 55.733842;
constexpr double kMoscowLon = 37.588144;
constexpr double kInvalidLat = 91.0;
constexpr double kInvalidLon = -181.0;

constexpr geobase::RegionId kMoscowId = 213;
constexpr geobase::RegionId kRussiaId = 225;

const std::string kMoscowIsoName = "ru-mow";
const std::string kRussiaIsoName = "ru";

const std::string kMoscowName = "Москва";

const std::string kMoscowTimezone = "Europe/Moscow";

class GeobaseUtils : public ::testing::Test {
 public:
  static void SetUpTestSuite() {
    std::string filename;
    geobase::InitTraits traits;
#if defined(ARCADIA_ROOT)
    filename = JoinFsPaths(GetWorkPath(), "geobase_data/geodata6.bin");
    traits.TzDataPath(
        JoinFsPaths(GetWorkPath(), "geobase_data/tzdata/zones_bin"));
#elif defined(__APPLE__)
    filename = "/usr/local/etc/yandex/geobase/geobase6.conf";
#else
    filename = "/etc/yandex/geobase/geobase6.conf";
#endif
    lookup_ptr_ = std::make_shared<geobase::Lookup>(filename, traits);
  }

  static void TearDownTestSuite() { lookup_ptr_.reset(); }

 protected:
  const geobase::Lookup& GetLookup() const {
    UINVARIANT(lookup_ptr_, "Lookup was not initialized");
    return *lookup_ptr_;
  }

 private:
  static geobase::LookupPtr lookup_ptr_;
};

geobase::LookupPtr GeobaseUtils::lookup_ptr_{};

}  // namespace

TEST_F(GeobaseUtils, ByIpAddress) {
  EXPECT_EQ(geobase::GetCityIdByIpAddress(kMoscowIp, GetLookup()), kMoscowId);
  EXPECT_EQ(geobase::GetCityIsoNameByIpAddress(kMoscowIp, GetLookup()),
            kMoscowIsoName);
  EXPECT_EQ(geobase::GetCountryIdByIpAddress(kMoscowIp, GetLookup()),
            kRussiaId);
  EXPECT_EQ(geobase::GetCountryByIpAddress(kMoscowIp, GetLookup()),
            kRussiaIsoName);

  EXPECT_THROW(geobase::GetCityIdByIpAddress(kInvalidIp, GetLookup()),
               geobase::LookupError);
  EXPECT_THROW(geobase::GetCityIsoNameByIpAddress(kInvalidIp, GetLookup()),
               geobase::LookupError);
  EXPECT_THROW(geobase::GetCountryIdByIpAddress(kInvalidIp, GetLookup()),
               geobase::LookupError);
  EXPECT_THROW(geobase::GetCountryByIpAddress(kInvalidIp, GetLookup()),
               geobase::LookupError);
}

TEST_F(GeobaseUtils, ByPosition) {
  EXPECT_EQ(geobase::GetCityIdByPosition(kMoscowLon, kMoscowLat, GetLookup()),
            kMoscowId);
  EXPECT_EQ(
      geobase::GetCityIsoNameByPosition(kMoscowLon, kMoscowLat, GetLookup()),
      kMoscowIsoName);
  EXPECT_EQ(
      geobase::GetCountryIdByPosition(kMoscowLon, kMoscowLat, GetLookup()),
      kRussiaId);
  EXPECT_EQ(geobase::GetCountryByPosition(kMoscowLon, kMoscowLat, GetLookup()),
            kRussiaIsoName);
  EXPECT_EQ(geobase::GetTimezoneByPosition(kMoscowLon, kMoscowLat, GetLookup()),
            kMoscowTimezone);

  EXPECT_THROW(
      geobase::GetCityIdByPosition(kInvalidLon, kInvalidLat, GetLookup()),
      geobase::LookupError);
  EXPECT_THROW(
      geobase::GetCityIsoNameByPosition(kInvalidLon, kInvalidLat, GetLookup()),
      geobase::LookupError);
  EXPECT_THROW(
      geobase::GetCountryIdByPosition(kInvalidLon, kInvalidLat, GetLookup()),
      geobase::LookupError);
  EXPECT_THROW(
      geobase::GetCountryByPosition(kInvalidLon, kInvalidLat, GetLookup()),
      geobase::LookupError);
}

TEST_F(GeobaseUtils, ByRegionId) {
  EXPECT_EQ(geobase::GetCityNameByRegionId(kMoscowId, GetLookup()),
            kMoscowName);
  EXPECT_EQ(geobase::GetTimezoneByRegionId(kMoscowId, GetLookup()),
            kMoscowTimezone);

  EXPECT_THROW(geobase::GetCityNameByRegionId(0, GetLookup()),
               geobase::LookupError);
}

TEST_F(GeobaseUtils, IpTraits) {
  EXPECT_NO_THROW(geobase::GetIpBasicTraits(kMoscowIp, GetLookup()));
  EXPECT_FALSE(geobase::IsHosting(kMoscowIp, GetLookup()));

  EXPECT_THROW(geobase::GetIpBasicTraits(kInvalidIp, GetLookup()),
               geobase::LookupError);
  EXPECT_THROW(geobase::IsHosting(kInvalidIp, GetLookup()),
               geobase::LookupError);
}

TEST_F(GeobaseUtils, GeobaseTzNames) {
  EXPECT_EQ("UTC", geobase::AdjustGeobaseTzname("UTC+0"));
  EXPECT_EQ("Fixed/UTC+11:00:00", geobase::AdjustGeobaseTzname("UTC+11"));

  EXPECT_NO_THROW(utils::datetime::Timestring(
      std::chrono::system_clock::time_point{},
      geobase::GetTimezoneByPosition(0, 0, GetLookup()), ""));
  EXPECT_NO_THROW(utils::datetime::Timestring(
      std::chrono::system_clock::time_point{},
      geobase::GetTimezoneByPosition(170, -26, GetLookup()), ""));
}
