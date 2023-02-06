#include <plugins/common/registry.hpp>

#include <gtest/gtest.h>

namespace {

namespace plugins = routestats::plugins::common;

struct TestPluginA : public plugins::PluginBase {
  std::string Name() const override { return "A"; }
};

}  // namespace

TEST(TestRegistry, Basic) {
  plugins::Registry<plugins::PluginBase> registry;
  ASSERT_TRUE(registry.GetRegisteredPlugins().empty());

  const auto plugin = std::make_shared<TestPluginA>();
  registry.RegisterPlugin(plugin);
  const auto registered_plugins = registry.GetRegisteredPlugins();
  ASSERT_EQ(static_cast<size_t>(1), registered_plugins.size());
  ASSERT_EQ("A", registered_plugins[0]->Name());

  ASSERT_TRUE(registry.HasPlugin("A"));
  ASSERT_FALSE(registry.HasPlugin("B"));
}

TEST(TestRegistry, CheckAlreadyRegistered) {
  plugins::Registry<plugins::PluginBase> registry;
  const auto plugin = std::make_shared<TestPluginA>();
  registry.RegisterPlugin(plugin);

  ASSERT_THROW(registry.RegisterPlugin(plugin), plugins::RegistryException);
}
