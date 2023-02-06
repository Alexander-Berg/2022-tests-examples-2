
#include <set>

#include <userver/utest/utest.hpp>

#include <testing/taxi_config.hpp>
#include <userver/cache/caching_component_base.hpp>

#include <candidates/filters/meta_factory.hpp>
#include <candidates/filters/self_diagnostics.hpp>
#include <candidates/filters/test/dummy.hpp>

namespace cf = candidates::filters;
using FilterConfigs = candidates::models::FilterConfigs;

namespace {

auto CreateEnvironment() {
  return candidates::Environment{dynamic_config::GetDefaultSnapshot()};
}

auto CreateFilter(const cf::FilterInfo& info) {
  return std::make_unique<cf::test::AllowAll>(info);
}

auto CreateFactory(const cf::FilterInfo& info) {
  return std::make_shared<cf::test::DummyFactory<cf::test::AllowAll>>(info);
}

auto CreateMetaFactory(
    std::initializer_list<std::shared_ptr<cf::Factory>> factories,
    cf::Statistics& stats) {
  return cf::MetaFactory(
      factories, []() { return cf::SelfDiagnosticsData{}; }, stats);
}

auto GetNames(const std::vector<std::unique_ptr<cf::Filter>>& filters) {
  std::set<std::string> names;
  for (const auto& filter : filters) names.insert(filter->name());
  return names;
}

auto MakeSet(std::set<std::string> names) { return names; }

}  // namespace

TEST(FilterMetaFactory, CustomMap) {
  cf::Statistics stats;
  cf::FilterInfo filter_info{"f1", {}, {}, false, {}};
  formats::json::Value params;
  const auto& env = CreateEnvironment();
  // Use custom map, expect it has no filters from static map
  const auto& f = CreateMetaFactory({CreateFactory(filter_info)}, stats);
  candidates::configs::Filters configs(f, {});
  std::vector<std::unique_ptr<cf::Filter>> res;
  EXPECT_NO_THROW((res = f.Create({filter_info.name}, params, env, configs)));
  ASSERT_EQ(res.size(), 1);
  EXPECT_EQ(res.front()->name(), filter_info.name);
}

TEST(FilterMetaFactory, UnknownFilter) {
  cf::Statistics stats;
  formats::json::Value params;
  const auto& env = CreateEnvironment();
  const auto& f = CreateMetaFactory({}, stats);
  candidates::configs::Filters configs(f, {});

  std::vector<std::unique_ptr<cf::Filter>> res;
  EXPECT_THROW((res = f.Create({"unittest_unknown"}, params, env, configs)),
               cf::NotFoundError);

  cf::FilterInfo f1_info{"f1", {}, {}, false, {}};
  std::vector<std::unique_ptr<cf::Filter>> custom_filters;
  custom_filters.push_back(CreateFilter(f1_info));
  EXPECT_THROW(
      (res = f.Create({}, params, env, configs, std::move(custom_filters))),
      cf::NotFoundError);
}

TEST(FilterMetaFactory, AlreadyRegisteredFilter) {
  cf::Statistics stats;
  cf::FilterInfo filter_info{"f1", {}, {}, false, {}};
  const auto factory = CreateFactory(filter_info);
  EXPECT_THROW(CreateMetaFactory({factory, factory}, stats), cf::Exception);
}

TEST(FilterMetaFactory, EmptyRequest) {
  cf::Statistics stats;
  cf::FilterInfo filter_info{"f1", {}, {}, false, {}};
  const auto& f = CreateMetaFactory({CreateFactory(filter_info)}, stats);
  candidates::configs::Filters configs(f, {});
  formats::json::Value params;
  const auto& env = CreateEnvironment();
  std::vector<std::unique_ptr<cf::Filter>> res;
  EXPECT_NO_THROW((res = f.Create({}, params, env, configs)));
  EXPECT_TRUE(res.empty());
}

TEST(FilterMetaFactory, CreateWithDeps) {
  cf::Statistics stats;
  cf::FilterInfo f1_info{"f1", {}, {}, false, {}};
  cf::FilterInfo f2_info{"f2", {"f1"}, {}, false, {}};
  cf::FilterInfo f3_info{"f3", {"f2"}, {}, false, {}, 0, 2, 5};
  cf::FilterInfo f4_info{"f4", {"f2", "f1"}, {}, false, {}, 0, 3, 5};
  cf::FilterInfo f5_info{"f5", {"f1"}, {}, false, {}, 0, 4, 5};

  const auto& f = CreateMetaFactory(
      {CreateFactory(f1_info), CreateFactory(f2_info), CreateFactory(f3_info),
       CreateFactory(f4_info), CreateFactory(f5_info)},
      stats);
  candidates::configs::Filters configs(f, {});

  formats::json::Value params;
  const auto& env = CreateEnvironment();
  auto filters = f.Create({"f1"}, params, env, configs);
  ASSERT_EQ(filters.size(), 1);
  EXPECT_EQ(filters[0]->name(), "f1");

  filters = f.Create({"f2"}, params, env, configs);
  ASSERT_EQ(filters.size(), 2);
  EXPECT_EQ(filters[0]->name(), "f1");
  EXPECT_EQ(filters[1]->name(), "f2");

  filters = f.Create({"f3"}, params, env, configs);
  ASSERT_EQ(filters.size(), 3);
  EXPECT_EQ(filters[0]->name(), "f1");
  EXPECT_EQ(filters[1]->name(), "f2");
  EXPECT_EQ(filters[2]->name(), "f3");

  filters = f.Create({"f1", "f3"}, params, env, configs);
  ASSERT_EQ(filters.size(), 3);
  EXPECT_EQ(filters[0]->name(), "f1");
  EXPECT_EQ(filters[1]->name(), "f2");
  EXPECT_EQ(filters[2]->name(), "f3");

  filters = f.Create({"f2", "f3"}, params, env, configs);
  ASSERT_EQ(filters.size(), 3);
  EXPECT_EQ(filters[0]->name(), "f1");
  EXPECT_EQ(filters[1]->name(), "f2");
  EXPECT_EQ(filters[2]->name(), "f3");

  filters = f.Create({"f4", "f3"}, params, env, configs);
  ASSERT_EQ(filters.size(), 4);
  EXPECT_EQ(filters[0]->name(), "f1");
  EXPECT_EQ(filters[1]->name(), "f2");
  EXPECT_EQ(filters[2]->name(), "f4");
  EXPECT_EQ(filters[3]->name(), "f3");

  filters = f.Create({"f1", "f2", "f3", "f4", "f5"}, params, env, configs);
  ASSERT_EQ(filters.size(), 5);
  EXPECT_EQ(filters[0]->name(), "f1");
  EXPECT_EQ(filters[1]->name(), "f5");
  EXPECT_EQ(filters[2]->name(), "f2");
  EXPECT_EQ(filters[3]->name(), "f4");
  EXPECT_EQ(filters[4]->name(), "f3");

  filters = f.Create({"f5", "f4", "f3", "f2", "f1"}, params, env, configs);
  ASSERT_EQ(filters.size(), 5);
  EXPECT_EQ(filters[0]->name(), "f1");
  EXPECT_EQ(filters[1]->name(), "f5");
  EXPECT_EQ(filters[2]->name(), "f2");
  EXPECT_EQ(filters[3]->name(), "f4");
  EXPECT_EQ(filters[4]->name(), "f3");

  {
    std::vector<std::unique_ptr<cf::Filter>> custom_filters;
    custom_filters.push_back(CreateFilter(f4_info));
    filters = f.Create({}, params, env, configs, std::move(custom_filters));
    EXPECT_EQ(GetNames(filters), MakeSet({"f1", "f2", "f4"}));
  }
  {
    std::vector<std::unique_ptr<cf::Filter>> custom_filters;
    custom_filters.push_back(CreateFilter(f4_info));
    filters = f.Create({"f4"}, params, env, configs, std::move(custom_filters));
    EXPECT_EQ(GetNames(filters), MakeSet({"f1", "f2", "f4"}));
  }
}

TEST(FilterMetaFactory, CreateWithOptionalDeps) {
  cf::Statistics stats;
  cf::FilterInfo f1_info{"f1", {}, {}, false, {}, 0, 1, 4};
  cf::FilterInfo f2_info{"f2", {}, {}, false, {}};
  cf::FilterInfo f3_info{"f3", {}, {"f2"}, false, {}, 0, 2, 5};
  cf::FilterInfo f4_info{"f4", {"f2"}, {"f1"}, false, {}};

  const auto& f =
      CreateMetaFactory({CreateFactory(f1_info), CreateFactory(f2_info),
                         CreateFactory(f3_info), CreateFactory(f4_info)},
                        stats);
  candidates::configs::Filters configs(f, {});

  formats::json::Value params;
  const auto& env = CreateEnvironment();
  auto filters = f.Create({"f3"}, params, env, configs);
  ASSERT_EQ(filters.size(), 2);
  EXPECT_EQ(filters[0]->name(), "f2");
  EXPECT_EQ(filters[1]->name(), "f3");

  filters = f.Create({"f4"}, params, env, configs);
  ASSERT_EQ(filters.size(), 3);
  EXPECT_EQ(filters[0]->name(), "f2");
  EXPECT_EQ(filters[1]->name(), "f1");
  EXPECT_EQ(filters[2]->name(), "f4");

  filters = f.Create({"f4", "f3"}, params, env, configs);
  ASSERT_EQ(filters.size(), 4);
  EXPECT_EQ(filters[0]->name(), "f2");
  EXPECT_EQ(filters[1]->name(), "f3");
  EXPECT_EQ(filters[2]->name(), "f1");
  EXPECT_EQ(filters[3]->name(), "f4");
}

TEST(FilterMetaFactory, DependencyCycle) {
  {
    cf::Statistics stats;
    cf::FilterInfo f1_info{"f1", {"f1"}, {}, false, {}};
    EXPECT_THROW(CreateMetaFactory({CreateFactory(f1_info)}, stats),
                 cf::Exception);
  }

  {
    cf::Statistics stats;
    cf::FilterInfo f1_info{"f1", {}, {"f1"}, false, {}};
    EXPECT_THROW(CreateMetaFactory({CreateFactory(f1_info)}, stats),
                 cf::Exception);
  }

  {
    cf::Statistics stats;
    cf::FilterInfo f1_info{"f1", {"f2"}, {}, false, {}};
    cf::FilterInfo f2_info{"f2", {"f2"}, {}, false, {}};
    EXPECT_THROW(CreateMetaFactory(
                     {CreateFactory(f1_info), CreateFactory(f2_info)}, stats),
                 cf::Exception);
  }

  {
    cf::Statistics stats;
    cf::FilterInfo f1_info{"f1", {}, {"f2"}, false, {}};
    cf::FilterInfo f2_info{"f2", {}, {"f2"}, false, {}};
    EXPECT_THROW(CreateMetaFactory(
                     {CreateFactory(f1_info), CreateFactory(f2_info)}, stats),
                 cf::Exception);
  }

  {
    cf::Statistics stats;
    cf::FilterInfo f1_info{"f1", {"f2"}, {}, false, {}};
    cf::FilterInfo f2_info{"f2", {"f1"}, {}, false, {}};
    EXPECT_THROW(CreateMetaFactory(
                     {CreateFactory(f1_info), CreateFactory(f2_info)}, stats),
                 cf::Exception);
  }

  {
    cf::Statistics stats;
    cf::FilterInfo f1_info{"f1", {}, {"f2"}, false, {}};
    cf::FilterInfo f2_info{"f2", {}, {"f1"}, false, {}};
    EXPECT_THROW(CreateMetaFactory(
                     {CreateFactory(f1_info), CreateFactory(f2_info)}, stats),
                 cf::Exception);
  }

  {
    cf::Statistics stats;
    cf::FilterInfo f1_info{"f1", {"f2"}, {}, false, {}};
    cf::FilterInfo f2_info{"f2", {"f3"}, {}, false, {}};
    cf::FilterInfo f3_info{"f3", {"f1"}, {}, false, {}};
    EXPECT_THROW(
        CreateMetaFactory({CreateFactory(f1_info), CreateFactory(f2_info),
                           CreateFactory(f3_info)},
                          stats),
        cf::Exception);
  }

  {
    cf::Statistics stats;
    cf::FilterInfo f1_info{"f1", {}, {"f2"}, false, {}};
    cf::FilterInfo f2_info{"f2", {}, {"f3"}, false, {}};
    cf::FilterInfo f3_info{"f3", {}, {"f1"}, false, {}};
    EXPECT_THROW(
        CreateMetaFactory({CreateFactory(f1_info), CreateFactory(f2_info),
                           CreateFactory(f3_info)},
                          stats),
        cf::Exception);
  }

  {
    cf::Statistics stats;
    cf::FilterInfo f1_info{"f1", {}, {}, false, {"f1"}};
    EXPECT_THROW(CreateMetaFactory({CreateFactory(f1_info)}, stats),
                 cf::Exception);
  }

  {
    cf::Statistics stats;
    cf::FilterInfo f1_info{"f1", {"f2"}, {}, false, {}};
    cf::FilterInfo f2_info{"f2", {}, {}, false, {"f1"}};
    EXPECT_THROW(CreateMetaFactory(
                     {CreateFactory(f1_info), CreateFactory(f2_info)}, stats),
                 cf::Exception);
  }
}

TEST(FilterMetaFactory, MissingDependency) {
  {
    cf::Statistics stats;
    cf::FilterInfo f1_info{"f1", {}, {}, false, {}};
    cf::FilterInfo f2_info{"f2", {"f1"}, {}, false, {}};
    cf::FilterInfo f3_info{"f3", {"f2", "f1"}, {}, false, {}};
    cf::FilterInfo f4_info{"f4", {"f2", "f5"}, {}, false, {}};

    EXPECT_THROW(
        CreateMetaFactory({CreateFactory(f1_info), CreateFactory(f2_info),
                           CreateFactory(f3_info), CreateFactory(f4_info)},
                          stats),
        cf::Exception);
  }
  {
    cf::Statistics stats;
    cf::FilterInfo f1_info{"f1", {}, {}, false, {}};
    cf::FilterInfo f2_info{"f2", {"f1"}, {}, false, {}};
    cf::FilterInfo f3_info{"f3", {"f2"}, {"f4"}, false, {}};

    EXPECT_THROW(
        CreateMetaFactory({CreateFactory(f1_info), CreateFactory(f2_info),
                           CreateFactory(f3_info)},
                          stats),
        cf::Exception);
  }
  {
    cf::Statistics stats;
    cf::FilterInfo f1_info{"f1", {}, {}, false, {"f2"}};

    EXPECT_THROW(CreateMetaFactory({CreateFactory(f1_info)}, stats),
                 cf::Exception);
  }
}

UTEST(FilterMetaFactory, BlockedFilter) {
  cf::Statistics stats;
  cf::FilterInfo f1_info{"f1", {}, {}, false, {}};
  cf::FilterInfo f2_info{"f2", {"f1"}, {}, false, {}};
  cf::FilterInfo f3_info{"f3", {"f2", "f1"}, {}, false, {}};
  cf::FilterInfo f4_info{"f4", {"f1", "f2"}, {}, false, {}};
  cf::SelfDiagnosticsData self_diag_data;
  cf::MetaFactory factory(
      {CreateFactory(f1_info), CreateFactory(f2_info), CreateFactory(f3_info),
       CreateFactory(f4_info)},
      [&self_diag_data]() { return self_diag_data; }, stats);
  candidates::configs::Filters configs(factory, {});
  formats::json::Value params;
  const auto& env = CreateEnvironment();
  {
    self_diag_data.blocked = {factory.GetIdxDict().GetIdx("f1")};
    const auto& filters = factory.Create({"f1"}, params, env, configs);
    EXPECT_TRUE(filters.empty());
  }
  {
    self_diag_data.blocked = {factory.GetIdxDict().GetIdx("f1")};
    const auto& filters = factory.Create({"f2"}, params, env, configs);
    EXPECT_TRUE(filters.empty());
  }
  {
    self_diag_data.blocked = {factory.GetIdxDict().GetIdx("f1")};
    const auto& filters = factory.Create({"f3"}, params, env, configs);
    EXPECT_TRUE(filters.empty());
  }
  {
    self_diag_data.blocked = {factory.GetIdxDict().GetIdx("f2")};
    const auto& filters = factory.Create({"f3", "f1"}, params, env, configs);
    ASSERT_EQ(filters.size(), 1);
    EXPECT_EQ(filters.front()->name(), "f1");
  }
  {
    self_diag_data.blocked = {factory.GetIdxDict().GetIdx("f2")};
    const auto& filters = factory.Create({"f4", "f1"}, params, env, configs);
    ASSERT_EQ(filters.size(), 1);
    EXPECT_EQ(filters.front()->name(), "f1");
  }
  {
    self_diag_data.blocked = {factory.GetIdxDict().GetIdx("f1")};
    std::vector<std::unique_ptr<cf::Filter>> custom_filters;
    custom_filters.push_back(CreateFilter(f1_info));
    const auto& filters =
        factory.Create({}, params, env, configs, std::move(custom_filters));
    EXPECT_EQ(GetNames(filters), MakeSet({}));
  }
  {
    self_diag_data.blocked = {factory.GetIdxDict().GetIdx("f1")};
    std::vector<std::unique_ptr<cf::Filter>> custom_filters;
    custom_filters.push_back(CreateFilter(f2_info));
    const auto& filters =
        factory.Create({}, params, env, configs, std::move(custom_filters));
    EXPECT_EQ(GetNames(filters), MakeSet({}));
  }
}

UTEST(FilterMetaFactory, BlockedOptionalFilter) {
  cf::Statistics stats;
  cf::FilterInfo f1_info{"f1", {}, {}, false, {}};
  cf::FilterInfo f2_info{"f2", {}, {"f1"}, false, {}};
  cf::FilterInfo f3_info{"f3", {"f1"}, {"f2"}, false, {}};
  cf::FilterInfo f4_info{"f4", {}, {"f3"}, false, {}};
  cf::SelfDiagnosticsData self_diag_data;
  cf::MetaFactory factory(
      {CreateFactory(f1_info), CreateFactory(f2_info), CreateFactory(f3_info),
       CreateFactory(f4_info)},
      [&self_diag_data]() { return self_diag_data; }, stats);
  candidates::configs::Filters configs(factory, {});
  formats::json::Value params;
  const auto& env = CreateEnvironment();
  {
    self_diag_data.blocked = {factory.GetIdxDict().GetIdx("f1")};
    const auto& filters = factory.Create({"f2"}, params, env, configs);
    ASSERT_EQ(filters.size(), 1);
    EXPECT_EQ(filters.front()->name(), "f2");
  }
  {
    self_diag_data.blocked = {factory.GetIdxDict().GetIdx("f2")};
    const auto& filters = factory.Create({"f3"}, params, env, configs);
    ASSERT_EQ(filters.size(), 2);
    EXPECT_EQ(filters[0]->name(), "f1");
    EXPECT_EQ(filters[1]->name(), "f3");
  }
  {
    self_diag_data.blocked = {factory.GetIdxDict().GetIdx("f1")};
    const auto& filters = factory.Create({"f4"}, params, env, configs);
    ASSERT_EQ(filters.size(), 1);
    EXPECT_EQ(filters[0]->name(), "f4");
  }
  {
    self_diag_data.blocked = {factory.GetIdxDict().GetIdx("f2")};
    std::vector<std::unique_ptr<cf::Filter>> custom_filters;
    custom_filters.push_back(CreateFilter(f3_info));
    const auto& filters =
        factory.Create({}, params, env, configs, std::move(custom_filters));
    EXPECT_EQ(GetNames(filters), MakeSet({"f1", "f3"}));
  }
}

UTEST(FilterMetaFactory, BlockedWithReplacement) {
  cf::Statistics stats;
  cf::FilterInfo f1_info{"f1", {}, {}, false, {"f2"}};
  cf::FilterInfo f2_info{"f2", {}, {}, false, {}};
  cf::FilterInfo f3_info{"f3", {"f1"}, {}, false, {}};
  cf::FilterInfo f4_info{"f4", {}, {"f3"}, false, {}};
  cf::SelfDiagnosticsData self_diag_data;
  cf::MetaFactory factory(
      {CreateFactory(f1_info), CreateFactory(f2_info), CreateFactory(f3_info),
       CreateFactory(f4_info)},
      [&self_diag_data]() { return self_diag_data; }, stats);
  candidates::configs::Filters configs(factory, {});
  formats::json::Value params;
  const auto& env = CreateEnvironment();
  {
    self_diag_data.blocked = {factory.GetIdxDict().GetIdx("f1")};
    const auto& filters = factory.Create({"f1"}, params, env, configs);
    ASSERT_EQ(filters.size(), 1);
    EXPECT_EQ(filters[0]->name(), "f2");
  }
  {
    self_diag_data.blocked = {factory.GetIdxDict().GetIdx("f2")};
    const auto& filters = factory.Create({"f1"}, params, env, configs);
    ASSERT_EQ(filters.size(), 1);
    EXPECT_EQ(filters[0]->name(), "f1");
  }
  {
    self_diag_data.blocked = {factory.GetIdxDict().GetIdx("f2"),
                              factory.GetIdxDict().GetIdx("f1")};
    const auto& filters = factory.Create({"f1"}, params, env, configs);
    EXPECT_TRUE(filters.empty());
  }
  {
    self_diag_data.blocked = {factory.GetIdxDict().GetIdx("f1")};
    const auto& filters = factory.Create({"f3"}, params, env, configs);
    EXPECT_EQ(GetNames(filters), MakeSet({"f3", "f2"}));
  }
  {
    self_diag_data.blocked = {factory.GetIdxDict().GetIdx("f1")};
    const auto& filters = factory.Create({"f4"}, params, env, configs);
    EXPECT_EQ(GetNames(filters), MakeSet({"f4", "f3", "f2"}));
  }
  {
    self_diag_data.blocked = {factory.GetIdxDict().GetIdx("f1")};
    const auto& filters = factory.Create({"f4"}, params, env, configs);
    EXPECT_EQ(GetNames(filters), MakeSet({"f4", "f3", "f2"}));
  }
  {
    self_diag_data.blocked = {factory.GetIdxDict().GetIdx("f1")};
    std::vector<std::unique_ptr<cf::Filter>> custom_filters;
    custom_filters.push_back(CreateFilter(f1_info));
    const auto& filters =
        factory.Create({"f3"}, params, env, configs, std::move(custom_filters));
    EXPECT_EQ(GetNames(filters), MakeSet({"f2", "f3"}));
  }
}

UTEST(FilterMetaFactory, Required) {
  cf::Statistics stats;
  cf::FilterInfo f1_info{"f1", {}, {}, false, {}};
  cf::FilterInfo f2_info{"f2", {"f1"}, {}, false, {}};
  cf::FilterInfo f3_info{"f3", {}, {"f1"}, false, {}};
  cf::FilterInfo f4_info{"f4", {}, {}, false, {"f1"}};
  cf::FilterInfo f5_info{"f5", {"f1"}, {"f2"}, false, {}};
  cf::FilterInfo f6_info{"f6", {"f4"}, {}, false, {}};
  cf::FilterInfo f7_info{"f7", {}, {}, false, {}};
  cf::FilterInfo f8_info{"f8", {}, {}, false, {"f7"}};
  cf::FilterInfo f9_info{"f9", {"f8"}, {}, false, {}};
  cf::SelfDiagnosticsData self_diag_data;
  cf::MetaFactory factory(
      {
          CreateFactory(f1_info),
          CreateFactory(f2_info),
          CreateFactory(f3_info),
          CreateFactory(f4_info),
          CreateFactory(f5_info),
          CreateFactory(f6_info),
          CreateFactory(f7_info),
          CreateFactory(f8_info),
          CreateFactory(f9_info),
      },
      [&self_diag_data]() { return self_diag_data; }, stats);
  self_diag_data.blocked = {factory.GetIdxDict().GetIdx("f1"),
                            factory.GetIdxDict().GetIdx("f8")};
  formats::json::Value params;
  const auto& env = CreateEnvironment();
  {
    FilterConfigs configs;
    configs["f1"].required = true;
    auto filters = factory.Create({"f1"}, params, env, {factory, configs});
    EXPECT_EQ(GetNames(filters), MakeSet({"f1"}));
  }
  {
    FilterConfigs configs;
    configs["f2"].required = true;
    auto filters = factory.Create({"f2"}, params, env, {factory, configs});
    EXPECT_EQ(GetNames(filters), MakeSet({"f1", "f2"}));
  }
  {
    FilterConfigs configs;
    configs["f3"].required = true;
    auto filters = factory.Create({"f3"}, params, env, {factory, configs});
    EXPECT_EQ(GetNames(filters), MakeSet({"f3"}));
  }
  {
    FilterConfigs configs;
    configs["f4"].required = true;
    auto filters =
        factory.Create({"f2", "f4"}, params, env, {factory, configs});
    EXPECT_EQ(GetNames(filters), MakeSet({"f1", "f2", "f4"}));
  }
  {
    FilterConfigs configs;
    configs["f2"].required = true;
    auto filters =
        factory.Create({"f1", "f4"}, params, env, {factory, configs});
    EXPECT_EQ(GetNames(filters), MakeSet({"f4"}));
  }
  {
    FilterConfigs configs;
    configs["f2"].required = true;
    auto filters =
        factory.Create({"f2", "f5"}, params, env, {factory, configs});
    EXPECT_EQ(GetNames(filters), MakeSet({"f1", "f2", "f5"}));
  }
  {
    FilterConfigs configs;
    configs["f5"].required = true;

    auto filters =
        factory.Create({"f2", "f5"}, params, env, {factory, configs});
    EXPECT_EQ(GetNames(filters), MakeSet({"f1", "f2", "f5"}));
  }
  {
    FilterConfigs configs;
    configs["f5"].required = true;
    configs["f2"].disabled = true;

    auto filters = factory.Create({"f5"}, params, env, {factory, configs});
    EXPECT_EQ(GetNames(filters), MakeSet({"f1", "f5"}));
  }
  {
    FilterConfigs configs;
    configs["f2"].required = true;
    configs["f2"].disabled = true;

    auto filters = factory.Create({"f5"}, params, env, {factory, configs});
    EXPECT_EQ(GetNames(filters), MakeSet({}));
  }
  {
    FilterConfigs configs;
    configs["f4"].disabled = true;

    auto filters = factory.Create({"f6"}, params, env, {factory, configs});
    EXPECT_EQ(GetNames(filters), MakeSet({"f6"}));
  }
  {
    FilterConfigs configs;
    configs["f6"].disabled = true;
    configs["f6"].required = true;

    auto filters = factory.Create({"f6"}, params, env, {factory, configs});
    EXPECT_EQ(GetNames(filters), MakeSet({}));
  }
  {
    FilterConfigs configs;
    configs["f7"].disabled = true;

    auto filters = factory.Create({"f8"}, params, env, {factory, configs});
    EXPECT_EQ(GetNames(filters), MakeSet({}));
  }
  {
    FilterConfigs configs;
    configs["f7"].disabled = true;

    auto filters = factory.Create({"f9"}, params, env, {factory, configs});
    EXPECT_EQ(GetNames(filters), MakeSet({}));
  }
}

namespace candidates::filters::test {

class ParseErrorFactory : public Factory {
 public:
  using Factory::Factory;

  std::unique_ptr<Filter> Create(
      const formats::json::Value& params,
      [[maybe_unused]] const FactoryEnvironment& env) const override {
    params["missing_field"].As<int>();
    return {};
  }
};

}  // namespace candidates::filters::test

UTEST(FilterMetaFactory, BlockedOnParseError) {
  cf::Statistics stats;
  cf::SelfDiagnosticsData data;
  cf::FilterInfo f1_info{"f1", {}, {}, false, {}};
  cf::FilterInfo f2_info{"f2", {}, {}, true, {}};
  cf::MetaFactory f(
      {std::make_shared<cf::test::ParseErrorFactory>(f1_info),
       std::make_shared<cf::test::ParseErrorFactory>(f2_info)},
      [&data]() { return data; }, stats);
  candidates::configs::Filters configs(f, {});
  formats::json::Value params;
  const auto& env = CreateEnvironment();
  EXPECT_THROW(f.Create({"f1"}, params, env, configs),
               formats::json::Exception);
  EXPECT_THROW(f.Create({"f2"}, params, env, configs),
               formats::json::Exception);

  std::vector<std::unique_ptr<cf::Filter>> filters;
  data.ignore_on_factory_errors = {f.GetIdxDict().GetIdx("f1"),
                                   f.GetIdxDict().GetIdx("f2")};
  EXPECT_NO_THROW(filters = f.Create({"f1"}, params, env, configs));
  EXPECT_TRUE(filters.empty());
  EXPECT_THROW(f.Create({"f2"}, params, env, configs),
               formats::json::Exception);
}

UTEST(FilterMetaFactory, BlockedOnParseErrorDeps) {
  cf::Statistics stats;
  cf::SelfDiagnosticsData data;
  cf::FilterInfo f1_info{"f1", {}, {}, false, {}};
  cf::FilterInfo f2_info{"f2", {"f1"}, {}, false, {}};
  cf::FilterInfo f3_info{"f3", {}, {"f1"}, false, {}};

  cf::MetaFactory f(
      {
          std::make_shared<cf::test::ParseErrorFactory>(f1_info),
          CreateFactory(f2_info),
          CreateFactory(f3_info),
      },
      [&data]() { return data; }, stats);
  candidates::configs::Filters configs(f, {});
  formats::json::Value params;
  const auto& env = CreateEnvironment();
  std::vector<std::unique_ptr<cf::Filter>> filters;
  data.ignore_on_factory_errors = {f.GetIdxDict().GetIdx("f1")};
  EXPECT_NO_THROW(filters = f.Create({"f2"}, params, env, configs));
  EXPECT_TRUE(filters.empty());
  EXPECT_NO_THROW(filters = f.Create({"f3"}, params, env, configs));
  ASSERT_EQ(filters.size(), 1);
}

UTEST(FilterMetaFactory, BlockedOnParseErrorWithReplacement) {
  cf::Statistics stats;
  cf::SelfDiagnosticsData data;
  cf::FilterInfo f1_info{"f1", {}, {}, false, {"f2"}};
  cf::FilterInfo f2_info{"f2", {}, {}, false, {}};
  cf::FilterInfo f3_info{"f3", {"f1"}, {}, false, {}};
  cf::FilterInfo f4_info{"f4", {}, {"f3"}, false, {}};

  cf::MetaFactory f(
      {
          std::make_shared<cf::test::ParseErrorFactory>(f1_info),
          CreateFactory(f2_info),
          CreateFactory(f3_info),
          CreateFactory(f4_info),
      },
      [&data]() { return data; }, stats);
  candidates::configs::Filters configs(f, {});
  formats::json::Value params;
  const auto& env = CreateEnvironment();
  std::vector<std::unique_ptr<cf::Filter>> filters;
  EXPECT_NO_THROW(filters = f.Create({"f1"}, params, env, configs));
  EXPECT_EQ(GetNames(filters), MakeSet({"f2"}));
  data.ignore_on_factory_errors = {f.GetIdxDict().GetIdx("f1")};
  EXPECT_NO_THROW(filters = f.Create({"f1"}, params, env, configs));
  EXPECT_EQ(GetNames(filters), MakeSet({"f2"}));
  EXPECT_NO_THROW(filters = f.Create({"f3"}, params, env, configs));
  EXPECT_EQ(GetNames(filters), MakeSet({"f3", "f2"}));
  data.blocked = {f.GetIdxDict().GetIdx("f2")};
  EXPECT_NO_THROW(filters = f.Create({"f3"}, params, env, configs));
  EXPECT_TRUE(filters.empty());
  EXPECT_NO_THROW(filters = f.Create({"f4"}, params, env, configs));
  EXPECT_EQ(GetNames(filters), MakeSet({"f4"}));
}

namespace candidates::filters::test {

class MetaFilterFactory : public Factory {
 public:
  MetaFilterFactory(const FilterInfo& info, std::vector<std::string> names)
      : Factory(info), names_(std::move(names)) {}

  std::unique_ptr<Filter> Create(const formats::json::Value& params,
                                 const FactoryEnvironment& env) const override {
    std::vector<std::unique_ptr<Filter>> filters;
    for (const auto& name : names_) {
      auto filter = env.CreateFilter(name, params);
      if (filter) filters.push_back(std::move(filter));
    }
    if (filters.empty()) return {};
    return std::make_unique<AllowAll>(info());
  }

 private:
  const std::vector<std::string> names_;
};

}  // namespace candidates::filters::test

UTEST_MT(FilterMetaFactory, MetaFilter, 2) {
  cf::Statistics stats;
  cf::SelfDiagnosticsData data;
  cf::FilterInfo f1_info{"f1", {}, {}, false, {}};
  cf::FilterInfo f2_info{"f2", {"f4"}, {}, false, {}};
  cf::FilterInfo f3_info{"f3", {}, {}, false, {}};
  cf::FilterInfo f4_info{"f4", {}, {}, false, {}};

  cf::MetaFactory f(
      {
          std::make_shared<cf::test::MetaFilterFactory>(
              f1_info, std::vector<std::string>{"f2", "f3"}),
          CreateFactory(f2_info),
          CreateFactory(f3_info),
          CreateFactory(f4_info),
      },
      [&data]() { return data; }, stats);
  candidates::configs::Filters configs(f, {});
  formats::json::Value params;
  const auto& env = CreateEnvironment();
  std::vector<std::unique_ptr<cf::Filter>> filters;
  filters = f.Create({"f1"}, params, env, configs);
  EXPECT_EQ(filters.size(), 2);
  data.blocked = {f.GetIdxDict().GetIdx("f1")};
  filters = f.Create({"f1"}, params, env, configs);
  EXPECT_TRUE(filters.empty());
  data.blocked = {f.GetIdxDict().GetIdx("f2")};
  filters = f.Create({"f1"}, params, env, configs);
  EXPECT_EQ(filters.size(), 1);
  data.blocked = {f.GetIdxDict().GetIdx("f3")};
  filters = f.Create({"f1"}, params, env, configs);
  EXPECT_EQ(filters.size(), 2);
  data.blocked = {f.GetIdxDict().GetIdx("f2"), f.GetIdxDict().GetIdx("f3")};
  filters = f.Create({"f1"}, params, env, configs);
  EXPECT_TRUE(filters.empty());
  data.blocked = {};
  {
    FilterConfigs configs;
    configs["f4"].disabled = true;

    filters = f.Create({"f1"}, params, env, {f, configs});
    EXPECT_EQ(filters.size(), 1);
  }
  {
    FilterConfigs configs;
    configs["f2"].disabled = true;

    filters = f.Create({"f1"}, params, env, {f, configs});
    EXPECT_EQ(filters.size(), 1);
  }
  {
    FilterConfigs configs;
    configs["f3"].disabled = true;

    filters = f.Create({"f1"}, params, env, {f, configs});
    EXPECT_EQ(filters.size(), 2);
  }
  {
    FilterConfigs configs;
    configs["f2"].disabled = true;
    configs["f3"].disabled = true;

    filters = f.Create({"f1"}, params, env, {f, configs});
    EXPECT_TRUE(filters.empty());
  }
  {
    FilterConfigs configs;
    configs["f1"].disabled = true;

    filters = f.Create({"f1"}, params, env, {f, configs});
    EXPECT_TRUE(filters.empty());
  }
}

UTEST_MT(FilterMetaFactory, MetaFilterWithReplacement, 2) {
  cf::Statistics stats;
  cf::SelfDiagnosticsData data;
  cf::FilterInfo f1_info{"f1", {}, {}, false, {}};
  cf::FilterInfo f2_info{"f2", {}, {}, false, {"f3"}};
  cf::FilterInfo f3_info{"f3", {"f4"}, {}, false, {}};
  cf::FilterInfo f4_info{"f4", {}, {}, false, {}};

  cf::MetaFactory f(
      {
          std::make_shared<cf::test::MetaFilterFactory>(
              f1_info, std::vector<std::string>{"f2"}),
          CreateFactory(f2_info),
          CreateFactory(f3_info),
          CreateFactory(f4_info),
      },
      [&data]() { return data; }, stats);
  candidates::configs::Filters configs(f, {});
  formats::json::Value params;
  const auto& env = CreateEnvironment();
  std::vector<std::unique_ptr<cf::Filter>> filters;
  data.blocked = {f.GetIdxDict().GetIdx("f2")};
  filters = f.Create({"f1"}, params, env, configs);
  EXPECT_EQ(GetNames(filters), MakeSet({"f1", "f4"}));
  {
    FilterConfigs configs;
    configs["f4"].disabled = true;

    filters = f.Create({"f1"}, params, env, {f, configs});
    EXPECT_EQ(filters.size(), 1);
  }
  {
    FilterConfigs configs;
    configs["f3"].disabled = true;

    filters = f.Create({"f1"}, params, env, {f, configs});
    EXPECT_TRUE(filters.empty());
  }
  {
    FilterConfigs configs;
    configs["f2"].disabled = true;

    filters = f.Create({"f1"}, params, env, {f, configs});
    EXPECT_TRUE(filters.empty());
  }
}

UTEST_MT(FilterMetaFactory, RemoveConflicts, 2) {
  cf::Statistics stats;
  cf::FilterInfo f1_info{"f1", {}, {}, false, {}};
  cf::FilterInfo f2_info{"f2", {}, {}, false, {"f1"}};
  cf::FilterInfo f3_info{"f3", {}, {}, false, {"f1"}};

  const auto f = CreateMetaFactory(
      {
          CreateFactory(f1_info),
          CreateFactory(f2_info),
          CreateFactory(f3_info),
      },
      stats);
  candidates::configs::Filters configs(f, {});
  formats::json::Value params;
  const auto& env = CreateEnvironment();
  std::vector<std::unique_ptr<cf::Filter>> filters;
  filters = f.Create({"f1", "f2", "f3"}, params, env, configs);
  EXPECT_EQ(GetNames(filters), MakeSet({"f2", "f3"}));

  std::vector<std::unique_ptr<cf::Filter>> custom_filters;
  custom_filters.push_back(CreateFilter(f1_info));
  filters =
      f.Create({"f2", "f3"}, params, env, configs, std::move(custom_filters));
  EXPECT_EQ(GetNames(filters), MakeSet({"f2", "f3"}));
}

namespace candidates::filters::test {

template <typename Exception>
class ThrowException : public Factory {
 public:
  using Factory::Factory;

  std::unique_ptr<Filter> Create(
      [[maybe_unused]] const formats::json::Value& params,
      [[maybe_unused]] const FactoryEnvironment& env) const override {
    throw Exception("some text");
  }
};

}  // namespace candidates::filters::test

UTEST_MT(FilterMetaFactory, UninitializedCache, 2) {
  using cache::EmptyCacheError;

  cf::Statistics stats;
  cf::FilterInfo f1_info{"f1", {}, {}, false, {}};
  cf::FilterInfo f2_info{"f2", {}, {}, true, {}};
  cf::FilterInfo f3_info{"f3", {}, {}, false, {}};
  cf::FilterInfo f4_info{"f4", {}, {"f1"}, false, {}};

  const auto f = CreateMetaFactory(
      {
          std::make_shared<cf::test::ThrowException<EmptyCacheError>>(f1_info),
          std::make_shared<cf::test::ThrowException<EmptyCacheError>>(f2_info),
          std::make_shared<cf::test::ThrowException<std::runtime_error>>(
              f3_info),
          CreateFactory(f4_info),
      },
      stats);
  candidates::configs::Filters configs(f, {});
  formats::json::Value params;
  const auto& env = CreateEnvironment();
  std::vector<std::unique_ptr<cf::Filter>> filters;
  EXPECT_NO_THROW(filters = f.Create({"f1"}, params, env, configs));
  EXPECT_TRUE(filters.empty());
  EXPECT_THROW(f.Create({"f2"}, params, env, configs), EmptyCacheError);
  EXPECT_THROW(f.Create({"f3"}, params, env, configs), std::runtime_error);
  EXPECT_NO_THROW(filters = f.Create({"f4"}, params, env, configs));
  EXPECT_EQ(GetNames(filters), MakeSet({"f4"}));
}

namespace candidates::filters::test {
class NewInfoFactory : public Factory {
 public:
  NewInfoFactory(const FilterInfo& info, const FilterInfo& new_info)
      : Factory(info), new_info_(new_info) {}

  std::unique_ptr<Filter> Create(const formats::json::Value&,
                                 const FactoryEnvironment&) const override {
    return std::make_unique<AllowAll>(new_info_);
  }

 private:
  FilterInfo new_info_;
};
}  // namespace candidates::filters::test

UTEST(FilterMetaFactory, DynamicDependencies) {
  cf::Statistics stats;
  cf::FilterInfo f1_info{"f1", {}, {}, false, {}};
  cf::FilterInfo f2_info{"f2", {}, {}, false, {}};
  cf::FilterInfo f3_info{"f3", {}, {}, false, {}};

  cf::FilterInfo factory4_info{"f4", {"f1", "f2"}, {}, false, {}};
  cf::FilterInfo filter4_valid_info{"f4", {"f1"}, {}, false, {}};

  cf::FilterInfo factory5_info{"f5", {"f1", "f2"}, {}, false, {}};
  cf::FilterInfo filter5_invalid_info{"f5", {"f1", "f3"}, {}, false, {}};

  const auto f = CreateMetaFactory(
      {CreateFactory(f1_info), CreateFactory(f2_info), CreateFactory(f3_info),
       std::make_shared<cf::test::NewInfoFactory>(factory4_info,
                                                  filter4_valid_info),
       std::make_shared<cf::test::NewInfoFactory>(factory5_info,
                                                  filter5_invalid_info)},
      stats);
  candidates::configs::Filters configs(f, {});
  formats::json::Value params;
  const auto& env = CreateEnvironment();
  std::vector<std::unique_ptr<cf::Filter>> filters;
  EXPECT_NO_THROW(filters = f.Create({"f4"}, params, env, configs));
  EXPECT_EQ(GetNames(filters), MakeSet({"f4", "f1"}));

  EXPECT_THROW(filters = f.Create({"f5"}, params, env, configs), cf::Exception);
}

UTEST_MT(FilterMetaFactory, DependenciesScores, 2) {
  cf::FilterInfo f1_info{"f1", {}, {}, false, {}};
  cf::FilterInfo f2_info{"f2", {}, {}, false, {}};
  cf::FilterInfo f3_info{"f3", {}, {}, false, {}};
  cf::FilterInfo f4_info{"f4", {"f2"}, {"f3", "f1"}, false, {}};

  const auto diagnostics_getter = []() {
    cf::SelfDiagnosticsData data;
    data.scores = {5, 3, 4, 9};
    return data;
  };

  cf::Statistics statistics;
  cf::MetaFactory f(
      {
          CreateFactory(f1_info),
          CreateFactory(f2_info),
          CreateFactory(f3_info),
          CreateFactory(f4_info),
      },
      diagnostics_getter, statistics);
  candidates::configs::Filters configs(f, {});

  formats::json::Value params;
  const auto& env = CreateEnvironment();
  auto filters = f.Create({"f4"}, params, env, configs, {}, true);
  ASSERT_EQ(filters.size(), 4);
  EXPECT_EQ(filters[0]->name(), "f1");
  EXPECT_EQ(filters[1]->name(), "f3");
  EXPECT_EQ(filters[2]->name(), "f2");
  EXPECT_EQ(filters[3]->name(), "f4");
}
