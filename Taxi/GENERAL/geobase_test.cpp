#include "utils/helpers/geobase.hpp"
#include "utils/geometry.hpp"

#include <gtest/gtest.h>
#include <geobase6/lookup.hpp>

// Standard path to geobase config.
constexpr const char* kGeoBaseConfigPath = "/etc/yandex/geobase/geobase6.conf";

class Geobase : public testing::Test {
 public:
  Geobase() : lookup(new geobase6::Lookup(kGeoBaseConfigPath)) {}
  static const NGeobase::NImpl::Id kRussiaGeoId = 225;
  static const NGeobase::NImpl::Id kUkrainGeoId = 187;

 protected:
  std::unique_ptr<geobase6::Lookup> lookup;
};

const NGeobase::NImpl::Id Geobase::kRussiaGeoId;
const NGeobase::NImpl::Id Geobase::kUkrainGeoId;

TEST_F(Geobase, GetCountryName) {
  namespace uh = utils::helpers;
  typedef utils::geometry::Point UGPoint;

  ASSERT_TRUE(lookup);
  // Moscow
  ASSERT_EQ(uh::GetCountryName(UGPoint{37.6, 55.7}, *lookup), "ru");
  // Crimea
  ASSERT_EQ(uh::GetCountryName(UGPoint{33.9, 45.5}, *lookup), "ru");
  ASSERT_EQ(uh::GetCountryName(UGPoint{33.9, 45.5}, *lookup, false), "ua");
  // No region - ocean
  ASSERT_EQ(uh::GetCountryName(UGPoint{-37.0, 55.0}, *lookup), "");
  // Côte d'Ivoire
  ASSERT_EQ(uh::GetCountryName(UGPoint{-4.07, 5.44}, *lookup), "ci");

  std::string remote_ip = "2002:510:4266:0:99bc:cef2:ceff:d4f2";
  ASSERT_NO_THROW(lookup->GetRegionByIp(remote_ip));
}

TEST_F(Geobase, CheckUkranianIP) {
  const std::string ukrainianIP = "5.105.0.1";
  const std::string russianIP = "2a02:6b8::2:242";
  ASSERT_EQ(lookup->GetCountryId(lookup->GetRegionByIp(ukrainianIP).GetId()),
            kUkrainGeoId);
  ASSERT_EQ(lookup->GetCountryId(lookup->GetRegionByIp(russianIP).GetId()),
            kRussiaGeoId);
}
