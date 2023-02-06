#include <gtest/gtest.h>

#include <candidates/search_settings/getter.hpp>
#include <filters/infrastructure/fetch_final_classes/fetch_final_classes.hpp>
#include <filters/infrastructure/fetch_route_info/fetch_route_info.hpp>
#include <filters/infrastructure/fetch_route_info/models/route_info.hpp>
#include <filters/infrastructure/fetch_transport_type/fetch_transport_type.hpp>
#include <models/classes.hpp>
#include <testing/taxi_config.hpp>
#include <userver/dynamic_config/fwd.hpp>
#include <userver/dynamic_config/value.hpp>
#include <userver/utest/utest.hpp>
#include <utils/mock_dispatch_settings.hpp>
#include "route_info.hpp"

namespace cf = candidates::filters;

namespace {

cf::Context CreateContext(const models::RouteInfo& route_info) {
  cf::Context context;
  cf::infrastructure::FetchRouteInfo::Set(context, route_info);
  return context;
}

cf::Context CreateContext(const models::RouteInfo& route_info,
                          const models::TransportType transport_type,
                          const models::Classes classes) {
  auto context = CreateContext(route_info);
  cf::infrastructure::FetchFinalClasses::Set(context, classes);
  cf::infrastructure::FetchTransportType::Set(context, transport_type);
  return context;
}

const cf::FilterInfo kEmptyInfo;

}  // namespace

UTEST(RouteInfoFilter, Basic) {
  candidates::GeoMember driver;

  dispatch_settings::models::SettingsValues setting;
  setting.max_robot_distance = 1000;
  setting.max_robot_time = 100;
  setting.pedestrian_max_search_route_distance = 2000;
  setting.pedestrian_max_search_route_time = std::chrono::seconds{2000};

  dispatch_settings::models::SettingsValues::PedestrianSettings
      pedestrian_settings;
  pedestrian_settings.max_search_route_distance = 2000;
  pedestrian_settings.max_search_route_time = std::chrono::seconds{2000};
  setting.pedestrian_settings = dynamic_config::ValueDict<
      dispatch_settings::models::SettingsValues::PedestrianSettings>{
      "PEDESTRIAN_SETTINGS",
      {{dynamic_config::kValueDictDefaultName, pedestrian_settings}}};

  std::unordered_map<std::string, dispatch_settings::models::SettingsValues>
      settings;
  settings["econom"] = setting;
  setting.max_robot_distance = 2000;
  setting.max_robot_time = 2000;
  setting.pedestrian_disabled = true;
  settings["comfort"] = setting;

  formats::json::ValueBuilder builder;
  builder["zone_id"] = "zone";
  builder["allowed_classes"].PushBack("econom");
  builder["allowed_classes"].PushBack("comfort");

  const auto& config = dynamic_config::GetDefaultSnapshot();
  const auto& search_settings =
      std::make_shared<candidates::search_settings::Getter>(
          builder.ExtractValue(),
          std::make_shared<utils::MockDispatchSettings>(std::move(settings)),
          nullptr, nullptr, config);
  cf::infrastructure::RouteInfo filter(kEmptyInfo, search_settings);

  std::vector<models::RouteInfo> bad_infos = {
      clients::routing::RouteInfo{150, 900},
      clients::routing::RouteInfo{50, 1050},
      clients::routing::RouteInfo{200, 2000},
  };
  for (const auto& info : bad_infos) {
    auto context = CreateContext(info, models::TransportType::kCar,
                                 models::Classes{"econom"});
    EXPECT_EQ(filter.Process(driver, context), cf::Result::kDisallow);
  }

  for (const auto& info : bad_infos) {
    auto context = CreateContext(info, models::TransportType::kCar,
                                 models::Classes{"econom", "comfort"});
    EXPECT_EQ(filter.Process(driver, context), cf::Result::kAllow);
  }

  for (const auto& info : bad_infos) {
    auto context = CreateContext(info, models::TransportType::kBicycle,
                                 models::Classes{"econom"});
    EXPECT_EQ(filter.Process(driver, context), cf::Result::kAllow);
  }

  for (const auto& info : bad_infos) {
    auto context = CreateContext(info, models::TransportType::kBicycle,
                                 models::Classes{"comfort"});
    EXPECT_EQ(filter.Process(driver, context), cf::Result::kDisallow);
  }

  const std::vector<models::RouteInfo> ok_infos = {
      clients::routing::RouteInfo{50, 500},
      clients::routing::RouteInfo{100, 950},
      clients::routing::RouteInfo{95, 1000},
      clients::routing::RouteInfo{100, 1000},
  };
  for (const auto& info : ok_infos) {
    auto context = CreateContext(info, models::TransportType::kBicycle,
                                 models::Classes{"econom"});
    EXPECT_EQ(filter.Process(driver, context), cf::Result::kAllow);
  }
}
