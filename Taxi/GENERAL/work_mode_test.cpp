#include <gtest/gtest.h>

#include <userver/utest/utest.hpp>

#include <filters/infrastructure/fetch_driver/fetch_driver.hpp>
#include <userver/formats/json/value_builder.hpp>

#include "work_mode.hpp"

namespace cf = candidates::filters;

namespace {

const std::string kDbidUuid{"dbid_uuid"};

cf::Context GetContext() {
  auto driver_info = std::make_shared<models::Driver>();
  driver_info->id = models::DriverId::FromDbidUuid(kDbidUuid);
  cf::Context context;
  cf::infrastructure::FetchDriver::Set(context, driver_info);
  return context;
}

using Properties = std::vector<std::string>;

cf::efficiency::WorkMode GetFilter(
    const Properties& filter_work_modes,
    const std::optional<Properties>& properties = std::nullopt) {
  auto drivers_work_modes = std::make_shared<models::DriversWorkModes>();

  if (properties) {
    drivers_work_modes->Set(kDbidUuid, {{}, *properties});
  }
  const cf::FilterInfo empty_info;
  return cf::efficiency::WorkMode{
      empty_info, drivers_work_modes,
      models::work_modes::Properties(filter_work_modes)};
}

}  // namespace

struct WorkModePropertiesTestData {
  Properties filter_properties;
  std::optional<Properties> driver_properties;
  cf::Result expected;
};

struct WorkModePropertiesTestDataParametrized
    : public ::testing::TestWithParam<WorkModePropertiesTestData> {};

UTEST_P(WorkModePropertiesTestDataParametrized, Variants) {
  const auto param = GetParam();

  auto context = GetContext();
  const candidates::GeoMember geo_member{models::geometry::Point{}, kDbidUuid};

  const auto filter =
      GetFilter(param.filter_properties, param.driver_properties);
  EXPECT_EQ(filter.Process(geo_member, context), param.expected);
}

const Properties kDefaultProperties = {"property1", "property2"};
const Properties kPropertiesFilterNoIntersect = {"property3", "property4"};
const Properties kPropertiesFilterIntersects = {"property2", "property5"};

const std::vector<WorkModePropertiesTestData> kTestData = {
    {{}, {}, cf::Result::kDisallow},
    {{}, kDefaultProperties, cf::Result::kDisallow},
    {kPropertiesFilterIntersects, {}, cf::Result::kDisallow},
    {kPropertiesFilterNoIntersect, kDefaultProperties, cf::Result::kDisallow},
    {kPropertiesFilterIntersects, kDefaultProperties, cf::Result::kAllow}};

INSTANTIATE_UTEST_SUITE_P(WorkModePropertiesFilter,
                          WorkModePropertiesTestDataParametrized,
                          ::testing::ValuesIn(kTestData));
