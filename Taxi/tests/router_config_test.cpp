#include <clients/router_config.hpp>

#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>

TEST(RouterConfig, Ping) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);

  ASSERT_NO_THROW(config.Get<config::Router>());
}

namespace {

class RouterConfigOrderByZoneMapParams
    : public testing::Test,
      public testing::WithParamInterface<
          std::tuple<std::string, std::string, std::string>> {
 public:
  static void SetUpTestCase() {
    auto docs_map = config::DocsMapForTest();

    const std::map<std::string, std::vector<std::string>> order_by_zone = {
        {"__default__", {"0"}},
        {"msk", {"1"}},
        {"tula,omsk", {"2"}},
        {"calculator::__default__", {"3"}},
        {"calculator::spb,riga", {"4"}},
    };
    docs_map.Override("ROUTER_ORDER_BY_ZONE", order_by_zone);

    config_s = std::make_unique<config::Config>(docs_map);
  }

  static void TearDownTestCase() { config_s.reset(); }

 protected:
  static std::unique_ptr<config::Config> config_s;
};

std::unique_ptr<config::Config> RouterConfigOrderByZoneMapParams::config_s;

}  // namespace

TEST_P(RouterConfigOrderByZoneMapParams, Check) {
  const auto& result = std::get<0>(GetParam());
  const auto& target = std::get<1>(GetParam());
  const auto& zone = std::get<2>(GetParam());
  const auto& order_by_zone = config_s->Get<config::Router>().order_by_zone;

  const auto& res = order_by_zone.Get(target, {}, zone);
  EXPECT_EQ(std::vector<std::string>{{result}}, res);
}

INSTANTIATE_TEST_CASE_P(
    Serial, RouterConfigOrderByZoneMapParams,
    testing::Values(std::make_tuple("0", "hello", "world"),
                    std::make_tuple("0", "", ""),
                    std::make_tuple("1", "", "msk"),
                    std::make_tuple("2", "", "omsk"),
                    std::make_tuple("2", "", "tula"),
                    std::make_tuple("3", "calculator", ""),
                    std::make_tuple("4", "calculator", "spb"),
                    std::make_tuple("4", "calculator", "riga")), );

TEST(PedestrianRouterConfig, Ping) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);

  ASSERT_NO_THROW(config.Get<config::PedestrianRouter>());
}
