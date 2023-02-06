#include <plugins/common/runner.hpp>

#include <userver/utest/utest.hpp>

namespace {

namespace plugins = routestats::plugins::common;
using plugins::PluginsVec;

struct TestContext {
  size_t called_times = 0;
};

struct Result {
  size_t from_plugin_id;
};

static const std::string kHookName = "process something";
static const std::string kVoidHookName = "process something void";

struct TestPluginBase : public plugins::PluginBase {
  virtual Result OnProcessSomething(TestContext& ctx) = 0;
  virtual void OnProcessSomethingVoid(TestContext& ctx) = 0;
};

struct TestPlugin : public TestPluginBase {
  TestPlugin(size_t id = 0) : id{id} {}
  std::string Name() const override { return std::to_string(id); }
  Result OnProcessSomething(TestContext& ctx) override {
    ++ctx.called_times;
    return {id};
  }

  void OnProcessSomethingVoid(TestContext& ctx) override { ++ctx.called_times; }

  size_t id;
};

struct ThrowingPlugin : public TestPluginBase {
  ThrowingPlugin(size_t id = 0, bool need_throw = true)
      : id{id}, need_throw{need_throw} {}
  std::string Name() const override { return std::to_string(id); }
  Result OnProcessSomething(TestContext&) override {
    if (need_throw) throw std::runtime_error("test exceptions");
    return Result{id};
  }

  void OnProcessSomethingVoid(TestContext&) override {}

  size_t id;
  bool need_throw;
};

struct OptionalReturnPlugin : public ThrowingPlugin {
  OptionalReturnPlugin(const std::optional<std::string>& title, size_t id = 0,
                       bool need_throw = true)
      : ThrowingPlugin(id, need_throw), title_(title) {}

  std::optional<std::string> GetTitle() const {
    if (need_throw) throw std::runtime_error("test exceptions");
    return title_;
  }

  std::optional<std::string> title_;
};

}  // namespace

UTEST(TestRun, VoidResultHandler) {
  PluginsVec<TestPluginBase> plugins{std::make_shared<TestPlugin>()};

  TestContext ctx;
  const auto results = plugins::Runner{}.Run(
      plugins, kVoidHookName, &TestPluginBase::OnProcessSomethingVoid, ctx);
  ASSERT_EQ(plugins.size(), results.size());
  ASSERT_EQ(plugins.size(), ctx.called_times);
}

UTEST(TestRun, ResultsAreOrdered) {
  PluginsVec<TestPluginBase> plugins{
      std::make_shared<TestPlugin>(0),
      std::make_shared<TestPlugin>(1),
      std::make_shared<TestPlugin>(2),
      std::make_shared<TestPlugin>(3),
  };

  TestContext ctx;
  const auto results = plugins::Runner{}.Run(
      plugins, kHookName, &TestPluginBase::OnProcessSomething, ctx);
  ASSERT_EQ(plugins.size(), results.size());
  ASSERT_EQ(plugins.size(), ctx.called_times);
  for (size_t i = 0; i < plugins.size(); ++i)
    ASSERT_EQ(i, results[i]->from_plugin_id);
}

UTEST(TestRun, EmptyPluginList) {
  PluginsVec<TestPluginBase> plugins;

  TestContext ctx;
  const auto results = plugins::Runner{}.Run(
      plugins, kHookName, &TestPluginBase::OnProcessSomething, ctx);
  ASSERT_TRUE(results.empty());
  ASSERT_EQ(plugins.size(), ctx.called_times);
}

UTEST(TestRun, Exceptions) {
  PluginsVec<TestPluginBase> plugins{std::make_shared<ThrowingPlugin>()};

  TestContext ctx;
  const auto results = plugins::Runner{}.Run(
      plugins, kHookName, &TestPluginBase::OnProcessSomething, ctx);
  ASSERT_FALSE(results[0].has_value());
}

UTEST(TestRun, OptionalReturn) {
  std::vector<std::shared_ptr<OptionalReturnPlugin>> plugins{
      std::make_shared<OptionalReturnPlugin>(std::nullopt, 0, false),
      std::make_shared<OptionalReturnPlugin>(std::nullopt, 1, true),
      std::make_shared<OptionalReturnPlugin>("title1", 2, true),
      std::make_shared<OptionalReturnPlugin>("title2", 3, false),
  };
  plugins::Runner runner;

  std::vector<std::optional<std::string>> first_results =
      runner.Run(plugins, "get_title", &OptionalReturnPlugin::GetTitle);

  // results from every plugin
  ASSERT_EQ(4, first_results.size());

  // 2 plugins has failed, filter it
  ASSERT_EQ(2, plugins.size());

  std::vector<std::string> filtered =
      plugins::FilterOutFailedOrEmptyRuns(first_results);
  ASSERT_EQ(filtered.size(), 1);
  ASSERT_EQ(filtered[0], "title2");
}

UTEST(TestRun, FailedPluginsAreDisabled) {
  constexpr bool kNeedThrow = true;
  std::vector<std::shared_ptr<TestPluginBase>> plugins{
      std::make_shared<ThrowingPlugin>(0, kNeedThrow),
      std::make_shared<ThrowingPlugin>(1, !kNeedThrow),
      std::make_shared<ThrowingPlugin>(2, kNeedThrow),
      std::make_shared<ThrowingPlugin>(3, !kNeedThrow),
  };
  plugins::Runner runner;
  TestContext ctx;

  // Run first time.
  const auto first_results =
      runner.Run(plugins, kHookName, &TestPluginBase::OnProcessSomething, ctx);
  ASSERT_EQ(4, first_results.size());
  ASSERT_EQ(2, plugins.size());

  ASSERT_FALSE(first_results[0].has_value());
  ASSERT_TRUE(first_results[1].has_value());
  ASSERT_FALSE(first_results[2].has_value());
  ASSERT_TRUE(first_results[3].has_value());

  // Run second time another hook and check that failed in the first run
  // plugins were disabled.
  const auto second_results = runner.Run(
      plugins, kVoidHookName, &TestPluginBase::OnProcessSomethingVoid, ctx);
  ASSERT_EQ(2, second_results.size());
  ASSERT_EQ(2, plugins.size());

  ASSERT_TRUE(second_results[0].has_value());
  ASSERT_TRUE(second_results[1].has_value());
}
