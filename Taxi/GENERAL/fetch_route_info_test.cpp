#include <userver/engine/sleep.hpp>
#include <userver/utest/utest.hpp>

#include <taxi_config/variables/CANDIDATES_FEATURE_SWITCHES.hpp>

#include <clients/routing/router.hpp>
#include <clients/routing/test/test_router_selector.hpp>
#include <filters/infrastructure/fetch_transport_type/fetch_transport_type.hpp>
#include <geometry/distance.hpp>
#include <infraver-router/router.hpp>
#include <models/geometry/point.hpp>
#include <testing/taxi_config.hpp>

#include "fetch_route_info.hpp"

namespace {

namespace cf = candidates::filters;
using cf::infrastructure::FetchRouteInfo;

const cf::FilterInfo kEmptyInfo;

using TestRouterSelector = clients::routing::TestRouterSelector;

class TestRouter : public clients::routing::Router {
  static inline const std::string kName = "linear-fallback";

 public:
  TestRouter(const clients::routing::RouterVehicleType& type)
      : Router(type, kName) {}

  bool IsEnabled() const override { return true; };

  bool HasFeatures(
      clients::routing::RouterFeaturesType features) const override {
    static const auto kFeatures = clients::routing::RouterFeatures::kRouteInfo;
    return kFeatures & features;
  }

  clients::routing::RouterResponse<clients::routing::RouteInfo> FetchRouteInfo(
      const clients::routing::Path& path, const clients::routing::DirectionOpt&,
      const clients::routing::RouterSettings& = {},
      const clients::routing::QuerySettings& = {}) const override {
    clients::routing::RouteInfo ret;
    ret.distance = ::geometry::GreatCircleDistance(path.at(0), path.at(1));
    const auto type = GetType();
    switch (type) {
      case clients::routing::RouterVehicleType::kVehicleCar:
      case clients::routing::RouterVehicleType::kVehicleTaxi:
      case clients::routing::RouterVehicleType::kVehicleTruck:
        ret.time = std::chrono::seconds(1);
        return ret;
      case clients::routing::RouterVehicleType::kVehicleBicycle:
      case clients::routing::RouterVehicleType::kVehicleScooter:
        ret.time = std::chrono::seconds(2);
        return ret;
      case clients::routing::RouterVehicleType::kVehicleMasstransit:
        ret.time = std::chrono::seconds(3);
        return ret;
      case clients::routing::RouterVehicleType::kVehiclePedestrian:
        ret.time = std::chrono::seconds(4);
        return ret;
      default:
        ret.time = std::chrono::seconds(5);
    }
    return ret;
  }
};

void WaitProcess(const cf::Filter& filter, const candidates::GeoMember& member,
                 cf::Context& context) {
  for (int i = 0; i < 10; ++i) {
    engine::SleepFor(std::chrono::milliseconds(10));
    const auto& result = filter.Process(member, context);
    if (result == cf::Result::kAllow) break;
  }
}

}  // namespace

UTEST(FetchRouteInfoTest, Basic) {
  auto config_storage = dynamic_config::MakeDefaultStorage(
      {{taxi_config::CANDIDATES_FEATURE_SWITCHES,
        formats::json::FromString(R"({"use_bicycle_router":true})")}});
  auto config = config_storage.GetSnapshot();
  TestRouterSelector router_selector(config_storage.GetSource(), nullptr);
  for (size_t i = 0;
       i < static_cast<size_t>(clients::routing::RouterVehicleType::kEnd);
       ++i) {
    router_selector.AddRouter(std::make_shared<TestRouter>(
        static_cast<clients::routing::RouterVehicleType>(i)));
  }

  const auto& positions = std::make_shared<models::DriverPositions>();

  FetchRouteInfo filter(
      kEmptyInfo,
      std::make_shared<infraver_router::Router>(
          router_selector, "", std::optional<std::string>{},
          clients::routing::QuerySettings{}, nullptr, config,
          infraver_router::Router::MasstransitSettings{10000, 1000}),
      {positions}, {positions}, {51, 51}, {}, {}, {});
  candidates::GeoMember member{{50, 50}, "id"};

  cf::Context context;

  models::RouteInfo route_info;

  // automobile
  cf::infrastructure::FetchTransportType::Set(
      context, contractor_transport::models::TransportType::kCar);
  EXPECT_EQ(cf::Result::kRepeat, filter.Process(member, context));
  WaitProcess(filter, member, context);
  EXPECT_NO_THROW(route_info = FetchRouteInfo::Get(context));
  EXPECT_EQ(1, route_info.time.count());

  // bicycle
  cf::infrastructure::FetchTransportType::Set(
      context, contractor_transport::models::TransportType::kBicycle);
  EXPECT_EQ(cf::Result::kRepeat, filter.Process(member, context));
  WaitProcess(filter, member, context);
  EXPECT_NO_THROW(route_info = FetchRouteInfo::Get(context));
  EXPECT_EQ(2, route_info.time.count());

  // rover
  cf::infrastructure::FetchTransportType::Set(
      context, contractor_transport::models::TransportType::kRover);
  EXPECT_EQ(cf::Result::kRepeat, filter.Process(member, context));
  WaitProcess(filter, member, context);
  EXPECT_NO_THROW(route_info = FetchRouteInfo::Get(context));
  EXPECT_EQ(2, route_info.time.count());

  // masstransit
  cf::infrastructure::FetchTransportType::Set(
      context, contractor_transport::models::TransportType::kPedestrian);
  EXPECT_EQ(cf::Result::kRepeat, filter.Process(member, context));
  WaitProcess(filter, member, context);
  EXPECT_NO_THROW(route_info = FetchRouteInfo::Get(context));
  EXPECT_EQ(3, route_info.time.count());

  // masstransit + pedestrian
  member.position = {50.99, 50.99};
  cf::infrastructure::FetchTransportType::Set(
      context, contractor_transport::models::TransportType::kPedestrian);
  EXPECT_EQ(cf::Result::kRepeat, filter.Process(member, context));
  WaitProcess(filter, member, context);
  EXPECT_NO_THROW(route_info = FetchRouteInfo::Get(context));
  EXPECT_EQ(3, route_info.time.count());

  // pedestrian
  member.position = {50.999, 50.999};
  cf::infrastructure::FetchTransportType::Set(
      context, contractor_transport::models::TransportType::kPedestrian);
  EXPECT_EQ(cf::Result::kRepeat, filter.Process(member, context));
  WaitProcess(filter, member, context);
  EXPECT_NO_THROW(route_info = FetchRouteInfo::Get(context));
  EXPECT_EQ(4, route_info.time.count());

  // no position
  context.ClearData();
  cf::infrastructure::FetchTransportType::Set(
      context, contractor_transport::models::TransportType::kPedestrian);
  EXPECT_EQ(cf::Result::kDisallow, filter.Process({{}, "id"}, context));
  EXPECT_FALSE(FetchRouteInfo::TryGet(context));
}

UTEST(FetchRouteInfoTest, TimeoutCondition) {
  const auto config_source = dynamic_config::GetDefaultSource();
  const auto config = dynamic_config::GetDefaultSnapshot();
  TestRouterSelector router_selector(config_source, nullptr);
  for (size_t i = 0;
       i < static_cast<size_t>(clients::routing::RouterVehicleType::kEnd);
       ++i) {
    router_selector.AddRouter(std::make_shared<TestRouter>(
        static_cast<clients::routing::RouterVehicleType>(i)));
  }

  const auto& positions = std::make_shared<models::DriverPositions>();
  const candidates::geoindexes::TimeoutCondition timeout_condition(
      formats::json::FromString(R"=({"timeout": 100})="));
  clients::routing::QuerySettings query_settings;
  query_settings.timeout = std::chrono::milliseconds{100};
  query_settings.retries = 1;

  FetchRouteInfo filter(kEmptyInfo,
                        std::make_shared<infraver_router::Router>(
                            router_selector, "", std::optional<std::string>{},
                            query_settings, nullptr, config),
                        {positions}, {positions}, {51, 51}, {},
                        timeout_condition, std::chrono::milliseconds{100});

  candidates::GeoMember member{{50, 50}, "id"};
  cf::Context context;
  models::RouteInfo route_info;

  cf::infrastructure::FetchTransportType::Set(
      context, contractor_transport::models::TransportType::kCar);
  EXPECT_EQ(cf::Result::kAllow, filter.Process(member, context));
  EXPECT_NO_THROW(route_info = FetchRouteInfo::Get(context));
  EXPECT_TRUE(route_info.approximate);
}
