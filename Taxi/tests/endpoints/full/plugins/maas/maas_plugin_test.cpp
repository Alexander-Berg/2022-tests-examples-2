
#include <functional>

#include <testing/taxi_config.hpp>
#include <userver/utest/utest.hpp>

#include <json-diff/json_diff.hpp>

#include <clients/maas/client_mock_base.hpp>
#include <core/context/clients/clients_impl.hpp>
#include <tests/context/clients_mock_test.hpp>
#include <tests/context/taxi_config_mock_test.hpp>
#include <tests/context_mock_test.hpp>
#include <tests/endpoints/common/service_level_mock_test.hpp>

#include <endpoints/full/common.hpp>
#include <endpoints/full/plugins/maas/consts.hpp>
#include <endpoints/full/plugins/maas/plugin.hpp>

#include <taxi_config/variables/MAAS_PAYMENT_METHODS_CHECKS.hpp>

namespace routestats::full::maas {

namespace {

const std::string kLocale = "ru";

using MaasCheckTripResponse =
    ::clients::maas::internal_maas_v1_check_trip_requirements::post::Response;
using MaasCheckTripRequest =
    ::clients::maas::internal_maas_v1_check_trip_requirements::post::Request;
using Route = std::vector<geometry::Position>;
using taxi_config::maas_payment_methods_checks::MaasPaymentMethodsChecks;

MaasCheckTripResponse CreateMaasCheckTripResponse(
    bool valid = true,
    const std::optional<std::string>& failed_check_id = std::nullopt) {
  MaasCheckTripResponse response;

  response.valid = valid;
  response.failed_check_id = failed_check_id;

  return response;
}

class MaasClientMock : public ::clients::maas::ClientMockBase {
 public:
  MaasClientMock(
      const MaasCheckTripResponse& response,
      std::function<void(const MaasCheckTripRequest&)> request_validator)
      : request_validator_(request_validator), response_(response) {}

  static std::shared_ptr<MaasClientMock> CreateClientPtr(
      const MaasCheckTripResponse& response,
      std::function<void(const MaasCheckTripRequest&)> request_validator =
          [](const auto&) { return; }) {
    return std::make_shared<MaasClientMock>(response, request_validator);
  }

  MaasCheckTripResponse InternalMaasV1CheckTripRequirements(
      const MaasCheckTripRequest& request,
      const ::clients::maas::CommandControl& /*command_control*/ = {}) const {
    request_validator_(request);
    return response_;
  }

 private:
  std::function<void(const MaasCheckTripRequest&)> request_validator_;
  MaasCheckTripResponse response_;
};

core::Experiments MockExperiments(const std::vector<std::string>& checks) {
  core::ExpMappedData experiments;
  using Exp = experiments3::MaasTariffUnavailable;

  formats::json::ValueBuilder exp_value = formats::json::Type::kObject;
  exp_value["enabled"] = true;
  exp_value["mappings"] = formats::json::Type::kArray;

  for (const auto& check_id : checks) {
    auto field = [&check_id](const std::string& name) {
      return check_id + "_" + name;
    };

    formats::json::ValueBuilder tariff_unavailable =
        formats::json::Type::kObject;
    tariff_unavailable["code"] = field("code");
    tariff_unavailable["message_key"] = field("message_key");
    tariff_unavailable["branding_id"] = field("branding_id");

    formats::json::ValueBuilder mapping = formats::json::Type::kObject;
    mapping["failed_check_id"] = check_id;
    mapping["tariff_unavailable"] = tariff_unavailable;

    exp_value["mappings"].PushBack(std::move(mapping));
  }

  experiments[Exp::kName] = {
      Exp::kName, formats::json::ValueBuilder{exp_value}.ExtractValue(), {}};

  return {std::move(experiments)};
}

struct ContextOverrides {
  bool is_maas_request;
  std::optional<std::string> coupon;
  std::optional<handlers::RequestPayment> payment;
  std::optional<Route> route;
  std::optional<std::vector<std::string>> checks;
};

class TestContext {
 public:
  TestContext(std::shared_ptr<MaasClientMock> maas_client_mock)
      : maas_client_mock_(maas_client_mock) {}

  std::shared_ptr<const ::routestats::plugins::top_level::Context>
  GetTopLevelContext(const ContextOverrides overrides = ContextOverrides{}) {
    auto context = test::full::GetDefaultContext();
    context.user.auth_context.locale = kLocale;
    context.clients.maas =
        core::MakeClient<::clients::maas::Client>(*maas_client_mock_);

    if (overrides.checks.has_value()) {
      context.experiments.uservices_routestats_exps =
          MockExperiments(overrides.checks.value());
    }

    auto& request = context.input.original_request;

    if (overrides.is_maas_request) {
      request.state = ::handlers::RoutestatsRequestState();
      request.state->fields.push_back(
          ::handlers::RequestStateField{"maas", std::nullopt});
    }

    if (overrides.coupon.has_value()) {
      request.requirements = ::handlers::RoutestatsRequestRequirements();
      request.requirements->extra["coupon"] = overrides.coupon.value();
      context.input.coupon = overrides.coupon;
    }

    if (overrides.payment.has_value()) {
      request.payment = overrides.payment;
    }

    if (overrides.route.has_value()) {
      request.route = overrides.route;
    }

    auto config_storage = dynamic_config::MakeDefaultStorage({
        {taxi_config::MAAS_PAYMENT_METHODS_CHECKS,
         {{"card"},
          {
              {"__default__", "unsupported_payment_method"},
              {"cash", "cash_payment_method"},
          }}},
    });
    context.taxi_configs =
        std::make_shared<test::TaxiConfigsMock>(std::move(config_storage));

    return test::full::MakeTopLevelContext(context);
  }

 private:
  std::shared_ptr<MaasClientMock> maas_client_mock_;
};

ServiceLevel CreateServiceLevel(
    const std::string& class_, const std::optional<bool>& is_fixed_price,
    const std::optional<double>& original_price,
    const std::optional<double>& final_price,
    const std::optional<core::ServiceLevelCoupon>& coupon_info) {
  auto service_level = test::MockDefaultServiceLevel(class_);

  service_level.is_fixed_price = is_fixed_price;
  service_level.original_price = std::nullopt;
  service_level.final_price = std::nullopt;
  service_level.coupon = std::nullopt;

  if (original_price.has_value()) {
    service_level.internal_original_price =
        core::Decimal::FromFloatInexact(original_price.value());
  }

  if (final_price.has_value()) {
    service_level.final_price =
        core::Decimal::FromFloatInexact(final_price.value());
  }

  service_level.service_level_coupon = coupon_info;

  if (coupon_info.has_value() && coupon_info->valid &&
      coupon_info->value.has_value()) {
    service_level.coupon = core::Coupon{
        core::CouponAppliedType::kValue,
        core::Decimal::FromFloatInexact(coupon_info->value.value())};
  }

  return service_level;
}

ProtocolResponse CreateProtocolResponse(
    const std::optional<std::string>& route_distance = std::nullopt) {
  ProtocolResponse protocol_response;

  protocol_response.service_levels.push_back({"business"});
  protocol_response.service_levels.push_back({maas::consts::kMaasClass});

  if (route_distance.has_value()) {
    protocol_response.internal_data.route_info = {
        {route_distance.value(), "1"}};
  }

  return protocol_response;
}

core::ServiceLevelCoupon CreateCouponInfo(
    bool valid, const std::optional<double>& value = std::nullopt,
    const std::optional<std::string>& error_code = std::nullopt) {
  core::ServiceLevelCoupon result;

  result.valid = valid;
  result.value = value;
  result.error_code = error_code;

  return result;
}

void RunMaasPlugin(std::shared_ptr<MaasClientMock> maas_client_mock,
                   const ContextOverrides& context_overrides,
                   const ProtocolResponse& protocol_response,
                   std::vector<ServiceLevel>& service_levels) {
  auto test_context = TestContext(maas_client_mock);
  auto top_level_context = test_context.GetTopLevelContext(context_overrides);
  MaasPlugin plugin;

  plugin.OnContextBuilt(top_level_context);

  plugin.OnGotProtocolResponse(top_level_context, protocol_response);

  const auto& extensions =
      plugin.ExtendServiceLevels(top_level_context, service_levels);

  test::ApplyExtensions(extensions, service_levels);
}

core::TariffUnavailable CreateTariffUnavailable(
    const std::optional<std::string>& failed_check_id = std::nullopt) {
  auto field = [&failed_check_id](const std::string& name) {
    return failed_check_id.value() + "_" + name;
  };
  auto localize = [](const std::string& text) { return text + "##" + kLocale; };
  auto text_field = [&localize, &field](const std::string& name) {
    return localize(field(name));
  };

  if (failed_check_id.has_value()) {
    return core::TariffUnavailable{field("code"), text_field("message_key"),
                                   field("branding_id")};
  } else {
    return core::TariffUnavailable{maas::codes::kMaasUnavailableUnknownReason,
                                   localize(maas::keys::kMessage)};
  }
}

void AssertEq(const core::TariffUnavailable& expected,
              const core::TariffUnavailable& actual) {
  ASSERT_EQ(expected.code, actual.code);
  ASSERT_EQ(expected.message, actual.message);
  ASSERT_EQ(expected.branding_id.has_value(), actual.branding_id.has_value());

  if (expected.branding_id.has_value() && actual.branding_id.has_value()) {
    ASSERT_EQ(expected.branding_id.value(), actual.branding_id.value());
  }
}

}  // namespace

TEST(MaasPluginTest, HappyPath) {
  RunInCoro([] {
    auto maas_check_trip_response = CreateMaasCheckTripResponse(true);
    auto maas_client_mock =
        MaasClientMock::CreateClientPtr(maas_check_trip_response);
    auto context_overrides = ContextOverrides{
        true, "coupon", handlers::RequestPayment{"card"}, Route(), {}};
    auto coupon_info = CreateCouponInfo(true, 1000);
    auto protocol_response = CreateProtocolResponse("4000");
    std::vector<ServiceLevel> service_levels{CreateServiceLevel(
        maas::consts::kMaasClass, true, 190, 0, coupon_info)};

    RunMaasPlugin(maas_client_mock, context_overrides, protocol_response,
                  service_levels);

    auto service_level = service_levels.front();

    ASSERT_FALSE(service_level.tariff_unavailable.has_value());
    ASSERT_FALSE(service_level.service_level_coupon.has_value());
  });
}

TEST(MaasPluginTest, ValidateMaasCheckTripRequest) {
  RunInCoro([] {
    auto context_overrides =
        ContextOverrides{true,
                         "coupon",
                         handlers::RequestPayment{"card"},
                         Route{{37.5 * geometry::lon, 55.5 * geometry::lat}},
                         {}};
    auto maas_check_trip_response = CreateMaasCheckTripResponse(true);
    auto maas_client_mock = MaasClientMock::CreateClientPtr(
        maas_check_trip_response,
        [&context_overrides](const MaasCheckTripRequest& request) {
          ASSERT_EQ(context_overrides.coupon.value(), request.body.coupon);
          ASSERT_EQ(context_overrides.route.value(), request.body.waypoints);
        });
    auto coupon_info = CreateCouponInfo(true, 1000);
    auto protocol_response = CreateProtocolResponse("4000");
    std::vector<ServiceLevel> service_levels{CreateServiceLevel(
        maas::consts::kMaasClass, true, 190, 0, coupon_info)};

    RunMaasPlugin(maas_client_mock, context_overrides, protocol_response,
                  service_levels);

    auto service_level = service_levels.front();

    ASSERT_FALSE(service_level.tariff_unavailable.has_value());
  });
}

TEST(MaasPluginTest, MaasCheckTripFailed) {
  RunInCoro([] {
    auto failed_check_id = "route_without_point_b";
    auto maas_check_trip_response =
        CreateMaasCheckTripResponse(false, failed_check_id);
    auto maas_client_mock =
        MaasClientMock::CreateClientPtr(maas_check_trip_response);
    auto context_overrides = ContextOverrides{true,
                                              "coupon",
                                              handlers::RequestPayment{"card"},
                                              Route(),
                                              {{failed_check_id}}};
    auto coupon_info = CreateCouponInfo(true, 1000);
    auto protocol_response = CreateProtocolResponse("4000");
    std::vector<ServiceLevel> service_levels{CreateServiceLevel(
        maas::consts::kMaasClass, true, 190, 0, coupon_info)};

    RunMaasPlugin(maas_client_mock, context_overrides, protocol_response,
                  service_levels);

    auto service_level = service_levels.front();

    ASSERT_TRUE(service_level.tariff_unavailable.has_value());
    AssertEq(CreateTariffUnavailable(failed_check_id),
             service_level.tariff_unavailable.value());
  });
}

TEST(MaasPluginTest, NoPaymentMethod) {
  RunInCoro([] {
    auto failed_check_id = maas::checks::kNoPaymentMethod;
    auto maas_check_trip_response = CreateMaasCheckTripResponse(true);
    auto maas_client_mock =
        MaasClientMock::CreateClientPtr(maas_check_trip_response);
    auto context_overrides = ContextOverrides{
        true, "coupon", std::nullopt, Route(), {{failed_check_id}}};
    auto coupon_info = CreateCouponInfo(true, 1000);
    auto protocol_response = CreateProtocolResponse("4000");
    std::vector<ServiceLevel> service_levels{CreateServiceLevel(
        maas::consts::kMaasClass, true, 190, 0, coupon_info)};

    RunMaasPlugin(maas_client_mock, context_overrides, protocol_response,
                  service_levels);

    auto service_level = service_levels.front();

    ASSERT_TRUE(service_level.tariff_unavailable.has_value());
    AssertEq(CreateTariffUnavailable(failed_check_id),
             service_level.tariff_unavailable.value());
  });
}

TEST(MaasPluginTest, NotMaasRequest) {
  RunInCoro([] {
    auto maas_check_trip_response = CreateMaasCheckTripResponse(true);
    auto maas_client_mock =
        MaasClientMock::CreateClientPtr(maas_check_trip_response);
    auto context_overrides =
        ContextOverrides{false, "coupon", std::nullopt, Route(), {}};
    auto coupon_info = CreateCouponInfo(true, 1000);
    auto protocol_response = CreateProtocolResponse("4000");
    std::vector<ServiceLevel> service_levels{CreateServiceLevel(
        maas::consts::kMaasClass, true, 190, 0, coupon_info)};

    RunMaasPlugin(maas_client_mock, context_overrides, protocol_response,
                  service_levels);

    auto service_level = service_levels.front();

    ASSERT_FALSE(service_level.tariff_unavailable.has_value());
  });
}

TEST(MaasPluginTest, CashPayment) {
  RunInCoro([] {
    auto failed_check_id = "cash_payment_method";
    auto maas_check_trip_response = CreateMaasCheckTripResponse(true);
    auto maas_client_mock =
        MaasClientMock::CreateClientPtr(maas_check_trip_response);
    auto context_overrides = ContextOverrides{true,
                                              "coupon",
                                              handlers::RequestPayment{"cash"},
                                              Route(),
                                              {{failed_check_id}}};
    auto coupon_info = CreateCouponInfo(true, 1000);
    auto protocol_response = CreateProtocolResponse("4000");
    std::vector<ServiceLevel> service_levels{CreateServiceLevel(
        maas::consts::kMaasClass, true, 190, 0, coupon_info)};

    RunMaasPlugin(maas_client_mock, context_overrides, protocol_response,
                  service_levels);

    auto service_level = service_levels.front();

    ASSERT_TRUE(service_level.tariff_unavailable.has_value());
    AssertEq(CreateTariffUnavailable(failed_check_id),
             service_level.tariff_unavailable.value());
  });
}

TEST(MaasPluginTest, UnsupportedPaymentMethod) {
  RunInCoro([] {
    auto failed_check_id = "unsupported_payment_method";
    auto maas_check_trip_response = CreateMaasCheckTripResponse(true);
    auto maas_client_mock =
        MaasClientMock::CreateClientPtr(maas_check_trip_response);
    auto context_overrides =
        ContextOverrides{true,
                         "coupon",
                         handlers::RequestPayment{"undefined_method"},
                         Route(),
                         {{failed_check_id}}};
    auto coupon_info = CreateCouponInfo(true, 1000);
    auto protocol_response = CreateProtocolResponse("4000");
    std::vector<ServiceLevel> service_levels{CreateServiceLevel(
        maas::consts::kMaasClass, true, 190, 0, coupon_info)};

    RunMaasPlugin(maas_client_mock, context_overrides, protocol_response,
                  service_levels);

    auto service_level = service_levels.front();

    ASSERT_TRUE(service_level.tariff_unavailable.has_value());
    AssertEq(CreateTariffUnavailable(failed_check_id),
             service_level.tariff_unavailable.value());
  });
}

TEST(MaasPluginTest, NoCoupon) {
  RunInCoro([] {
    auto failed_check_id = maas::checks::kNoCoupon;
    auto maas_check_trip_response = CreateMaasCheckTripResponse(true);
    auto maas_client_mock =
        MaasClientMock::CreateClientPtr(maas_check_trip_response);
    auto context_overrides = ContextOverrides{true,
                                              std::nullopt,
                                              handlers::RequestPayment{"card"},
                                              Route(),
                                              {{failed_check_id}}};
    auto coupon_info = CreateCouponInfo(true, 1000);
    auto protocol_response = CreateProtocolResponse("4000");
    std::vector<ServiceLevel> service_levels{CreateServiceLevel(
        maas::consts::kMaasClass, true, 190, 0, coupon_info)};

    RunMaasPlugin(maas_client_mock, context_overrides, protocol_response,
                  service_levels);

    auto service_level = service_levels.front();

    ASSERT_TRUE(service_level.tariff_unavailable.has_value());
    AssertEq(CreateTariffUnavailable(failed_check_id),
             service_level.tariff_unavailable.value());
  });
}

TEST(MaasPluginTest, NoRoute) {
  RunInCoro([] {
    auto failed_check_id = maas::checks::kNoRoute;
    auto maas_check_trip_response = CreateMaasCheckTripResponse(true);
    auto maas_client_mock =
        MaasClientMock::CreateClientPtr(maas_check_trip_response);
    auto context_overrides = ContextOverrides{true,
                                              "coupon",
                                              handlers::RequestPayment{"card"},
                                              std::nullopt,
                                              {{failed_check_id}}};
    auto coupon_info = CreateCouponInfo(true, 1000);
    auto protocol_response = CreateProtocolResponse("4000");
    std::vector<ServiceLevel> service_levels{CreateServiceLevel(
        maas::consts::kMaasClass, true, 190, 0, coupon_info)};

    RunMaasPlugin(maas_client_mock, context_overrides, protocol_response,
                  service_levels);

    auto service_level = service_levels.front();

    ASSERT_TRUE(service_level.tariff_unavailable.has_value());
    AssertEq(CreateTariffUnavailable(failed_check_id),
             service_level.tariff_unavailable.value());
  });
}

TEST(MaasPluginTest, PriceTooHigh) {
  RunInCoro([] {
    auto failed_check_id = maas::checks::kPriceTooHigh;
    auto maas_check_trip_response = CreateMaasCheckTripResponse(true);
    auto maas_client_mock =
        MaasClientMock::CreateClientPtr(maas_check_trip_response);
    auto context_overrides = ContextOverrides{true,
                                              "coupon",
                                              handlers::RequestPayment{"card"},
                                              Route(),
                                              {{failed_check_id}}};
    auto coupon_info = CreateCouponInfo(false, 1000);
    auto protocol_response = CreateProtocolResponse("4000");
    std::vector<ServiceLevel> service_levels{CreateServiceLevel(
        maas::consts::kMaasClass, true, 1068, 1068, coupon_info)};

    RunMaasPlugin(maas_client_mock, context_overrides, protocol_response,
                  service_levels);

    auto service_level = service_levels.front();

    ASSERT_TRUE(service_level.tariff_unavailable.has_value());
    AssertEq(CreateTariffUnavailable(failed_check_id),
             service_level.tariff_unavailable.value());
  });
}

TEST(MaasPluginTest, MaasLevelNotFixedPrice) {
  RunInCoro([] {
    auto failed_check_id = maas::checks::kNotFixedPrice;
    auto maas_check_trip_response = CreateMaasCheckTripResponse(true);
    auto maas_client_mock =
        MaasClientMock::CreateClientPtr(maas_check_trip_response);
    auto context_overrides = ContextOverrides{true,
                                              "coupon",
                                              handlers::RequestPayment{"card"},
                                              Route(),
                                              {{failed_check_id}}};
    auto protocol_response = CreateProtocolResponse("4000");
    std::vector<ServiceLevel> service_levels{
        CreateServiceLevel(maas::consts::kMaasClass, false, std::nullopt,
                           std::nullopt, std::nullopt)};

    RunMaasPlugin(maas_client_mock, context_overrides, protocol_response,
                  service_levels);

    auto service_level = service_levels.front();

    ASSERT_TRUE(service_level.tariff_unavailable.has_value());
    AssertEq(CreateTariffUnavailable(failed_check_id),
             service_level.tariff_unavailable.value());
  });
}

TEST(MaasPluginTest, MaasLevelWithoutOriginalPrice) {
  RunInCoro([] {
    auto failed_check_id = maas::checks::kUnknownReason;
    auto maas_check_trip_response = CreateMaasCheckTripResponse(true);
    auto maas_client_mock =
        MaasClientMock::CreateClientPtr(maas_check_trip_response);
    auto context_overrides = ContextOverrides{true,
                                              "coupon",
                                              handlers::RequestPayment{"card"},
                                              Route(),
                                              {{failed_check_id}}};
    auto coupon_info = CreateCouponInfo(false, 1000);
    auto protocol_response = CreateProtocolResponse("4000");
    std::vector<ServiceLevel> service_levels{CreateServiceLevel(
        maas::consts::kMaasClass, true, std::nullopt, 100, coupon_info)};

    RunMaasPlugin(maas_client_mock, context_overrides, protocol_response,
                  service_levels);

    auto service_level = service_levels.front();

    ASSERT_TRUE(service_level.tariff_unavailable.has_value());
    AssertEq(CreateTariffUnavailable(failed_check_id),
             service_level.tariff_unavailable.value());
  });
}

TEST(MaasPluginTest, MaasLevelWithoutProtocolCoupon) {
  RunInCoro([] {
    auto failed_check_id = maas::checks::kUnknownReason;
    auto maas_check_trip_response = CreateMaasCheckTripResponse(true);
    auto maas_client_mock =
        MaasClientMock::CreateClientPtr(maas_check_trip_response);
    auto context_overrides = ContextOverrides{true,
                                              "coupon",
                                              handlers::RequestPayment{"card"},
                                              Route(),
                                              {{failed_check_id}}};
    auto protocol_response = CreateProtocolResponse(std::nullopt);
    std::vector<ServiceLevel> service_levels{CreateServiceLevel(
        maas::consts::kMaasClass, true, 190, 190, std::nullopt)};

    RunMaasPlugin(maas_client_mock, context_overrides, protocol_response,
                  service_levels);

    auto service_level = service_levels.front();

    ASSERT_TRUE(service_level.tariff_unavailable.has_value());
    AssertEq(CreateTariffUnavailable(failed_check_id),
             service_level.tariff_unavailable.value());
  });
}

TEST(MaasPluginTest, MaasCheckTripError) {
  RunInCoro([] {
    auto maas_check_trip_response = CreateMaasCheckTripResponse(true);
    auto maas_client_mock = MaasClientMock::CreateClientPtr(
        maas_check_trip_response,
        [](const auto&) { throw std::runtime_error("internal server error"); });
    auto context_overrides = ContextOverrides{
        true, "coupon", handlers::RequestPayment{"card"}, Route(), {}};
    auto coupon_info = CreateCouponInfo(true, 1000);
    auto protocol_response = CreateProtocolResponse("4000");
    std::vector<ServiceLevel> service_levels{CreateServiceLevel(
        maas::consts::kMaasClass, true, 190, 0, coupon_info)};

    RunMaasPlugin(maas_client_mock, context_overrides, protocol_response,
                  service_levels);

    auto service_level = service_levels.front();

    ASSERT_FALSE(service_level.tariff_unavailable.has_value());
  });
}

TEST(MaasPluginTest, CouponWasNotApplied) {
  RunInCoro([] {
    auto failed_check_id = maas::checks::kUnknownReason;
    auto maas_check_trip_response = CreateMaasCheckTripResponse(true);
    auto maas_client_mock =
        MaasClientMock::CreateClientPtr(maas_check_trip_response);
    auto context_overrides = ContextOverrides{true,
                                              "coupon",
                                              handlers::RequestPayment{"card"},
                                              Route(),
                                              {{failed_check_id}}};
    auto protocol_response = CreateProtocolResponse("4000");
    std::vector<ServiceLevel> service_levels{CreateServiceLevel(
        maas::consts::kMaasClass, true, 190, 190, std::nullopt)};

    RunMaasPlugin(maas_client_mock, context_overrides, protocol_response,
                  service_levels);

    auto service_level = service_levels.front();

    ASSERT_TRUE(service_level.tariff_unavailable.has_value());
    AssertEq(CreateTariffUnavailable(failed_check_id),
             service_level.tariff_unavailable.value());
  });
}

TEST(MaasPluginTest, CouponcheckErrorCountExceeded) {
  RunInCoro([] {
    auto failed_check_id =
        maas::consts::kCouponcheckPrefix + "error_count_exceeded";
    auto maas_check_trip_response = CreateMaasCheckTripResponse(true);
    auto maas_client_mock =
        MaasClientMock::CreateClientPtr(maas_check_trip_response);
    auto context_overrides = ContextOverrides{true,
                                              "coupon",
                                              handlers::RequestPayment{"card"},
                                              Route(),
                                              {{failed_check_id}}};
    auto coupon_info =
        CreateCouponInfo(false, std::nullopt, "ERROR_COUNT_EXCEEDED");
    auto protocol_response = CreateProtocolResponse("4000");
    std::vector<ServiceLevel> service_levels{CreateServiceLevel(
        maas::consts::kMaasClass, true, 190, 190, coupon_info)};

    RunMaasPlugin(maas_client_mock, context_overrides, protocol_response,
                  service_levels);

    auto service_level = service_levels.front();

    ASSERT_TRUE(service_level.tariff_unavailable.has_value());
    AssertEq(CreateTariffUnavailable(failed_check_id),
             service_level.tariff_unavailable.value());
  });
}

TEST(MaasPluginTest, CouponcheckErrorFallbackToUnknownReason) {
  RunInCoro([] {
    auto maas_check_trip_response = CreateMaasCheckTripResponse(true);
    auto maas_client_mock =
        MaasClientMock::CreateClientPtr(maas_check_trip_response);
    auto context_overrides = ContextOverrides{true,
                                              "coupon",
                                              handlers::RequestPayment{"card"},
                                              Route(),
                                              {{maas::checks::kUnknownReason}}};
    auto coupon_info =
        CreateCouponInfo(false, std::nullopt, "ERROR_COUNT_EXCEEDED");
    auto protocol_response = CreateProtocolResponse("4000");
    std::vector<ServiceLevel> service_levels{CreateServiceLevel(
        maas::consts::kMaasClass, true, 190, 190, coupon_info)};

    RunMaasPlugin(maas_client_mock, context_overrides, protocol_response,
                  service_levels);

    auto service_level = service_levels.front();

    ASSERT_TRUE(service_level.tariff_unavailable.has_value());
    // actual failed check is couponcheck:error_count_exceeded,
    // but it was not found in exp
    AssertEq(CreateTariffUnavailable(maas::checks::kUnknownReason),
             service_level.tariff_unavailable.value());
  });
}

TEST(MaasPluginTest, ModifyOnlyMaasClass) {
  RunInCoro([] {
    auto failed_check_id = maas::checks::kUnknownReason;
    auto maas_check_trip_response = CreateMaasCheckTripResponse(true);
    auto maas_client_mock =
        MaasClientMock::CreateClientPtr(maas_check_trip_response);
    auto context_overrides = ContextOverrides{true,
                                              "coupon",
                                              handlers::RequestPayment{"card"},
                                              Route(),
                                              {{failed_check_id}}};
    auto protocol_response = CreateProtocolResponse("4000");
    std::vector<ServiceLevel> service_levels{
        CreateServiceLevel("comfort", true, 190, 190, std::nullopt),
        CreateServiceLevel(maas::consts::kMaasClass, true, 190, 190,
                           std::nullopt),
        CreateServiceLevel("business", true, 190, 190, std::nullopt)};

    RunMaasPlugin(maas_client_mock, context_overrides, protocol_response,
                  service_levels);

    auto comfort_service_level = service_levels.at(0);
    auto maas_service_level = service_levels.at(1);
    auto business_service_level = service_levels.at(2);

    ASSERT_FALSE(comfort_service_level.tariff_unavailable.has_value());

    ASSERT_TRUE(maas_service_level.tariff_unavailable.has_value());
    AssertEq(CreateTariffUnavailable(failed_check_id),
             maas_service_level.tariff_unavailable.value());

    ASSERT_FALSE(business_service_level.tariff_unavailable.has_value());
  });
}

TEST(MaasPluginTest, DefaultTariffUnavailable_NoExp) {
  RunInCoro([] {
    auto maas_check_trip_response = CreateMaasCheckTripResponse(true);
    auto maas_client_mock =
        MaasClientMock::CreateClientPtr(maas_check_trip_response);
    auto context_overrides =
        ContextOverrides{true, "coupon", handlers::RequestPayment{"card"},
                         Route(), std::nullopt};
    auto protocol_response = CreateProtocolResponse("4000");
    std::vector<ServiceLevel> service_levels{CreateServiceLevel(
        maas::consts::kMaasClass, true, 1068, 1068, std::nullopt)};

    RunMaasPlugin(maas_client_mock, context_overrides, protocol_response,
                  service_levels);

    auto service_level = service_levels.front();

    ASSERT_TRUE(service_level.tariff_unavailable.has_value());
    // actual failed check maas::checks::kPriceTooHigh
    AssertEq(CreateTariffUnavailable(),  // create default tariff_unavailable
             service_level.tariff_unavailable.value());
  });
}

TEST(MaasPluginTest, DefaultTariffUnavailable_NoCheckInExp) {
  RunInCoro([] {
    auto maas_check_trip_response = CreateMaasCheckTripResponse(true);
    auto maas_client_mock =
        MaasClientMock::CreateClientPtr(maas_check_trip_response);
    auto context_overrides = ContextOverrides{true,
                                              "coupon",
                                              handlers::RequestPayment{"card"},
                                              Route(),
                                              {{maas::checks::kNoRoute}}};
    auto protocol_response = CreateProtocolResponse("4000");
    std::vector<ServiceLevel> service_levels{CreateServiceLevel(
        maas::consts::kMaasClass, true, 1068, 1068, std::nullopt)};

    RunMaasPlugin(maas_client_mock, context_overrides, protocol_response,
                  service_levels);

    auto service_level = service_levels.front();

    ASSERT_TRUE(service_level.tariff_unavailable.has_value());
    // actual failed check maas::checks::kPriceTooHigh
    AssertEq(CreateTariffUnavailable(),  // create default tariff_unavailable
             service_level.tariff_unavailable.value());
  });
}

TEST(MaasPluginTest, RouteTooLong) {
  RunInCoro([] {
    auto failed_check_id = maas::checks::kRouteTooLong;
    auto maas_check_trip_response = CreateMaasCheckTripResponse(true);
    auto maas_client_mock =
        MaasClientMock::CreateClientPtr(maas_check_trip_response);
    auto context_overrides = ContextOverrides{true,
                                              "coupon",
                                              handlers::RequestPayment{"card"},
                                              Route(),
                                              {{failed_check_id}}};
    auto coupon_info = CreateCouponInfo(true, 1000);
    auto protocol_response = CreateProtocolResponse("5001");
    std::vector<ServiceLevel> service_levels{CreateServiceLevel(
        maas::consts::kMaasClass, true, 190, 0, coupon_info)};

    RunMaasPlugin(maas_client_mock, context_overrides, protocol_response,
                  service_levels);

    auto service_level = service_levels.front();

    ASSERT_TRUE(service_level.tariff_unavailable.has_value());
    AssertEq(CreateTariffUnavailable(failed_check_id),
             service_level.tariff_unavailable.value());
  });
}

}  // namespace routestats::full::maas
