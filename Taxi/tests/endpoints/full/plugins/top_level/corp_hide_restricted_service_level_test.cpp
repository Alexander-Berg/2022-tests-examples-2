#include <gtest/gtest.h>

#include <clients/taxi-corp-integration/client_mock_base.hpp>
#include <core/context/clients/clients_impl.hpp>
#include <endpoints/full/plugins/corp_hide_restricted_service_level/plugin.hpp>
#include <experiments3/corp_hide_restricted_service_level_experiment.hpp>
#include <tests/context/translator_mock_test.hpp>
#include <tests/context_mock_test.hpp>

namespace routestats::full::brandings {

namespace {

const std::string kServiceLevelNotEnabled = "service_level_not_enabled";
const std::string kServiceLevelNotEnabledKey =
    "corp.corp_hide_restricted_service_level.service_level_not_enabled";
const std::string kServiceLevelNotEnabledMessage =
    "Corp payment method not available!";

static test::TranslationHandler translation_handler =
    [](const core::Translation& translation,
       [[maybe_unused]] const std::string& locale)
    -> std::optional<std::string> {
  if (translation->main_key.key == kServiceLevelNotEnabledKey) {
    return "Corp payment method not available!";
  }
  return "Big sad";
};

void AssertKwarg(const experiments3::models::KwargsBase& kwarg,
                 const std::string& key, const std::string& value) {
  const auto& arg = kwarg.FindOptional(key);
  if (arg) {
    ASSERT_EQ(std::get<std::string>(*arg), value);
  }
}

experiments3::models::ClientsCache::MappedData MockExperiment(
    const std::string& name, bool exp_enabled) {
  using formats::json::ValueBuilder;

  if (!exp_enabled) return {};

  ValueBuilder exp_builder{};
  exp_builder["enabled"] = exp_enabled;

  return {{name, experiments3::models::ExperimentResult{
                     name, exp_builder.ExtractValue(),
                     experiments3::models::ResultMetaInfo{}}}};
}

using Kwargs = experiments3::models::KwargsBuilderWithConsumer;

using UserClassesAvailableRequest =
    ::clients::taxi_corp_integration::v1_user_classes_available::post::Request;
using UserClassesAvailableResponse =
    ::clients::taxi_corp_integration::v1_user_classes_available::post::Response;

UserClassesAvailableResponse CreateTaxiCorpIntegrationResponse(
    std::unordered_set<std::string>&& classes) {
  UserClassesAvailableResponse response;

  response.classes_available = std::move(classes);

  return response;
}

class TaxiCorpIntegrationClientMock
    : public ::clients::taxi_corp_integration::ClientMockBase {
 public:
  TaxiCorpIntegrationClientMock(
      const UserClassesAvailableResponse& response,
      std::function<void(const UserClassesAvailableRequest&)> request_validator)
      : request_validator_(request_validator), response_(response) {}

  static std::shared_ptr<TaxiCorpIntegrationClientMock> CreateClientPtr(
      const UserClassesAvailableResponse& response,
      std::function<void(const UserClassesAvailableRequest&)>
          request_validator = [](const auto&) { return; }) {
    return std::make_shared<TaxiCorpIntegrationClientMock>(response,
                                                           request_validator);
  }

  UserClassesAvailableResponse V1UserClassesAvailable(
      const UserClassesAvailableRequest& request,
      const ::clients::taxi_corp_integration::
          CommandControl& /*command_control*/
      = {}) const {
    request_validator_(request);
    return response_;
  }

 private:
  std::function<void(const UserClassesAvailableRequest&)> request_validator_;
  UserClassesAvailableResponse response_;
};

class TestContext {
 public:
  TestContext(UserClassesAvailableResponse&& taxi_corp_integration_resp,
              std::string&& payment_type, std::string&& payment_id,
              std::string&& phone_id, bool exp_enabled,
              std::function<void(const experiments3::models::KwargsBase&)>&&
                  kwarg_checker)
      : taxi_corp_integration_resp_(std::move(taxi_corp_integration_resp)),
        payment_type_(std::move(payment_type)),
        payment_id_(std::move(payment_id)),
        phone_id_(std::move(phone_id)),
        exp_enabled_(exp_enabled),
        kwarg_checker_(std::move(kwarg_checker)) {}

  std::shared_ptr<const ::routestats::plugins::top_level::Context>
  GetTopLevelContext() {
    full::ContextData context = test::full::GetDefaultContext();

    context.input.original_request.payment =
        ::handlers::RequestPayment{payment_type_, payment_id_, std::nullopt};
    context.user.auth_context.yandex_taxi_phoneid = phone_id_;
    context.rendering.translator =
        std::make_shared<test::TranslatorMock>(translation_handler);

    context.get_experiments_mapped_data = [this](const Kwargs& kwargs)
        -> experiments3::models::ClientsCache::MappedData {
      kwarg_checker_(kwargs.Build());

      return MockExperiment(
          experiments3::CorpHideRestrictedServiceLevelExperiment::kName,
          exp_enabled_);
    };

    taxi_corp_integration_mock_ =
        TaxiCorpIntegrationClientMock::CreateClientPtr(
            taxi_corp_integration_resp_);

    context.clients.taxi_corp_integration =
        core::MakeClient<::clients::taxi_corp_integration::Client>(
            *taxi_corp_integration_mock_);
    return test::full::MakeTopLevelContext(context);
  }

 private:
  UserClassesAvailableResponse taxi_corp_integration_resp_;
  std::shared_ptr<TaxiCorpIntegrationClientMock> taxi_corp_integration_mock_;
  std::string payment_type_;
  std::string payment_id_;
  std::string phone_id_;
  bool exp_enabled_;
  std::function<void(const experiments3::models::KwargsBase&)> kwarg_checker_;
};

std::vector<core::ServiceLevel> MockServiceLevels() {
  auto classes = {"econom", "comfort"};
  std::vector<core::ServiceLevel> result;
  for (auto&& cls : classes) {
    core::ServiceLevel level;
    level.class_ = std::move(cls);
    result.push_back(level);
  }
  return result;
}

}  // namespace

TEST(TestRestrictedServiceLevel, HideNonAllowed) {
  RunInCoro([] {
    auto taxi_corp_integration_response =
        CreateTaxiCorpIntegrationResponse({"econom"});

    auto test_ctx = TestContext{
        std::move(taxi_corp_integration_response),
        "corp",
        "corp-d65dd1d23ec14f8a9d6a8bf9835ad34e",
        "123",
        true,
        [](const auto& kwarg) { AssertKwarg(kwarg, "phone_id", "123"); }};
    auto ctx = test_ctx.GetTopLevelContext();

    CorpHideRestrictedServiceLevelPlugin plugin;
    plugin.OnContextBuilt(ctx);

    auto service_levels = MockServiceLevels();

    auto extensions = plugin.ExtendServiceLevels(ctx, service_levels);

    for (auto& level : service_levels) {
      if (extensions.count(level.class_)) {
        extensions.at(level.class_)
            ->Apply("corp_hide_restricted_service_level", level);
      }
    }

    for (const auto& level : service_levels) {
      if (level.Class() != "econom") {
        ASSERT_EQ(level.tariff_unavailable->code, kServiceLevelNotEnabled);
        ASSERT_EQ(level.tariff_unavailable->message,
                  kServiceLevelNotEnabledMessage);
      }
    }
  });
}

TEST(TestRestrictedServiceLevel,
     CorpHideRestrictedServiceLevelExperimentDisabled) {
  RunInCoro([] {
    auto taxi_corp_integration_response = CreateTaxiCorpIntegrationResponse({});

    auto test_ctx = TestContext{
        std::move(taxi_corp_integration_response),
        "corp",
        "corp-d65dd1d23ec14f8a9d6a8bf9835ad34e",
        "123",
        false,
        [](const auto& kwarg) { AssertKwarg(kwarg, "phone_id", "123"); }};
    auto ctx = test_ctx.GetTopLevelContext();

    CorpHideRestrictedServiceLevelPlugin plugin;
    plugin.OnContextBuilt(ctx);

    auto service_levels = MockServiceLevels();

    auto extensions = plugin.ExtendServiceLevels(ctx, service_levels);

    for (auto& level : service_levels) {
      if (extensions.count(level.class_)) {
        extensions.at(level.class_)
            ->Apply("corp_hide_restricted_service_level", level);
      }
    }

    for (const auto& level : service_levels) {
      ASSERT_FALSE(level.tariff_unavailable.has_value());
    }
  });
}

TEST(TestRestrictedServiceLevel, NotCorp) {
  RunInCoro([] {
    auto taxi_corp_integration_response = CreateTaxiCorpIntegrationResponse({});

    auto test_ctx = TestContext{std::move(taxi_corp_integration_response),
                                "cash",
                                "",
                                "123",
                                true,
                                [](const auto&) {}};
    auto ctx = test_ctx.GetTopLevelContext();

    CorpHideRestrictedServiceLevelPlugin plugin;
    plugin.OnContextBuilt(ctx);

    auto service_levels = MockServiceLevels();

    auto extensions = plugin.ExtendServiceLevels(ctx, service_levels);

    for (auto& level : service_levels) {
      if (extensions.count(level.class_)) {
        extensions.at(level.class_)
            ->Apply("corp_hide_restricted_service_level", level);
      }
    }

    for (const auto& level : service_levels) {
      ASSERT_FALSE(level.tariff_unavailable.has_value());
    }
  });
}

TEST(TestRestrictedServiceLevel, CannotParsePaymentClientIdFromPayment) {
  RunInCoro([] {
    auto taxi_corp_integration_response = CreateTaxiCorpIntegrationResponse({});

    auto test_ctx = TestContext{std::move(taxi_corp_integration_response),
                                "corp",
                                "<broken id>",
                                "123",
                                true,
                                [](const auto&) {}};
    auto ctx = test_ctx.GetTopLevelContext();

    CorpHideRestrictedServiceLevelPlugin plugin;
    plugin.OnContextBuilt(ctx);

    auto service_levels = MockServiceLevels();

    auto extensions = plugin.ExtendServiceLevels(ctx, service_levels);

    for (auto& level : service_levels) {
      if (extensions.count(level.class_)) {
        extensions.at(level.class_)
            ->Apply("corp_hide_restricted_service_level", level);
      }
    }

    for (const auto& level : service_levels) {
      ASSERT_FALSE(level.tariff_unavailable.has_value());
    }
  });
}

}  // namespace routestats::full::brandings
