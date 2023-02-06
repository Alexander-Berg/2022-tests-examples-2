#include <clients/eats-core-restapp/client_gmock.hpp>
#include <userver/utest/utest.hpp>

#include <defs/api/promo.hpp>
#include <defs/definitions.hpp>
#include <experiments3/eats_restapp_promo_settings.hpp>
#include <utils/promo_features_validators/min_order_price.hpp>

namespace eats_restapp_promo::utils {
using namespace ::testing;

TEST(GetPlaceAvaregeCheques, CheckGetPlaceAvaregeCheques) {
  StrictMock<clients::eats_core_restapp::ClientGMock> eats_core_restapp;
  clients::eats_core_restapp::v1_places_receipts_get_average::get::Response
      response;
  response.payload = {{1, 5}, {2, 50}, {3, 100}};
  EXPECT_CALL(eats_core_restapp, V1PlacesReceiptsGetAverage(_, _))
      .WillOnce(Return(response));
  std::unordered_map<int64_t, int64_t> expected_result = {
      {1, 5}, {2, 50}, {3, 100}};
  ASSERT_EQ(GetPlaceAvaregeCheques(eats_core_restapp,
                                   types::RequestInfo{1, {1, 2, 3}}),
            expected_result);
}

TEST(GetPlaceAvaregeCheques, CheckGetEmptyPlaceAvaregeCheques) {
  StrictMock<clients::eats_core_restapp::ClientGMock> eats_core_restapp;
  clients::eats_core_restapp::v1_places_receipts_get_average::get::Response
      response;
  EXPECT_CALL(eats_core_restapp, V1PlacesReceiptsGetAverage(_, _))
      .WillOnce(Return(response));
  std::unordered_map<int64_t, int64_t> expected_result;
  ASSERT_EQ(GetPlaceAvaregeCheques(eats_core_restapp,
                                   types::RequestInfo{1, {1, 2, 3}}),
            expected_result);
}

TEST(ValivatationMinOrderPriceWithoutFeatureDataFull,
     DontThrowExceptionForOtherPromos) {
  StrictMock<clients::eats_core_restapp::ClientGMock> eats_core_restapp;
  clients::eats_core_restapp::v1_places_receipts_get_average::get::Response
      response;
  response.payload = {{1, 5}, {2, 50}, {3, 100}};
  EXPECT_CALL(eats_core_restapp, V1PlacesReceiptsGetAverage(_, _))
      .WillOnce(Return(response));
  ASSERT_NO_THROW(
      ValidateMinOrderPrice(eats_core_restapp, {}, {1, {1, 2, 3}},
                            std::optional<handlers::MinMaxOrderPrice>()));
  ASSERT_NO_THROW(ValidateMinOrderPrice(
      eats_core_restapp, {}, {1, {1, 2, 3}},
      handlers::MinMaxOrderPrice{decimal64::Decimal<2>::FromFloatInexact(1.0),
                                 std::nullopt}));
}

TEST(ValivatationMinOrderPriceWithoutFeatureDataFull,
     DontThrowExceptionIfPlaceIdsIsEmpty) {
  StrictMock<clients::eats_core_restapp::ClientGMock> eats_core_restapp;
  clients::eats_core_restapp::v1_places_receipts_get_average::get::Response
      response;
  response.payload = {{1, 5}, {2, 50}, {3, 100}};
  EXPECT_CALL(eats_core_restapp, V1PlacesReceiptsGetAverage(_, _))
      .WillOnce(Return(response));
  ASSERT_NO_THROW(ValidateMinOrderPrice(
      eats_core_restapp, {}, {1, {}},
      handlers::MinMaxOrderPrice{decimal64::Decimal<2>::FromFloatInexact(120.0),
                                 std::nullopt}));
}

TEST(ValivatationMinOrderPriceWithoutFeatureDataFull,
     DontThrowExceptionIfCoreResponseIsEmpty) {
  StrictMock<clients::eats_core_restapp::ClientGMock> eats_core_restapp;
  clients::eats_core_restapp::v1_places_receipts_get_average::get::Response
      response;
  EXPECT_CALL(eats_core_restapp, V1PlacesReceiptsGetAverage(_, _))
      .WillOnce(Return(response));
  ASSERT_NO_THROW(ValidateMinOrderPrice(
      eats_core_restapp, {}, {1, {1, 2, 3}},
      handlers::MinMaxOrderPrice{decimal64::Decimal<2>::FromFloatInexact(120.0),
                                 std::nullopt}));
}

TEST(ValivatationMinOrderPriceWithoutFeatureDataFull,
     ThrowExceptionIfAvaragePriceLessMinOrderPrice) {
  StrictMock<clients::eats_core_restapp::ClientGMock> eats_core_restapp;
  clients::eats_core_restapp::v1_places_receipts_get_average::get::Response
      response;
  response.payload = {{1, 5}, {2, 50}, {3, 100}};
  EXPECT_CALL(eats_core_restapp, V1PlacesReceiptsGetAverage(_, _))
      .WillOnce(Return(response));
  ASSERT_THROW(
      ValidateMinOrderPrice(
          eats_core_restapp, {}, {1, {1, 2}},
          handlers::MinMaxOrderPrice{
              decimal64::Decimal<2>::FromFloatInexact(10.0), std::nullopt}),
      models::ValidationError);
}

TEST(ValidateMinOrderPrice,
     DontThrowExceptionForFreeDeliveryIfMinOrderPriceNotInSettings) {
  StrictMock<clients::eats_core_restapp::ClientGMock> eats_core_restapp;
  clients::eats_core_restapp::v1_places_receipts_get_average::get::Response
      response;
  response.payload = {{1, 5}, {2, 50}, {3, 100}};
  EXPECT_CALL(eats_core_restapp, V1PlacesReceiptsGetAverage(_, _))
      .WillOnce(Return(response));
  ASSERT_NO_THROW(ValidateMinOrderPrice(
      eats_core_restapp, {}, types::RequestInfo{1, {1, 2, 3}},
      handlers::MinMaxOrderPrice{decimal64::Decimal<2>::FromFloatInexact(3.1),
                                 std::nullopt}));
}

TEST(ValidateMinOrderPrice,
     DontThrowExceptionForFreeDeliveryIfMinOrderPriceIsOk) {
  StrictMock<clients::eats_core_restapp::ClientGMock> eats_core_restapp;
  clients::eats_core_restapp::v1_places_receipts_get_average::get::Response
      response;
  response.payload = {{1, 5}, {2, 50}, {3, 100}};
  EXPECT_CALL(eats_core_restapp, V1PlacesReceiptsGetAverage(_, _))
      .WillOnce(Return(response));
  ASSERT_NO_THROW(ValidateMinOrderPrice(
      eats_core_restapp, {}, types::RequestInfo{1, {1, 2, 3}},
      handlers::MinMaxOrderPrice{decimal64::Decimal<2>::FromFloatInexact(1.5),
                                 std::nullopt}));
}

TEST(ValidateMinOrderPrice,
     ThrowExceptionForFreeDeliveryIfMinOrderPriceLargeThenAvaregeCheque) {
  StrictMock<clients::eats_core_restapp::ClientGMock> eats_core_restapp;
  clients::eats_core_restapp::v1_places_receipts_get_average::get::Response
      response;
  response.payload = {{1, 5}, {2, 50}, {3, 100}};
  EXPECT_CALL(eats_core_restapp, V1PlacesReceiptsGetAverage(_, _))
      .WillOnce(Return(response));
  ASSERT_THROW(
      ValidateMinOrderPrice(
          eats_core_restapp, {}, types::RequestInfo{1, {1, 2, 3}},
          handlers::MinMaxOrderPrice{
              decimal64::Decimal<2>::FromFloatInexact(6.0), std::nullopt}),
      models::ValidationError);
}

TEST(
    ValidateMinOrderPrice,
    ThrowExceptionForFreeDeliveryIfMinOrderPriceLargeThenAvaregeChequeWithAdditionalAmount) {
  StrictMock<clients::eats_core_restapp::ClientGMock> eats_core_restapp;
  clients::eats_core_restapp::v1_places_receipts_get_average::get::Response
      response;
  response.payload = {{1, 5}, {2, 50}, {3, 100}};
  EXPECT_CALL(eats_core_restapp, V1PlacesReceiptsGetAverage(_, _))
      .WillOnce(Return(response));
  models::PromoChecks checks;
  checks.average_cheque_checker.amount =
      decimal64::Decimal<2, decimal64::DefRoundPolicy>{"1"};
  ASSERT_NO_THROW(ValidateMinOrderPrice(
      eats_core_restapp, checks, types::RequestInfo{1, {1, 2, 3}},
      handlers::MinMaxOrderPrice{decimal64::Decimal<2>::FromFloatInexact(6.0),
                                 std::nullopt}));
}

TEST(
    ValidateMinOrderPrice,
    DontThrowExceptionForFreeDeliveryIfMinOrderPriceLargeThenAvaregeChequeAndAvaregeChequeNotInCoreRrsponse) {
  StrictMock<clients::eats_core_restapp::ClientGMock> eats_core_restapp;
  clients::eats_core_restapp::v1_places_receipts_get_average::get::Response
      response;
  response.payload = {{1, 5}, {2, 50}, {3, 100}};
  EXPECT_CALL(eats_core_restapp, V1PlacesReceiptsGetAverage(_, _))
      .WillOnce(Return(response));
  ASSERT_NO_THROW(ValidateMinOrderPrice(
      eats_core_restapp, {}, types::RequestInfo{1, {2, 3, 4}},
      handlers::MinMaxOrderPrice{decimal64::Decimal<2>::FromFloatInexact(6.0),
                                 std::nullopt}));
}

TEST(
    ValidateMinOrderPrice,
    DontThrowExceptionForFreeDeliveryIfMinOrderPriceLargeThenAvaregeChequeAndAvaregeChequesIsEmpty) {
  StrictMock<clients::eats_core_restapp::ClientGMock> eats_core_restapp;
  clients::eats_core_restapp::v1_places_receipts_get_average::get::Response
      response;
  EXPECT_CALL(eats_core_restapp, V1PlacesReceiptsGetAverage(_, _))
      .WillOnce(Return(response));
  ASSERT_NO_THROW(ValidateMinOrderPrice(
      eats_core_restapp, {}, types::RequestInfo{1, {2, 3, 4}},
      handlers::MinMaxOrderPrice{decimal64::Decimal<2>::FromFloatInexact(6.0),
                                 std::nullopt}));
}

}  // namespace eats_restapp_promo::utils
