#include "discount_usages.hpp"

#include <clients/eats-discounts-statistics/client_gmock.hpp>
#include <defs/all_definitions.hpp>
#include <userver/utest/utest.hpp>

namespace utils {

namespace {

const int64_t kYandexUid = 123;
const std::string kPersonalPhoneId = "test_personal_phone_id";
const std::string kEater = "test_eater_id";
std::vector<int64_t> kDiscountIds = {1, 2};
size_t kCountUsages = 2;

auto MatchRequest(
    const clients::eats_discounts_statistics::v1_get::post::Request& request) {
  return ::testing::Field(
      &clients::eats_discounts_statistics::v1_get::post::Request::body,
      request.body);
}

ACTION(Exception) { throw std::exception{}; }

}  // namespace

UTEST(GetDiscountUsages, Ok) {
  clients::eats_discounts_statistics::ClientGMock client;
  clients::eats_discounts_statistics::v1_get::post::Request expected_request;
  expected_request.body.yandex_uid = std::to_string(kYandexUid);
  expected_request.body.personal_phone_id = kPersonalPhoneId;
  expected_request.body.eater_id = kEater;

  clients::eats_discounts_statistics::v1_get::post::Response200 response;
  for (auto discount_id : kDiscountIds) {
    response.items.push_back({discount_id, kCountUsages, 1000});
  }

  EXPECT_CALL(client, V1Get(MatchRequest(expected_request), testing::_))
      .Times(1)
      .WillOnce(testing::Return(response));

  DiscountUsages expected;
  for (auto discount_id : kDiscountIds) {
    expected[discount_id] = kCountUsages;
  }

  auto discount_usages = GetDiscountUsages(handlers::User{kPersonalPhoneId},
                                           kEater, kYandexUid, client);
  EXPECT_EQ(discount_usages, expected);
}

UTEST(GetDiscountUsages, ErrorInClient) {
  clients::eats_discounts_statistics::ClientGMock client;
  EXPECT_CALL(client, V1Get(testing::_, testing::_))
      .Times(1)
      .WillOnce(Exception());
  auto discount_usages = GetDiscountUsages(handlers::User{kPersonalPhoneId},
                                           kEater, kYandexUid, client);
  EXPECT_EQ(discount_usages, std::nullopt);
}

}  // namespace utils
