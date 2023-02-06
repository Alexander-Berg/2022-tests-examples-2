#pragma once

#include <gmock/gmock.h>
#include <gtest/gtest.h>
#include <userver/utest/utest.hpp>

#include <clients/routing/router.hpp>
#include <clients/routing/router_selector.hpp>

namespace clients::routing {

class RouterMock : public Router {
 public:
  RouterMock(RouterVehicleType type,
             const std::string& router_name = "router_gmock")
      : Router(type, router_name) {}

  /// Call this method to enable reasonable defaults for mock behaviour:
  /// Make router enabled
  /// Enable all features
  /// You override any of this with custom ON_CALL invocations later
  void EnableDefaults() {
    using testing::Return;
    using testing::ReturnRef;
    static std::string router_name{"router_gmock"};

    ON_CALL(*this, IsEnabled).WillByDefault(Return(true));
    ON_CALL(*this, HasFeatures).WillByDefault(Return(true));
  }

  /// You can use this method with ON_CALL or EXPECT_CALL to emulate
  /// returning path from start to end with only one point in it - destination
  static RoutePath MakeOnePointRoute(
      const std::vector<::geometry::Position>& path, const DirectionOpt&,
      const RouterSettings&, const QuerySettings&);

  /// Similar to the method MakeOnePointRoute, this one will return
  /// a route with two points in it - the first one from \p path
  /// and the last one from \p path
  static RoutePath MakeTwoPointsRoute(
      const std::vector<::geometry::Position>& path, const DirectionOpt&,
      const RouterSettings&, const QuerySettings&);

  /// Similar to the method MakeTwoPointsRoute, this one will return
  /// a route with N (N >= 2) points in it - all points from \p path
  static RoutePath MakeNPointsRoute(
      const std::vector<::geometry::Position>& path, const DirectionOpt&,
      const RouterSettings&, const QuerySettings&);

  /// Set MakeTwoPointsRoute as default mock behaviour for fetch route/fetch
  /// route info
  void SetDefaultMakeTwoPointsRoute();
  /// Set MakeOnePointRoute as default behaviour fetch route/fetch route info
  void SetDefaultMakeOnePointRoute();
  /// Set MakeNPointRoute as default behaviour fetch route/fetch route info
  void SetDefaultMakeNPointsRoute();

  /// Set given callable as default behaviour for fetch route/fetch route info
  /// callbable must be copyable because we will set it into several functions
  template <typename Callable>
  void SetDefaultFetchRoutePathAndInfo(Callable callable);

  /// check that router is enabled by config
  /// @return enabled (true) or disabled (false)
  MOCK_METHOD(bool, IsEnabled, (), (const, override));

  /// check that router has features
  /// @param features features to check
  /// @return has features (true) or not (false)
  MOCK_METHOD(bool, HasFeatures, (RouterFeaturesType features),
              (const, override));

  /// fetch summary route info from router
  /// @param path path is a set of points, which should be present in built
  /// route
  /// @param source_direction direction of start path point (optional)
  /// @param router_settings settings for router @see
  /// clients::routing::RouterSettings
  /// @param query_settings settings for query to router @see
  /// clients::routing::QuerySettings
  /// @return @see routing_base::RouteInfo
  MOCK_METHOD(RouterResponse<RouteInfo>, FetchRouteInfo,
              (const Path& path, const DirectionOpt& source_direction,
               const RouterSettings& router_settings,
               const QuerySettings& query_settings),
              (const, override));

  /// fetch full route info with path from router
  /// @param path path is a set of points, which should be present in built
  /// route
  /// @param source_direction direction of start path point (optional)
  /// @param router_settings settings for router @see
  /// clients::routing::RouterSettings
  /// @param query_settings settings for query to router @see
  /// clients::routing::QuerySettings
  /// @return @see routing_base::RouteInfo
  MOCK_METHOD(RouterResponse<RoutePath>, FetchRoutePath,
              (const Path& path, const DirectionOpt& source_direction,
               const RouterSettings& router_settings,
               const QuerySettings& query_settings),
              (const, override));

  /// fetch a few summary routes info from router
  /// @param path path is a set of points, which should be present in built
  /// route
  /// @param source_direction direction of start path point (optional)
  /// @param settings settings for router @see
  /// clients::routing::RouterSettings
  /// @param query_settings settings for query to router @see
  /// clients::routing::QuerySettings
  /// @return @see routing_base::RouteInfo
  MOCK_METHOD(RouterResponse<std::vector<RouteInfo>>, FetchRouteInfos,
              (const Path& path, const DirectionOpt& source_direction,
               const RouterSettings& settings,
               const QuerySettings& query_settings),
              (const, override));

  /// fetch a few full routes info with path from router
  /// @param path path is a set of points, which should be present in built
  /// route
  /// @param source_direction direction of start path point (optional)
  /// @param settings settings for router @see
  /// clients::routing::RouterSettings
  /// @param query_settings settings for query to router @see
  /// clients::routing::QuerySettings
  /// @return @see routing_base::RoutePath
  MOCK_METHOD(RouterResponse<std::vector<RoutePath>>, FetchRoutePaths,
              (const Path& path, const DirectionOpt& source_direction,
               const RouterSettings& settings,
               const QuerySettings& query_settings),
              (const, override));

  /// fetch summary info about routes between each point from
  /// srcs vector to each point from dsts vector
  /// @param srcs vector of source points
  /// @param srcs_dirs vector of source points directions
  /// @param dsts vector of destination points
  /// @param dsts_dirs vector of destination points directions
  /// @param router_settings settings for router @see
  /// clients::routing::RouterSettings
  /// @param query_settings settings for query to router @see
  /// clients::routing::QuerySettings
  /// @return vector of routing_base::MatrixInfo for each pair of points
  /// index for (src_i, dst_j) must be src_i * size(src) + dst_j
  /// if no route found point time and distance will be std::nullopt
  MOCK_METHOD(RouterResponse<narray::Array2D<MatrixInfo>>, FetchMatrixInfo,
              (const Points& srcs, const Directions& srcs_dirs,
               const Points& dsts, const Directions& dsts_dirs,
               const RouterSettings& router_settings,
               const QuerySettings& query_settings),
              (const, override));
};

}  // namespace clients::routing

#include "router_mock_impl.hpp"
