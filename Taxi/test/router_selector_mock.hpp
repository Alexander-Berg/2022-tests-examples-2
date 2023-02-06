#include <gmock/gmock.h>
#include <gtest/gtest.h>
#include <userver/utest/utest.hpp>

#include <clients/routing/router_selector.hpp>

namespace clients::routing {

class RouterSelectorMock : public RouterSelector {
 public:
  MOCK_METHOD(const RouterQuery, GetRouterQuery,
              (RouterVehicleType vehicle_type,
               const std::optional<RouterZoneId>& id,
               const std::optional<std::string>& target, bool allow_fallback),
              (const, override));
  MOCK_METHOD(const RouterQuery, GetFallbackRouterQuery,
              (RouterVehicleType type), (const, override));

  // deprecated API
  MOCK_METHOD(RouterQuery, GetCarRouter,
              (const std::optional<RouterZoneId>& id,
               const std::optional<std::string>& target, bool allow_fallback),
              (const, override));

  MOCK_METHOD(RouterQuery, GetPedestrianRouter,
              (const std::optional<RouterZoneId>& id,
               const std::optional<std::string>& target, bool allow_fallback),
              (const, override));

  MOCK_METHOD(RouterQuery, GetBicycleRouter,
              (const std::optional<RouterZoneId>& id,
               const std::optional<std::string>& target, bool allow_fallback),
              (const, override));

  MOCK_METHOD(RouterQuery, GetMasstransitRouter,
              (const std::optional<RouterZoneId>& id,
               const std::optional<std::string>& target, bool allow_fallback),
              (const, override));

  MOCK_METHOD(RouterQuery, GetFallbackRouter, (const RouterType& type),
              (const, override));
};

}  // namespace clients::routing
