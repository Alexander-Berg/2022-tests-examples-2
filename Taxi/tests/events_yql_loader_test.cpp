
#include <functional>

#include <userver/utest/parameter_names.hpp>
#include <userver/utest/utest.hpp>

#include <clients/yql/client_mock_base.hpp>

#include <events/query.hpp>
#include <events/yql_loader.hpp>

namespace coupons::events {

namespace {

const std::string kYqlToken = "yql_secret_token";
const std::string kEnvName = "testing";
const std::string kOperationId = "605837690b8423c82c37d834";
const std::string kUnknown = "UNKNOWN";
const std::string kTimestringFormat = "%Y-%m-%dT%H:%M:%E6S";

TimePoint TimePointFromString(const std::string& source) {
  return ::utils::datetime::Stringtime(
      source, ::utils::datetime::kDefaultTimezone, kTimestringFormat);
}

EventsQuery SimpleQuery() {
  EventsQuery query;
  query.coupon = "promocode";
  return query;
}

YqlLoader CreateYqlLoader(const clients::yql::Client& yql_client) {
  using namespace std::chrono_literals;
  const YqlLoaderParams::StatusPolling status_polling_params{1ms, 5ms};
  return {yql_client, kYqlToken, kEnvName, {status_polling_params}};
}

namespace yql_operations = clients::yql::api_v2_operations;
using ExecuteOperationRequest = yql_operations::post::Request;
using ExecuteOperationResponse = yql_operations::post::Response;
using ExecuteOperationHandler =
    std::function<ExecuteOperationResponse(const ExecuteOperationRequest&)>;

namespace yql_operation_status = clients::yql::api_v2_operations_operation_id;
using OperationStatusRequest = yql_operation_status::get::Request;
using OperationStatusResponse = yql_operation_status::get::Response;
using OperationStatusHandler =
    std::function<OperationStatusResponse(const OperationStatusRequest&)>;

namespace yql_operation_results =
    clients::yql::api_v2_operations_operation_id_results_data;
using OperationResultsRequest = yql_operation_results::get::Request;
using OperationResultsResponse = yql_operation_results::get::Response;
using OperationResultsHandler =
    std::function<OperationResultsResponse(const OperationResultsRequest&)>;

class YqlClientMock : public clients::yql::ClientMockBase {
 public:
  ExecuteOperationResponse ExecuteOperation(
      const ExecuteOperationRequest& request,
      const clients::yql::CommandControl& = {}) const override {
    if (execute_operation_handler_) {
      return (*execute_operation_handler_)(request);
    }

    ExecuteOperationResponse response;
    response.id = kOperationId;
    return response;
  }

  void SetExecuteOperationHandler(const ExecuteOperationHandler& handler) {
    execute_operation_handler_ = handler;
  }

  OperationStatusResponse OperationStatus(
      const OperationStatusRequest& request,
      const clients::yql::CommandControl& = {}) const override {
    if (operation_status_handler_) {
      return (*operation_status_handler_)(request);
    }

    OperationStatusResponse response;
    response.id = kOperationId;
    response.status = GetOperationStatus();
    return response;
  }

  void SetOperationStatusHandler(const OperationStatusHandler& handler) {
    operation_status_handler_ = handler;
  }

  void SetOperationStatusResponses(
      const std::vector<clients::yql::OperationStatus>& responses) {
    status_responses_ = responses;
  }

  OperationResultsResponse OperationResultsData(
      const OperationResultsRequest& request,
      const clients::yql::CommandControl& = {}) const override {
    if (operation_results_handler_) {
      return (*operation_results_handler_)(request);
    }

    OperationResultsResponse response;
    response.body = operation_results_data_.value_or("");
    return response;
  }

  void SetOperationResultsHandler(const OperationResultsHandler& handler) {
    operation_results_handler_ = handler;
  }

  void SetOperationResultsData(const std::string& data) {
    operation_results_data_ = data;
  }

 private:
  std::optional<ExecuteOperationHandler> execute_operation_handler_;
  std::optional<OperationStatusHandler> operation_status_handler_;
  std::optional<OperationResultsHandler> operation_results_handler_;

  mutable std::size_t status_handler_times_called_ = 0;
  std::vector<clients::yql::OperationStatus> status_responses_;

  std::optional<std::string> operation_results_data_;

  clients::yql::OperationStatus GetOperationStatus() const {
    if (status_responses_.empty()) {
      return clients::yql::OperationStatus::kCompleted;
    }
    if (status_handler_times_called_ >= status_responses_.size()) {
      return status_responses_.back();
    }
    return status_responses_[status_handler_times_called_++];
  }
};

}  // namespace

struct OperationNotCreatedParams {
  ExecuteOperationHandler execute_operation_handler;
  std::string test_name;
};

class EventsYqlLoaderOperationNotCreated
    : public testing::Test,
      public testing::WithParamInterface<OperationNotCreatedParams> {};

const std::vector<OperationNotCreatedParams> operation_not_created_params{
    {
        [](const ExecuteOperationRequest&) -> ExecuteOperationResponse {
          throw clients::http::TimeoutException();
        },
        "YqlClientTimeout",
    },
    {
        [](const ExecuteOperationRequest&) -> ExecuteOperationResponse {
          throw clients::http::HttpClientException(500, {});
        },
        "YqlClientInternalServerError",
    },
    {
        [](const ExecuteOperationRequest&) {
          return ExecuteOperationResponse{};
        },
        "OperationIdMissingFromResponse",
    },
};

TEST_P(EventsYqlLoaderOperationNotCreated, ) {
  YqlClientMock yql_client;
  yql_client.SetExecuteOperationHandler(GetParam().execute_operation_handler);
  auto loader = CreateYqlLoader(yql_client);

  EXPECT_THROW(loader.LoadEvents(SimpleQuery()), LoaderException);
}

INSTANTIATE_TEST_SUITE_P(, EventsYqlLoaderOperationNotCreated,
                         testing::ValuesIn(operation_not_created_params),
                         ::utest::PrintTestName());

struct OperationPollingFailedParams {
  std::optional<OperationStatusHandler> operation_status_handler;
  std::optional<std::vector<clients::yql::OperationStatus>> status_responses;
  std::string test_name;
};

class EventsYqlLoaderOperationPollingFailed
    : public testing::Test,
      public testing::WithParamInterface<OperationPollingFailedParams> {};

const std::vector<OperationPollingFailedParams> operation_polling_failed_params{
    {
        [](const OperationStatusRequest&) -> OperationStatusResponse {
          throw clients::http::TimeoutException();
        },
        {},
        "YqlClientTimeout",
    },
    {
        [](const OperationStatusRequest&) -> OperationStatusResponse {
          throw clients::http::HttpClientException(500, {});
        },
        {},
        "YqlClientInternalServerError",
    },
    {
        [](const OperationStatusRequest&) { return OperationStatusResponse{}; },
        {},
        "OperationIdMissingFromResponse",
    },
    {
        [](const OperationStatusRequest&) {
          OperationStatusResponse response;
          response.id = kOperationId;
          return response;
        },
        {},
        "OperationStatusMissingFromResponse",
    },
    {
        {},
        {{
            clients::yql::OperationStatus::kIdle,
            clients::yql::OperationStatus::kPending,
            clients::yql::OperationStatus::kRunning,
            clients::yql::OperationStatus::kError,
        }},
        "OperationStatusNotSuccess",
    },
};

TEST_P(EventsYqlLoaderOperationPollingFailed, ) {
  const auto& params = GetParam();

  YqlClientMock yql_client;
  if (params.operation_status_handler) {
    yql_client.SetOperationStatusHandler(*params.operation_status_handler);
  }
  if (params.status_responses) {
    yql_client.SetOperationStatusResponses(*params.status_responses);
  }

  auto loader = CreateYqlLoader(yql_client);
  RunInCoro([&loader] {
    EXPECT_THROW(loader.LoadEvents(SimpleQuery()), LoaderException);
  });
}

INSTANTIATE_TEST_SUITE_P(, EventsYqlLoaderOperationPollingFailed,
                         testing::ValuesIn(operation_polling_failed_params),
                         ::utest::PrintTestName());

struct OperationResultsErrorParams {
  OperationResultsHandler operation_results_handler;
  std::string test_name;
};

class EventsYqlLoaderOperationResultsError
    : public testing::Test,
      public testing::WithParamInterface<OperationResultsErrorParams> {};

const std::vector<OperationResultsErrorParams> operation_results_error_params{
    {
        [](const OperationResultsRequest&) -> OperationResultsResponse {
          throw clients::http::TimeoutException();
        },
        "YqlClientTimeout",
    },
    {
        [](const OperationResultsRequest&) -> OperationResultsResponse {
          throw clients::http::HttpClientException(500, {});
        },
        "YqlClientInternalServerError",
    },
};

TEST_P(EventsYqlLoaderOperationResultsError, ) {
  YqlClientMock yql_client;
  yql_client.SetOperationResultsHandler(GetParam().operation_results_handler);
  auto loader = CreateYqlLoader(yql_client);

  RunInCoro([&loader] {
    EXPECT_THROW(loader.LoadEvents(SimpleQuery()), LoaderException);
  });
}

INSTANTIATE_TEST_SUITE_P(, EventsYqlLoaderOperationResultsError,
                         testing::ValuesIn(operation_results_error_params),
                         ::utest::PrintTestName());

struct HappyPathParams {
  std::string operation_results_data;
  std::vector<Event> expected_events;
  std::string test_name;
};

class EventsYqlLoaderHappyPath
    : public testing::Test,
      public testing::WithParamInterface<HappyPathParams> {};

const std::vector<HappyPathParams> happy_path_params{
    {
        "",
        {},
        "EmptyResult",
    },
    {
        "{}",
        {{
            {},
            kUnknown,
            {kUnknown, kUnknown},
            {kUnknown, kUnknown},
            {},
        }},
        "DocWithoutData",
    },
    {
        R"-({
          "moment":"2021-03-01T15:27:58.147636",
          "type":"activate",
          "phone_id":"5d0b7fb1629526419ee8cfad",
          "yandex_uid":"4032745524",
          "coupon":"biguserlimit",
          "series":"biguserlimit",
          "extra":"\"{\\\"status\\\": \\\"valid\\\"}\""
        })-",
        {{
            TimePointFromString("2021-03-01T15:27:58.147636"),
            "activate",
            {"5d0b7fb1629526419ee8cfad", "4032745524"},
            {"biguserlimit", "biguserlimit"},
            {},  // TODO: add parsing extra field
        }},
        "DocWithFullData",
    },
    {
        R"-(
        {
          "moment":"2021-03-01T15:27:58.147636",
          "type":"activate",
          "phone_id":"5d0b7fb1629526419ee8cfad",
          "yandex_uid":"4032745524",
          "coupon":"biguserlimit",
          "series":"biguserlimit",
          "extra":"\"{\\\"status\\\": \\\"valid\\\"}\""
        }
        {
          "moment":"2021-03-05T15:27:58.147636",
          "type":"activate",
          "phone_id":"5d0b7fb1629526419ee8cfad",
          "yandex_uid":"4032745524",
          "coupon":"yandextaxi",
          "series":"yandextaxi",
          "extra":""
        }
        )-",
        {{
             TimePointFromString("2021-03-01T15:27:58.147636"),
             "activate",
             {"5d0b7fb1629526419ee8cfad", "4032745524"},
             {"biguserlimit", "biguserlimit"},
             {},  // TODO: add parsing extra field
         },
         {
             TimePointFromString("2021-03-05T15:27:58.147636"),
             "activate",
             {"5d0b7fb1629526419ee8cfad", "4032745524"},
             {"yandextaxi", "yandextaxi"},
             {},  // TODO: add parsing extra field
         }},
        "MultipleDocsWithFullData",
    },
};

TEST_P(EventsYqlLoaderHappyPath, ) {
  YqlClientMock yql_client;
  yql_client.SetOperationResultsData(GetParam().operation_results_data);
  auto loader = CreateYqlLoader(yql_client);

  RunInCoro([&loader] {
    const auto events = loader.LoadEvents(SimpleQuery());
    EXPECT_EQ(events, GetParam().expected_events);
  });
}

INSTANTIATE_TEST_SUITE_P(, EventsYqlLoaderHappyPath,
                         testing::ValuesIn(happy_path_params),
                         ::utest::PrintTestName());

}  // namespace coupons::events
