#include <gtest/gtest.h>

#include <clients/routing/test/test_router_selector.hpp>
#include <geometry/units.hpp>
#include <userver/clients/http/error.hpp>
#include <userver/dynamic_config/snapshot.hpp>
#include <userver/formats/json/serialize_container.hpp>
#include <userver/formats/json/value_builder.hpp>
#include <userver/utest/utest.hpp>
#include <utest/routing/mock_config_test.hpp>
#include <utility>
#include <vendors/fallback/router_fallback.hpp>
#include <vendors/tigraph/router_tigraph.hpp>

#include "clients/routing/router_selector_impl.hpp"

using clients::routing::DirectionOpt;
using clients::routing::ExecutionSettings;
using clients::routing::MatrixInfo;
using clients::routing::Path;
using clients::routing::Points;
using clients::routing::QuerySettings;
using clients::routing::RouteInfo;
using clients::routing::RoutePath;
using clients::routing::Router;
using RouterPtr = clients::routing::Vendor::RouterPtr;
using RouterBasePtr = clients::routing::Vendor::RouterBasePtr;
using clients::routing::RouterResponse;
using clients::routing::RouterSelectorImpl;
using clients::routing::RouterSettings;
using clients::routing::RouterType;
using clients::routing::RouterZoneId;
using clients::routing::Vendor;
using clients::routing::utest::CreateRouterConfig;
using clients::routing::utest::RouterSelect;
using routing_base::RouterVehicleType;

namespace clients::routing {

class RouterTest : public Router {
 public:
  RouterTest(const std::string& name, const RouterVehicleType& type,
             bool is_enabled = true)
      : Router(type, name), name_(name), is_enabled_(is_enabled) {}

  bool IsEnabled() const override { return is_enabled_; }

  bool HasFeatures(clients::routing::RouterFeaturesType) const override {
    return true;
  }

  RouterResponse<RouteInfo> FetchRouteInfo(
      const Path&, const std::optional<::geometry::Azimuth>&,
      const RouterSettings&, const QuerySettings&) const override {
    return RouteInfo{};
  }

  RouterResponse<RoutePath> FetchRoutePath(
      const Path&, const std::optional<::geometry::Azimuth>&,
      const RouterSettings&, const QuerySettings&) const override {
    return RoutePath{};
  }

 protected:
  const std::string name_;
  const bool is_enabled_;
};

class AlwaysThrowingRouter : public RouterTest {
 public:
  using RouterTest::RouterTest;

  RouterResponse<RouteInfo> FetchRouteInfo(
      const Path&, const std::optional<::geometry::Azimuth>&,
      const RouterSettings&, const QuerySettings&) const override {
    throw clients::http::HttpClientException(400, clients::http::LocalStats());
  }

  RouterResponse<RoutePath> FetchRoutePath(
      const Path&, const std::optional<::geometry::Azimuth>&,
      const RouterSettings&, const QuerySettings&) const override {
    throw clients::http::HttpClientException(400, clients::http::LocalStats());
  }
};

template <typename T>
class VendorTest : public Vendor {
 public:
  VendorTest(const std::string& name) : Vendor(name) {}

  RouterPtr GetRouterByType(RouterVehicleType vehicle_type) const override {
    return std::make_shared<T>(GetName(), vehicle_type);
  }
};

class RouterSelectorTest {
 public:
  RouterSelectorTest(
      dynamic_config::StorageMock&& storage, ::caches::Experiments3* exp3_cache,
      const std::optional<std::string>& tvm_name = std::nullopt) {
    storage_ = std::move(storage);
    selector_ = std::unique_ptr<RouterSelectorImpl>(new RouterSelectorImpl(
        storage_.GetSource(), exp3_cache, nullptr, tvm_name));
  }

  ~RouterSelectorTest() {
    // remove actual selector before storage_ is destroyed
    selector_ = nullptr;
  };

  void AddVendor(const std::string& name) {
    return selector_->AddVendor(std::make_shared<VendorTest<RouterTest>>(name));
  }

  void AddVendorAlias(const std::string& name, const std::string& alias) {
    return selector_->AddVendorAlias(name, alias);
  }

  void AddAlwaysThrowingRouter(const std::string& name) {
    return selector_->AddVendor(
        std::make_shared<VendorTest<AlwaysThrowingRouter>>(name));
  }

  template <typename... T>
  auto GetCarRouter(T&&... args) {
    return selector_->GetCarRouter(std::forward<T>(args)...);
  }

  template <typename... T>
  auto GetCarRouter(T&&... args) const {
    return selector_->GetCarRouter(std::forward<T>(args)...);
  }

  template <typename... T>
  auto GetRouterQuery(T&&... args) const {
    return selector_->GetRouterQuery(std::forward<T>(args)...);
  }

 private:
  std::unique_ptr<RouterSelectorImpl> selector_;
  // storage must outlive selector_;
  dynamic_config::StorageMock storage_;
};

std::unique_ptr<RouterSelectorTest> CreateSelector() {
  std::vector<RouterSelect> rules{
      {
          // default rule
          std::nullopt,                             // service
          std::nullopt,                             // target
          std::nullopt,                             // type
          std::nullopt,                             // ids
          {"tigraph", "yamaps", "linear-fallback"}  // routers
      },
      {
          std::nullopt,                             // service
          std::nullopt,                             // target
          std::nullopt,                             // type
          {{"yamapszone"}},                         // ids
          {"yamaps", "tigraph", "linear-fallback"}  // routers
      },
      {
          std::nullopt,                             // service
          std::nullopt,                             // target
          std::nullopt,                             // type
          {{"tigraphzone"}},                        // ids
          {"tigraph", "yamaps", "linear-fallback"}  // routers
      },
      {
          std::nullopt,                             // service
          std::nullopt,                             // target
          std::nullopt,                             // type
          {{"otherzone"}},                          // ids
          {"yamaps", "tigraph", "linear-fallback"}  // routers
      },
  };

  auto selector =
      std::make_unique<RouterSelectorTest>(CreateRouterConfig(rules), nullptr);

  selector->AddVendor("yamaps");
  selector->AddVendor("tigraph");
  selector->AddVendor("linear-fallback");

  return selector;
}

UTEST(RouterSelectorImpl, One) {
  using namespace std::string_literals;

  const auto selector = CreateSelector();

  // default router
  EXPECT_EQ("tigraph", selector->GetCarRouter().GetRouters()[0]);
  EXPECT_EQ("tigraph", selector->GetCarRouter("invalid_zone"s).GetRouters()[0]);

  // for zone_id
  EXPECT_EQ("tigraph", selector->GetCarRouter("tigraphzone"s).GetRouters()[0]);
  EXPECT_EQ("yamaps", selector->GetCarRouter("otherzone"s).GetRouters()[0]);
  EXPECT_EQ("yamaps", selector->GetCarRouter("yamapszone"s).GetRouters()[0]);
}

std::unique_ptr<RouterSelectorTest> CreateSelectorAgglomerationConfig() {
  using namespace std::string_literals;

  std::vector<RouterSelect> rules;

  // default rule
  rules.push_back(RouterSelect{
      std::nullopt,                             // service
      std::nullopt,                             // target
      std::nullopt,                             // type
      std::nullopt,                             // ids
      {"yamaps", "tigraph", "linear-fallback"}  // routers
  });

  rules.push_back(RouterSelect{
      "agglomeration_service"s,                                // service
      "agglomeration"s,                                        // target
      std::nullopt,                                            // type
      std::vector{"zone1"s, "zone2"s},                         // ids
      {"agglomeration1", "agglomeration2", "linear-fallback"}  // routers
  });

  rules.push_back(RouterSelect{
      "agglomeration_service",                                 // service
      "agglomeration"s,                                        // target
      std::nullopt,                                            // type
      std::nullopt,                                            // ids
      {"agglomeration2", "agglomeration1", "linear-fallback"}  // routers
  });

  rules.push_back(RouterSelect{
      std::nullopt,                             // service
      std::nullopt,                             // target
      std::nullopt,                             // type
      std::vector{"zone1"s, "zone2"s},          // ids
      {"tigraph", "yamaps", "linear-fallback"}  // routers
  });

  auto selector = std::make_unique<RouterSelectorTest>(
      CreateRouterConfig(rules), nullptr, "agglomeration_service");

  // for common usage
  selector->AddVendor("yamaps");
  selector->AddVendor("tigraph");
  selector->AddVendor("linear-fallback");

  // for agglomerations
  selector->AddVendor("agglomeration1");
  selector->AddVendor("agglomeration2");

  return selector;
}

UTEST(RouterSelectorImpl, Agglomerations) {
  using namespace std::string_literals;

  const auto& selector = CreateSelectorAgglomerationConfig();

  // default router
  EXPECT_EQ(
      "agglomeration2",
      selector->GetCarRouter(std::nullopt, "agglomeration"s).GetRouters()[0]);
  EXPECT_EQ("agglomeration2",
            selector->GetCarRouter("invalid_zone"s, "agglomeration"s)
                .GetRouters()[0]);

  // for id
  EXPECT_EQ("agglomeration1",
            selector->GetCarRouter("zone1"s, "agglomeration"s).GetRouters()[0]);
  EXPECT_EQ("agglomeration1",
            selector->GetCarRouter("zone2"s, "agglomeration"s).GetRouters()[0]);

  // for id without agglomeration
  EXPECT_EQ("tigraph", selector->GetCarRouter("zone1"s).GetRouters()[0]);
  EXPECT_EQ("tigraph", selector->GetCarRouter("zone2"s).GetRouters()[0]);
}

std::unique_ptr<RouterSelectorTest> CreateSelectorProdConfig() {
  using namespace std::string_literals;

  std::vector<RouterSelect> rules;

  // default rule
  rules.push_back(RouterSelect{
      std::nullopt,                  // service
      std::nullopt,                  // target
      std::nullopt,                  // type
      std::nullopt,                  // ids
      {"yamaps", "linear-fallback"}  // routers
  });

  rules.push_back(RouterSelect{
      "test_service"s,                          // service
      "calculator"s,                            // target
      std::nullopt,                             // type
      std::vector{"riga"s, "yurmala"s},         // ids
      {"tigraph", "yamaps", "linear-fallback"}  // routers
  });

  rules.push_back(RouterSelect{
      std::nullopt,                             // service
      std::nullopt,                             // target
      std::nullopt,                             // type
      std::vector{"riga"s, "yurmala"s},         // ids
      {"tigraph", "yamaps", "linear-fallback"}  // routers
  });

  auto selector = std::make_unique<RouterSelectorTest>(
      CreateRouterConfig(rules), nullptr, "test_service");

  // for common usage
  selector->AddVendor("yamaps");
  selector->AddVendor("tigraph");
  selector->AddVendor("linear-fallback");

  return selector;
}

UTEST(RouterSelectorImpl, Prod) {
  using namespace std::string_literals;

  const auto& selector = CreateSelectorProdConfig();

  // default router
  {
    const auto& router = selector->GetCarRouter();
    const auto& routers = router.GetRouters();
    EXPECT_EQ(2, routers.size());
    EXPECT_EQ("yamaps", routers[0]);
    EXPECT_EQ("linear-fallback", routers[1]);
  }
  {
    const auto& router = selector->GetCarRouter("moscow"s);
    const auto& routers = router.GetRouters();
    EXPECT_EQ(2, routers.size());
    EXPECT_EQ("yamaps", routers[0]);
    EXPECT_EQ("linear-fallback", routers[1]);
  }

  // default calculator
  {
    const auto& router = selector->GetCarRouter(std::nullopt, "calculator"s);
    const auto& routers = router.GetRouters();
    EXPECT_EQ(2, routers.size());
    EXPECT_EQ("yamaps", routers[0]);
    EXPECT_EQ("linear-fallback", routers[1]);
  }
  {
    const auto& router = selector->GetCarRouter("moscow"s, "calculator"s);
    const auto& routers = router.GetRouters();
    EXPECT_EQ(2, routers.size());
    EXPECT_EQ("yamaps", routers[0]);
    EXPECT_EQ("linear-fallback", routers[1]);
  }

  // calculator from config
  {
    const auto& router = selector->GetCarRouter("riga"s, "calculator"s);
    const auto& routers = router.GetRouters();
    EXPECT_EQ(3, routers.size());
    EXPECT_EQ("tigraph", routers[0]);
    EXPECT_EQ("yamaps", routers[1]);
    EXPECT_EQ("linear-fallback", routers[2]);
  }
  {
    const auto& router = selector->GetCarRouter("yurmala"s, "calculator"s);
    const auto& routers = router.GetRouters();
    EXPECT_EQ(3, routers.size());
    EXPECT_EQ("tigraph", routers[0]);
    EXPECT_EQ("yamaps", routers[1]);
    EXPECT_EQ("linear-fallback", routers[2]);
  }

  // router from config
  {
    const auto& router = selector->GetCarRouter("riga"s);
    const auto& routers = router.GetRouters();
    EXPECT_EQ(3, routers.size());
    EXPECT_EQ("tigraph", routers[0]);
    EXPECT_EQ("yamaps", routers[1]);
    EXPECT_EQ("linear-fallback", routers[2]);
  }
  {
    const auto& router = selector->GetCarRouter("yurmala"s);
    const auto& routers = router.GetRouters();
    EXPECT_EQ(3, routers.size());
    EXPECT_EQ("tigraph", routers[0]);
    EXPECT_EQ("yamaps", routers[1]);
    EXPECT_EQ("linear-fallback", routers[2]);
  }
}

std::unique_ptr<RouterSelectorTest> CreateConfigForFetchRouteTest() {
  using namespace std::string_literals;

  std::vector<RouterSelect> rules;

  // default rule
  rules.push_back(RouterSelect{
      std::nullopt,                                      // service
      std::nullopt,                                      // target
      std::nullopt,                                      // type
      std::nullopt,                                      // ids
      {"tigraph", "always-throwing", "linear-fallback"}  // routers
  });
  rules.push_back(RouterSelect{
      std::nullopt,                                      // service
      std::nullopt,                                      // target
      std::nullopt,                                      // type
      std::vector{"riga"s},                              // ids
      {"always-throwing", "tigraph", "linear-fallback"}  // routers
  });
  rules.push_back(RouterSelect{
      std::nullopt,             // service
      std::nullopt,             // target
      std::nullopt,             // type
      std::vector{"yurmala"s},  // ids
      {"always-throwing"}       // routers
  });

  auto selector = std::make_unique<RouterSelectorTest>(
      CreateRouterConfig(rules), nullptr, "test_service");

  selector->AddAlwaysThrowingRouter("always-throwing");
  selector->AddVendor("tigraph");
  selector->AddVendor("linear-fallback");

  return selector;
}

UTEST(RouterSelectorImpl, FetchRouteWithFallback) {
  using namespace std::string_literals;
  using namespace geometry::literals;

  const auto& selector = CreateConfigForFetchRouteTest();
  const Path path = {{37.0_lon, 55.0_lat}, {37.1_lon, 55.1_lat}};
  const DirectionOpt direction(std::in_place,
                               geometry::Azimuth::from_value(0.0));
  const RouterSettings settings;
  const ExecutionSettings execution_settings_parallel = {
      ExecutionSettings::Algorithm::kFirstSuitableWithParallelFallbacks};

  {
    const auto& router = selector->GetCarRouter();
    // should use "tigraph" router and pass, not "always-throwing" router
    EXPECT_NO_THROW(router.FetchRoutePath(path, direction, settings));
  }
  {
    clients::routing::RouterQuery router = selector->GetCarRouter();
    // should use "tigraph" router and catch exception from "always-throwing"
    // router
    EXPECT_NO_THROW(router.FetchRoutePath(path, direction, settings, {},
                                          execution_settings_parallel));
  }

  {
    const auto& router = selector->GetCarRouter("riga"s);
    // now "always-throwing" router is first, should catch exception
    EXPECT_THROW(router.FetchRoutePath(path, direction, settings),
                 clients::http::HttpException);
  }
  {
    clients::routing::RouterQuery router = selector->GetCarRouter("riga"s);
    // now "always-throwing" router is first, should catch exception, then
    // return result of normal router
    EXPECT_NO_THROW(router.FetchRoutePath(path, direction, settings, {},
                                          execution_settings_parallel));
  }

  {
    const auto& router = selector->GetCarRouter("riga"s);
    // now "always-throwing" router is first, should catch exception
    EXPECT_THROW(router.FetchRouteInfo(path, direction, settings),
                 clients::http::HttpException);
  }
  {
    clients::routing::RouterQuery router = selector->GetCarRouter("riga"s);
    // now "always-throwing" router is first, but should use
    // FetchRoutePathWithParallelFallback
    EXPECT_NO_THROW(router.FetchRouteInfo(path, direction, settings, {},
                                          execution_settings_parallel));
  }

  {
    const auto& router = selector->GetCarRouter("riga"s);
    // but now should use "tigraph" as fallback and don't throw
    EXPECT_NO_THROW(
        router.FetchRoutePathWithParallelFallback(path, direction, settings));
  }
  {
    const auto& router = selector->GetCarRouter("riga"s);
    // and now should use "tigraph" as fallback and don't throw
    EXPECT_NO_THROW(
        router.FetchRouteInfoWithParallelFallback(path, direction, settings));
  }
  {
    const auto& router = selector->GetCarRouter("yurmala"s);
    // now there is no fallback router, only "always-throwing" one
    EXPECT_THROW(
        router.FetchRoutePathWithParallelFallback(path, direction, settings),
        clients::http::HttpException);
  }
}

UTEST(RouterSelectorImpl, FetchRouteUserSelect) {
  using namespace std::string_literals;
  using namespace geometry::literals;

  const auto& selector = CreateConfigForFetchRouteTest();
  const Path path = {{37.0_lon, 55.0_lat}, {37.1_lon, 55.1_lat}};
  const DirectionOpt direction(std::in_place,
                               geometry::Azimuth::from_value(0.0));
  const RouterSettings settings;
  const ExecutionSettings execution_settings_user_select = {
      ExecutionSettings::Algorithm::kUserSelect};

  {
    clients::routing::RouterQuery router = selector->GetCarRouter();
    // should use "tigraph" router and catch exception from "always-throwing"
    // router
    EXPECT_NO_THROW(router.FetchRoutePath(path, direction, settings, {},
                                          execution_settings_user_select));
  }
  {
    clients::routing::RouterQuery router = selector->GetCarRouter("riga"s);
    // now "always-throwing" router is first, should catch exception, then
    // return result of normal router
    EXPECT_NO_THROW(router.FetchRoutePath(path, direction, settings, {},
                                          execution_settings_user_select));
  }
  {
    const auto& router = selector->GetCarRouter("yurmala"s);
    // now there is no fallback router, only "always-throwing" one
    EXPECT_THROW(
        router.FetchRoutePathWithParallelFallback(path, direction, settings),
        clients::http::HttpException);
  }
}

std::unique_ptr<RouterSelectorTest> CreatePerTypeSelector() {
  using namespace std::string_literals;
  namespace trs = taxi_config::router_select;
  using RuleType = trs::RuleType;
  std::vector<RouterSelect> rules{{
      RouterSelect{
          // default rule
          "per_type_test_tvm"s,  // service
          std::nullopt,          // target
          RuleType::kCar,        // type
          std::nullopt,          // ids
          {"A", "a", "B", "C"}   // routers
      },
      RouterSelect{
          "per_type_test_tvm"s,    // service
          std::nullopt,            // target
          RuleType::kMasstransit,  // type
          std::nullopt,            // ids
          {"X", "a", "B", "C"}     // routers
      },
      RouterSelect{
          "per_type_test_tvm"s,   // service
          std::nullopt,           // target
          RuleType::kPedestrian,  // type
          std::nullopt,           // ids
          {"Y", "B", "C"}         // routers
      },
      RouterSelect{
          "per_type_test_tvm"s,  // service
          std::nullopt,          // target
          RuleType::kBicycle,    // type
          std::nullopt,          // ids
          {"Z", "B", "C"}        // routers
      },
  }};

  auto selector = std::make_unique<RouterSelectorTest>(
      CreateRouterConfig(rules), nullptr, "per_type_test_tvm");

  selector->AddVendor("A");
  selector->AddVendor("B");
  selector->AddVendor("C");
  selector->AddVendor("X");
  selector->AddVendor("X");
  selector->AddVendor("Y");
  selector->AddVendor("Z");

  return selector;
}

UTEST(RouterSelectorImpl, AlliasTest) {
  using namespace std::string_literals;

  const auto selector = CreatePerTypeSelector();
  selector->AddVendor("A");
  selector->AddVendorAlias("A", "a");

  EXPECT_EQ(selector->GetRouterQuery(RouterVehicleType::kVehicleCar)
                .GetRouters()
                .size(),
            3);
  EXPECT_EQ(
      "A",
      selector->GetRouterQuery(RouterVehicleType::kVehicleCar).GetRouters()[0]);
  EXPECT_EQ(
      "B",
      selector->GetRouterQuery(RouterVehicleType::kVehicleCar).GetRouters()[1]);
  EXPECT_EQ(
      "C",
      selector->GetRouterQuery(RouterVehicleType::kVehicleCar).GetRouters()[2]);

  EXPECT_EQ(selector->GetRouterQuery(RouterVehicleType::kVehicleMasstransit)
                .GetRouters()
                .size(),
            4);
  EXPECT_EQ("X",
            selector->GetRouterQuery(RouterVehicleType::kVehicleMasstransit)
                .GetRouters()[0]);
  EXPECT_EQ("A",
            selector->GetRouterQuery(RouterVehicleType::kVehicleMasstransit)
                .GetRouters()[1]);
  EXPECT_EQ("B",
            selector->GetRouterQuery(RouterVehicleType::kVehicleMasstransit)
                .GetRouters()[2]);
  EXPECT_EQ("C",
            selector->GetRouterQuery(RouterVehicleType::kVehicleMasstransit)
                .GetRouters()[3]);

  EXPECT_EQ("Y", selector->GetRouterQuery(RouterVehicleType::kVehiclePedestrian)
                     .GetRouters()[0]);

  EXPECT_EQ("Z", selector->GetRouterQuery(RouterVehicleType::kVehicleBicycle)
                     .GetRouters()[0]);
}

}  // namespace clients::routing
