#include <endpoints/full/plugins/verticals/verticals_selector.hpp>

#include <fmt/format.h>
#include <tests/context/translator_mock_test.hpp>
#include <tests/context_mock_test.hpp>
#include <tests/endpoints/common/service_level_mock_test.hpp>
#include <userver/utest/utest.hpp>

namespace routestats::plugins::verticals {
bool operator==(const Tariff& l_tariff, const Tariff& r_tariff) {
  return l_tariff.class_ == r_tariff.class_;
}

std::ostream& operator<<(std::ostream& os, const Tariff& tariff) {
  return os << tariff.class_;
}
namespace {
using SelectorTariff = experiments3::verticals_selector::Tariff;

struct TestGroupVertical
    : public experiments3::verticals_selector::GroupVertical {
  TestGroupVertical(const std::string& id_val,
                    const std::string& default_tariff_val,
                    const std::vector<SelectorTariff>& tariffs_val,
                    const bool tariffs_use_config_order_val) {
    type = experiments3::verticals_selector::GroupVerticalType::kGroup;
    title = "test_title";
    id = id_val;
    default_tariff = default_tariff_val;
    tariffs = tariffs_val;
    tariffs_use_config_order = tariffs_use_config_order_val;
  }
};

experiments3::VerticalsSelector::Value PrepareVerticalsSelectorSettings(
    const bool use_config_order) {
  experiments3::VerticalsSelector::Value selector_settings;

  TestGroupVertical delivery_vertical(
      "delivery", "express",
      {SelectorTariff{"cargo"}, SelectorTariff{"express"},
       SelectorTariff{"courier"}},
      use_config_order);
  selector_settings.verticals.emplace_back(delivery_vertical);

  TestGroupVertical ultima_vertical(
      "ultima", "business",
      {SelectorTariff{"business"}, SelectorTariff{"vip"},
       SelectorTariff{"maybach"}},
      use_config_order);
  selector_settings.verticals.emplace_back(ultima_vertical);

  selector_settings.rest_tariffs.id = "rest_tariffs";

  return selector_settings;
}

full::ContextData PrepareCtxData(const std::optional<std::vector<std::string>>&
                                     supported_verticals = std::nullopt) {
  full::ContextData ctx = test::full::GetDefaultContext();
  ctx.user.auth_context.locale = "ru";
  ctx.rendering = test::full::GetDefaultRendering();
  test::TranslationHandler handler =
      [](const core::Translation& translation,
         const std::string& locale) -> std::optional<std::string> {
    return translation->main_key.key + "##" + locale + "##" +
           translation->main_key.args["minimal_price"];
  };
  ctx.rendering.translator = std::make_shared<test::TranslatorMock>(handler);
  ctx.input.original_request.supported_verticals = supported_verticals;
  return ctx;
}

std::shared_ptr<const top_level::Context> GetContext() {
  return test::full::MakeTopLevelContext(PrepareCtxData());
}

void CheckResultVertical(const GroupVertical& vertical,
                         const std::string& expected_id,
                         const std::string& expected_default_tariff,
                         const std::vector<Tariff>& expected_tariffs,
                         const int expected_price) {
  ASSERT_EQ(vertical.core.id, expected_id);
  ASSERT_EQ(vertical.default_tariff, expected_default_tariff);
  ASSERT_EQ(vertical.core.tariffs, expected_tariffs);
  const std::string& expected_fmt_price = fmt::format(
      "interval_description##ru##{},0 $SIGN$$CURRENCY$", expected_price);
  ASSERT_EQ(vertical.formatted_price, expected_fmt_price);
}

core::ServiceLevel MockServiceLevel(std::string class_, core::Decimal price,
                                    bool is_hidden = false) {
  auto result = test::MockDefaultServiceLevel(class_);
  result.final_price = std::move(price);
  result.is_hidden = is_hidden;
  return result;
}

}  // namespace

UTEST(TestVerticalsPluginVerticalsSelector, HappyPath) {
  const auto service_levels = std::vector<core::ServiceLevel>{
      MockServiceLevel("vip", core::Decimal{500}),
      MockServiceLevel("business", core::Decimal{400}),
      MockServiceLevel("express", core::Decimal{200}),
      MockServiceLevel("cargo", core::Decimal{250}),
      MockServiceLevel("econom", core::Decimal{150}),
  };

  const bool use_config_order = true;
  const auto selector_settings =
      PrepareVerticalsSelectorSettings(use_config_order);
  const auto ctx = GetContext();
  const auto& verticals_selector = BuildVerticalsWithSelector(
      ctx->Get<VerticalsContext>(), service_levels, selector_settings);

  ASSERT_EQ(verticals_selector.size(), 3);

  const auto& ultima_vertical =
      std::get<GroupVertical>(verticals_selector.at(0));
  CheckResultVertical(ultima_vertical, "ultima", "business",
                      {Tariff{"business"}, Tariff{"vip"}}, 400);

  const auto& delivery_vertical =
      std::get<GroupVertical>(verticals_selector.at(1));
  CheckResultVertical(delivery_vertical, "delivery", "express",
                      {Tariff{"cargo"}, Tariff{"express"}}, 200);

  const auto& rest_tariffs_vertical =
      std::get<GroupVertical>(verticals_selector.at(2));
  CheckResultVertical(rest_tariffs_vertical, "rest_tariffs", "econom",
                      {Tariff{"econom"}}, 150);
}

UTEST(TestVerticalsPluginVerticalsSelector, NoDefaultTariffsOnSummary) {
  const auto service_levels = std::vector<core::ServiceLevel>{
      MockServiceLevel("vip", core::Decimal{500}),
      MockServiceLevel("maybach", core::Decimal{400}),
      MockServiceLevel("courier", core::Decimal{200}),
      MockServiceLevel("cargo", core::Decimal{250}),
      MockServiceLevel("econom", core::Decimal{150}),
  };

  const bool use_config_order = true;
  const auto selector_settings =
      PrepareVerticalsSelectorSettings(use_config_order);
  const auto& verticals_selector = BuildVerticalsWithSelector(
      GetContext()->Get<VerticalsContext>(), service_levels, selector_settings);

  ASSERT_EQ(verticals_selector.size(), 3);

  const auto& ultima_vertical =
      std::get<GroupVertical>(verticals_selector.at(0));
  CheckResultVertical(ultima_vertical, "ultima", "vip",
                      {Tariff{"vip"}, Tariff{"maybach"}}, 400);

  const auto& delivery_vertical =
      std::get<GroupVertical>(verticals_selector.at(1));
  CheckResultVertical(delivery_vertical, "delivery", "cargo",
                      {Tariff{"cargo"}, Tariff{"courier"}}, 200);

  const auto& rest_tariffs_vertical =
      std::get<GroupVertical>(verticals_selector.at(2));
  CheckResultVertical(rest_tariffs_vertical, "rest_tariffs", "econom",
                      {Tariff{"econom"}}, 150);
}

UTEST(TestVerticalsPluginVerticalsSelector, DoNotUseConfigOrder) {
  const auto service_levels = std::vector<core::ServiceLevel>{
      MockServiceLevel("vip", core::Decimal{500}),
      MockServiceLevel("business", core::Decimal{400}),
      MockServiceLevel("express", core::Decimal{200}),
      MockServiceLevel("cargo", core::Decimal{250}),
      MockServiceLevel("econom", core::Decimal{150}),
  };

  const bool use_config_order = false;
  const auto selector_settings =
      PrepareVerticalsSelectorSettings(use_config_order);

  const auto& verticals_selector = BuildVerticalsWithSelector(
      GetContext()->Get<VerticalsContext>(), service_levels, selector_settings);

  ASSERT_EQ(verticals_selector.size(), 3);

  const auto& ultima_vertical =
      std::get<GroupVertical>(verticals_selector.at(0));
  CheckResultVertical(ultima_vertical, "ultima", "business",
                      {Tariff{"vip"}, Tariff{"business"}}, 400);

  const auto& delivery_vertical =
      std::get<GroupVertical>(verticals_selector.at(1));
  CheckResultVertical(delivery_vertical, "delivery", "express",
                      {Tariff{"express"}, Tariff{"cargo"}}, 200);

  const auto& rest_tariffs_vertical =
      std::get<GroupVertical>(verticals_selector.at(2));
  CheckResultVertical(rest_tariffs_vertical, "rest_tariffs", "econom",
                      {Tariff{"econom"}}, 150);
}

UTEST(TestVerticalsPluginVerticalsSelector, SomeTariffsAreInvisible) {
  const auto service_levels = std::vector<core::ServiceLevel>{
      MockServiceLevel("vip", core::Decimal{500}, true /*is_hidden*/),
      MockServiceLevel("business", core::Decimal{400}),
      MockServiceLevel("express", core::Decimal{200}),
      MockServiceLevel("cargo", core::Decimal{250}, true /*is_hidden*/),
      MockServiceLevel("econom", core::Decimal{150}),
      MockServiceLevel("courier", core::Decimal{200}),
      MockServiceLevel("maybach", core::Decimal{800}),
  };

  const bool use_config_order = true;
  const auto selector_settings =
      PrepareVerticalsSelectorSettings(use_config_order);

  const auto ctx = GetContext();

  const auto& verticals_selector = BuildVerticalsWithSelector(
      ctx->Get<VerticalsContext>(), service_levels, selector_settings);

  ASSERT_EQ(verticals_selector.size(), 3);

  const auto& ultima_vertical =
      std::get<GroupVertical>(verticals_selector.at(0));
  CheckResultVertical(ultima_vertical, "ultima", "business",
                      {Tariff{"business"}, Tariff{"maybach"}}, 400);

  const auto& delivery_vertical =
      std::get<GroupVertical>(verticals_selector.at(1));
  CheckResultVertical(delivery_vertical, "delivery", "express",
                      {Tariff{"express"}, Tariff{"courier"}}, 200);

  const auto& rest_tariffs_vertical =
      std::get<GroupVertical>(verticals_selector.at(2));
  CheckResultVertical(rest_tariffs_vertical, "rest_tariffs", "econom",
                      {Tariff{"econom"}}, 150);
}

UTEST(TestVerticalsPluginVerticalsSelector,
      OneTariffVertical_MoveToRestTariffs) {
  // only courier is visible
  const auto service_levels = std::vector<core::ServiceLevel>{
      MockServiceLevel("vip", core::Decimal{500}, true /*is_hidden*/),
      MockServiceLevel("business", core::Decimal{400}, true /*is_hidden*/),
      MockServiceLevel("express", core::Decimal{200}),
      MockServiceLevel("cargo", core::Decimal{250}, true /*is_hidden*/),
      MockServiceLevel("econom", core::Decimal{150}),
      MockServiceLevel("courier", core::Decimal{200}),
      MockServiceLevel("maybach", core::Decimal{800}),
  };

  const bool use_config_order = true;
  auto selector_settings = PrepareVerticalsSelectorSettings(use_config_order);
  selector_settings.verticals[1].check_tariffs_number = true;

  const auto ctx = GetContext();

  const auto& verticals_selector = BuildVerticalsWithSelector(
      ctx->Get<VerticalsContext>(), service_levels, selector_settings);

  ASSERT_EQ(verticals_selector.size(), 2);

  const auto& rest_tariffs_vertical =
      std::get<GroupVertical>(verticals_selector.at(1));
  CheckResultVertical(rest_tariffs_vertical, "rest_tariffs", "econom",
                      {Tariff{"econom"}, Tariff{"maybach"}}, 150);
}

UTEST(TestVerticalsPluginVerticalsSelector, OneTariffVertical_RemoveVertical) {
  const auto service_levels = std::vector<core::ServiceLevel>{
      MockServiceLevel("cargo", core::Decimal{250}, true /*is_hidden*/),
      MockServiceLevel("express", core::Decimal{200}),
      MockServiceLevel("courier", core::Decimal{200}),

      MockServiceLevel("vip", core::Decimal{500}, true /*is_hidden*/),
      MockServiceLevel("business", core::Decimal{400}, true /*is_hidden*/),
      MockServiceLevel("maybach", core::Decimal{800}),

      MockServiceLevel("econom", core::Decimal{150}),
  };

  const bool use_config_order = true;
  auto selector_settings = PrepareVerticalsSelectorSettings(use_config_order);
  selector_settings.verticals[1].check_tariffs_number = true;
  selector_settings.verticals[0].tariffs.push_back(SelectorTariff{"maybach"});

  const auto ctx = GetContext();

  const auto& verticals_selector = BuildVerticalsWithSelector(
      ctx->Get<VerticalsContext>(), service_levels, selector_settings);

  ASSERT_EQ(verticals_selector.size(), 2);

  const auto& delivery_vertical =
      std::get<GroupVertical>(verticals_selector.at(0));
  CheckResultVertical(delivery_vertical, "delivery", "express",
                      {Tariff{"express"}, Tariff{"courier"}, Tariff{"maybach"}},
                      200);

  const auto& rest_tariffs_vertical =
      std::get<GroupVertical>(verticals_selector.at(1));
  CheckResultVertical(rest_tariffs_vertical, "rest_tariffs", "econom",
                      {Tariff{"econom"}}, 150);
}

UTEST(TestVerticalsPluginVerticalsSelector,
      SupportedVerticals_MoveToTaxiVertical) {
  const auto service_levels = std::vector<core::ServiceLevel>{
      MockServiceLevel("cargo", core::Decimal{250}, true /*is_hidden*/),
      MockServiceLevel("express", core::Decimal{200}),
      MockServiceLevel("courier", core::Decimal{200}),

      MockServiceLevel("vip", core::Decimal{500}, true /*is_hidden*/),
      MockServiceLevel("business", core::Decimal{400}, true /*is_hidden*/),
      MockServiceLevel("maybach", core::Decimal{800}),

      MockServiceLevel("econom", core::Decimal{150}),
  };

  const bool use_config_order = true;
  auto selector_settings = PrepareVerticalsSelectorSettings(use_config_order);
  ASSERT_EQ(selector_settings.verticals[0].id, "delivery");
  selector_settings.verticals[0].tariffs.emplace_back(
      SelectorTariff{"maybach"});
  selector_settings.verticals[0].tariffs.emplace_back(SelectorTariff{"econom"});

  // typical verticals_selector has taxi as 1st vertical
  selector_settings.verticals.insert(
      selector_settings.verticals.begin(),
      TestGroupVertical{"taxi",
                        "taxi",
                        {SelectorTariff{"econom"}, SelectorTariff{"express"}},
                        use_config_order});

  auto ctx = test::full::MakeTopLevelContext(PrepareCtxData(
      std::optional<std::vector<std::string>>({"taxi", "ultima"})));

  const auto& verticals_selector = BuildVerticalsWithSelector(
      ctx->Get<VerticalsContext>(), service_levels, selector_settings);

  ASSERT_EQ(verticals_selector.size(), 2);

  const auto& ultima_vertical =
      std::get<GroupVertical>(verticals_selector.at(0));
  CheckResultVertical(ultima_vertical, "ultima", "maybach", {Tariff{"maybach"}},
                      800);

  const auto& taxi_vertical = std::get<GroupVertical>(verticals_selector.at(1));
  CheckResultVertical(taxi_vertical, "taxi", "econom",
                      {Tariff{"econom"}, Tariff{"express"}, Tariff{"courier"}},
                      150);
}

UTEST(TestVerticalsPluginVerticalsSelector,
      SupportedVerticals_RemoveTariffsWhenTaxiVerticalDoesNotExists) {
  const auto service_levels = std::vector<core::ServiceLevel>{
      MockServiceLevel("cargo", core::Decimal{250}, true /*is_hidden*/),
      MockServiceLevel("express", core::Decimal{200}),
      MockServiceLevel("courier", core::Decimal{200}),

      MockServiceLevel("vip", core::Decimal{500}, true /*is_hidden*/),
      MockServiceLevel("business", core::Decimal{400}, true /*is_hidden*/),
      MockServiceLevel("maybach", core::Decimal{800}),

      MockServiceLevel("econom", core::Decimal{150}),
  };

  const bool use_config_order = true;
  auto selector_settings = PrepareVerticalsSelectorSettings(use_config_order);

  selector_settings.verticals[0].tariffs.push_back(SelectorTariff{"econom"});

  auto ctx = test::full::MakeTopLevelContext(
      PrepareCtxData(std::optional<std::vector<std::string>>({"ultima"})));

  const auto& verticals_selector = BuildVerticalsWithSelector(
      ctx->Get<VerticalsContext>(), service_levels, selector_settings);

  ASSERT_EQ(verticals_selector.size(), 1);

  const auto& ultima_vertical =
      std::get<GroupVertical>(verticals_selector.at(0));
  CheckResultVertical(ultima_vertical, "ultima", "maybach", {Tariff{"maybach"}},
                      800);
}

UTEST(TestVerticalsPluginVerticalsSelector, DropByRequirementOverrides) {
  const auto service_levels = std::vector<core::ServiceLevel>{
      MockServiceLevel("child_tariff", core::Decimal{200}),
      MockServiceLevel("business", core::Decimal{200}),
      MockServiceLevel("vip", core::Decimal{800}),
  };

  const experiments3::VerticalsSelector::Value selector_settings = []() {
    experiments3::VerticalsSelector::Value selector_settings;

    TestGroupVertical child_vertical(
        "child", "child_tariff",
        {SelectorTariff{"child_tariff"}, SelectorTariff{"business"},
         SelectorTariff{"vip"}},
        true);
    experiments3::verticals_selector::Requirement ro;
    ro.name = "childchair_v2";
    child_vertical.requirement_overrides = {std::move(ro)};
    selector_settings.verticals.emplace_back(std::move(child_vertical));
    selector_settings.rest_tariffs.id = "rest_tariffs";

    return selector_settings;
  }();

  auto ctx_data =
      PrepareCtxData(std::optional<std::vector<std::string>>({"child"}));

  const auto MakeCategory = [](const std::string& name, bool has_chair = true) {
    clients::taxi_tariffs::Category cat;
    cat.name = name;
    if (has_chair) cat.client_requirements = {"childchair_v2"};
    return cat;
  };
  ctx_data.zone = core::Zone{};
  auto& tariff_settings = ctx_data.zone->tariff_settings;
  tariff_settings.categories = {MakeCategory("child_tariff"),
                                MakeCategory("business"),
                                MakeCategory("vip", false)};  // no chairs

  auto ctx = test::full::MakeTopLevelContext(std::move(ctx_data));

  const auto& verticals_selector = BuildVerticalsWithSelector(
      ctx->Get<VerticalsContext>(), service_levels, selector_settings);

  ASSERT_EQ(verticals_selector.size(), 1);

  const auto& child_vertical =
      std::get<GroupVertical>(verticals_selector.at(0));
  CheckResultVertical(child_vertical, "child", "child_tariff",
                      {Tariff{"child_tariff"}, Tariff{"business"}}, 200);
}

}  // namespace routestats::plugins::verticals
