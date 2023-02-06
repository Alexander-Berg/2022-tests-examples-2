#include <plugins/common/plugin_base.hpp>
#include <userver/utest/utest.hpp>

#include <endpoints/common/core/service_level/extender.hpp>
#include <tests/endpoints/common/service_level_mock_test.hpp>

namespace routestats {
namespace {
class TestPlugin : public plugins::common::PluginBase {
 public:
  TestPlugin(const std::string& name) : name_(name) {}
  std::string Name() const override { return name_; }

 private:
  std::string name_;
};

struct TestLevelExtension : public core::ServiceLevelExtension {
  using core::ServiceLevelExtension::ServiceLevelExtension;

  std::optional<core::EstimatedWaiting> eta;
  std::optional<core::DescriptionParts> description_parts;
  std::optional<core::TariffUnavailable> tariff_unavailable;
  bool throws = false;

  void Apply(const std::string& /*source plugin*/,
             core::ServiceLevel& level) override {
    if (throws) throw std::runtime_error("test exception");
    if (eta) level.eta = eta;
    if (description_parts) level.description_parts = description_parts;
    if (tariff_unavailable) level.tariff_unavailable = tariff_unavailable;
  }
};

}  // namespace

TEST(TestExtender, HappyPath) {
  // 1. prepare plugins
  std::vector<plugins::common::PluginPtr> plugins{
      std::make_shared<TestPlugin>("plugin_1"),
      std::make_shared<TestPlugin>("plugin_2"),
      std::make_shared<TestPlugin>("plugin_3"),
  };

  // 2. prepare service levels
  auto vip_sl = test::MockDefaultServiceLevel("vip");
  vip_sl.tariff_unavailable = core::TariffUnavailable{"code", "msg"};
  std::vector<core::ServiceLevel> levels{
      test::MockDefaultServiceLevel("econom"),
      vip_sl,
      test::MockDefaultServiceLevel("business"),
      test::MockDefaultServiceLevel("maybach"),
  };

  // 3. prepare extensions
  core::ServiceLevelExtensionsMap plugin3_extensions;
  {
    auto econom_ext = std::make_shared<TestLevelExtension>("econom");
    econom_ext->eta = core::EstimatedWaiting{71, "tula"};
    plugin3_extensions["econom"] = econom_ext;

    auto vip_ext = std::make_shared<TestLevelExtension>("vip");
    vip_ext->tariff_unavailable =
        core::TariffUnavailable{"free_cars", "No cars"};
    vip_ext->eta = core::EstimatedWaiting{999, "long wait"};
    plugin3_extensions["vip"] = vip_ext;

    plugin3_extensions["maybach"] = nullptr;

    auto business_ext = std::make_shared<TestLevelExtension>("business");
    business_ext->throws = true;
    plugin3_extensions["business"] = business_ext;
  }

  std::vector<std::optional<core::ServiceLevelExtensionsMap>> extensions;
  extensions.push_back(std::nullopt);                       // plugin 1 result
  extensions.push_back(core::ServiceLevelExtensionsMap{});  // plugin 2 result
  extensions.push_back(plugin3_extensions);                 // plugin 3 result

  // 4. Run !
  core::ApplyServiceLevelExtensions(plugins, extensions, levels);
  // econom
  ASSERT_EQ(levels[0].eta->seconds, 71);
  ASSERT_EQ(levels[0].eta->message, "tula");
  ASSERT_FALSE(levels[0].tariff_unavailable);

  // vip
  ASSERT_EQ(levels[1].eta->seconds, 999);
  ASSERT_EQ(levels[1].eta->message, "long wait");
  ASSERT_TRUE(levels[1].tariff_unavailable);
  ASSERT_EQ(levels[1].tariff_unavailable->code, "free_cars");
  ASSERT_EQ(levels[1].tariff_unavailable->message, "No cars");

  // rest
  ASSERT_EQ(levels[2].eta->seconds, 60);
  ASSERT_FALSE(levels[2].tariff_unavailable);
  ASSERT_FALSE(levels[3].tariff_unavailable);
}

}  // namespace routestats
