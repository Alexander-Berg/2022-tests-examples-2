#include <grocery-shared/countries.hpp>

#include <userver/utest/utest.hpp>

namespace grocery_shared::geo {

namespace {
constexpr auto kFranceGeobaseId = 124;
constexpr auto kFranceCountryName = "France";
constexpr auto kFranceIso2 = "FR";
constexpr auto kFranceIso3 = "FRA";
constexpr auto kEuro = "EUR";

void CheckIsFrance(const CountryInfo& info) {
  ASSERT_EQ(info.country, Country::kFrance);
  ASSERT_EQ(info.geobase_country_id, kFranceGeobaseId);
  ASSERT_EQ(info.geo3_country_name, ToCountryIso3(Country::kFrance));
  ASSERT_EQ(info.geobase_en_country_name_full, ToString(Country::kFrance));
  ASSERT_EQ(info.currency, kEuro);
}
}  // namespace

TEST(Countries_France, ToString) {
  ASSERT_EQ(ToString(Country::kFrance), kFranceCountryName);
}

TEST(Countries_France, ToCountryIso2) {
  ASSERT_EQ(ToCountryIso2(Country::kFrance), kFranceIso2);
}

TEST(Countries_France, ToCountryIso3) {
  ASSERT_EQ(ToCountryIso3(Country::kFrance), kFranceIso3);
}

TEST(Countries_France, FromCountryIso2) {
  ASSERT_EQ(FromCountryIso2(kFranceIso2), Country::kFrance);
}

TEST(Countries_France, FromCountryIso3) {
  ASSERT_EQ(FromCountryIso3(kFranceIso3), Country::kFrance);
}

TEST(Countries_France, GetCountryInfoByName) {
  const auto country_info = GetCountryInfoByName(kFranceCountryName);
  ASSERT_TRUE(country_info);
  CheckIsFrance(*country_info);
}

TEST(Countries_France, GetCountryInfoByGeo3) {
  const auto country_info = GetCountryInfoByGeo3(kFranceIso3);
  ASSERT_TRUE(country_info);
  CheckIsFrance(*country_info);
}

TEST(Countries_France, GetCountryInfoByGeoId) {
  const auto country_info = GetCountryInfoByGeoId(kFranceGeobaseId);
  ASSERT_TRUE(country_info);
  CheckIsFrance(*country_info);
}

TEST(Countries_France, GetCountryInfo) {
  const auto& country_info = GetCountryInfo(Country::kFrance);
  CheckIsFrance(country_info);
}

TEST(Countries_France, GetIso3CountryName_by_id) {
  const auto& name = GetIso3CountryName(kFranceGeobaseId);
  ASSERT_EQ(name, ToCountryIso3(Country::kFrance));
}

TEST(Countries_France, GetIso3CountryName_by_name) {
  const auto& name = GetIso3CountryName(kFranceCountryName);
  ASSERT_EQ(name, ToCountryIso3(Country::kFrance));
}

}  // namespace grocery_shared::geo
