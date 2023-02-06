#include <gtest/gtest.h>

#include <userver/utest/utest.hpp>

#include <filters/infrastructure/fetch_driver/fetch_driver.hpp>
#include <userver/formats/json/value_builder.hpp>

#include "driver_work_mode.hpp"

namespace cf = candidates::filters;

namespace {

const std::string kDbidUuid{"dbid_uuid"};
const std::string kDefaultWorkMode{"orders"};

cf::Context GetContext() {
  auto driver_info = std::make_shared<models::Driver>();
  driver_info->id = models::DriverId::FromDbidUuid(kDbidUuid);
  cf::Context context;
  cf::infrastructure::FetchDriver::Set(context, driver_info);
  return context;
}

cf::efficiency::DriverWorkMode GetFilter(
    std::vector<std::string>&& filter_work_modes,
    const std::optional<std::string>& work_mode = std::nullopt) {
  auto drivers_work_modes = std::make_shared<models::DriversWorkModes>();

  if (work_mode) {
    drivers_work_modes->Set(
        kDbidUuid, {models::work_modes::ModeMapper::Parse(*work_mode), {}});
  }
  const cf::FilterInfo empty_info;
  return cf::efficiency::DriverWorkMode{
      empty_info, drivers_work_modes,
      models::work_modes::Modes(std::move(filter_work_modes))};
}

}  // namespace

UTEST(DriverWorkModeFilter, Basic) {
  auto context = GetContext();

  const candidates::GeoMember geo_member{models::geometry::Point{}, kDbidUuid};
  // empty work_modes:
  {
    const auto filter = GetFilter({});

    EXPECT_EQ(filter.Process(geo_member, context), cf::Result::kDisallow);
  }
  {
    const auto filter = GetFilter({}, kDefaultWorkMode);
    EXPECT_EQ(filter.Process(geo_member, context), cf::Result::kDisallow);
  }
  {
    const auto filter = GetFilter({}, "mode1");
    EXPECT_EQ(filter.Process(geo_member, context), cf::Result::kDisallow);
  }

  // mode1
  {
    const auto filter = GetFilter({"mode1"});

    EXPECT_EQ(filter.Process(geo_member, context), cf::Result::kDisallow);
  }
  {
    const auto filter = GetFilter({"mode1"}, kDefaultWorkMode);
    EXPECT_EQ(filter.Process(geo_member, context), cf::Result::kDisallow);
  }
  {
    const auto filter = GetFilter({"mode1"}, "mode1");
    EXPECT_EQ(filter.Process(geo_member, context), cf::Result::kAllow);
  }
  {
    const auto filter = GetFilter({"mode1"}, "mode2");
    EXPECT_EQ(filter.Process(geo_member, context), cf::Result::kDisallow);
  }

  // mode1 + default
  {
    const auto filter = GetFilter({"mode1", kDefaultWorkMode});

    EXPECT_EQ(filter.Process(geo_member, context), cf::Result::kAllow);
  }
  {
    const auto filter =
        GetFilter({"mode1", kDefaultWorkMode}, kDefaultWorkMode);
    EXPECT_EQ(filter.Process(geo_member, context), cf::Result::kAllow);
  }

  // mode1 + mode2
  {
    const auto filter = GetFilter({"mode1", "mode2"}, "mode1");
    EXPECT_EQ(filter.Process(geo_member, context), cf::Result::kAllow);
  }
  {
    const auto filter = GetFilter({"mode1", "mode2"}, "mode2");
    EXPECT_EQ(filter.Process(geo_member, context), cf::Result::kAllow);
  }
}
