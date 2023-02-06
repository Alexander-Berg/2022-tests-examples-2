#include <userver/utest/utest.hpp>

#include <algorithm>
#include <unordered_map>

#include <userver/dump/common.hpp>
#include <userver/dump/config.hpp>
#include <userver/dynamic_config/storage_mock.hpp>
#include <userver/formats/json/serialize.hpp>
#include <userver/formats/yaml/serialize.hpp>
#include <userver/fs/blocking/temp_directory.hpp>
#include <userver/logging/log.hpp>
#include <userver/testsuite/dump_control.hpp>
#include <userver/utils/datetime.hpp>
#include <userver/utils/mock_now.hpp>
#include <userver/utils/text.hpp>

#include <components/dumpable_driver_orders_cache.hpp>
#include <eventus/mappers/remote/fetch_driver_orders_mapper.hpp>
#include <test/common.hpp>
#include <test/mocks/driver_orders_client_mock.hpp>

namespace {

using Request = clients::driver_orders::v1_parks_orders_list::post::Request;
using Response =
    clients::driver_orders::v1_parks_orders_list::post::Response200;
using RequestBody = clients::driver_orders::v1_parks_orders_list::post::Body;
using test::common::OperationArgsV;

const auto kProfilesSrcKey = "unique_driver_profiles";
const auto kDriverOrdersDstKey = "driver_orders";
const auto kRelativeTimepointKey = "time_point";
const auto kTestTimestamp = "2020-06-12T00:00:00.124+03:00";

const auto kBookedSinceOffset = "4d";
const auto kBookedUntilOffset = "3d";

std::string TestTimestring(
    const std::chrono::system_clock::time_point& timestamp) {
  return utils::datetime::Timestring(timestamp,
                                     utils::datetime::kDefaultTimezone,
                                     utils::datetime::kRfc3339Format);
}

std::chrono::system_clock::time_point TestStringtime(
    const std::string& timestring) {
  return utils::datetime::Stringtime(timestring,
                                     utils::datetime::kDefaultTimezone,
                                     utils::datetime::kRfc3339Format);
}

RequestBody MakeRequestBody(const std::string& park_id,
                            const std::string& driver_profile_id,
                            std::chrono::system_clock::time_point mock_now) {
  const auto booked_from =
      TestTimestring(mock_now - utils::StringToDuration(kBookedSinceOffset));
  const auto booked_to =
      TestTimestring(mock_now - utils::StringToDuration(kBookedUntilOffset));

  const std::string body_json_str = R"({
              "query": {
                "park": {
                  "id": ")" + park_id +
                                    R"(",
                  "order": {
                    "booked_at": {
                      "from": ")" + booked_from +
                                    R"(",
                      "to": ")" + booked_to +
                                    R"("
                    },
                    "statuses": ["complete"],
                    "payment_methods": ["cash"],
                    "providers": ["formula"],
                    "categories": ["category1", "category2"]
                  },
                  "driver_profile": {
                    "id": ")" + driver_profile_id +
                                    R"("
                  }
                }
              },
              "limit": 1
            })";
  return clients::driver_orders::v1_parks_orders_list::post::Parse(
      formats::json::FromString(body_json_str),
      formats::parse::To<RequestBody>());
}

clients::driver_orders::Order MakeResponseOrder(
    const int offset, const std::chrono::system_clock::time_point& mock_now) {
  clients::driver_orders::Order order;
  order.id = "65304769439718f698a7c26ccc" + std::to_string(270952 + offset);
  order.short_id = 116757 + offset;
  order.status = clients::driver_orders::Status::kComplete;
  order.created_at = mock_now;
  order.booked_at = mock_now;
  order.provider = clients::driver_orders::Provider::kPlatform;
  order.category = "express";
  return order;
}

MATCHER_P(MatchDriverOrderRequestWrapper, suite, "") {
  return suite->PushRequest(arg);
}

std::string PrintOperationArgsParam(
    const ::testing::TestParamInfo<OperationArgsV>& data) {
  return test::common::PrintOperationArgs(data.param);
}

struct Responses {
  std::vector<Response> responses;
  std::vector<formats::json::Value> expected_value;
};

Responses BuildResponses(
    const std::chrono::system_clock::time_point& mock_now) {
  // XXX: there is no Parse implementation from json-string into
  // Response200, so fill it manually
  std::vector<Response> responses;
  std::vector<formats::json::Value> expected_value;
  {
    const auto order = MakeResponseOrder(0, mock_now);
    expected_value.push_back(clients::driver_orders::Serialize(
        order, formats::serialize::To<formats::json::Value>()));

    Response response;
    response.orders.push_back(order);
    responses.push_back(std::move(response));
  }
  {
    const auto order1 = MakeResponseOrder(1, mock_now);
    expected_value.push_back(clients::driver_orders::Serialize(
        order1, formats::serialize::To<formats::json::Value>()));

    const auto order2 =
        MakeResponseOrder(2, mock_now + std::chrono::seconds(5));
    expected_value.push_back(clients::driver_orders::Serialize(
        order2, formats::serialize::To<formats::json::Value>()));

    Response response;
    response.orders.push_back(order1);
    response.orders.push_back(order2);
    responses.push_back(std::move(response));
  }
  return {responses, expected_value};
}

formats::json::Value BuildCachedResponses(
    const std::chrono::system_clock::time_point& mock_now) {
  formats::json::ValueBuilder builder(formats::json::Type::kArray);
  {
    const auto order = MakeResponseOrder(0, mock_now);
    const auto order_json = clients::driver_orders::Serialize(
        order, formats::serialize::To<formats::json::Value>());
    builder.PushBack(std::move(order_json));
  }
  {
    const auto order2 =
        MakeResponseOrder(2, mock_now + std::chrono::seconds(5));
    const auto order_json2 = clients::driver_orders::Serialize(
        order2, formats::serialize::To<formats::json::Value>());
    builder.PushBack(std::move(order_json2));
  }
  return builder.ExtractValue();
}

template <typename T>
void AssertDatetimeInterval(
    const std::optional<T>& datetime_interval,
    const std::chrono::system_clock::time_point& timestamp) {
  if (!datetime_interval) {
    return;
  }

  ASSERT_LT(datetime_interval->from, timestamp);
  ASSERT_LT(datetime_interval->to, timestamp);
  ASSERT_GT(datetime_interval->from, timestamp - 7 * std::chrono::hours(24));
  ASSERT_GT(datetime_interval->to, timestamp - 7 * std::chrono::hours(24));
}

class DriverOrdersMapperSuite : public ::testing::Test {
 public:
  std::vector<Request> requests;

  bool PushRequest(const Request& request) {
    auto found = std::find_if(
        std::begin(requests), std::end(requests), [&request](const auto& item) {
          return request.body.query.park.id == item.body.query.park.id;
        });

    using namespace formats::serialize;
    To<formats::json::Value> adl_helper;
    if (found == std::end(requests)) {
      LOG_DEBUG() << "Unexpected request: "
                  << ToString(Serialize(request.body, adl_helper));
    }
    EXPECT_TRUE(found != std::end(requests));
    EXPECT_EQ(Serialize(found->body, adl_helper),
              Serialize(request.body, adl_helper));
    return true;
  }

  eventus::mappers::remote::FetchDriverOrdersMapper::BaseTypePtr MakeMapper(
      clients::driver_orders::Client& driver_orders_client_mock,
      components::detail::DriverOrdersCache& driver_orders_cache,
      bool with_ref_time_point = true) {
    OperationArgsV opargs{
        {"driver_profiles_src_key", kProfilesSrcKey},
        {"driver_orders_dst_key", kDriverOrdersDstKey},
        {"orders_booked_since_offset", kBookedSinceOffset},
        {"orders_booked_until_offset", kBookedUntilOffset},
        {"order_statuses", std::vector<std::string>{"complete"}},
        {"order_payment_methods", std::vector<std::string>{"cash"}},
        {"order_providers", std::vector<std::string>{"formula"}},
        {"order_categories",
         std::vector<std::string>{
             "category1",
             "category2",
         }},
        {"debug", "yes"},
    };
    if (with_ref_time_point) {
      opargs.emplace_back("reference_time_point_key",
                          std::string{"time_point"});
    }
    return test::common::MakeOperation<
        eventus::mappers::remote::FetchDriverOrdersMapper>(
        opargs, driver_orders_client_mock, driver_orders_cache);
  }

  template <typename T = std::chrono::system_clock::time_point>
  eventus::mappers::Event MakeOrderEvent(
      std::optional<T> ref_time_point = std::nullopt) {
    eventus::mappers::Event event({});
    if (ref_time_point.has_value()) {
      if constexpr (std::is_same_v<T, double>) {
        event.Set(kRelativeTimepointKey, *ref_time_point);
      } else {
        event.Set(kRelativeTimepointKey, TestTimestring(*ref_time_point));
      }
    }

    event.Set(kProfilesSrcKey, formats::json::FromString(R"([
        {
          "park_id":"park-id1",
          "driver_profile_id":"driver-profile-id1",
          "park_driver_profile_id":"park-driver-profile-id1"
        },
        {
          "park_id":"park-id2",
          "driver_profile_id":"driver-profile-id2",
          "park_driver_profile_id":"park-driver-profile-id2"
        }
    ])"));
    return event;
  }
};

}  // namespace

class DriverOrdersMapperBadArgumentsSuite
    : public ::testing::TestWithParam<OperationArgsV> {};

INSTANTIATE_UTEST_SUITE_P(
    /**/, DriverOrdersMapperBadArgumentsSuite,
    ::testing::Values(
        OperationArgsV{{"orders_booked_until_offset", "3d"}},
        OperationArgsV{{"orders_booked_since_offset", "4d"}},
        OperationArgsV{{"orders_ended_until_offset", "3d"}},
        OperationArgsV{{"orders_ended_since_offset", "4d"}},
        OperationArgsV{{"orders_booked_until_offset", "-3d"},
                       {"orders_booked_since_offset", "4d"}},
        OperationArgsV{{"orders_ended_until_offset", "3d"},
                       {"orders_ended_since_offset", "-4d"}},
        OperationArgsV{{"order_statuses", std::vector<std::string>{}}},
        OperationArgsV{
            {"order_statuses", std::vector<std::string>{"bad-value"}}},
        OperationArgsV{{"order_payment_methods", std::vector<std::string>{}}},
        OperationArgsV{
            {"order_payment_methods", std::vector<std::string>{"bad-value"}}},
        OperationArgsV{{"order_providers", std::vector<std::string>{}}},
        OperationArgsV{
            {"order_providers", std::vector<std::string>{"bad-value"}}},
        OperationArgsV{{"order_categories", std::vector<std::string>{}}}),
    PrintOperationArgsParam);

UTEST_P(DriverOrdersMapperBadArgumentsSuite, RunTest) {
  using test::mocks::DriverOrdersClient;
  DriverOrdersClient driver_orders_client_mock;

  components::detail::DriverOrdersCache driver_orders_cache(100);
  const auto& param = GetParam();

  using namespace test::common;
  OperationArgsV base_args{
      {"driver_profiles_src_key", kProfilesSrcKey},
      {"driver_orders_dst_key", kDriverOrdersDstKey},
  };
  base_args.insert(base_args.end(), param.begin(), param.end());
  EXPECT_THROW(MakeOperation<eventus::mappers::remote::FetchDriverOrdersMapper>(
                   base_args, driver_orders_client_mock, driver_orders_cache),
               std::exception);
}

class DriverOrdersMapperGoodArgumentsSuite
    : public ::testing::TestWithParam<OperationArgsV> {};

INSTANTIATE_UTEST_SUITE_P(
    /**/, DriverOrdersMapperGoodArgumentsSuite,
    ::testing::Values(OperationArgsV{{"orders_booked_until_offset", "3d"},
                                     {"orders_booked_since_offset", "4d"}},
                      OperationArgsV{{"orders_booked_until_offset", "4d"},
                                     {"orders_booked_since_offset", "4d"}},
                      OperationArgsV{{"orders_ended_until_offset", "3d"},
                                     {"orders_ended_since_offset", "4d"}},
                      OperationArgsV{{"orders_ended_until_offset", "4d"},
                                     {"orders_ended_since_offset", "4d"}},
                      OperationArgsV{{"order_statuses",
                                      std::vector<std::string>{"complete"}}},
                      OperationArgsV{{"order_payment_methods",
                                      std::vector<std::string>{"cash"}}},
                      OperationArgsV{{"order_providers",
                                      std::vector<std::string>{"formula"}}},
                      OperationArgsV{{"order_categories",
                                      std::vector<std::string>{
                                          "category1",
                                          "category2",
                                      }}},
                      OperationArgsV{{"debug", "yes"}},
                      OperationArgsV{
                          {"debug", static_cast<double>(1234567890)}}),
    PrintOperationArgsParam);

UTEST_P(DriverOrdersMapperGoodArgumentsSuite, RunTest) {
  using test::mocks::DriverOrdersClient;
  DriverOrdersClient driver_orders_client_mock;

  components::detail::DriverOrdersCache driver_orders_cache(100);
  const auto& param = GetParam();

  using namespace test::common;
  OperationArgsV base_args{
      {"driver_profiles_src_key", kProfilesSrcKey},
      {"driver_orders_dst_key", kDriverOrdersDstKey},
  };
  eventus::common::OperationArgs param_args(param);
  if (!param_args.HasKey("orders_booked_since_offset") &&
      !param_args.HasKey("orders_ended_since_offset")) {
    OperationArgsV required_arguments{{"orders_booked_until_offset", "4d"},
                                      {"orders_booked_since_offset", "4d"}};
    base_args.insert(base_args.end(), required_arguments.begin(),
                     required_arguments.end());
  }

  base_args.insert(base_args.end(), param.begin(), param.end());
  EXPECT_NO_THROW(
      MakeOperation<eventus::mappers::remote::FetchDriverOrdersMapper>(
          base_args, driver_orders_client_mock, driver_orders_cache));
}

UTEST_F(DriverOrdersMapperSuite, FetchDriverOrdersMapperTest) {
  using test::mocks::DriverOrdersClient;
  DriverOrdersClient driver_orders_client_mock;

  components::detail::DriverOrdersCache driver_orders_cache(100);

  utils::datetime::MockNowSet(TestStringtime(kTestTimestamp));
  const auto mock_now = utils::datetime::MockNow();
  using namespace test::common;
  auto mapper = MakeMapper(driver_orders_client_mock, driver_orders_cache,
                           /* with_ref_time_point */ false);

  auto&& [responses, expected_value] = BuildResponses(mock_now);

  EXPECT_CALL(
      driver_orders_client_mock,
      V1ParksOrdersList(MatchDriverOrderRequestWrapper(this), testing::_))
      .WillOnce(testing::Return(responses[0]))
      .WillOnce(testing::Return(responses[1]));
  {
    Request request;
    request.body = MakeRequestBody("park-id1", "driver-profile-id1", mock_now);
    requests.push_back(request);
  }
  {
    Request request;
    request.body = MakeRequestBody("park-id2", "driver-profile-id2", mock_now);
    requests.push_back(request);
  }

  auto event = MakeOrderEvent();
  mapper->Map(event);

  std::sort(requests.begin(), requests.end(),
            [](const auto& lhs, const auto& rhs) {
              return lhs.body.query.park.id.compare(rhs.body.query.park.id) < 0;
            });
  ASSERT_EQ(requests[0].body.query.park.id, "park-id1");
  AssertDatetimeInterval(requests[0].body.query.park.order.booked_at, mock_now);
  AssertDatetimeInterval(requests[0].body.query.park.order.ended_at, mock_now);

  ASSERT_EQ(requests[1].body.query.park.id, "park-id2");
  AssertDatetimeInterval(requests[1].body.query.park.order.booked_at, mock_now);
  AssertDatetimeInterval(requests[1].body.query.park.order.ended_at, mock_now);

  ASSERT_TRUE(event.HasKey(kDriverOrdersDstKey));
  {
    formats::json::ValueBuilder builder(expected_value);
    ASSERT_EQ(event.Get<formats::json::Value>(kDriverOrdersDstKey),
              builder.ExtractValue());
  }

  // Check value were cached already
  auto event_from_cache = MakeOrderEvent();

  EXPECT_CALL(
      driver_orders_client_mock,
      V1ParksOrdersList(MatchDriverOrderRequestWrapper(this), testing::_))
      .Times(0);
  mapper->Map(event_from_cache);

  ASSERT_TRUE(event.HasKey(kDriverOrdersDstKey));
  const auto cached_responses = BuildCachedResponses(mock_now);
  ASSERT_EQ(event_from_cache.Get<formats::json::Value>(kDriverOrdersDstKey),
            cached_responses);
}

UTEST_F(DriverOrdersMapperSuite, FetchDriverOrdersMapperTimePointKeyTest) {
  using test::mocks::DriverOrdersClient;
  DriverOrdersClient driver_orders_client_mock;

  components::detail::DriverOrdersCache driver_orders_cache(100);

  utils::datetime::MockNowSet(TestStringtime(kTestTimestamp));
  const auto mock_now = utils::datetime::MockNow();
  const auto expected_time = mock_now - std::chrono::hours(24);
  using namespace test::common;
  auto mapper = MakeMapper(driver_orders_client_mock, driver_orders_cache);

  auto&& [responses, expected_value] = BuildResponses(mock_now);

  EXPECT_CALL(
      driver_orders_client_mock,
      V1ParksOrdersList(MatchDriverOrderRequestWrapper(this), testing::_))
      .WillOnce(testing::Return(responses[0]))
      .WillOnce(testing::Return(responses[1]));
  {
    Request request;
    request.body =
        MakeRequestBody("park-id1", "driver-profile-id1", expected_time);
    requests.push_back(request);
  }
  {
    Request request;
    request.body =
        MakeRequestBody("park-id2", "driver-profile-id2", expected_time);
    requests.push_back(request);
  }

  auto event =
      MakeOrderEvent(std::optional<decltype(expected_time)>{expected_time});
  mapper->Map(event);

  std::sort(requests.begin(), requests.end(),
            [](const auto& lhs, const auto& rhs) {
              return lhs.body.query.park.id.compare(rhs.body.query.park.id) < 0;
            });
  ASSERT_EQ(requests[0].body.query.park.id, "park-id1");
  ASSERT_EQ(requests[1].body.query.park.id, "park-id2");
  AssertDatetimeInterval(requests[0].body.query.park.order.booked_at,
                         expected_time);
  AssertDatetimeInterval(requests[0].body.query.park.order.ended_at,
                         expected_time);
  AssertDatetimeInterval(requests[1].body.query.park.order.booked_at,
                         expected_time);
  AssertDatetimeInterval(requests[1].body.query.park.order.ended_at,
                         expected_time);

  ASSERT_TRUE(event.HasKey(kDriverOrdersDstKey));
  {
    formats::json::ValueBuilder builder(expected_value);
    ASSERT_EQ(event.Get<formats::json::Value>(kDriverOrdersDstKey),
              builder.ExtractValue());
  }

  // Check value were cached already
  auto event_from_cache = MakeOrderEvent(std::optional<double>{
      static_cast<double>(expected_time.time_since_epoch().count()) / 1e9});

  EXPECT_CALL(
      driver_orders_client_mock,
      V1ParksOrdersList(MatchDriverOrderRequestWrapper(this), testing::_))
      .Times(0);
  mapper->Map(event_from_cache);

  ASSERT_TRUE(event.HasKey(kDriverOrdersDstKey));
  const auto cached_responses = BuildCachedResponses(mock_now);
  ASSERT_EQ(event_from_cache.Get<formats::json::Value>(kDriverOrdersDstKey),
            cached_responses);
}
