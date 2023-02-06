#include <chrono>
#include <fstream>
#include <functional>

#include <boost/filesystem.hpp>

#include <userver/crypto/base64.hpp>
#include <userver/formats/bson.hpp>
#include <userver/formats/json.hpp>
#include <userver/utest/utest.hpp>

#include <testing/source_path.hpp>

#include <clients/alt-offer-discount/client_mock_base.hpp>
#include <taxi_config/variables/MIN_ESTIMATED_WAITING.hpp>

#include <core/context/clients/clients_impl.hpp>
#include <endpoints/common/builders/service_level_builder.hpp>
#include <endpoints/common/core/alternative/extender.hpp>
#include <endpoints/common/core/protocol_request/extender.hpp>
#include <endpoints/common/presenters/alternatives.hpp>
#include <endpoints/full/plugins/perfect_chain/plugin.hpp>
#include <tests/context/taxi_config_mock_test.hpp>
#include <tests/context/translator_mock_test.hpp>
#include <tests/context_mock_test.hpp>

namespace {

const boost::filesystem::path kTestFilePath(
    utils::CurrentSourcePath("src/tests/endpoints/full/plugins/perfect_chain"));
const std::string kTestDataDir = kTestFilePath.string() + "/static/";
const std::string kSuffixExpJson = "_exp.json";

const std::string kPerfectChain = "perfect_chain";
const std::string kIcon = "icon";

const std::string kResponseDecorationExp = "perfect_chain_response_decoration";
const std::string kEtaExp = "perfect_chain_routestats_eta_fallback";
const std::string kDisplaySettings = "perfect_chain_display_settings";
const std::string kOffersInfoExp = "perfect_chain_routestats_offers_info";
const std::string kDisabledExp = "disabled";

formats::json::Value LoadJsonFromFile(const std::string& filename) {
  std::ifstream f(filename);
  if (!f.is_open()) {
    throw std::runtime_error(fmt::format("Couldn't open file '{}'", filename));
  }
  return formats::json::FromString(std::string(
      std::istreambuf_iterator<char>(f), std::istreambuf_iterator<char>()));
}

struct MockExperiment {
  std::string name;
  std::string file_name;
};

}  // namespace

namespace routestats::full::perfect_chain {

namespace {

using OffersInfoResponse =
    ::clients::alt_offer_discount::v1_offers_info::post::Response;
using OffersInfoRequest =
    ::clients::alt_offer_discount::v1_offers_info::post::Request;
using OffersInfoA = ::clients::alt_offer_discount::OffersInfoA;
using PerfectChainAlternative =
    ::clients::alt_offer_discount::PerfectChainAlternative;

struct ContextOverrides {
  Experiments experiments;
  OffersInfoResponse offers_info_response;
  std::function<void(const OffersInfoRequest&)> offers_info_validator;
};

void CheckCommandControlOffersInfo(
    const ::clients::alt_offer_discount::CommandControl& command_control) {
  ASSERT_EQ(command_control.timeout.value().count(), 30);
  ASSERT_EQ(command_control.retries.value(), 1);
}

class OffersInfoMock : public ::clients::alt_offer_discount::ClientMockBase {
 public:
  OffersInfoMock(
      const OffersInfoResponse& response = {},
      std::function<void(const OffersInfoRequest&)> request_validator =
          [](const auto&) { return; })
      : request_validator_(request_validator), response_(response) {}

  static std::shared_ptr<OffersInfoMock> CreateClientPtr(
      const OffersInfoResponse& response,
      std::function<void(const OffersInfoRequest&)> request_validator =
          [](const auto&) { return; }) {
    return std::make_shared<OffersInfoMock>(response, request_validator);
  }

  OffersInfoResponse V1OffersInfo(
      const OffersInfoRequest& request,
      const ::clients::alt_offer_discount::CommandControl& command_control)
      const {
    CheckCommandControlOffersInfo(command_control);
    request_validator_(request);
    return response_;
  }

 private:
  std::function<void(const OffersInfoRequest&)> request_validator_;
  OffersInfoResponse response_;
};

core::ExpMappedData MakeMappedData(std::vector<MockExperiment> experiments) {
  std::unordered_map<std::string, experiments3::models::ExperimentResult>
      mapped_data;

  for (const auto& experiment : experiments) {
    mapped_data[experiment.name] = experiments3::models::ExperimentResult{
        experiment.name,
        LoadJsonFromFile(kTestDataDir + std::move(experiment.file_name)),
        {}};
  }

  return mapped_data;
}

core::TaxiConfigsPtr MakeConfigs() {
  auto config_storage = dynamic_config::MakeDefaultStorage({
      {taxi_config::MIN_ESTIMATED_WAITING, 120},
  });

  return std::make_shared<test::TaxiConfigsMock>(std::move(config_storage));
}

OffersInfoResponse MakeOffersInfoResponse(size_t eta_sec) {
  OffersInfoResponse offers_info_response;
  offers_info_response.offers_info.push_back(
      OffersInfoA(PerfectChainAlternative{
          clients::alt_offer_discount::AltOfferType::kPerfectChain,
          {std::chrono::seconds(eta_sec)}}));
  return offers_info_response;
}

ContextOverrides MakeContextOverrides(
    std::vector<MockExperiment> configs,
    std::vector<MockExperiment> experiments,
    OffersInfoResponse offers_info_response = {},
    std::function<void(const OffersInfoRequest&)> offers_info_validator =
        [](const auto&) { return; }) {
  ContextOverrides context_overrides;

  context_overrides.experiments = {{MakeMappedData(std::move(experiments))},
                                   {{MakeMappedData(std::move(configs))}}};

  context_overrides.offers_info_response = std::move(offers_info_response);
  context_overrides.offers_info_validator = offers_info_validator;
  return context_overrides;
}

std::shared_ptr<const ::routestats::plugins::top_level::Context> MakeContext(
    ContextOverrides context_overrides,
    std::shared_ptr<OffersInfoMock> offers_info_mock) {
  auto context = routestats::test::full::GetDefaultContext();

  context.user.auth_context.locale = "ru";

  context.experiments = context_overrides.experiments;

  context.clients.alt_offer_discount =
      core::MakeClient<::clients::alt_offer_discount::Client>(
          *offers_info_mock);

  test::TranslationHandler translation_handler =
      [](const core::Translation& translation,
         const std::string& locale) -> std::optional<std::string> {
    std::vector<std::string> args;
    for (const auto& [key, value] : translation->main_key.args) {
      args.push_back(fmt::format("{}:{}", key, value));
    }

    std::sort(args.begin(), args.end());

    return fmt::format("{}##[{}]##{}", translation->main_key.key,
                       fmt::join(args, ","), locale);
  };

  context.rendering.translator =
      std::make_shared<test::TranslatorMock>(translation_handler);
  context.taxi_configs = MakeConfigs();

  return test::full::MakeTopLevelContext(context);
}

ProtocolResponse MakeProtocolResponse(
    std::vector<std::string> alternative_types) {
  ProtocolResponse protocol_response;
  protocol_response.alternatives.emplace();
  protocol_response.alternatives->options.emplace();
  protocol_response.alternatives->options->reserve(alternative_types.size());
  for (auto& type : alternative_types) {
    formats::json::ValueBuilder builder(
        LoadJsonFromFile(kTestDataDir + "alternatives_options.json"));
    builder["type"] = type;

    auto alternative =
        builder.ExtractValue()
            .As<clients::protocol_routestats::AlternativesOption>();

    protocol_response.alternatives->options->push_back(std::move(alternative));
  }

  if (std::find(alternative_types.begin(), alternative_types.end(),
                kPerfectChain) != alternative_types.end()) {
    auto& prepared_altoffers =
        protocol_response.internal_data.prepared_altoffers;
    if (!prepared_altoffers) {
      prepared_altoffers.emplace();
    }

    formats::bson::ValueBuilder builder;
    formats::bson::ValueBuilder item;
    item["pricing_data"]["links"]["prepare"] = "request_id";
    builder["prices"].PushBack(std::move(item));
    const auto& binary_string = crypto::base64::Base64Encode(
        formats::bson::ToBinaryString(builder.ExtractValue()).ToString());

    prepared_altoffers->push_back({binary_string, kPerfectChain});
  }

  return protocol_response;
}

void CheckProtocolRequest(const ProtocolRequestBody& protocol_request) {
  ASSERT_EQ(protocol_request.feature_flags.has_value(), true);
  ASSERT_EQ(protocol_request.feature_flags->prepare_altoffers.has_value(),
            true);
  const auto& prepare_altoffers =
      *protocol_request.feature_flags->prepare_altoffers;
  ASSERT_EQ(prepare_altoffers.size(), 1);
  ASSERT_EQ(prepare_altoffers[0], kPerfectChain);
}

handlers::RoutestatsResponse MakeRoutestatsResponse(
    ContextOverrides context_overrides, ProtocolResponse protocol_response) {
  auto offers_info_ptr =
      OffersInfoMock::CreateClientPtr(context_overrides.offers_info_response,
                                      context_overrides.offers_info_validator);

  auto plugin_context =
      MakeContext(std::move(context_overrides), offers_info_ptr);

  using plugins::top_level::PerfectChainPlugin;

  auto [service_levels, alternatives] = common::BuildModels(protocol_response);

  auto plugin_ptr = std::make_shared<PerfectChainPlugin>();
  auto& plugin = *plugin_ptr;
  std::vector<std::shared_ptr<PerfectChainPlugin>> plugins{plugin_ptr};

  plugin.OnContextBuilt(plugin_context);

  ProtocolRequestBody protocol_request;
  std::vector<std::optional<ProtocolRequestExtensions>> request_extensions;
  request_extensions.push_back(
      plugin.ModifyProtocolRequestBody(protocol_request, plugin_context));
  core::ApplyProtocolRequestExtensions(plugins, request_extensions,
                                       protocol_request);

  CheckProtocolRequest(protocol_request);

  plugin.OnGotProtocolResponse(plugin_context, protocol_response);

  auto plugin_extensions =
      plugin.ModifyAlternatives(alternatives, plugin_context);

  std::vector<std::optional<core::AlternativeExtensionsMap>> extensions;
  extensions.push_back(plugin_extensions);

  core::ApplyAlternativesExtensions<decltype(plugin_ptr)>(
      {plugin_ptr}, extensions, alternatives);

  handlers::RoutestatsResponse response;

  std::vector<handlers::AlternativesOption> response_options;
  for (const auto& opt : alternatives.options) {
    if (!opt) continue;

    handlers::AlternativesOption option;

    core::alternatives::SerializeInView(*opt, option, {} /* protocol_extra */);

    auto root_render =
        plugin.OnAlternativeOptionRootRendering(*opt, plugin_context);

    if (root_render) {
      plugins::common::ResultWrapper<handlers::AlternativesOption> root_wrapper(
          option);
      root_render->SerializeInPlace(root_wrapper);
    }

    if (opt->service_levels.size()) {
      option.service_levels.emplace();
    }

    for (const auto& sl : opt->service_levels) {
      handlers::AlternativesOptionServiceLevel service_level;

      core::alternatives::service_level::SerializeInView(
          sl, service_level, {} /* protocol_extra */);

      auto sl_render = plugin.OnAlternativeOptionServiceLevelRendering(
          *opt, sl, plugin_context);
      if (!sl_render) continue;

      plugins::common::ResultWrapper<handlers::AlternativesOptionServiceLevel>
          sl_wrapper(service_level);
      sl_render->SerializeInPlace(sl_wrapper);

      option.service_levels->push_back(std::move(service_level));
    }

    response_options.push_back(std::move(option));
  }

  if (!response_options.empty()) {
    response.alternatives.emplace().options = response_options;
  }
  return response;
}

void CheckBase(const RoutestatsResponse& response, const int eta_sec,
               const int eta_min) {
  ASSERT_EQ(response.alternatives.has_value(), true);
  ASSERT_EQ(response.alternatives->options.has_value(), true);
  const auto& alternatives = *response.alternatives->options;
  ASSERT_EQ(alternatives.size(), 2);

  const auto& perfect_chain = alternatives[0];

  ASSERT_TRUE(perfect_chain.service_levels.has_value());

  const auto& service_level = (*perfect_chain.service_levels)[0];

  ASSERT_TRUE(service_level.estimated_waiting);
  ASSERT_EQ(service_level.estimated_waiting->seconds, eta_sec);
  ASSERT_EQ(service_level.estimated_waiting->message,
            fmt::format("estimated_waiting_message##[eta:{},eta_min:{}]##ru",
                        eta_min, eta_min));

  ASSERT_TRUE(service_level.selector.has_value());
  ASSERT_TRUE(service_level.selector->icon.has_value());

  const auto& icon = service_level.selector->icon;
  ASSERT_EQ(icon->url, "new_url");
  ASSERT_EQ(icon->size_hint, 390);

  ASSERT_TRUE(icon->url_parts.has_value());
  ASSERT_EQ(icon->url_parts->key, "TC");
  ASSERT_EQ(icon->url_parts->path, "url_parts_path");

  ASSERT_EQ(service_level.selector->tooltip,
            fmt::format("tooltip##[eta:{},eta_min:{}]##ru", eta_min, eta_min));

  ASSERT_TRUE(service_level.extra["paid_options"].IsNull());

  ASSERT_TRUE(perfect_chain.show_in_tariff_selector);
  ASSERT_TRUE(*perfect_chain.show_in_tariff_selector);
  ASSERT_TRUE(perfect_chain.use_for_promos_on_summary);
  ASSERT_FALSE(*perfect_chain.use_for_promos_on_summary);
}

}  // namespace

UTEST(PerfectChainPlugin, Base) {
  std::vector<MockExperiment> configs = {
      {kResponseDecorationExp, kResponseDecorationExp + kSuffixExpJson},
      {kEtaExp, kEtaExp + kSuffixExpJson},
      {kDisplaySettings, kDisplaySettings + kSuffixExpJson},
      {kOffersInfoExp, kOffersInfoExp + kSuffixExpJson}};
  auto context_overrides = MakeContextOverrides(
      configs, {}, MakeOffersInfoResponse(179), [](const auto& request) {
        ASSERT_EQ(request.body.request_id, "request_id");
        ASSERT_EQ(request.body.alternatives.size(), 1);
        ASSERT_EQ(request.body.alternatives[0].type,
                  clients::alt_offer_discount::AltOfferType::kPerfectChain);
      });

  const auto response =
      MakeRoutestatsResponse(std::move(context_overrides),
                             MakeProtocolResponse({kPerfectChain, "other"}));

  CheckBase(response, 120, 2);
}

UTEST(PerfectChainPlugin, OffersInfoFallback) {
  auto context_overrides = MakeContextOverrides(
      {{kResponseDecorationExp, kResponseDecorationExp + kSuffixExpJson},
       {kEtaExp, kEtaExp + kSuffixExpJson},
       {kDisplaySettings, kDisplaySettings + kSuffixExpJson},
       {kOffersInfoExp, kDisabledExp + kSuffixExpJson}},
      {}, MakeOffersInfoResponse(88));

  const auto response =
      MakeRoutestatsResponse(std::move(context_overrides),
                             MakeProtocolResponse({kPerfectChain, "other"}));

  CheckBase(response, 900, 15);
}

UTEST(PerfectChainPlugin, OffersInfoException) {
  auto context_overrides = MakeContextOverrides(
      {{kResponseDecorationExp, kResponseDecorationExp + kSuffixExpJson},
       {kEtaExp, kEtaExp + kSuffixExpJson},
       {kDisplaySettings, kDisplaySettings + kSuffixExpJson},
       {kOffersInfoExp, kOffersInfoExp + kSuffixExpJson}},
      {}, MakeOffersInfoResponse(99), [](const auto&) {
        throw clients::alt_offer_discount::v1_offers_info::post::Exception{};
      });

  const auto response =
      MakeRoutestatsResponse(std::move(context_overrides),
                             MakeProtocolResponse({kPerfectChain, "other"}));

  CheckBase(response, 900, 15);
}

UTEST(PerfectChainPlugin, NoPreparedOffer) {
  auto context_overrides = MakeContextOverrides(
      {{kResponseDecorationExp, kResponseDecorationExp + kSuffixExpJson},
       {kEtaExp, kEtaExp + kSuffixExpJson},
       {kDisplaySettings, kDisplaySettings + kSuffixExpJson},
       {kOffersInfoExp, kOffersInfoExp + kSuffixExpJson}},
      {}, MakeOffersInfoResponse(99));

  auto protocol_response = MakeProtocolResponse({kPerfectChain, "other"});
  protocol_response.internal_data.prepared_altoffers.value().clear();

  const auto response = MakeRoutestatsResponse(std::move(context_overrides),
                                               std::move(protocol_response));

  ASSERT_EQ(response.alternatives->options.value()[0].type, "other");
}

UTEST(PerfectChainPlugin, NoPricingLink) {
  auto context_overrides = MakeContextOverrides(
      {{kResponseDecorationExp, kResponseDecorationExp + kSuffixExpJson},
       {kEtaExp, kEtaExp + kSuffixExpJson},
       {kDisplaySettings, kDisplaySettings + kSuffixExpJson},
       {kOffersInfoExp, kOffersInfoExp + kSuffixExpJson}},
      {}, MakeOffersInfoResponse(99));

  auto protocol_response = MakeProtocolResponse({kPerfectChain, "other"});

  formats::bson::ValueBuilder builder;
  builder["prices"] = formats::bson::MakeArray();
  const auto& binary_string = crypto::base64::Base64Encode(
      formats::bson::ToBinaryString(builder.ExtractValue()).ToString());

  protocol_response.internal_data.prepared_altoffers.value()[0].serialized_doc =
      binary_string;
  auto response = MakeRoutestatsResponse(context_overrides, protocol_response);
  CheckBase(response, 900, 15);

  protocol_response.internal_data.prepared_altoffers.value()[0].serialized_doc =
      "BQAAAAA=";
  response = MakeRoutestatsResponse(std::move(context_overrides),
                                    std::move(protocol_response));
  CheckBase(response, 900, 15);
}

UTEST(PerfectChainPlugin, EtaRounding) {
  std::vector<MockExperiment> configs = {
      {kResponseDecorationExp, kResponseDecorationExp + kSuffixExpJson},
      {kEtaExp, kEtaExp + kSuffixExpJson},
      {kDisplaySettings, kDisplaySettings + kSuffixExpJson},
      {kOffersInfoExp, kOffersInfoExp + kSuffixExpJson}};
  auto context_overrides =
      MakeContextOverrides(configs, {}, MakeOffersInfoResponse(61));

  auto response =
      MakeRoutestatsResponse(std::move(context_overrides),
                             MakeProtocolResponse({kPerfectChain, "other"}));

  CheckBase(response, 120, 2);

  context_overrides =
      MakeContextOverrides(configs, {}, MakeOffersInfoResponse(181));
  response =
      MakeRoutestatsResponse(std::move(context_overrides),
                             MakeProtocolResponse({kPerfectChain, "other"}));

  CheckBase(response, 180, 3);
}

UTEST(PerfectChainPlugin, NoPerfectChain) {
  auto context_overrides = MakeContextOverrides(
      {{kResponseDecorationExp, kResponseDecorationExp + kSuffixExpJson},
       {kEtaExp, kEtaExp + kSuffixExpJson},
       {kDisplaySettings, kDisplaySettings + kSuffixExpJson}},
      {});

  const auto response = MakeRoutestatsResponse(
      std::move(context_overrides), MakeProtocolResponse({"other1", "other2"}));

  ASSERT_TRUE(response.alternatives.has_value());
  ASSERT_TRUE(response.alternatives->options.has_value());

  const auto& alternatives = *response.alternatives->options;
  ASSERT_EQ(alternatives.size(), 2);
  ASSERT_EQ(alternatives[0].type, "other1");
  ASSERT_EQ(alternatives[1].type, "other2");
}

UTEST(PerfectChainPlugin, DisabledEtaExp) {
  auto context = MakeContextOverrides(
      {{kResponseDecorationExp, kResponseDecorationExp + kSuffixExpJson},
       {kDisplaySettings, kDisplaySettings + kSuffixExpJson}},
      {});

  const auto response = MakeRoutestatsResponse(
      std::move(context), MakeProtocolResponse({kPerfectChain}));

  ASSERT_EQ(response.alternatives.has_value(), false);
}

UTEST(PerfectChainPlugin, DisabledResponseDecorationExp) {
  auto context = MakeContextOverrides(
      {{kEtaExp, kEtaExp + kSuffixExpJson},
       {kDisplaySettings, kDisplaySettings + kSuffixExpJson}},
      {});

  const auto response = MakeRoutestatsResponse(
      std::move(context), MakeProtocolResponse({kPerfectChain, "other"}));

  ASSERT_TRUE(response.alternatives.has_value());
  ASSERT_TRUE(response.alternatives->options.has_value());

  const auto& alternatives = *response.alternatives->options;
  ASSERT_EQ(alternatives.size(), 1);
  ASSERT_EQ(alternatives[0].type, "other");
}

UTEST(PerfectChainPlugin, DisabledDisplaySettingsExp) {
  auto context = MakeContextOverrides(
      {{kResponseDecorationExp, kResponseDecorationExp + kSuffixExpJson},
       {kEtaExp, kEtaExp + kSuffixExpJson}},
      {});

  const auto response = MakeRoutestatsResponse(
      std::move(context), MakeProtocolResponse({kPerfectChain}));

  ASSERT_EQ(response.alternatives.has_value(), true);
  ASSERT_EQ(response.alternatives->options.has_value(), true);
  const auto& alternatives = *response.alternatives->options;
  ASSERT_EQ(alternatives.size(), 1);
  ASSERT_EQ(alternatives[0].type, kPerfectChain);
}

}  // namespace routestats::full::perfect_chain
