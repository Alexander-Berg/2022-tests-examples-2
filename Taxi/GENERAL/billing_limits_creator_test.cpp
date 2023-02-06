#include <string>

#include <discounts/models/error.hpp>
#include <userver/tracing/span.hpp>
#include <userver/utest/utest.hpp>

#include <clients/billing-limits/client.hpp>
#include <clients/billing-limits/client_gmock.hpp>
#include <clients/billing-limits/definitions.hpp>
#include <defs/all_definitions.hpp>
#include <utils/billing_limits_creator.hpp>

const auto kLimit = formats::json::FromString(R"JSON(
{
    "currency": "RUB",
    "label": "Discount limit id",
    "windows": [
        {
            "type": "sliding",
            "value": "350000.0000",
            "size": 604800,
            "label": "Weekly limit",
            "threshold": 100
        },
        {
            "type": "tumbling",
            "value": "50000.0000",
            "size": 86400,
            "label": "Daily limit",
            "threshold": 100,
            "tumbling_start": "2021-10-10T21:00:00+00:00"
        }
    ],
    "tickets": [
        "TICKET-1"
    ],
    "tags": ["ride-discounts"],
    "ref": "discount_limit_id",
    "account_id": "discount_account_id",
    "approvers": [
        "staff_login"
    ]
}
)JSON")
                        .As<clients::billing_limits::Limit>();

const auto kLimitDraft = formats::json::FromString(R"JSON(
{
    "currency": "RUB",
    "label": "Discount limit new_discount_limit_id",
    "windows": [
        {
            "type": "tumbling",
            "value": "60000",
            "size": 86400,
            "label": "Daily limit",
            "threshold": 100,
            "tumbling_start": "2021-10-10T21:00:00+00:00"
        },
        {
            "type": "sliding",
            "value": "360000",
            "size": 604800,
            "label": "Weekly limit",
            "threshold": 100
        }
    ],
    "tickets": [
        "TICKET-1"
    ],
    "tags": ["ride-discounts"],
    "ref": "new_discount_limit_id",
    "account_id": "discount_account_id",
    "approvers": [
        "staff_login"
    ]
}
)JSON")
                             .As<clients::billing_limits::LimitDraft>();

auto MatchRequest(
    const clients::billing_limits::v1_get::post::Request& request) {
  return ::testing::Field(&clients::billing_limits::v1_get::post::Request::body,
                          request.body);
}

auto MatchLimit(const clients::billing_limits::LimitDraft& body) {
  return ::testing::AllOf(
      ::testing::Field(&clients::billing_limits::LimitDraft::ref, body.ref),
      ::testing::Field(&clients::billing_limits::LimitDraft::currency,
                       body.currency),
      ::testing::Field(&clients::billing_limits::LimitDraft::label, body.label),
      ::testing::Field(&clients::billing_limits::LimitDraft::windows,
                       body.windows),
      ::testing::Field(&clients::billing_limits::LimitDraft::tickets,
                       body.tickets),
      ::testing::Field(&clients::billing_limits::LimitDraft::approvers,
                       body.approvers),
      ::testing::Field(&clients::billing_limits::LimitDraft::tags, body.tags),
      ::testing::Field(&clients::billing_limits::LimitDraft::account_id,
                       body.account_id));
}

auto MatchRequest(
    const clients::billing_limits::v1_create::post::Request& request) {
  return ::testing::Field(
      &clients::billing_limits::v1_create::post::Request::body,
      MatchLimit(request.body));
}

UTEST(BillingLimitsCreator, WithoutCreateNewLimit) {
  clients::billing_limits::ClientGMock client;
  clients::billing_limits::v1_get::post::Request request_get{
      {"discount_limit_id"}};
  clients::billing_limits::v1_get::post::Response200 response_get{
      clients::billing_limits::GetResponse{kLimit}};

  EXPECT_CALL(client, get(MatchRequest(request_get), testing::_))
      .Times(2)
      .WillRepeatedly(testing::Return(response_get));

  EXPECT_CALL(client, create(testing::_, testing::_)).Times(0);

  utils::BillingLimitsCreator creator(client);
  auto limits = handlers::Limits{
      "discount_limit_id", handlers::LimitsDailylimit{"50000", 100},
      handlers::LimitsWeeklylimit{"350000", 100,
                                  handlers::LimitsWeeklylimitType::kSliding}};
  auto now = utils::datetime::Now();
  EXPECT_THROW(creator.Create(limits, "discount_limit_id", "USD", now, {}, {}),
               discounts::models::Error);
  EXPECT_NO_THROW(
      creator.Create(limits, "discount_limit_id", "RUB", now, {}, {}));
}

UTEST(BillingLimitsCreator, WithCreateNewLimit) {
  clients::billing_limits::ClientGMock client;
  clients::billing_limits::v1_get::post::Request request_get{
      {"discount_limit_id"}};
  clients::billing_limits::v1_get::post::Response200 response_get{
      clients::billing_limits::GetResponse{kLimit}};

  EXPECT_CALL(client, get(MatchRequest(request_get), testing::_))
      .Times(2)
      .WillRepeatedly(testing::Return(response_get));

  clients::billing_limits::v1_create::post::Request request_create{
      tracing::Span::CurrentSpan().GetLink(),
      clients::billing_limits::CreateRequest{kLimitDraft}};

  clients::billing_limits::v1_create::post::Response200 response_create{
      clients::billing_limits::CreateResponse{kLimit}};
  EXPECT_CALL(client, create(MatchRequest(request_create), testing::_))
      .Times(1)
      .WillRepeatedly(testing::Return(response_create));
  utils::BillingLimitsCreator creator(client);
  auto limits = handlers::Limits{
      "new_discount_limit_id", handlers::LimitsDailylimit{"60000", 100},
      handlers::LimitsWeeklylimit{"360000", 100,
                                  handlers::LimitsWeeklylimitType::kSliding}};

  auto now = utils::datetime::Stringtime("2021-10-10T21:00:00+00:00", "UTC",
                                         utils::kBillingLimitsDatetimeFormat);
  EXPECT_NO_THROW(creator.Create(limits, "discount_limit_id", "RUB", now,
                                 {"staff_login"}, {"TICKET-1"}));
  EXPECT_THROW(creator.Create(limits, "discount_limit_id", "USD", now, {}, {}),
               discounts::models::Error);
}
