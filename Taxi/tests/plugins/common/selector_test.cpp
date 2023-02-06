#include <plugins/common/selector.hpp>

#include <gtest/gtest.h>

namespace {

namespace plugins = routestats::plugins::common;

using ExpResult = experiments3::models::ExperimentResult;
using Configs = experiments3::models::ClientsCache::MappedData;

ExpResult MockExp(const std::string& name, const formats::json::Value& val) {
  return ExpResult{name, val, {}};
}

struct TestPluginBase : public plugins::PluginBase {
  virtual void Handle() = 0;
};

struct TestPluginA : public TestPluginBase {
  std::string Name() const override { return "a"; }
  void Handle() override {}
};

struct TestPluginB : public TestPluginBase {
  std::string Name() const override { return "b"; }
  void Handle() override {}
};

}  // namespace

TEST(TestSelector, Basic) {
  plugins::Registry<TestPluginBase> registry;
  const auto plugin_a = std::make_shared<TestPluginA>();
  registry.RegisterPlugin(plugin_a);
  const auto plugin_b = std::make_shared<TestPluginB>();
  registry.RegisterPlugin(plugin_b);

  plugins::Selector<TestPluginBase> selector{"routestats:uservices", registry};

  formats::json::ValueBuilder config_json_builder;
  config_json_builder["enabled"] = true;

  Configs configs;
  configs["routestats:uservices:plugins:b"] = MockExp(
      "routestats:uservices:plugins:b", config_json_builder.ExtractValue());

  const auto plugins = selector.GetEnabledPlugins(configs);

  ASSERT_EQ(1, plugins.size());
  ASSERT_EQ(plugin_b->Name(), plugins[0]->Name());
}

TEST(TestSelector, AlwaysEnable) {
  plugins::Registry<TestPluginBase> registry;
  registry.RegisterPlugin(std::make_shared<TestPluginA>());
  registry.RegisterPlugin(std::make_shared<TestPluginB>());

  plugins::Selector<TestPluginBase> selector{"routestats:uservices", registry};
  selector.AlwaysEnablePlugin("a");

  Configs configs;
  configs["routestats:uservices:plugins:b"] =
      MockExp("routestats:uservices:plugins:b", {});

  const auto plugins = selector.GetEnabledPlugins(configs);

  ASSERT_EQ(1, plugins.size());
  ASSERT_EQ("a", plugins[0]->Name());
}
