#include "view.hpp"

#include <clients/routing/router_selector.hpp>
#include <clients/routing/router_types.hpp>

namespace handlers::test_router_query::post {

namespace {

using RouterVehicleType = routing_base::RouterVehicleType;

routing_base::RouterVehicleType ParseVehicleType(const Request& request) {
  RouterVehicleType result{RouterVehicleType::kVehicleCar};
  // Take first from router_type param
  const auto& type = request.body.router_type;
  switch (type) {
    case handlers::TestRouteRequestRoutertype::kCar: {
      result = RouterVehicleType::kVehicleCar;
      break;
    }
    case handlers::TestRouteRequestRoutertype::kPedestrian: {
      result = RouterVehicleType::kVehiclePedestrian;
      break;
    }
    case handlers::TestRouteRequestRoutertype::kBicycle: {
      result = RouterVehicleType::kVehicleBicycle;
      break;
    }
    case handlers::TestRouteRequestRoutertype::kMasstransit: {
      result = RouterVehicleType::kVehicleMasstransit;
      break;
    }
  }

  // and overwrite from vehicle, if present
  const auto& req_vehicle = request.body.vehicle;
  if (req_vehicle) {
    if (req_vehicle->type) {
      if (*req_vehicle->type == handlers::TestRouteRequestVehicleType::kCar) {
        result = routing_base::RouterVehicleType::kVehicleCar;
      } else if (*req_vehicle->type ==
                 handlers::TestRouteRequestVehicleType::kTaxi) {
        result = routing_base::RouterVehicleType::kVehicleTaxi;
      } else if (*req_vehicle->type ==
                 handlers::TestRouteRequestVehicleType::kTruck) {
        result = routing_base::RouterVehicleType::kVehicleTruck;
      }
    }
  }

  return result;
}

std::optional<routing_base::RouterVehicle> ParseVehicle(
    const Request& request) {
  const auto& req_vehicle = request.body.vehicle;
  if (!req_vehicle) {
    return std::nullopt;
  }

  routing_base::RouterVehicle vehicle;

  vehicle.vehicle_pass_ids = req_vehicle->pass_ids;
  if (req_vehicle->weight) {
    vehicle.vehicle_weight = *req_vehicle->weight * routing_base::units::tons;
  }
  if (req_vehicle->axle_weight) {
    vehicle.vehicle_axle_weight =
        *req_vehicle->axle_weight * routing_base::units::tons;
  }
  if (req_vehicle->max_weight) {
    vehicle.vehicle_max_weight =
        *req_vehicle->max_weight * routing_base::units::tons;
  }
  if (req_vehicle->height) {
    vehicle.vehicle_height = *req_vehicle->height * routing_base::units::meters;
  }
  if (req_vehicle->width) {
    vehicle.vehicle_width = *req_vehicle->width * routing_base::units::meters;
  }
  if (req_vehicle->length) {
    vehicle.vehicle_length = *req_vehicle->length * routing_base::units::meters;
  }
  if (req_vehicle->payload) {
    vehicle.vehicle_payload = *req_vehicle->payload * routing_base::units::tons;
  }
  if (req_vehicle->eco_class) {
    vehicle.vehicle_eco_class =
        static_cast<routing_base::units::EcoClass>(*req_vehicle->eco_class);
  }
  vehicle.vehicle_has_trailer = req_vehicle->has_trailer;

  return vehicle;
}

std::optional<routing_base::RouterTransportType> ParseAvoidTransport(
    const Request& request) {
  const auto& req_avoid_transport = request.body.avoid_transport;
  if (!req_avoid_transport) {
    return std::nullopt;
  }

  routing_base::RouterTransportType avoid_transport =
      routing_base::RouterTransportTypes::kTransportNone;

  for (const auto& t : *req_avoid_transport) {
    if (t == handlers::TestRouteRequestAvoidtransportA::kBus) {
      avoid_transport |= routing_base::RouterTransportTypes::kTransportBus;
    }
    if (t == handlers::TestRouteRequestAvoidtransportA::kMinibus) {
      avoid_transport |= routing_base::RouterTransportTypes::kTransportMinibus;
    }
    if (t == handlers::TestRouteRequestAvoidtransportA::kRailway) {
      avoid_transport |= routing_base::RouterTransportTypes::kTransportRailway;
    }
    if (t == handlers::TestRouteRequestAvoidtransportA::kSuburban) {
      avoid_transport |= routing_base::RouterTransportTypes::kTransportSuburban;
    }
    if (t == handlers::TestRouteRequestAvoidtransportA::kTramway) {
      avoid_transport |= routing_base::RouterTransportTypes::kTransportTramway;
    }
    if (t == handlers::TestRouteRequestAvoidtransportA::kTrolleybus) {
      avoid_transport |=
          routing_base::RouterTransportTypes::kTransportTrolleybus;
    }
    if (t == handlers::TestRouteRequestAvoidtransportA::kUnderground) {
      avoid_transport |=
          routing_base::RouterTransportTypes::kTransportUnderground;
    }
  }

  return avoid_transport;
}

}  // namespace

Response View::Handle(Request&& request, Dependencies&& dependencies) {
  const auto& points_from = request.body.points_from;
  const auto& points_to = request.body.points_to;
  const auto& route = request.body.route;

  const auto& id = request.body.id;
  const auto& target = request.body.target;
  const auto& selector = dependencies.extra.router_selector;
  const auto& type = ParseVehicleType(request);
  const auto router = selector.GetRouterQuery(type, id, target);

  routing_base::RouterSettings settings;
  settings.jams = (request.body.use_jams ? routing_base::RouterJams::kJams
                                         : routing_base::RouterJams::kNoJams);
  settings.tolls =
      (request.body.use_tolls ? routing_base::RouterTolls::kTolls
                              : routing_base::RouterTolls::kNoTolls);
  settings.vehicle = ParseVehicle(request);

  if (type == RouterVehicleType::kVehicleMasstransit) {
    settings.avoid_transport = ParseAvoidTransport(request);
  }

  Response200 response;
  if (router.HasRouters()) {
    response.router_name = router.GetRouters().front();
  }

  if (request.body.request_type ==
      handlers::TestRouteRequestRequesttype::kSummary) {
    if (!route) {
      throw Response404({"empty route parameter for request type summary"});
    }

    handlers::TestRouteResponsePath ret;
    const auto info = router.FetchRouteInfo(*route, std::nullopt, settings);

    if (info.time) {
      ret.duration = info.time->count();
    }
    if (info.distance) {
      ret.length = info.distance->value();
    }
    if (info.blocked) {
      ret.has_closure = *info.blocked;
    }
    if (info.has_dead_jam) {
      ret.has_dead_jam = *info.has_dead_jam;
    }
    if (info.has_toll_roads) {
      ret.has_toll_roads = *info.has_toll_roads;
    }

    response.paths.emplace_back(std::move(ret));
  } else if (request.body.request_type ==
             handlers::TestRouteRequestRequesttype::kPath) {
    if (!route) {
      throw Response404({"empty route parameter for request type path"});
    }

    handlers::TestRouteResponsePath ret;
    const auto path = router.FetchRoutePath(*route, std::nullopt, settings);

    if (path.info.time) {
      ret.duration = path.info.time->count();
    }
    if (path.info.distance) {
      ret.length = path.info.distance->value();
    }
    if (path.info.blocked) {
      ret.has_closure = *path.info.blocked;
    }
    if (path.info.has_dead_jam) {
      ret.has_dead_jam = *path.info.has_dead_jam;
    }
    if (path.info.has_toll_roads) {
      ret.has_toll_roads = *path.info.has_toll_roads;
    }

    std::vector<geometry::Position> ret_path;
    ret_path.reserve(path.path.size());
    for (const auto& point : path.path) {
      ret_path.emplace_back(std::move(point));
    }
    ret.path = ret_path;

    response.paths.emplace_back(std::move(ret));
  } else {
    if (!points_from) {
      throw Response404(
          {"empty points_from parameter for request type matrix"});
    }
    if (!points_to) {
      throw Response404({"empty points_to parameter for request type matrix"});
    }

    const auto infos =
        router.FetchMatrixInfo(*points_from, *points_to, settings)
            .DetachUnderlying();
    for (const auto& info : infos) {
      handlers::TestRouteResponsePath ret;

      if (info.time) {
        ret.duration = info.time->count();
      }
      if (info.distance) {
        ret.length = info.distance->value();
      }
      if (info.blocked) {
        ret.has_closure = *info.blocked;
      }
      if (info.has_dead_jam) {
        ret.has_dead_jam = *info.has_dead_jam;
      }
      if (info.has_toll_roads) {
        ret.has_toll_roads = *info.has_toll_roads;
      }

      response.paths.emplace_back(std::move(ret));
    }
  }

  return response;
}

// clang-format off
} // namespace handlers::test_router_query::post
// clang-format on
