#include <endpoints/full/plugins/title/subplugins/title_proxy.hpp>
#include <tests/context_mock_test.hpp>

#include <clients/protocol-routestats/responses.hpp>
#include <userver/utest/utest.hpp>

namespace routestats::full::title {

namespace {

using plugins::top_level::ProtocolResponse;

ProtocolResponse GetBasicTestProtocolResponse(
    const std::string& class_, const std::optional<::std::string>& title) {
  ProtocolResponse protocol_response;
  clients::protocol_routestats::ServiceLevel service_level;
  service_level.class_ = class_;
  service_level.title = title;
  protocol_response.service_levels.push_back(service_level);
  return protocol_response;
}

}  // namespace

void TestTitleProxyPlugin(const std::string& class_,
                          const std::optional<std::string>& title,
                          const std::string& expected_title) {
  TitleProxyPlugin plugin;
  ProtocolResponse protocol_response =
      GetBasicTestProtocolResponse(class_, title);
  plugin.OnGotProtocolResponse(protocol_response);
  const auto result_title = plugin.GetTitle(
      class_, test::full::MakeTopLevelContext(test::full::GetDefaultContext()));
  ASSERT_EQ(result_title, expected_title);
}

TEST(TitleProxyPlugin, valid) {
  TestTitleProxyPlugin("econom", "some_title", "some_title");
}

TEST(TitleProxyPlugin, empty) { TestTitleProxyPlugin("econom", "", ""); }

}  // namespace routestats::full::title
