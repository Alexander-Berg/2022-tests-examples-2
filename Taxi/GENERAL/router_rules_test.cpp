#include <userver/utest/utest.hpp>

#include <taxi_config/taxi_config.hpp>
#include <userver/utils/rand.hpp>

#include <base-proxy/http_request.hpp>
#include <base-proxy/router_rule.hpp>

#include <router_rules.hpp>

using taxi_config::driver_authproxy_route_rules::Rule;

class RandomMock : public utils::RandomBase {
 public:
  RandomMock(uint32_t return_val) : return_val_{return_val} {}
  uint32_t operator()() override { return return_val_; }

 private:
  uint32_t return_val_;
};

TEST(TestGetRouterRule, TestProbabilityDistribution) {
  base_proxy::HttpRequest request{};
  request.path_query = "prefix";

  Rule r0{};
  r0.proxy.probability_percent = 0;
  r0.output.upstream = "r0";

  Rule r1{};
  r1.proxy.probability_percent = 42;
  r1.output.upstream = "r1";

  Rule r2{};
  r2.proxy.probability_percent = 10;
  r2.output.upstream = "r2";

  Rule r3{};
  r3.proxy.probability_percent = 1;
  r3.output.upstream = "r3";

  std::vector<Rule> rules{r0, r1, r2, r3};
  for (auto& r : rules) {
    r.input.http_path_prefix = request.path_query;
    r.proxy.server_hosts.push_back("*");
  }

  Rule r_another_prefix{};
  r_another_prefix.input.http_path_prefix = "another_prefix";
  r_another_prefix.proxy.server_hosts.push_back("*");
  r_another_prefix.proxy.probability_percent = 100;
  r_another_prefix.output.upstream = "r_another_prefix";
  rules.push_back(r_another_prefix);

  std::unordered_map<std::string, uint> rules_distribution{};
  for (uint i = 1234; i < 1234 + 100; ++i) {
    auto rng = RandomMock(i);
    const auto& selected_rule =
        driver_authproxy::GetRouterRule(request, rules, &rng);
    ++rules_distribution[selected_rule.to];
  }

  EXPECT_EQ(rules_distribution["r0"], 0);
  EXPECT_EQ(rules_distribution["r1"], 42);
  EXPECT_EQ(rules_distribution["r2"], 10);
  EXPECT_EQ(rules_distribution["r3"], 100 - 42 - 10);  // Added up to 100

  EXPECT_EQ(rules_distribution["r_another_prefix"], 0);
}
