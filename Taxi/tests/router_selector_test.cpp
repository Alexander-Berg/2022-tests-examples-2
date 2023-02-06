#include <clients/router_selector.hpp>

#include <gtest/gtest.h>

#include <clients/graphite.hpp>
#include <clients/router_fallback.hpp>
#include <clients/router_here.hpp>
#include <clients/router_tigraph.hpp>
#include <clients/router_yamaps.hpp>
#include <common/test_config.hpp>
#include <config/config.hpp>
#include <models/driver_experiments.hpp>
#include <threads/async.hpp>
#include <utils/limit_keeper.hpp>

namespace {

const std::string kBaseUrl = "http://route.cit.api.here.com";
const std::string kAppId = "unit";
const std::string kAppCode = "test";

using clients::routing::RouterFallback;
using clients::routing::RouterHere;
using clients::routing::RouterSelector;
using clients::routing::RouterTiGraph;
using clients::routing::RouterYaMaps;
using clients::routing::RouterYaMapsTaxi;
using clients::routing::Target;

const clients::Graphite& graphite() {
  static const clients::Graphite client;
  return client;
}

const utils::http::Client& http_client() {
  static utils::Async async(2, "xx", false);
  static const utils::http::Client client(async, 1, "test_http_client", false);
  return client;
}

config::Config CreateConfig() {
  const std::map<std::string, std::vector<std::string>> order_by_zone = {
      {"__default__",
       {RouterTiGraph::name, RouterYaMaps::name, RouterHere::name,
        RouterFallback::name}},
      {"herezone",
       {RouterHere::name, RouterTiGraph::name, RouterYaMaps::name,
        RouterFallback::name}},
      {"yamapszone",
       {RouterYaMaps::name, RouterTiGraph::name, RouterHere::name,
        RouterFallback::name}},
      {"yamapstaxizone",
       {RouterYaMapsTaxi::name, RouterYaMaps::name, RouterTiGraph::name,
        RouterHere::name, RouterFallback::name}},
      {"router_yamaps:",
       {RouterYaMaps::name, RouterTiGraph::name, RouterHere::name,
        RouterFallback::name}},
      {"router_yamaps_taxi:",
       {RouterYaMapsTaxi::name, RouterYaMaps::name, RouterTiGraph::name,
        RouterHere::name, RouterFallback::name}},
      {"router_here:",
       {RouterHere::name, RouterTiGraph::name, RouterYaMaps::name,
        RouterFallback::name}},
      {"router_tigraph:",
       {RouterTiGraph::name, RouterYaMaps::name, RouterHere::name,
        RouterYaMapsTaxi::name, RouterFallback::name}},
      {"router_here_otherzone:otherzone",
       {RouterHere::name, RouterTiGraph::name, RouterYaMapsTaxi::name,
        RouterYaMaps::name, RouterFallback::name}},
      {"router_yamaps_otherzone:otherzone",
       {RouterYaMaps::name, RouterYaMapsTaxi::name, RouterTiGraph::name,
        RouterHere::name, RouterFallback::name}},
      {"router_yamaps_taxi_otherzone:otherzone",
       {RouterYaMapsTaxi::name, RouterYaMaps::name, RouterTiGraph::name,
        RouterHere::name, RouterFallback::name}}};

  config::DocsMap docs_map = config::DocsMapForTest();
  docs_map.Override("ROUTER_ORDER_BY_ZONE", order_by_zone);
  docs_map.Override("ROUTER_TIGRAPH_ENABLED", true);
  return config::Config(docs_map);
}

}  // namespace

TEST(RouterSelector, One) {
  const RouterHere here_router(http_client(), graphite(), "test", "test",
                               "test", "test");
  const RouterTiGraph tigraph_router(http_client(), graphite(), "test");
  const RouterYaMaps yamaps_router(http_client(), graphite(), "test");
  const RouterYaMapsTaxi yamaps_taxi_router(http_client(), graphite(), "test");
  const RouterFallback fallback_router;

  const RouterSelector selector(here_router, tigraph_router, yamaps_router,
                                yamaps_taxi_router, fallback_router);

  const config::Config& config = CreateConfig();

  // non user
  EXPECT_EQ(
      RouterTiGraph::name,
      selector.GetNonUser(Target::kCommon, config, "otherzone").GetName());
  EXPECT_EQ(RouterHere::name,
            selector.GetNonUser(Target::kCommon, config, "herezone").GetName());
  EXPECT_EQ(
      RouterYaMaps::name,
      selector.GetNonUser(Target::kCommon, config, "yamapszone").GetName());
  EXPECT_EQ(
      RouterYaMapsTaxi::name,
      selector.GetNonUser(Target::kCommon, config, "yamapstaxizone").GetName());

  // with experiment
  EXPECT_EQ(
      RouterTiGraph::name,
      selector.Get(Target::kCommon, config, "otherzone", {"any_experiment"})
          .GetName());
  EXPECT_EQ(
      RouterHere::name,
      selector.Get(Target::kCommon, config, "herezone", {"any_experiment"})
          .GetName());
  EXPECT_EQ(
      RouterYaMaps::name,
      selector.Get(Target::kCommon, config, "yamapszone", {"any_experiment"})
          .GetName());
  EXPECT_EQ(
      RouterYaMapsTaxi::name,
      selector
          .Get(Target::kCommon, config, "yamapstaxizone", {"any_experiment"})
          .GetName());
}

TEST(RouterSelector, Experiments) {
  const RouterHere here_router(http_client(), graphite(), "test", "test",
                               "test", "test");
  const RouterTiGraph tigraph_router(http_client(), graphite(), "test");
  const RouterYaMaps yamaps_router(http_client(), graphite(), "test");
  const RouterYaMapsTaxi yamaps_taxi_router(http_client(), graphite(), "test");
  const RouterFallback fallback_router;

  const RouterSelector selector(here_router, tigraph_router, yamaps_router,
                                yamaps_taxi_router, fallback_router);

  const config::Config& config = CreateConfig();

  // base
  EXPECT_EQ(
      RouterTiGraph::name,
      selector.Get(Target::kCommon, config, "otherzone", {"any_experiment"})
          .GetName());

  // all
  EXPECT_EQ(RouterYaMaps::name, selector
                                    .Get(Target::kCommon, config, "otherzone",
                                         {"router_yamaps", "any_experiment"})
                                    .GetName());
  EXPECT_EQ(RouterYaMapsTaxi::name,
            selector
                .Get(Target::kCommon, config, "otherzone",
                     {"router_yamaps_taxi", "any_experiment"})
                .GetName());
  EXPECT_EQ(RouterHere::name, selector
                                  .Get(Target::kCommon, config, "otherzone",
                                       {"router_here", "any_experiment"})
                                  .GetName());
  EXPECT_EQ(RouterTiGraph::name, selector
                                     .Get(Target::kCommon, config, "otherzone",
                                          {"router_tigraph", "any_experiment"})
                                     .GetName());

  // zone
  EXPECT_EQ(RouterTiGraph::name,
            selector
                .Get(Target::kCommon, config, "otherzone",
                     {"router_here_yamapszone", "any_experiment"})
                .GetName());
  EXPECT_EQ(RouterHere::name,
            selector
                .Get(Target::kCommon, config, "otherzone",
                     {"router_here_otherzone", "any_experiment"})
                .GetName());

  // priority
  EXPECT_EQ(
      RouterYaMaps::name,
      selector
          .Get(Target::kCommon, config, "otherzone",
               {"router_here", "router_yamaps_otherzone", "any_experiment"})
          .GetName());
}

TEST(RouterSelector, Limits) {
  const RouterHere here_router(http_client(), graphite(), "test", "test",
                               "test", "test");
  const RouterTiGraph tigraph_router(http_client(), graphite(), "test");
  const RouterYaMaps yamaps_router(http_client(), graphite(), "test");
  const RouterYaMapsTaxi yamaps_taxi_router(http_client(), graphite(), "test");
  const RouterFallback fallback_router;

  RouterSelector selector(here_router, tigraph_router, yamaps_router,
                          yamaps_taxi_router, fallback_router);
  utils::LimitCounter here_counter;
  here_counter.limit = 2u;
  selector.SetHereCounter(&here_counter);

  const config::Config& config = CreateConfig();

  utils::LimitKeeper first_keeper;
  const auto& first_router = selector.Get(Target::kCommon, config, "herezone",
                                          {}, first_keeper, true, {});
  EXPECT_EQ(RouterHere::name, first_router.GetName());
  {
    utils::LimitKeeper second_keeper;
    const auto& second_router = selector.Get(
        Target::kCommon, config, "herezone", {}, second_keeper, true, {});
    EXPECT_EQ(RouterHere::name, second_router.GetName());
    utils::LimitKeeper third_keeper;
    const auto& third_router = selector.Get(Target::kCommon, config, "herezone",
                                            {}, third_keeper, true, {});
    EXPECT_EQ(RouterTiGraph::name, third_router.GetName());
  }
  utils::LimitKeeper fourth_keeper;
  const auto& fourth_router = selector.Get(Target::kCommon, config, "herezone",
                                           {}, fourth_keeper, true, {});
  EXPECT_EQ(RouterHere::name, fourth_router.GetName());

  // test when here router captured in the same thread
  EXPECT_EQ(RouterHere::name, selector
                                  .Get(Target::kCommon, config, "herezone", {},
                                       fourth_keeper, true, {})
                                  .GetName());
  EXPECT_EQ(RouterHere::name, selector
                                  .Get(Target::kCommon, config, "herezone", {},
                                       fourth_keeper, true, {})
                                  .GetName());

  utils::LimitKeeper overlimit_keeper;
  const auto& switch_to_fallback_router = selector.Get(
      Target::kCommon, config, "herezone", {}, overlimit_keeper, true, {});
  EXPECT_EQ(RouterTiGraph::name, switch_to_fallback_router.GetName());

  utils::LimitKeeper dummy_keeper;
  const auto& without_limit_router = selector.Get(
      Target::kCommon, config, "yamapszone", {}, dummy_keeper, true, {});
  EXPECT_EQ(RouterYaMaps::name, without_limit_router.GetName());
}
