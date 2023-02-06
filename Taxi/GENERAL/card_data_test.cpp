#include "card_data.hpp"
#include <clients/cardstorage/client_gmock.hpp>
#include <clients/cardstorage/requests.hpp>
#include <clients/taxi-shared-payments/client_gmock.hpp>
#include <taxi_config/variables/CARDSTORAGE_SUPPORTED_PAYMENT_TYPES.hpp>
#include <taxi_config/variables/RIDE_DISCOUNTS_FETCHING_DATA_SETTINGS.hpp>
#include <testing/taxi_config.hpp>
#include <userver/utest/utest.hpp>

namespace {

auto MatchRequest(const clients::cardstorage::v1_card::post::Request& request) {
  return ::testing::Field(&clients::cardstorage::v1_card::post::Request::body,
                          request.body);
}

auto MatchRequest(
    const clients::taxi_shared_payments::
        internal_coop_account_paymentmethod_short_info::get::Request& request) {
  return ::testing::Field(&clients::taxi_shared_payments::
                              internal_coop_account_paymentmethod_short_info::
                                  get::Request::account_id,
                          request.account_id);
}

const std::string kYandexUid = "123123123";
const std::string kCoopYandexUid = "8888888";
const std::string kMethodId = "card-1231312323";
const std::string kCoopMethodId = "card-9999999";
const std::string kBin = "123456";
const std::string kCardType = "card";
const std::string kCoopAccountType = "coop_account";

ACTION(Exception) { throw std::exception{}; }

dynamic_config::StorageMock GetConfigStorage(
    bool cardstorage_enabled = true, bool taxi_shared_payments_enabled = true) {
  taxi_config::ride_discounts_fetching_data_settings::VariableType
      fetching_data_settings;
  fetching_data_settings.cardstorage = {cardstorage_enabled};
  fetching_data_settings.taxi_shared_payments = {taxi_shared_payments_enabled};
  auto storage = dynamic_config::MakeDefaultStorage(
      {{taxi_config::RIDE_DISCOUNTS_FETCHING_DATA_SETTINGS,
        fetching_data_settings},
       {taxi_config::CARDSTORAGE_SUPPORTED_PAYMENT_TYPES, {"card"}}});
  return storage;
}

}  // namespace

UTEST(FetchCardData, WithoutMethodId) {
  clients::cardstorage::ClientGMock cardstorage_mock;
  EXPECT_CALL(cardstorage_mock, V1Card(testing::_, testing::_)).Times(0);
  clients::taxi_shared_payments::ClientGMock taxi_shared_payments_mock;
  EXPECT_CALL(taxi_shared_payments_mock,
              getAccountPaymentmethodShortInfo(testing::_, testing::_))
      .Times(0);
  handlers::Payment payment;
  payment.type = kCardType;
  auto storage = GetConfigStorage();
  EXPECT_EQ(models::FetchCardData(std::nullopt, payment, storage.GetSnapshot(),
                                  cardstorage_mock, taxi_shared_payments_mock)
                .bin,
            std::nullopt);
}

UTEST(FetchCardData, CardWithoutYandexUid) {
  clients::cardstorage::ClientGMock cardstorage_mock;
  EXPECT_CALL(cardstorage_mock, V1Card(testing::_, testing::_)).Times(0);
  clients::taxi_shared_payments::ClientGMock taxi_shared_payments_mock;
  EXPECT_CALL(taxi_shared_payments_mock,
              getAccountPaymentmethodShortInfo(testing::_, testing::_))
      .Times(0);

  handlers::Payment payment;
  payment.method_id = kMethodId;
  payment.type = kCardType;
  auto storage = GetConfigStorage();
  EXPECT_EQ(models::FetchCardData(std::nullopt, payment, storage.GetSnapshot(),
                                  cardstorage_mock, taxi_shared_payments_mock)
                .bin,
            std::nullopt);
}

UTEST(FetchCardData, CardWithConfigDisabled) {
  clients::cardstorage::ClientGMock cardstorage_mock;
  EXPECT_CALL(cardstorage_mock, V1Card(testing::_, testing::_)).Times(0);
  clients::taxi_shared_payments::ClientGMock taxi_shared_payments_mock;
  EXPECT_CALL(taxi_shared_payments_mock,
              getAccountPaymentmethodShortInfo(testing::_, testing::_))
      .Times(0);

  handlers::Payment payment;
  payment.method_id = kMethodId;
  payment.type = kCardType;
  auto storage = GetConfigStorage(false, true);
  EXPECT_EQ(models::FetchCardData(kYandexUid, payment, storage.GetSnapshot(),
                                  cardstorage_mock, taxi_shared_payments_mock)
                .bin,
            std::nullopt);
}

UTEST(FetchCardData, CardWithErrorInClient) {
  clients::cardstorage::ClientGMock cardstorage_mock;
  EXPECT_CALL(cardstorage_mock, V1Card(testing::_, testing::_))
      .Times(1)
      .WillOnce(Exception());
  clients::taxi_shared_payments::ClientGMock taxi_shared_payments_mock;
  EXPECT_CALL(taxi_shared_payments_mock,
              getAccountPaymentmethodShortInfo(testing::_, testing::_))
      .Times(0);

  handlers::Payment payment;
  payment.method_id = kMethodId;
  payment.type = kCardType;
  auto storage = GetConfigStorage(true, true);
  EXPECT_EQ(models::FetchCardData(kYandexUid, payment, storage.GetSnapshot(),
                                  cardstorage_mock, taxi_shared_payments_mock)
                .bin,
            std::nullopt);
}

UTEST(FetchCardData, CardWithConfigEnabled) {
  clients::cardstorage::ClientGMock cardstorage_mock;

  clients::cardstorage::v1_card::post::Request request;
  request.body.yandex_uid = kYandexUid;
  request.body.card_id = kMethodId;

  clients::cardstorage::v1_card::post::Response response;
  response.bin = kBin;
  EXPECT_CALL(cardstorage_mock, V1Card(MatchRequest(request), testing::_))
      .Times(1)
      .WillOnce(testing::Return(response));

  clients::taxi_shared_payments::ClientGMock taxi_shared_payments_mock;
  EXPECT_CALL(taxi_shared_payments_mock,
              getAccountPaymentmethodShortInfo(testing::_, testing::_))
      .Times(0);

  handlers::Payment payment;
  payment.method_id = kMethodId;
  payment.type = kCardType;
  auto storage = GetConfigStorage(true, true);
  EXPECT_EQ(models::FetchCardData(kYandexUid, payment, storage.GetSnapshot(),
                                  cardstorage_mock, taxi_shared_payments_mock)
                .bin,
            kBin);
}

UTEST(FetchCardData, CoopAccountWithConfigDisabled) {
  clients::cardstorage::ClientGMock cardstorage_mock;
  EXPECT_CALL(cardstorage_mock, V1Card(testing::_, testing::_)).Times(0);

  clients::taxi_shared_payments::ClientGMock taxi_shared_payments_mock;
  EXPECT_CALL(taxi_shared_payments_mock,
              getAccountPaymentmethodShortInfo(testing::_, testing::_))
      .Times(0);

  handlers::Payment payment;
  payment.method_id = kMethodId;
  payment.type = kCoopAccountType;
  auto storage = GetConfigStorage(true, false);
  EXPECT_EQ(models::FetchCardData(kYandexUid, payment, storage.GetSnapshot(),
                                  cardstorage_mock, taxi_shared_payments_mock)
                .bin,
            std::nullopt);
}

UTEST(FetchCardData, CoopAccountWithErrorInClient) {
  clients::cardstorage::ClientGMock cardstorage_mock;
  EXPECT_CALL(cardstorage_mock, V1Card(testing::_, testing::_)).Times(0);

  clients::taxi_shared_payments::ClientGMock taxi_shared_payments_mock;
  EXPECT_CALL(taxi_shared_payments_mock,
              getAccountPaymentmethodShortInfo(testing::_, testing::_))
      .Times(1)
      .WillOnce(Exception());

  handlers::Payment payment;
  payment.method_id = kMethodId;
  payment.type = kCoopAccountType;
  auto storage = GetConfigStorage(true, true);
  EXPECT_EQ(models::FetchCardData(kYandexUid, payment, storage.GetSnapshot(),
                                  cardstorage_mock, taxi_shared_payments_mock)
                .bin,
            std::nullopt);
}

UTEST(FetchCardData, CoopAccountWithConfigEnabled) {
  clients::cardstorage::ClientGMock cardstorage_mock;

  clients::cardstorage::v1_card::post::Request cardstorage_request;
  cardstorage_request.body.yandex_uid = kCoopYandexUid;
  cardstorage_request.body.card_id = kCoopMethodId;

  clients::cardstorage::v1_card::post::Response cardstorage_response;
  cardstorage_response.bin = kBin;
  EXPECT_CALL(cardstorage_mock,
              V1Card(MatchRequest(cardstorage_request), testing::_))
      .Times(1)
      .WillOnce(testing::Return(cardstorage_response));

  clients::taxi_shared_payments::ClientGMock taxi_shared_payments_mock;
  clients::taxi_shared_payments::
      internal_coop_account_paymentmethod_short_info::get::Response
          shared_payments_response;

  clients::taxi_shared_payments::
      internal_coop_account_paymentmethod_short_info::get::Request request;
  request.account_id = kMethodId;
  shared_payments_response.owner_uid = kCoopYandexUid;
  shared_payments_response.payment_method_id = kCoopMethodId;
  EXPECT_CALL(taxi_shared_payments_mock, getAccountPaymentmethodShortInfo(
                                             MatchRequest(request), testing::_))
      .Times(1)
      .WillOnce(testing::Return(shared_payments_response));

  handlers::Payment payment;
  payment.method_id = kMethodId;
  payment.type = kCoopAccountType;
  auto storage = GetConfigStorage(true, true);
  EXPECT_EQ(models::FetchCardData(kYandexUid, payment, storage.GetSnapshot(),
                                  cardstorage_mock, taxi_shared_payments_mock)
                .bin,
            kBin);
}

UTEST(FetchCardData, InvalidType) {
  clients::cardstorage::ClientGMock cardstorage_mock;
  EXPECT_CALL(cardstorage_mock, V1Card(testing::_, testing::_)).Times(0);
  clients::taxi_shared_payments::ClientGMock taxi_shared_payments_mock;
  EXPECT_CALL(taxi_shared_payments_mock,
              getAccountPaymentmethodShortInfo(testing::_, testing::_))
      .Times(0);

  handlers::Payment payment;
  payment.method_id = kMethodId;
  payment.type = "invalid";
  auto storage = GetConfigStorage(true, true);
  EXPECT_EQ(models::FetchCardData(kYandexUid, payment, storage.GetSnapshot(),
                                  cardstorage_mock, taxi_shared_payments_mock)
                .bin,
            std::nullopt);
}
