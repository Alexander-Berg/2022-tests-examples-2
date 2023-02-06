#include <branding/applications.hpp>

#include <testing/taxi_config.hpp>
#include <userver/dynamic_config/snapshot.hpp>
#include <userver/formats/json.hpp>
#include <userver/utest/utest.hpp>

#include <taxi_config/variables/APPLICATION_BRAND_RELATED_BRANDS.hpp>
#include <taxi_config/variables/APPLICATION_MAP_BRAND.hpp>

#include "docs_map.hpp"

namespace {

std::vector<dynamic_config::KeyValue> ToRelatedBrands(
    const std::string& brand, const std::unordered_set<std::string>& related) {
  return {{taxi_config::APPLICATION_BRAND_RELATED_BRANDS,
           {{brand, {related.begin(), related.end()}}}}};
}

std::vector<dynamic_config::KeyValue> ToBrandMap(
    const std::unordered_map<std::string, std::string>& mapping) {
  return {{taxi_config::APPLICATION_MAP_BRAND, mapping}};
}

}  // namespace

UTEST(TestApplications, RelatedBrandsEmpty) {
  dynamic_config::StorageMock config_storage{DefaultConfigsForTests()};
  const auto config = config_storage.GetSnapshot();

  const std::string& brand = "yataxi";
  auto related = branding::GetRelatedBrands(brand, config);
  ASSERT_EQ(related.empty(), true);
}

UTEST(TestApplications, RelatedBrands) {
  const std::string brand = "yataxi";
  std::unordered_set<std::string> mock_related{"uber_az", "uber_kz", "yango"};

  dynamic_config::StorageMock config_storage{
      ToRelatedBrands("yataxi", {"uber_az", "uber_kz", "yango"})};
  const auto config = config_storage.GetSnapshot();

  auto related = branding::GetRelatedBrands(brand, config);
  ASSERT_EQ(related, mock_related);
}

UTEST(TestApplications, BrandApplicationsNoApps) {
  const std::string brand = "yataxi";

  dynamic_config::StorageMock config_storage{DefaultConfigsForTests()};
  const auto config = config_storage.GetSnapshot();

  auto apps = branding::GetApplicationsForBrand(brand, config);
  ASSERT_EQ(apps.empty(), true);
}

UTEST(TestApplications, BrandApplicationsNoRelated) {
  const std::string& brand = "yataxi";

  dynamic_config::StorageMock config_storage{DefaultConfigsForTests()};
  config_storage.Extend({{taxi_config::APPLICATION_MAP_BRAND,
                          {{"iphone", "yataxi"},
                           {"android", "yataxi"},
                           {"uber", "yauber"},
                           {"yango_iphone", "yango"}}}});
  const auto config = config_storage.GetSnapshot();

  std::unordered_set<std::string> expected{"iphone", "android"};
  auto apps = branding::GetApplicationsForBrand(brand, config);
  ASSERT_EQ(apps, expected);
}

UTEST(TestApplications, BrandApplicationsRelated) {
  const std::string& brand = "yataxi";

  dynamic_config::StorageMock config_storage;
  config_storage.Extend(ToRelatedBrands(brand, {"yauber"}));
  config_storage.Extend(ToBrandMap({{"iphone", "yataxi"},
                                    {"android", "yataxi"},
                                    {"uber", "yauber"},
                                    {"yango_iphone", "yango"}}));
  const auto config = config_storage.GetSnapshot();

  std::unordered_set<std::string> expected{"iphone", "android", "uber"};
  auto apps = branding::GetApplicationsForBrand(brand, config);
  ASSERT_EQ(apps, expected);
}
