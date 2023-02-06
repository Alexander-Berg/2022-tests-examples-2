#include "registry.hpp"

#include <gtest/gtest.h>

struct TestContext {};

enum TestPluginHook {
  Main,
};

struct TestPluginMeta {
  using ContextType = TestContext;
  using HookType = TestPluginHook;
};

struct TestPluginA : public common::plugins::PluginBase<TestPluginMeta> {
  std::string Name() const override { return "A"; }
  void Handle(TestPluginHook, const TestContext&) override {}
  void HandleFallback(TestPluginHook, const TestContext&,
                      const std::exception&) const override {}
};

TEST(TestRegistry, Simple) {
  common::plugins::Registry<TestPluginMeta> registry;
  EXPECT_TRUE(registry.GetRegisteredPlugins().empty());

  registry.RegisterPlugin(std::make_shared<TestPluginA>());
  const auto registered_plugins = registry.GetRegisteredPlugins();
  EXPECT_EQ(static_cast<size_t>(1), registered_plugins.size());
  EXPECT_EQ("A", registered_plugins[0]->Name());
}

TEST(TestRegistry, CheckAlreadyRegistered) {
  common::plugins::Registry<TestPluginMeta> registry;
  registry.RegisterPlugin(std::make_shared<TestPluginA>());

  EXPECT_THROW(registry.RegisterPlugin(std::make_shared<TestPluginA>()),
               common::plugins::BasePluginException);
}
