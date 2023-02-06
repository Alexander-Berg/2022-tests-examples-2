#include <fmt/format.h>
#include <userver/logging/log.hpp>
#include <userver/utils/exception.hpp>

#include <clients/routing/exceptions.hpp>
#include <clients/routing/router_query.hpp>
#include <clients/routing/test/test_router_selector.hpp>

#include <vendors/vendor.hpp>

#include "clients/routing/router_selector_impl.hpp"

namespace clients::routing {

class TestRouterSelector::VendorWrapper : public Vendor {
 public:
  VendorWrapper(const std::string& name) : Vendor(name) {}

  RouterPtr GetRouterByType(RouterVehicleType vehicle_type) const override {
    return routers[vehicle_type];
  }

  mutable std::unordered_map<RouterVehicleType, RouterPtr> routers;
};

TestRouterSelector::~TestRouterSelector() = default;

TestRouterSelector::TestRouterSelector(
    dynamic_config::Source config_source, ::caches::Experiments3* exp3_cache,
    const std::optional<std::string>& tvm_service_name)
    : selector_(std::unique_ptr<RouterSelectorImpl>(new RouterSelectorImpl(
          config_source, exp3_cache, nullptr, tvm_service_name))) {
  const auto config = config_source.GetSnapshot();
  selector_->FillRules(config);
}

void TestRouterSelector::AddVendor(TestRouterSelector::VendorPtr&& vendor) {
  selector_->AddVendor(std::move(vendor));
}

void TestRouterSelector::AddRouter(TestRouterSelector::RouterPtr&& router) {
  std::shared_ptr<VendorWrapper> vendor;
  const auto& name = router->GetName();
  auto fit = vendors_.find(name);
  if (fit == vendors_.end()) {
    vendor = std::make_shared<VendorWrapper>(name);
    selector_->AddVendor(std::static_pointer_cast<Vendor>(vendor));
    vendors_[name] = vendor;
  } else {
    vendor = fit->second;
  }

  vendor->routers[router->GetType()] = router;
}

RouterQuery TestRouterSelector::GetCarRouter(
    const std::optional<RouterZoneId>& id,
    const std::optional<std::string>& target, bool allow_fallback) const {
  return selector_->GetCarRouter(id, target, allow_fallback);
}

RouterQuery TestRouterSelector::GetPedestrianRouter(
    const std::optional<RouterZoneId>& id,
    const std::optional<std::string>& target, bool allow_fallback) const {
  return selector_->GetPedestrianRouter(id, target, allow_fallback);
}

RouterQuery TestRouterSelector::GetBicycleRouter(
    const std::optional<RouterZoneId>& id,
    const std::optional<std::string>& target, bool allow_fallback) const {
  return selector_->GetBicycleRouter(id, target, allow_fallback);
}

RouterQuery TestRouterSelector::GetMasstransitRouter(
    const std::optional<RouterZoneId>& id,
    const std::optional<std::string>& target, bool allow_fallback) const {
  return selector_->GetMasstransitRouter(id, target, allow_fallback);
}

RouterQuery TestRouterSelector::GetFallbackRouter(
    const RouterType& type) const {
  return selector_->GetFallbackRouter(type);
}

const RouterQuery TestRouterSelector::GetFallbackRouterQuery(
    RouterVehicleType type) const {
  return selector_->GetFallbackRouterQuery(type);
}

const RouterQuery TestRouterSelector::GetRouterQuery(
    RouterVehicleType vehicle_type, const std::optional<RouterZoneId>& id,
    const std::optional<std::string>& target, bool allow_fallback) const {
  return selector_->GetRouterQuery(vehicle_type, id, target, allow_fallback);
}

}  // namespace clients::routing
