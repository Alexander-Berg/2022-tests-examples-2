#include <endpoints/full/plugins/subtitle/subplugins/subtitle_proxy.hpp>

#include <clients/protocol-routestats/responses.hpp>
#include <tests/context_mock_test.hpp>
#include <userver/utest/utest.hpp>

namespace routestats::plugins::subtitle {

namespace {

ProtocolResponse GetBasicTestProtocolResponse(
    const std::string& class_, const std::optional<::std::string>& subtitle) {
  ProtocolResponse protocol_response;
  clients::protocol_routestats::ServiceLevel service_level;
  service_level.class_ = class_;
  service_level.subtitle = subtitle;
  protocol_response.service_levels.push_back(service_level);
  return protocol_response;
}

}  // namespace

void TestSubtitleProxyPlugin(
    const std::string& class_, const std::optional<std::string>& subtitle,
    const std::optional<std::string>& expected_subtitle) {
  SubtitleProxyPlugin plugin;
  ProtocolResponse protocol_response =
      GetBasicTestProtocolResponse(class_, subtitle);
  plugin.OnGotProtocolResponse(protocol_response);
  const auto context =
      test::full::MakeTopLevelContext(test::full::GetDefaultContext());
  const std::optional<std::string>& result_subtitle =
      plugin.GetSubtitle(class_, context);
  ASSERT_EQ(result_subtitle, expected_subtitle);
}

TEST(SubtitleProxyPlugin, valid) {
  TestSubtitleProxyPlugin("econom", "some_subtitle", "some_subtitle");
}

TEST(TitleProxyPlugin, empty) {
  TestSubtitleProxyPlugin("econom", std::nullopt, std::nullopt);
}

}  // namespace routestats::plugins::subtitle
