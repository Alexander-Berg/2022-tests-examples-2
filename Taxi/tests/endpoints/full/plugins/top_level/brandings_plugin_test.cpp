#include <endpoints/full/plugins/brandings/plugin.hpp>

#include <tests/context_mock_test.hpp>
#include <tests/endpoints/common/service_level_mock_test.hpp>
#include <userver/utest/utest.hpp>

namespace routestats::full {

service_level::TariffBranding MockBranding(const std::string& type) {
  service_level::TariffBranding result;
  result.type = type;
  return result;
}

class TestSubplugin1 : public brandings::BrandingsSubpluginBase {
 public:
  std::string Name() const override { return "test_subplugin_1"; }
  std::vector<service_level::TariffBranding> GetBrandings(
      const std::string&) override {
    return {MockBranding("plus_promo")};
  }
};

class TestSubplugin2 : public brandings::BrandingsSubpluginBase {
  std::string Name() const override { return "test_subplugin_2"; }

 public:
  void OnGotProtocolResponse(const ProtocolResponse&) override {
    throw std::runtime_error("fail");
  }

 private:
  std::vector<service_level::TariffBranding> GetBrandings(
      const std::string&) override {
    return {MockBranding("cashback"), MockBranding("complement_payment")};
  }
};

UTEST(TestBrandingsPlugin, Ok) {
  BrandingsPlugin plugin(
      {std::make_shared<TestSubplugin1>(), std::make_shared<TestSubplugin2>()});

  full::ContextData test_ctx = test::full::GetDefaultContext();
  auto plugin_ctx = test::full::MakeTopLevelContext(test_ctx);

  auto serializable = plugin.OnServiceLevelRendering(
      test::MockDefaultServiceLevel("econom"), plugin_ctx);

  handlers::ServiceLevel sl_resp;
  plugins::common::ResultWrapper<handlers::ServiceLevel> wrapper(sl_resp);
  serializable->SerializeInPlace(wrapper);

  ASSERT_EQ(sl_resp.brandings->size(), 3);

  ASSERT_EQ(sl_resp.brandings->at(0).type, "plus_promo");
  ASSERT_EQ(sl_resp.brandings->at(1).type, "cashback");
  ASSERT_EQ(sl_resp.brandings->at(2).type, "complement_payment");
}

UTEST(TestBrandingsPlugin, WithException) {
  full::ContextData test_ctx = test::full::GetDefaultContext();
  auto plugin_ctx = test::full::MakeTopLevelContext(test_ctx);

  BrandingsPlugin plugin(
      {std::make_shared<TestSubplugin1>(), std::make_shared<TestSubplugin2>()});
  plugin.OnGotProtocolResponse(plugin_ctx, ProtocolResponse());
  auto serializable = plugin.OnServiceLevelRendering(
      test::MockDefaultServiceLevel("econom"), plugin_ctx);

  handlers::ServiceLevel sl_resp;
  plugins::common::ResultWrapper<handlers::ServiceLevel> wrapper(sl_resp);
  serializable->SerializeInPlace(wrapper);

  ASSERT_EQ(sl_resp.brandings->size(), 1);
  ASSERT_EQ(sl_resp.brandings->at(0).type, "plus_promo");
}

}  // namespace routestats::full
