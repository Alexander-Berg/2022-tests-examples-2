#pragma once

#include <gmock/gmock.h>
#include <clients/router.hpp>

class MockRouter : public clients::routing::Router {
 public:
  bool IsEnabled(const config::Config& /*config*/) const override {
    return true;
  }

  const std::string& GetName() const override {
    static const std::string name = "mock";
    return name;
  }

  // NOTE: gmock can not return unique_ptr
  std::unique_ptr<clients::routing::RouteInfoEx> RouteEx(
      const path_t& path, double, const handlers::Context& context,
      const std::set<std::string>&, const utils::misc::MetaInfo&) const final {
    return std::unique_ptr<clients::routing::RouteInfoEx>(
        RouteExProxy(path, context));
  }

  MOCK_CONST_METHOD2(RouteExProxy,
                     clients::routing::RouteInfoEx*(
                         const path_t& path, const handlers::Context& context));

  std::vector<clients::routing::RouteInfo> RouteBulk(
      const std::vector<path_t>&, const handlers::Context&,
      const std::set<std::string>&, const utils::misc::MetaInfo&) const final {
    throw std::runtime_error("not_implemented");
  }

  std::vector<clients::routing::RouteInfo> RouteBulk(
      const std::vector<clients::routing::TrackPoint>&,
      const clients::routing::Point&, const handlers::Context&,
      const std::set<std::string>&, const utils::misc::MetaInfo&) const final {
    throw std::runtime_error("not_implemented");
  }

  std::vector<clients::routing::DriverRouteInfo> RouteBulk(
      const std::vector<clients::routing::DriverPointEx>&,
      const clients::routing::Point&, const handlers::Context&,
      const std::set<std::string>&, const utils::misc::MetaInfo&) const final {
    throw std::runtime_error("not_implemented");
  }

  std::vector<clients::routing::DriverRouteInfo> RouteBulk(
      const std::vector<
          std::pair<clients::routing::DriverPointEx, utils::geometry::Point>>&,
      const handlers::Context&, const std::set<std::string>&,
      const utils::misc::MetaInfo&) const final {
    throw std::runtime_error("not_implemented");
  }

  std::vector<clients::routing::RouteInfo> RouteMatrix(
      const std::vector<clients::routing::Point>& /* from_bulk */,
      const clients::routing::Point& /* to */,
      const handlers::Context& /* context */,
      const std::set<std::string>& /* user_experiments */,
      const utils::misc::MetaInfo& /* infos */) const final {
    throw std::runtime_error("not_implemented");
  }

  std::unique_ptr<clients::routing::FutureRouteInfos> AsyncRouteBulk(
      const std::vector<path_t>&, const handlers::Context&,
      const std::set<std::string>&, const utils::misc::MetaInfo&) const final {
    throw std::runtime_error("not_implemented");
  }

  std::unique_ptr<clients::routing::FutureRouteInfos> AsyncRouteBulk(
      const std::vector<utils::geometry::TrackPoint>&,
      const clients::routing::Point&, const handlers::Context&,
      const std::set<std::string>&, const utils::misc::MetaInfo&) const final {
    throw std::runtime_error("not_implemented");
  }

  std::unique_ptr<clients::routing::FutureDriverRouteInfos> AsyncRouteBulk(
      const std::vector<
          std::pair<clients::routing::DriverPointEx, utils::geometry::Point>>&,
      const handlers::Context&, const std::set<std::string>&,
      const utils::misc::MetaInfo&) const final {
    throw std::runtime_error("not_implemented");
  }

  std::unique_ptr<clients::routing::FutureRouteInfos> AsyncRouteMatrix(
      const std::vector<clients::routing::Point>& /* from_bulk */,
      const clients::routing::Point& /* to */,
      const handlers::Context& /* context */,
      const std::set<std::string>& /* user_experiments */,
      const utils::misc::MetaInfo& /* infos */) const final {
    throw std::runtime_error("not_implemented");
  }

  std::unique_ptr<clients::routing::FutureRouteWaypointInfo> GetWaypointInfo(
      const path_t&, const handlers::Context&,
      const utils::misc::MetaInfo&) const final {
    throw std::runtime_error("not_implemented");
  }
};
