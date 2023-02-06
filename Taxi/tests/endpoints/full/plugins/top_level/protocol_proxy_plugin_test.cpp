#include <userver/utest/utest.hpp>

#include <endpoints/full/plugins/protocol_proxy/plugin.hpp>

#include <tests/context_mock_test.hpp>
#include <tests/endpoints/common/service_level_mock_test.hpp>

namespace routestats::full {

TEST(ProtocolProxyPlugin, Basic) {
  ProtocolResponse protocol_response;
  protocol_response.extra = formats::json::FromString(R"({"a": "b", "c": 1})");

  clients::protocol_routestats::ServiceLevel service_level;
  service_level.class_ = "econom";
  service_level.extra = formats::json::FromString(R"({"a": "b", "c": 1})");
  protocol_response.service_levels = {service_level};

  ProtocolProxyPlugin plugin;
  auto test_ctx = test::full::GetDefaultContext();
  auto plugin_ctx = test::full::MakeTopLevelContext(test_ctx);
  const ServiceLevel mock_service_level =
      test::MockDefaultServiceLevel("econom");

  plugin.OnGotProtocolResponse(plugin_ctx, protocol_response);
  const auto rendered_root = plugin.OnRootRendering(plugin_ctx);
  const auto rendered_service_level =
      plugin.OnServiceLevelRendering(mock_service_level, plugin_ctx);

  handlers::RoutestatsResponse response;
  plugins::common::ResultWrapper<handlers::RoutestatsResponse> root_wrapper(
      response);
  rendered_root->SerializeInPlace(root_wrapper);
  ASSERT_EQ(protocol_response.extra, response.extra);

  handlers::ServiceLevel service_level_response;
  plugins::common::ResultWrapper<handlers::ServiceLevel> service_level_wrapper(
      service_level_response);
  rendered_service_level->SerializeInPlace(service_level_wrapper);
  ASSERT_EQ(service_level.extra, service_level_response.extra);
}

}  // namespace routestats::full
