#include <userver/utest/utest.hpp>

#include <fleet-brands/fleet_brands.hpp>

taxi_config::fleet_ui_brands::FleetUiBrands GetTestConfig() {
  return {.default_ =
              {
                  .tanker_key = "default_name",
                  .logo = "default_logo",
                  .icon = "default_icon",
              },
          .brands = {{.tanker_key = "uber",
                      .logo = "uber_logo",
                      .icon = "uber_icon",
                      .countries = {"rus", "ukr"},
                      .park_types = {{"uberdriver"}}},
                     {
                         .tanker_key = "yandex",
                         .logo = "yandex_logo",
                         .icon = "yandex_icon",
                         .countries = {"rus"},
                     },
                     {
                         .tanker_key = "yandex_aze",
                         .logo = "yandex_aze_logo",
                         .icon = "yandex_aze_icon",
                         .countries = {"aze"},
                     }}};
}

TEST(GetBrandTest, One) {
  using namespace fleet_brands;
  const std::vector<std::tuple<std::string, std::optional<std::string>, Brand>>
      tests = {{"rus",
                {},
                Brand{
                    .logo = "yandex_logo",
                    .tanker_key = "yandex",
                    .icon = "yandex_icon",
                }},
               {"rus", "uberdriver",
                Brand{
                    .logo = "uber_logo",
                    .tanker_key = "uber",
                    .icon = "uber_icon",
                }},
               {"aze",
                {},
                Brand{
                    .logo = "yandex_aze_logo",
                    .tanker_key = "yandex_aze",
                    .icon = "yandex_aze_icon",
                }}};
  const auto config = GetTestConfig();
  for (const auto& [country_id, park_type, correct] : tests) {
    const auto brand = GetBrand(country_id, park_type, config);
    EXPECT_EQ(brand, correct);
  }
}
