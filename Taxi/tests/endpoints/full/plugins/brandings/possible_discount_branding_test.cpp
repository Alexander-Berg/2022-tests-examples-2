#include <core/context/clients/clients_impl.hpp>
#include <endpoints/full/core/input.hpp>
#include <endpoints/full/plugins/brandings/subplugins/possible_discount_branding.hpp>

#include <clients/ride-discounts/client_mock_base.hpp>
#include <userver/utest/utest.hpp>
#include <userver/utils/mock_now.hpp>

// #include <ua_parser/application.hpp>

#include <tests/context_mock_test.hpp>
#include <tests/endpoints/common/service_level_mock_test.hpp>

namespace routestats::full::brandings {

namespace {

const auto kNow = utils::datetime::Stringtime("2022-01-01 21:00:00", "UTC",
                                              "%Y-%m-%d %H:%M:%S");

using DiscountsAvailableRequest = clients::ride_discounts::
    v1_match_discounts_available_by_zone::post::Request;
using DiscountsAvailableResponse = clients::ride_discounts::
    v1_match_discounts_available_by_zone::post::Response;

void AssertEq(const DiscountsAvailableRequest& expected,
              const DiscountsAvailableRequest& actual) {
  ASSERT_EQ(expected.body.request_time, actual.body.request_time);
  ASSERT_EQ(expected.body.tariffs, actual.body.tariffs);
  ASSERT_EQ(expected.body.tariff_zone, actual.body.tariff_zone);
  ASSERT_EQ(expected.body.client_timezone, actual.body.client_timezone);
  ASSERT_EQ(expected.body.has_yaplus, actual.body.has_yaplus);
  ASSERT_EQ(expected.body.application_name, actual.body.application_name);
  ASSERT_EQ(expected.body.waypoints, actual.body.waypoints);
}

using DisountsHandler = std::function<DiscountsAvailableResponse()>;
class DiscountsClientMock : public clients::ride_discounts::ClientMockBase {
 public:
  DiscountsClientMock() {}

  DiscountsAvailableResponse V1MatchDiscountsAvailableByZone(
      const DiscountsAvailableRequest& request,
      const clients::ride_discounts::CommandControl&) const override {
    if (expected_request_.has_value()) {
      AssertEq(expected_request_.value(), request);
    }
    if (exception_msg_.has_value()) {
      throw std::runtime_error(exception_msg_.value());
    }

    DiscountsAvailableResponse response;
    response.tariffs_availability = tariffs_availability_;
    return response;
  }

  void SetResponseTariffsAvailability(
      std::vector<std::string> tariffs_availability) {
    tariffs_availability_ = tariffs_availability;
  }

  void SetExpectedRequest(std::unordered_set<std::string> tariffs) {
    expected_request_ = DiscountsAvailableRequest{};
    expected_request_->body.tariffs = tariffs;
    expected_request_->body.request_time = kNow;
    expected_request_->body.tariff_zone = "test_zone";
    expected_request_->body.client_timezone = "test_timezone";
    expected_request_->body.has_yaplus = true;
    expected_request_->body.application_name = "test_application_name";
    expected_request_->body.waypoints = std::vector<std::vector<double>>{
        {12.34, 56.78},
        {90.12, 34.56},
        {78.90, 21.43},
    };
  }

  void SetException(std::string&& message) { exception_msg_ = message; }

 private:
  std::optional<DiscountsAvailableRequest> expected_request_;
  std::vector<std::string> tariffs_availability_;
  std::optional<std::string> exception_msg_;
};

handlers::RequestTariffRequirement CreateTariffRequirement(
    std::string&& class_name) {
  return handlers::RequestTariffRequirement{class_name, std::nullopt};
}

struct CreateContextParams {
  bool has_zone;
  bool has_tariff_requirements;
  bool are_requirements_empty;

  CreateContextParams()
      : has_zone(true),
        has_tariff_requirements(true),
        are_requirements_empty(false) {}
};

std::shared_ptr<const ::routestats::plugins::top_level::Context> CreateContext(
    DiscountsClientMock&& discounts_client, CreateContextParams params = {}) {
  auto context = test::full::GetDefaultContext();
  if (params.has_zone) {
    context.zone->zone_name = "test_zone";
    context.zone->tariff_settings.timezone = "test_timezone";
  } else {
    context.zone = std::nullopt;
  }
  context.user.auth_context.flags.has_ya_plus = true;
  context.user.auth_context.app_vars = ua_parser::AppVars{
      ua_parser::AppVarsMap{{"app_name", "test_application_name"}}};
  context.input.original_request.route = std::vector<geometry::Position>{
      {geometry::Latitude(12.34), geometry::Longitude(56.78)},
      {geometry::Latitude(90.12), geometry::Longitude(34.56)},
      {geometry::Latitude(78.90), geometry::Longitude(21.43)},
  };
  if (params.has_tariff_requirements) {
    if (params.are_requirements_empty) {
      context.input.original_request.tariff_requirements = {};
    } else {
      context.input.original_request.tariff_requirements =
          std::vector<handlers::RequestTariffRequirement>{
              CreateTariffRequirement("class_with_discount"),
              CreateTariffRequirement("class_without_discount")};
    }
  } else {
    context.input.original_request.tariff_requirements = std::nullopt;
  }

  context.clients.ride_discounts =
      core::MakeClient<clients::ride_discounts::Client>(discounts_client);

  return test::full::MakeTopLevelContext(context);
}

service_level::TariffBranding CreateBranding() {
  service_level::TariffBranding branding;
  branding.type = "has_possible_discount";
  return branding;
}

void AssertEq(const service_level::TariffBranding& expected,
              const service_level::TariffBranding& actual) {
  ASSERT_EQ(expected.type, actual.type);
}

}  // namespace

UTEST(PossibleDiscountBrandingPlugin, BrandingsOk) {
  ::utils::datetime::MockNowSet(kNow);
  PossibleDiscountBrandingPlugin plugin;

  auto discounts_client = DiscountsClientMock();
  discounts_client.SetResponseTariffsAvailability({"class_with_discount"});
  discounts_client.SetExpectedRequest(
      {"class_with_discount", "class_without_discount"});

  auto context = CreateContext(std::move(discounts_client));

  plugin.OnContextBuilt(context);

  ASSERT_EQ(plugin.GetBrandings("class_without_discount").size(), 0);

  const auto& brandings = plugin.GetBrandings("class_with_discount");
  ASSERT_EQ(brandings.size(), 1);

  const auto& branding = brandings.front();
  AssertEq(CreateBranding(), branding);
}

UTEST(PossibleDiscountBrandingPlugin, NoZone) {
  ::utils::datetime::MockNowSet(kNow);
  PossibleDiscountBrandingPlugin plugin;

  auto discounts_client = DiscountsClientMock();
  discounts_client.SetException("Should not be called, because no zone");

  CreateContextParams ctxParams{};
  ctxParams.has_zone = false;
  auto context = CreateContext(std::move(discounts_client), ctxParams);

  plugin.OnContextBuilt(context);

  ASSERT_EQ(plugin.GetBrandings("class_without_discount").size(), 0);
  ASSERT_EQ(plugin.GetBrandings("class_with_discount").size(), 0);
}

UTEST(PossibleDiscountBrandingPlugin, NoTariffRequirements) {
  ::utils::datetime::MockNowSet(kNow);
  PossibleDiscountBrandingPlugin plugin;

  auto discounts_client = DiscountsClientMock();
  discounts_client.SetException(
      "Should not be called, because no tariff_requirements");

  CreateContextParams ctxParams{};
  ctxParams.has_tariff_requirements = false;
  auto context = CreateContext(std::move(discounts_client), ctxParams);

  plugin.OnContextBuilt(context);

  ASSERT_EQ(plugin.GetBrandings("class_without_discount").size(), 0);
  ASSERT_EQ(plugin.GetBrandings("class_with_discount").size(), 0);
}

UTEST(PossibleDiscountBrandingPlugin, EmptyRequirements) {
  ::utils::datetime::MockNowSet(kNow);
  PossibleDiscountBrandingPlugin plugin;

  auto discounts_client = DiscountsClientMock();
  discounts_client.SetException(
      "Should not be called, because empty tariff_requirements");

  CreateContextParams ctxParams{};
  ctxParams.are_requirements_empty = true;
  auto context = CreateContext(std::move(discounts_client), ctxParams);

  plugin.OnContextBuilt(context);

  ASSERT_EQ(plugin.GetBrandings("class_without_discount").size(), 0);
  ASSERT_EQ(plugin.GetBrandings("class_with_discount").size(), 0);
}

}  // namespace routestats::full::brandings
