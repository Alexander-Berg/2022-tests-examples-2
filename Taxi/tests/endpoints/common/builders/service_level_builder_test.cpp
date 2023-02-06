#include <endpoints/common/builders/service_level_builder.hpp>
#include <endpoints/common/core/service_level/price_utils.hpp>
#include <userver/utest/utest.hpp>

namespace routestats::common {

using InternalLevelData =
    clients::protocol_routestats::InternalServiceLevelData;
using LevelData = clients::protocol_routestats::AlternativesOptionServiceLevel;
using AlternativesOption = clients::protocol_routestats::AlternativesOption;
using InternalAlternative = clients::protocol_routestats::InternalAlternative;

InternalLevelData MockServiceInternalLevelData(const std::string& name,
                                               const std::string& price) {
  InternalLevelData level_data;
  level_data.class_ = name;
  level_data.final_price = price;
  return level_data;
}

InternalAlternative MockServiceInternalAlternative(
    const std::string& name, const std::vector<InternalLevelData>& levels) {
  InternalAlternative alternative;
  alternative.type = name;
  alternative.service_levels_data = levels;
  return alternative;
}

LevelData MockAlternativeServiceLevelData(const std::string& name,
                                          const std::string& price) {
  LevelData level_data;
  level_data.class_ = name;
  level_data.price = price;
  return level_data;
}

AlternativesOption MockAlternativesOption(
    const std::string& type, const std::string& time,
    const std::vector<LevelData>& levels) {
  AlternativesOption option;
  option.type = type;
  option.time = time;
  option.service_levels = levels;
  return option;
}

ProtocolResponse MockProtocolResponse() {
  using clients::protocol_routestats::EstimatedWaiting;

  ProtocolResponse response;
  response.service_levels.push_back({"econom", std::nullopt, true});
  response.service_levels.push_back({"maybah", std::nullopt, std::nullopt,
                                     std::nullopt,
                                     EstimatedWaiting{60, "1 min"}});
  response.service_levels.push_back(
      {"vip", std::nullopt, false, false, EstimatedWaiting{120, "2 min"}});

  response.internal_data.service_levels_data = {
      MockServiceInternalLevelData("econom", "300"),
      MockServiceInternalLevelData("vip", "400"),
      MockServiceInternalLevelData("maybah", "423av5hxx"),
  };

  response.internal_data.alternatives = {MockServiceInternalAlternative(
      "explicit_antisurge", {MockServiceInternalLevelData("econom", "400")})};

  response.alternatives.emplace();
  response.alternatives->options = {MockAlternativesOption(
      "explicit_antisurge", "some_alternative_time",
      {
          MockAlternativeServiceLevelData("econom", "300"),
          MockAlternativeServiceLevelData("comfort", "600"),
      })};
  return response;
}

TEST(BuildServiceLevels, Simple) {
  ProtocolResponse response = MockProtocolResponse();

  auto [service_levels, alternatives] = common::BuildModels(response);
  auto result = service_levels;

  ASSERT_EQ(result.size(), 3);

  auto econom = result[0];
  ASSERT_EQ(*econom.final_price, core::Decimal{300});
  ASSERT_EQ(econom.eta, std::nullopt);
  ASSERT_EQ(core::service_level::IsFixedPrice(econom), true);

  auto maybah = result[1];
  ASSERT_EQ(maybah.final_price, std::nullopt);
  ASSERT_EQ(maybah.eta->message, "1 min");
  ASSERT_EQ(maybah.eta->seconds, 60);
  ASSERT_EQ(core::service_level::IsFixedPrice(maybah), false);

  auto vip = result[2];
  ASSERT_EQ(*vip.final_price, core::Decimal{400});
  ASSERT_EQ(vip.eta->message, "2 min");
  ASSERT_EQ(vip.eta->seconds, 120);
  ASSERT_EQ(core::service_level::IsFixedPrice(vip), false);

  ASSERT_EQ(alternatives.options.size(), 1);
  ASSERT_EQ(alternatives.options[0]->time, "some_alternative_time");
  ASSERT_EQ(alternatives.options[0]->service_levels.size(), 2);

  const auto& econom_level = alternatives.options[0]->service_levels[0];
  ASSERT_EQ(econom_level.class_, "econom");
  ASSERT_EQ(econom_level.final_price, core::Decimal{400});
  ASSERT_EQ(econom_level.price, "300");

  const auto& comfort_level = alternatives.options[0]->service_levels[1];
  ASSERT_EQ(comfort_level.class_, "comfort");
  ASSERT_EQ(comfort_level.final_price, std::nullopt);
  ASSERT_EQ(comfort_level.price, "600");
}

}  // namespace routestats::common
