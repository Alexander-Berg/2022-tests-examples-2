#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include <config/stq_agent_cluster_settings.hpp>

namespace {
using config::StqAgentClusterSettings;

TEST(TestStqAgentClusterSettings, ConfigValue) {
  const auto config_str = R"({
	  "stq-agent": {
	    "tvm_name": "stq-agent",
	    "url": "http://stq-agent.taxi.tst.yandex.net"
	  },
	  "stq-agent-taxi-critical": {
	    "queues_in_process_of_cluster_switching": {
		"test_queue": {
			"percent": 50
		},
		"test_queue_2": {
			"percent": 20
		}
	    },
	    "tvm_name": "stq-agent-taxi-critical",
	    "url": "http://stq-agent-taxi-critical.taxi.tst.yandex.net"
	  }
  })";

  auto docs_map = config::DocsMapForTest();
  docs_map.Override("STQ_AGENT_CLUSTER_SETTINGS", mongo::fromjson(config_str));
  const auto& config = config::Config(docs_map);
  const auto& cfg = config.Get<config::StqAgentClusterSettings>();

  auto& val_map = cfg.cluster_settings_map;
  ASSERT_EQ(val_map.at("stq-agent").tvm_name, "stq-agent");
  ASSERT_EQ(val_map.at("stq-agent").url,
            "http://stq-agent.taxi.tst.yandex.net");
  ASSERT_EQ(val_map.at("stq-agent-taxi-critical").tvm_name,
            "stq-agent-taxi-critical");
  ASSERT_EQ(val_map.at("stq-agent-taxi-critical").url,
            "http://stq-agent-taxi-critical.taxi.tst.yandex.net");
  auto& queues_percent_map = *(val_map.at("stq-agent-taxi-critical")
                                   .queues_in_process_of_cluster_switching);
  ASSERT_EQ(queues_percent_map.at("test_queue").percent, 50);
  ASSERT_EQ(queues_percent_map.at("test_queue_2").percent, 20);
}

}  // namespace
