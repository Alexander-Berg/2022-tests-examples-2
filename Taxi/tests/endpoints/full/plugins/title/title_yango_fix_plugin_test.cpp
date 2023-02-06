#include <endpoints/full/plugins/title/subplugins/title_yango_fix.hpp>
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

void TestTitleYangoFixPlugin(const std::string& class_,
                             const std::optional<std::string>& title,
                             const std::optional<std::string>& expected_title) {
  TitleYangoFixPlugin plugin;
  ProtocolResponse protocol_response =
      GetBasicTestProtocolResponse(class_, title);
  plugin.OnGotProtocolResponse(protocol_response);
  const auto result_title = plugin.GetTitle(
      class_, test::full::MakeTopLevelContext(test::full::GetDefaultContext()));
  ASSERT_EQ(result_title, expected_title);
}

TEST(TitleYangoFixPlugin, valid) {
  TestTitleYangoFixPlugin("express", "some_title", "some_title");
}

TEST(TitleYangoFixPlugin, unrelated_tariff) {
  TestTitleYangoFixPlugin("econom", "some_title", std::nullopt);
}

TEST(TitleYangoFixPlugin, unrelated_tariff_missing_title) {
  TestTitleYangoFixPlugin("econom", std::nullopt, std::nullopt);
}

TEST(TitleYangoFixPlugin, empty) { TestTitleYangoFixPlugin("express", "", ""); }

TEST(TitleYangoFixPlugin, missing) {
  TestTitleYangoFixPlugin("express", std::nullopt, "");
}

}  // namespace routestats::full::title
