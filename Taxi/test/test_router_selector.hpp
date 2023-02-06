#pragma once

#include <experiments3/components/experiments3_cache.hpp>

#include <clients/routing/router_query.hpp>
#include <clients/routing/router_selector.hpp>
#include <components/routing/router_component.hpp>

namespace clients::routing {

class Vendor;

class TestRouterSelector : public RouterSelector {
 public:
  using VendorPtr = std::shared_ptr<Vendor>;
  using RouterPtr = std::shared_ptr<Router>;

  TestRouterSelector(
      dynamic_config::Source config, ::caches::Experiments3* exp3_cache,
      const std::optional<std::string>& tvm_service_name = std::nullopt);

  virtual const RouterQuery GetRouterQuery(
      RouterVehicleType vehicle_type = RouterVehicleType::kVehicleCar,
      const std::optional<RouterZoneId>& id = std::nullopt,
      const std::optional<std::string>& target = std::nullopt,
      bool allow_fallback = true) const override;

  virtual const RouterQuery GetFallbackRouterQuery(
      RouterVehicleType vehicle_type) const override;

  // deprecated API

  virtual RouterQuery GetCarRouter(
      const std::optional<RouterZoneId>& id = std::nullopt,
      const std::optional<std::string>& target = std::nullopt,
      bool allow_fallback = true) const override;

  virtual RouterQuery GetPedestrianRouter(
      const std::optional<RouterZoneId>& id = std::nullopt,
      const std::optional<std::string>& target = std::nullopt,
      bool allow_fallback = true) const override;

  virtual RouterQuery GetBicycleRouter(
      const std::optional<RouterZoneId>& id = std::nullopt,
      const std::optional<std::string>& target = std::nullopt,
      bool allow_fallback = true) const override;

  virtual RouterQuery GetMasstransitRouter(
      const std::optional<RouterZoneId>& id = std::nullopt,
      const std::optional<std::string>& target = std::nullopt,
      bool allow_fallback = true) const override;

  virtual RouterQuery GetFallbackRouter(const RouterType& type) const override;

  virtual ~TestRouterSelector();

  void AddVendor(VendorPtr&& vendor);
  void AddRouter(RouterPtr&& vendor);

 private:
  class VendorWrapper;
  std::unique_ptr<RouterSelectorImpl> selector_;
  std::unordered_map<std::string, std::shared_ptr<VendorWrapper>> vendors_;
};

}  // namespace clients::routing
