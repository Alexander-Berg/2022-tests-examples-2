
#include <functional>

#include <testing/taxi_config.hpp>
#include <userver/utest/utest.hpp>

#include <json-diff/json_diff.hpp>

#include <clients/antifraud/client_mock_base.hpp>
#include <clients/cardstorage/client_mock_base.hpp>
#include <core/context/clients/clients_impl.hpp>
#include <tests/context/clients_mock_test.hpp>
#include <tests/context/taxi_config_mock_test.hpp>
#include <tests/context_mock_test.hpp>
#include <tests/endpoints/common/service_level_mock_test.hpp>

#include <endpoints/full/common.hpp>
#include <endpoints/full/plugins/family_card/plugin.hpp>

namespace routestats::full::family_card {

namespace {

const std::string kLocale = "ru";

CardstorageResponse CreateCardstorageResponse(int limit, int expenses,
                                              const std::string& currency) {
  CardstorageResponse response;
  response.family = clients::cardstorage::FamilyCardInfo{
      false, "owner_uid1", limit, expenses, currency, "day",
  };

  return response;
}

template <typename Request, typename Response>
class ClientMock {
 public:
  ClientMock(const Response& response,
             std::function<void(const Request&)> request_validator)
      : request_validator_(request_validator), response_(response) {}

  void Validate(const Request& request) const { request_validator_(request); }

  const Response& GetResponse() const { return response_; }

 private:
  std::function<void(const Request&)> request_validator_;
  Response response_;
};

using CardstorageRequest = clients::cardstorage::v1_card::post::Request;

class CardstorageClientMock
    : public clients::cardstorage::ClientMockBase,
      public ClientMock<CardstorageRequest, CardstorageResponse> {
 public:
  CardstorageClientMock(
      const CardstorageResponse& response,
      std::function<void(const CardstorageRequest&)> request_validator)
      : ClientMock(response, request_validator) {}

  CardstorageResponse V1Card(
      const CardstorageRequest& request,
      const clients::cardstorage::CommandControl& /*command_control*/ = {})
      const override {
    Validate(request);
    return GetResponse();
  }
};

using ConvertRequest = clients::antifraud::v1_currency_convert::post::Request;
using ConvertResponse = clients::antifraud::v1_currency_convert::post::Response;

class AntifraudClientMock : public clients::antifraud::ClientMockBase,
                            public ClientMock<ConvertRequest, ConvertResponse> {
 public:
  AntifraudClientMock(
      const ConvertResponse& response,
      std::function<void(const ConvertRequest&)> request_validator)
      : ClientMock(response, request_validator) {}

  ConvertResponse currencyConvert(
      const ConvertRequest& request,
      const clients::antifraud::CommandControl& /*command_control*/ = {})
      const override {
    Validate(request);
    return GetResponse();
  }
};

class TestContext {
 public:
  TestContext(std::shared_ptr<CardstorageClientMock> cardstorage_client_mock,
              std::shared_ptr<AntifraudClientMock> antifraud_client_mock)
      : cardstorage_client_mock_(cardstorage_client_mock),
        antifraud_client_mock_(antifraud_client_mock) {}

  std::shared_ptr<const ::routestats::plugins::top_level::Context>
  GetTopLevelContext() {
    routestats::full::ContextData context = test::full::GetDefaultContext();
    context.user.auth_context.locale = kLocale;
    context.user.auth_context.yandex_uid = "yandex_uid1";
    context.user.auth_context.login_id = "yandex_login_id1";

    context.zone->country.currency_code = "RUB";

    context.clients.cardstorage =
        core::MakeClient<::clients::cardstorage::Client>(
            *cardstorage_client_mock_);
    context.clients.antifraud =
        core::MakeClient<::clients::antifraud::Client>(*antifraud_client_mock_);

    auto& request = context.input.original_request;

    request.payment =
        ::handlers::RequestPayment{"card", "card-x1234", std::nullopt, true};

    return test::full::MakeTopLevelContext(std::move(context));
  }

 private:
  std::shared_ptr<CardstorageClientMock> cardstorage_client_mock_;
  std::shared_ptr<AntifraudClientMock> antifraud_client_mock_;
};

ServiceLevel CreateServiceLevel(const std::string& class_, bool is_fixed_price,
                                const std::optional<double>& final_price) {
  auto service_level = test::MockDefaultServiceLevel(class_);

  service_level.is_fixed_price = is_fixed_price;

  if (final_price.has_value()) {
    service_level.final_price =
        core::Decimal::FromFloatInexact(final_price.value());
  }

  return service_level;
}

void RunFamilyCardPlugin(
    std::shared_ptr<CardstorageClientMock> cardstorage_client_mock,
    std::shared_ptr<AntifraudClientMock> antifraud_client_mock,
    std::vector<ServiceLevel>& service_levels) {
  auto test_context =
      TestContext(cardstorage_client_mock, antifraud_client_mock);
  auto top_level_context = test_context.GetTopLevelContext();
  FamilyCardPlugin plugin;

  plugin.OnContextBuilt(top_level_context);

  const auto& extensions =
      plugin.ExtendServiceLevels(top_level_context, service_levels);

  test::ApplyExtensions(extensions, service_levels);
}

core::TariffUnavailable CreateTariffUnavailable() {
  auto localize = [](const std::string& text) { return text + "##" + kLocale; };

  return core::TariffUnavailable{kFamilyCardUnavailableCode,
                                 localize(kFamilyCardUnavailableReasonKey)};
}

void AssertEq(const core::TariffUnavailable& expected,
              const core::TariffUnavailable& actual) {
  ASSERT_EQ(expected.code, actual.code);
  ASSERT_EQ(expected.message, actual.message);
}

}  // namespace

UTEST(FamilyCardPluginTest, Simple) {
  auto cardstorage_client_mock = std::make_shared<CardstorageClientMock>(
      CreateCardstorageResponse(250000, 150000, "RUB"),
      [](const CardstorageRequest& request) {
        ASSERT_EQ(request.body.card_id, "card-x1234");
        ASSERT_EQ(request.body.service_type, "card");
        ASSERT_EQ(request.body.yandex_uid, "yandex_uid1");
        ASSERT_EQ(request.body.yandex_login_id, "yandex_login_id1");
      });
  auto antifraud_client_mock = std::make_shared<AntifraudClientMock>(
      ConvertResponse{{1000.0}}, [](const ConvertRequest&) {
        throw std::runtime_error("should not be called!");
      });
  std::vector<ServiceLevel> service_levels{
      CreateServiceLevel("econom", true, 900),
      CreateServiceLevel("business", true, 1100),
  };

  RunFamilyCardPlugin(cardstorage_client_mock, antifraud_client_mock,
                      service_levels);

  ASSERT_FALSE(service_levels[0].tariff_unavailable.has_value());
  ASSERT_TRUE(service_levels[1].tariff_unavailable.has_value());
  AssertEq(service_levels[1].tariff_unavailable.value(),
           CreateTariffUnavailable());
}

UTEST(FamilyCardPluginTest, Convert) {
  auto cardstorage_client_mock = std::make_shared<CardstorageClientMock>(
      CreateCardstorageResponse(2500, 1500, "USD"),
      [](const CardstorageRequest& request) {
        ASSERT_EQ(request.body.card_id, "card-x1234");
        ASSERT_EQ(request.body.service_type, "card");
        ASSERT_EQ(request.body.yandex_uid, "yandex_uid1");
        ASSERT_EQ(request.body.yandex_login_id, "yandex_login_id1");
      });
  auto antifraud_client_mock = std::make_shared<AntifraudClientMock>(
      ConvertResponse{{1000.0}}, [](const ConvertRequest& request) {
        ASSERT_EQ(request.body.currency_from, "USD");
        ASSERT_EQ(request.body.currency_to, "RUB");
        ASSERT_EQ(request.body.value, 10.0);
      });
  std::vector<ServiceLevel> service_levels{
      CreateServiceLevel("econom", true, 900),
      CreateServiceLevel("business", true, 1100),
  };

  RunFamilyCardPlugin(cardstorage_client_mock, antifraud_client_mock,
                      service_levels);

  ASSERT_FALSE(service_levels[0].tariff_unavailable.has_value());
  ASSERT_TRUE(service_levels[1].tariff_unavailable.has_value());
  AssertEq(service_levels[1].tariff_unavailable.value(),
           CreateTariffUnavailable());
}

UTEST(FamilyCardPluginTest, Negative) {
  auto cardstorage_client_mock = std::make_shared<CardstorageClientMock>(
      CardstorageResponse{}, [](const CardstorageRequest&) {
        throw std::runtime_error("internal cardstorage failure");
      });
  auto antifraud_client_mock = std::make_shared<AntifraudClientMock>(
      ConvertResponse{{1000.0}}, [](const ConvertRequest&) {
        throw std::runtime_error("should not be called!");
      });
  std::vector<ServiceLevel> service_levels{
      CreateServiceLevel("econom", true, 900),
      CreateServiceLevel("business", true, 1100),
  };

  RunFamilyCardPlugin(cardstorage_client_mock, antifraud_client_mock,
                      service_levels);

  ASSERT_FALSE(service_levels[0].tariff_unavailable.has_value());
  ASSERT_FALSE(service_levels[1].tariff_unavailable.has_value());
}

UTEST(FamilyCardPluginTest, HasLimitsFromComplements) {
  ::handlers::RoutestatsRequest request;
  ::handlers::RequestPayment payment{
      "card",
      "card-x1234",
      {{::handlers::RequestPaymentComplement{"personal_wallet", "w/1234",
                                             true}}},
      std::nullopt,
  };
  request.payment = std::move(payment);

  ASSERT_TRUE(IsFamilyMemberCardRequest(request));
}

}  // namespace routestats::full::family_card
