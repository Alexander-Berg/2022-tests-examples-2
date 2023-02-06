#include <fstream>
#include <functional>

#include <boost/filesystem.hpp>

#include <testing/source_path.hpp>

#include <clients/order-core/client_mock_base.hpp>
#include <clients/order-core/requests.hpp>
#include <clients/order-core/responses.hpp>
#include <core/context/clients/clients_impl.hpp>
#include <endpoints/common/builders/service_level_builder.hpp>
#include <endpoints/common/core/alternative/extender.hpp>
#include <endpoints/common/core/protocol_request/extender.hpp>
#include <endpoints/common/presenters/alternatives.hpp>
#include <endpoints/full/builders/input_builder.hpp>
#include <endpoints/full/plugins/altpins_b/plugin.hpp>
#include <tests/context/translator_mock_test.hpp>
#include <tests/context_mock_test.hpp>

#include <userver/formats/json.hpp>
#include <userver/utest/utest.hpp>
#include <userver/utils/mock_now.hpp>

namespace {

const boost::filesystem::path kTestFilePath(
    utils::CurrentSourcePath("src/tests/endpoints/full/plugins/altpins_b"));
const std::string kTestDataDir = kTestFilePath.string() + "/static";

using ActiveOrdersRequest =
    clients::order_core::v1_tc_active_orders::get::Request;
using ActiveOrdersResponse =
    clients::order_core::v1_tc_active_orders::get::Response;

formats::json::Value LoadJsonFromFile(const std::string& filename) {
  std::ifstream f(filename);
  if (!f.is_open()) {
    throw std::runtime_error(std::string("Couldn't open file: ") + filename);
  }
  return formats::json::FromString(std::string(
      std::istreambuf_iterator<char>(f), std::istreambuf_iterator<char>()));
}

std::string StaticFilePath(const std::string& filename) {
  return kTestDataDir + std::string("/") + filename;
}

formats::json::Value GetAltpinsFiltersCfg() {
  return LoadJsonFromFile(StaticFilePath("exp_altpins_filters.json"));
}

formats::json::Value GetHideAltpinExp() {
  return LoadJsonFromFile(StaticFilePath("exp_hide_altpin.json"));
}

formats::json::Value GetAltpinBConfirmationScreenCfg() {
  return LoadJsonFromFile(
      StaticFilePath("exp_altpin_b_confirmation_screen.json"));
}

routestats::core::Configs3 MakeConfigs(bool confirmation_screen_failure) {
  experiments3::models::ExperimentResult altpins_filters{
      "altpins_filters", GetAltpinsFiltersCfg(), {}};
  experiments3::models::ExperimentResult altpin_b_confirmation_screen{
      "altpin_b_confirmation_screen", GetAltpinBConfirmationScreenCfg(), {}};

  std::unordered_map<std::string, experiments3::models::ExperimentResult>
      mapped_data{{"altpins_filters", altpins_filters}};
  if (!confirmation_screen_failure) {
    mapped_data["altpin_b_confirmation_screen"] = altpin_b_confirmation_screen;
  }
  return routestats::core::Configs3{{mapped_data}};
}

routestats::core::Experiments MakeExps() {
  experiments3::models::ExperimentResult hide_altpin{
      "hide_altpin", GetHideAltpinExp(), {}};
  std::unordered_map<std::string, experiments3::models::ExperimentResult>
      mapped_data{{"hide_altpin", hide_altpin}};
  return routestats::core::Experiments{{mapped_data}};
}

routestats::full::ProtocolResponse MakeProtocolResponse(
    std::vector<std::string> alternative_types) {
  routestats::full::ProtocolResponse protocol_response;
  protocol_response.alternatives.emplace();
  protocol_response.alternatives->options.emplace();
  protocol_response.alternatives->options->reserve(alternative_types.size());
  for (auto& type : alternative_types) {
    formats::json::ValueBuilder builder(
        LoadJsonFromFile(StaticFilePath("alternatives_options.json")));
    builder["type"] = type;

    auto alternative =
        builder.ExtractValue()
            .As<clients::protocol_routestats::AlternativesOption>();

    protocol_response.alternatives->options->push_back(std::move(alternative));

    if (type == "altpin_b") {
      formats::json::ValueBuilder builder_internal_data(
          LoadJsonFromFile(StaticFilePath("internal_data.json")));
      protocol_response.internal_data =
          builder_internal_data.ExtractValue()
              .As<clients::protocol_routestats::InternalData>();
    }
  }

  return protocol_response;
}

class OrderCoreClientMock : public clients::order_core::ClientMockBase {
 public:
  OrderCoreClientMock(bool has_active_order)
      : has_active_order(has_active_order) {}

  ActiveOrdersResponse V1TcActiveOrders(
      [[maybe_unused]] const ActiveOrdersRequest& request,
      [[maybe_unused]] const clients::order_core::CommandControl&)
      const override {
    if (!has_active_order) return ActiveOrdersResponse{};

    clients::order_core::ActiveOrder active_order;
    active_order.orderid = "a";
    ActiveOrdersResponse response;
    response.orders.push_back(active_order);
    return response;
  }

 private:
  bool has_active_order;
};

}  // namespace

namespace routestats::full {

namespace {

struct TagsTestParams {
  bool fields_in_state;
  bool tags_in_log;
};

routestats::full::ContextData MakeContext(
    OrderCoreClientMock&& order_core_client, const bool hide_altpin_exp,
    const TagsTestParams& tags_params, const bool banned_requirement,
    const bool confirmation_screen_failure = false) {
  auto context = routestats::test::full::GetDefaultContext();

  context.experiments = {{}, MakeConfigs(confirmation_screen_failure)};
  if (hide_altpin_exp) {
    context.experiments.uservices_routestats_exps = MakeExps();
  }

  context.clients.order_core =
      core::MakeClient<clients::order_core::Client>(order_core_client);
  context.user.auth_context.yandex_taxi_phoneid = "phoneid";

  auto& request = context.input.original_request;

  if (tags_params.fields_in_state) {
    request.state.emplace();
    if (tags_params.tags_in_log) {
      request.state->fields.push_back(
          {"b", "title",
           "{\"tags\":[\"org:rubric:name:Железнодорожный вокзал\"]}"});
    } else {
      request.state->fields.push_back({"b", "title", "{}"});
    }
  }

  request.tariff_requirements.emplace();
  if (banned_requirement) {
    formats::json::ValueBuilder builder;
    builder["class"] = "econom";
    {
      formats::json::ValueBuilder ski;
      ski["ski"] = true;
      builder["requirements"] = ski.ExtractValue();
    }

    handlers::RequestTariffRequirement tariff_requirement = handlers::Parse(
        builder.ExtractValue(),
        formats::parse::To<handlers::RequestTariffRequirement>{});

    request.tariff_requirements->push_back(std::move(tariff_requirement));
  }

  const auto point_a =
      ::geometry::Position{36.0 * ::geometry::lat, 55.0 * ::geometry::lon};
  const auto point_b =
      ::geometry::Position{36.2 * ::geometry::lat, 55.2 * ::geometry::lon};

  request.route = std::vector<::geometry::Position>{point_a, point_b};
  request.is_lightweight = false;

  const auto& input = context.input;
  context.input = routestats::full::BuildRoutestatsInput(
      request, input.tariff_requirements, input.supported_options);

  return context;
}

void DoCheck(bool preserved_after_modify_alternatives,
             bool has_confirmation_screen_after_root_rendering,
             const routestats::full::ContextData& context) {
  auto plugin_ctx = test::full::MakeTopLevelContext(context);

  auto [_, alternatives] =
      common::BuildModels(MakeProtocolResponse({"altpin_b"}));
  ASSERT_TRUE(alternatives.options.back()->altpin_b);

  auto plugin_ptr = std::make_shared<plugins::top_level::AltpinsBPlugin>();
  auto& plugin = *plugin_ptr;
  auto plugin_extensions = plugin.ModifyAlternatives(alternatives, plugin_ctx);

  std::vector<std::optional<core::AlternativeExtensionsMap>> extensions;
  extensions.push_back(plugin_extensions);

  core::ApplyAlternativesExtensions<decltype(plugin_ptr)>(
      {plugin_ptr}, extensions, alternatives);

  if (preserved_after_modify_alternatives) {
    for (const auto& alternative : alternatives.options) {
      ASSERT_TRUE(alternative);
      for (auto& service_level : alternative->service_levels) {
        ASSERT_TRUE(service_level.order_for_other_prohibited);
        ASSERT_TRUE(*service_level.order_for_other_prohibited);
      }
    }
  } else {
    for (const auto& alternative : alternatives.options) {
      ASSERT_FALSE(alternative);
    }
    return;
  }

  for (const auto& alternative : alternatives.options) {
    handlers::AlternativesOption option;
    core::alternatives::SerializeInView(*alternative, option,
                                        {} /* protocol_extra */);
    auto root_render =
        plugin.OnAlternativeOptionRootRendering(*alternative, plugin_ctx);

    plugins::common::ResultWrapper<handlers::AlternativesOption> root_wrapper(
        option);
    root_render->SerializeInPlace(root_wrapper);

    if (has_confirmation_screen_after_root_rendering) {
      ASSERT_TRUE(option.confirmation_screen);
    } else {
      ASSERT_FALSE(option.confirmation_screen);
    }
  }
}

}  // namespace

TEST(TestAltpinsBPlugin, AltpinsBFilterOrderForOtherProhibited) {
  RunInCoro([]() {
    OrderCoreClientMock order_core_client(false);
    auto context = MakeContext(std::move(order_core_client), false,
                               {false, false}, false, false);
    DoCheck(true, true, context);
  });
}

TEST(TestAltpinsBPlugin, AltpinsBFilterActiveOrder) {
  RunInCoro([]() {
    OrderCoreClientMock order_core_client(true);
    auto context = MakeContext(std::move(order_core_client), false,
                               {false, false}, false, false);
    DoCheck(false, false, context);
  });
}

TEST(TestAltpinsBPlugin, AltpinsBFilterHideAltpinExp) {
  RunInCoro([]() {
    OrderCoreClientMock order_core_client(false);
    auto context = MakeContext(std::move(order_core_client), true,
                               {false, false}, false, false);
    DoCheck(false, false, context);
  });
}

TEST(TestAltpinsBPlugin, AltpinsBFilterBannedTags) {
  RunInCoro([]() {
    OrderCoreClientMock order_core_client(false);
    auto context = MakeContext(std::move(order_core_client), false,
                               {true, true}, false, false);
    DoCheck(false, false, context);
  });
}

TEST(TestAltpinsBPlugin, AltpinsBFilterNoTagsInLog) {
  RunInCoro([]() {
    OrderCoreClientMock order_core_client(false);
    auto context = MakeContext(std::move(order_core_client), false,
                               {true, false}, false, false);
    DoCheck(true, true, context);
  });
}

TEST(TestAltpinsBPlugin, AltpinsBFilterBannedRequirements) {
  RunInCoro([]() {
    OrderCoreClientMock order_core_client(false);
    auto context = MakeContext(std::move(order_core_client), false,
                               {false, false}, true, false);
    ASSERT_EQ(context.input.original_request.tariff_requirements->at(0)
                  .requirements->extra.size(),
              1);
    DoCheck(false, false, context);
  });
}

TEST(TestAltpinsBPlugin, AltpinsBConfirmationScreenFailure) {
  RunInCoro([]() {
    OrderCoreClientMock order_core_client(false);
    auto context = MakeContext(std::move(order_core_client), false,
                               {false, false}, false, true);
    DoCheck(true, false, context);
  });
}

}  // namespace routestats::full
