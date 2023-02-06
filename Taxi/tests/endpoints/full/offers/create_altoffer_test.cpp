#include <fstream>

#include <boost/filesystem.hpp>

#include <userver/formats/bson/serialize.hpp>
#include <userver/utest/utest.hpp>
#include <userver/utils/algo.hpp>

#include <testing/source_path.hpp>

#include <tests/context/taxi_config_mock_test.hpp>
#include <tests/context_mock_test.hpp>

#include <endpoints/common/builders/service_level_builder.hpp>
#include <endpoints/common/core/alternative/extender.hpp>
#include <endpoints/common/core/protocol_request/extender.hpp>
#include <endpoints/full/plugins/combo/plugin.hpp>

namespace routestats::plugins::top_level {

namespace {

const boost::filesystem::path kTestFilePath(
    utils::CurrentSourcePath("src/tests/endpoints/full/offers"));
const std::string kTestDataDir = kTestFilePath.string() + "/static";

const std::string kProtocolResponseFilename = "protocol_response.json";
const std::string kAlternativeName = "test_alternative";

const std::string kEmptyBinaryAltoffer = "BQAAAAA=";

struct PrepareAltofferProtocolRequestExtension
    : public core::ProtocolRequestExtension {
  void Apply(const std::string&,
             core::ProtocolRequestBody& protocol_request) override {
    if (!protocol_request.feature_flags) {
      protocol_request.feature_flags.emplace();
    }
    if (!protocol_request.feature_flags->prepare_altoffers) {
      protocol_request.feature_flags->prepare_altoffers.emplace();
    }
    protocol_request.feature_flags->prepare_altoffers->push_back(
        kAlternativeName);
  }
};

struct PatchAltofferExtention : public core::AlternativeExtension {
  using core::AlternativeExtension::AlternativeExtension;

  void Apply(const std::string&,
             std::optional<Alternative>& alternative) override {
    if (!alternative || !alternative->prepared_altoffer) {
      return;
    }
    alternative->prepared_altoffer->offer_doc["new_field"] = "new_value";
  }
};

// This plugin patches altoffer `test_alternative`
class TestPlugin : public TopLevelPluginBase {
 public:
  static constexpr const char* kName = "top_level:test";
  std::string Name() const override { return kName; }

  core::ProtocolRequestExtensions ModifyProtocolRequestBody(
      const ProtocolRequestBody&, std::shared_ptr<const Context>) override {
    return core::ProtocolRequestExtensions{
        std::make_shared<PrepareAltofferProtocolRequestExtension>()};
  }

  AlternativeExtensions ModifyAlternatives(
      const Alternatives&, std::shared_ptr<const Context>) override {
    return AlternativeExtensions{
        {kAlternativeName,
         std::make_shared<PatchAltofferExtention>(kAlternativeName)}};
  }
};

formats::json::Value LoadJsonFromFile(const std::string& filename) {
  std::ifstream f(kTestDataDir + "/" + filename);
  if (!f.is_open()) {
    throw std::runtime_error(fmt::format("Couldn't open file '{}'", filename));
  }
  return formats::json::FromString(std::string(
      std::istreambuf_iterator<char>(f), std::istreambuf_iterator<char>()));
}

std::shared_ptr<const plugins::top_level::Context> BuildContext() {
  full::ContextData context = test::full::GetDefaultContext();
  return test::full::MakeTopLevelContext(context);
}
}  // namespace

UTEST(ModifyAltofferExample, Simple) {
  auto plugin = std::make_shared<TestPlugin>();
  std::vector<std::shared_ptr<TestPlugin>> plugins{plugin};

  auto context = BuildContext();

  // Extend protocol request
  ProtocolRequestBody protocol_request;
  ASSERT_FALSE(!!protocol_request.feature_flags);
  std::vector<std::optional<ProtocolRequestExtensions>> request_extentions;
  request_extentions.push_back(
      plugin->ModifyProtocolRequestBody(protocol_request, context));
  core::ApplyProtocolRequestExtensions(plugins, request_extentions,
                                       protocol_request);
  ASSERT_TRUE(!!protocol_request.feature_flags);
  ASSERT_TRUE(!!protocol_request.feature_flags->prepare_altoffers);
  ASSERT_EQ(!!protocol_request.feature_flags->prepare_altoffers->size(), 1u);
  ASSERT_EQ((*protocol_request.feature_flags->prepare_altoffers)[0],
            kAlternativeName);

  auto protocol_response =
      LoadJsonFromFile(kProtocolResponseFilename).As<ProtocolResponse>();
  auto [_, alternatives] = routestats::common::BuildModels(protocol_response);

  // Modify alternatives
  std::vector<std::optional<core::AlternativeExtensionsMap>>
      alternatives_extentions;
  alternatives_extentions.push_back(
      plugin->ModifyAlternatives(alternatives, context));
  core::ApplyAlternativesExtensions(plugins, alternatives_extentions,
                                    alternatives);

  ASSERT_EQ(alternatives.options.size(), 1u);
  ASSERT_TRUE(alternatives.options[0]);
  ASSERT_TRUE(alternatives.options[0]->prepared_altoffer);

  auto serialized_offer =
      formats::bson::ToCanonicalJsonString(
          alternatives.options[0]->prepared_altoffer->offer_doc.ExtractValue())
          .ToString();
  ASSERT_EQ(serialized_offer, "{ \"new_field\" : \"new_value\" }");
}

}  // namespace routestats::plugins::top_level
