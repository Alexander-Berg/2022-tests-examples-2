#include <userver/utest/utest.hpp>

#include <gmock/gmock.h>

#include <userver/formats/json/serialize.hpp>

#include <fts-universal-signal/conversions.hpp>

#include <client/query-positions-impl.hpp>
#include <clients/driver-trackstory/client_gmock.hpp>
#include <clients/internal-trackstory/client_gmock.hpp>
#include <clients/yagr-raw/client_gmock.hpp>

using namespace ::geometry::literals;
using ::testing::DoAll;
using ::testing::Return;
using ::testing::Throw;

namespace query_positions {

inline formats::json::Value operator"" _json(const char* str, size_t len) {
  return formats::json::FromString(std::string_view(str, len));
}

struct ClientPositionsFallbackFixture : public ::testing::Test {
  using YagrPosition =
      ::handlers::libraries::yagr_position_schema::V2StorePosition;
  using YagrSignalSource =
      handlers::libraries::geo_position_source::SignalSource;
  struct CommonInternalTrackstoryResponse {
    std::vector<clients::internal_trackstory::PositionsForContractor> body{};
  };

  Statistics stats;
  driver_id::DriverDbidUndscrUuid driver_id{"abc_def"};
  ContractorId contractor_id{driver_id::ContractorUuid(driver_id.GetUuid()),
                             driver_id::ContractorDbid(driver_id.GetDbid())};
  std::unique_ptr<clients::driver_trackstory::ClientGMock>
      driver_trackstory_mock;
  std::unique_ptr<clients::internal_trackstory::ClientGMock>
      internal_trackstory_mock;
  std::unique_ptr<clients::yagr_raw::ClientGMock> yagr_raw_mock;
  std::unique_ptr<QueryPositionsImpl> query_positions;
  std::vector<YagrPosition> client_positions;

  PositionRequestParams position_params;
  ShorttrackRequestParams shorttrack_params;
  TrackRequestParams track_params;

  ClientPositionsFallbackFixture();
  formats::json::Value CreateClientPositions();
  PositionsForContractor ExecuteRequest();

  DriverPositionWithSource CreatePositionWithSource(SignalSource source);
  YagrPosition CreateYagrPosition(YagrSignalSource source);
  static clients::driver_trackstory::query_positions::post::Response
  CreateResponse(const std::vector<DriverPositionWithSource>& response_data);

  CommonInternalTrackstoryResponse CreateCommonInternalTrackstoryResponse(
      const std::vector<std::string>& internal_sources);
  template <typename ResponseType>
  ResponseType CreateInternalTrackstoryResponse(
      const std::vector<std::string>& internal_sources);

  static bool IsDriverTrackstoryPosition(const PositionsForContractor& pos) {
    auto it = pos.extra.find("Verified");
    if (it == pos.extra.end()) {
      return false;
    }
    auto signal =
        fts_universal_signal::GetFirstUnshiftedPosition(it->second[0]);
    if (!signal) {
      return false;
    }
    return signal->longitude == 55.0_lon && signal->latitude == 37.0_lat;
  }

  static bool IsInternalTrackstoryPosition(
      const PositionsForContractor& signal,
      const std::vector<std::string>& expected_sources) {
    if (signal.extra.size() != expected_sources.size()) {
      return false;
    }
    for (auto& source : expected_sources) {
      auto it = signal.extra.find(source);
      if (it == signal.extra.end()) {
        return false;
      }
      auto geo_signal =
          fts_universal_signal::GetFirstUnshiftedPosition(it->second[0]);
      if (!geo_signal) {
        return false;
      }
      if (geo_signal->longitude != 57.0_lon ||
          geo_signal->latitude != 39.0_lat) {
        return false;
      }
    }
    return true;
  }

  static bool IsInternalTrackstoryPosition(
      const fts_universal_signal::UniversalSignal& signal) {
    auto geo_signal = fts_universal_signal::GetFirstUnshiftedPosition(signal);
    if (!geo_signal) {
      return false;
    }
    return geo_signal->longitude == 57.0_lon &&
           geo_signal->latitude == 39.0_lat;
  }
};

ClientPositionsFallbackFixture::ClientPositionsFallbackFixture()
    : driver_trackstory_mock(new clients::driver_trackstory::ClientGMock()),
      internal_trackstory_mock(new clients::internal_trackstory::ClientGMock()),
      yagr_raw_mock(new clients::yagr_raw::ClientGMock()),
      query_positions(
          new QueryPositionsImpl(*driver_trackstory_mock, *yagr_raw_mock,
                                 *internal_trackstory_mock, stats)) {
  position_params.algorithm =
      clients::internal_trackstory::AsOfNowAlgorithmParams{
          clients::internal_trackstory::Algorithm::kAsofnow};
}

formats::json::Value ClientPositionsFallbackFixture::CreateClientPositions() {
  ::handlers::libraries::yagr_position_schema::V2StoreRequest request;
  request.positions = client_positions;

  auto client_positions =
      Serialize(request, formats::serialize::To<formats::json::Value>{});

  return client_positions;
}

PositionsForContractor ClientPositionsFallbackFixture::ExecuteRequest() {
  return query_positions->QueryPositions(contractor_id, position_params,
                                         CreateClientPositions());
}

clients::driver_trackstory::query_positions::post::Response
ClientPositionsFallbackFixture::CreateResponse(
    const std::vector<DriverPositionWithSource>& response_data) {
  clients::driver_trackstory::QueryPositionsResponse actual_data;
  std::vector wrapper{1, response_data};
  actual_data.results = wrapper;

  return clients::driver_trackstory::query_positions::post::Response{
      actual_data};
}

ClientPositionsFallbackFixture::CommonInternalTrackstoryResponse
ClientPositionsFallbackFixture::CreateCommonInternalTrackstoryResponse(
    const std::vector<std::string>& internal_sources) {
  ClientPositionsFallbackFixture::CommonInternalTrackstoryResponse
      internal_response;

  clients::internal_trackstory::ContractorId contractor_id{
      ::driver_id::ContractorUuid(driver_id.GetUuid()),
      ::driver_id::ContractorDbid(driver_id.GetDbid())};
  std::unordered_map<std::string,
                     std::vector<::fts_universal_signal::UniversalSignal>>
      sources_with_positions;
  for (const auto& source : internal_sources) {
    std::vector<::fts_universal_signal::UniversalSignal> positions;
    ::fts_universal_signal::UniversalSignal signal(
        ::geometry::Position(39.0_lat, 57.0_lon), utils::datetime::Now());
    positions.push_back(std::move(signal));
    sources_with_positions[source] = std::move(positions);
  }
  clients::internal_trackstory::PositionsForContractor positions_for_contractor{
      contractor_id, sources_with_positions};

  internal_response.body.push_back(positions_for_contractor);

  return internal_response;
}

template <typename ResponseType>
ResponseType ClientPositionsFallbackFixture::CreateInternalTrackstoryResponse(
    const std::vector<std::string>& internal_sources) {
  ResponseType internal_response;

  internal_response.body =
      CreateCommonInternalTrackstoryResponse(internal_sources).body;

  return internal_response;
}

DriverPositionWithSource
ClientPositionsFallbackFixture::CreatePositionWithSource(SignalSource source) {
  return {source,
          ::gpssignal::GpsSignal(55.0_lon, 37.0_lat, std::nullopt, std::nullopt,
                                 std::nullopt, utils::datetime::Now())};
}

ClientPositionsFallbackFixture::YagrPosition
ClientPositionsFallbackFixture::CreateYagrPosition(YagrSignalSource source) {
  return YagrPosition{std::nullopt,
                      std::nullopt,
                      source,
                      38.0_lat,
                      56.0_lon,
                      std::chrono::duration_cast<std::chrono::seconds>(
                          utils::datetime::Now().time_since_epoch()),
                      std::nullopt,
                      std::nullopt,
                      std::nullopt,
                      std::nullopt};
}

TEST_F(ClientPositionsFallbackFixture, NoFallbackOnSuccess) {
  RunInCoro([this]() {
    /// If driver-trackstory returns data, client positions should not be used
    std::vector<DriverPositionWithSource> server_result;
    server_result.push_back(CreatePositionWithSource(SignalSource::kRaw));

    client_positions.push_back(CreateYagrPosition(YagrSignalSource::kVerified));

    EXPECT_CALL(*driver_trackstory_mock, QueryPositions)
        .WillOnce(Return(CreateResponse(server_result)));

    position_params.client_positions_fallback =
        ClientPositionsFallback::kNoFallback;
    auto result = ExecuteRequest();

    // should be one position and it should be from driver trackstory, not from
    // yagr
    ASSERT_EQ(1, FlattenContractorPositions(result).size());
    EXPECT_TRUE(IsDriverTrackstoryPosition(result));
  });
}

TEST_F(ClientPositionsFallbackFixture, NoFallbackOnFailure) {
  RunInCoro([this]() {
    /// If driver-trackstory returns no data, client positions still should not
    /// be used
    std::vector<DriverPositionWithSource> server_result;
    client_positions.push_back(CreateYagrPosition(YagrSignalSource::kVerified));

    EXPECT_CALL(*driver_trackstory_mock, QueryPositions)
        .WillOnce(Return(CreateResponse(server_result)));

    position_params.client_positions_fallback =
        ClientPositionsFallback::kNoFallback;
    auto result = ExecuteRequest();

    ASSERT_TRUE(query_positions->IsServerResponseEmpty(result));
  });
}

TEST_F(ClientPositionsFallbackFixture, NoFallbackOn50x) {
  RunInCoro([this]() {
    /// If driver-trackstory throws 50x, client positions still should not be
    /// used and exception should be forwarded
    using ResponseException =
        clients::driver_trackstory::query_positions::post::Response500;
    ResponseException server_exception{clients::driver_trackstory::PostError{}};

    client_positions.push_back(CreateYagrPosition(YagrSignalSource::kVerified));

    EXPECT_CALL(*driver_trackstory_mock, QueryPositions)
        .WillOnce(Throw(server_exception));

    position_params.client_positions_fallback =
        ClientPositionsFallback::kNoFallback;

    EXPECT_THROW(ExecuteRequest(), ResponseException);
  });
}
TEST_F(ClientPositionsFallbackFixture, NoFallbackOn40x) {
  RunInCoro([this]() {
    /// If driver-trackstory throws 40x, client positions still should not be
    /// used and exception should be forwarded
    using ResponseException =
        clients::driver_trackstory::query_positions::post::Response400;
    ResponseException server_exception{clients::driver_trackstory::PostError{}};

    client_positions.push_back(CreateYagrPosition(YagrSignalSource::kVerified));

    EXPECT_CALL(*driver_trackstory_mock, QueryPositions)
        .WillOnce(Throw(server_exception));

    position_params.client_positions_fallback =
        ClientPositionsFallback::kNoFallback;

    EXPECT_THROW(ExecuteRequest(), ResponseException);
  });
}
TEST_F(ClientPositionsFallbackFixture, NoFallbackOnTimeout) {
  RunInCoro([this]() {
    /// If driver-trackstory throws timeout , client positions still should not
    /// be used and exception should be forwarded
    using ResponseException =
        clients::driver_trackstory::query_positions::post::TimeoutException;
    ResponseException server_exception{};

    client_positions.push_back(CreateYagrPosition(YagrSignalSource::kVerified));

    EXPECT_CALL(*driver_trackstory_mock, QueryPositions)
        .WillOnce(Throw(server_exception));

    position_params.client_positions_fallback =
        ClientPositionsFallback::kNoFallback;

    EXPECT_THROW(ExecuteRequest(), ResponseException);
  });
}

// ==== kFallbackOnTotalFailure section ====

TEST_F(ClientPositionsFallbackFixture, TotalFailureFallbackOnSuccess) {
  RunInCoro([this]() {
    /// If driver-trackstory returns data, client positions should not be used
    std::vector<DriverPositionWithSource> server_result;
    server_result.push_back(CreatePositionWithSource(SignalSource::kRaw));

    client_positions.push_back(CreateYagrPosition(YagrSignalSource::kVerified));

    EXPECT_CALL(*driver_trackstory_mock, QueryPositions)
        .WillOnce(Return(CreateResponse(server_result)));

    position_params.client_positions_fallback =
        ClientPositionsFallback::kFallbackOnTotalFailure;
    auto result = ExecuteRequest();

    // should be one position and it should be from driver trackstory, not from
    // yagr
    ASSERT_EQ(1, FlattenContractorPositions(result).size());
    EXPECT_TRUE(IsDriverTrackstoryPosition(result));
  });
}

TEST_F(ClientPositionsFallbackFixture, TotalFailureFallbackOnFailure) {
  RunInCoro([this]() {
    /// If driver-trackstory returns no data, then client positions should be
    /// used
    std::vector<DriverPositionWithSource> server_result;

    client_positions.push_back(CreateYagrPosition(YagrSignalSource::kVerified));

    EXPECT_CALL(*driver_trackstory_mock, QueryPositions)
        .WillOnce(Return(CreateResponse(server_result)));

    position_params.client_positions_fallback =
        ClientPositionsFallback::kFallbackOnTotalFailure;
    auto result = ExecuteRequest();

    // should be one position and it should be from yagr
    ASSERT_EQ(1, FlattenContractorPositions(result).size());
    EXPECT_FALSE(IsDriverTrackstoryPosition(result));
  });
}

TEST_F(ClientPositionsFallbackFixture, TotalFailureFallbackOn50x) {
  RunInCoro([this]() {
    /// If driver-trackstory throws 50x, client positions still should not be
    /// used and exception should be forwarded
    using ResponseException =
        clients::driver_trackstory::query_positions::post::Response500;
    ResponseException server_exception{clients::driver_trackstory::PostError{}};

    client_positions.push_back(CreateYagrPosition(YagrSignalSource::kVerified));

    EXPECT_CALL(*driver_trackstory_mock, QueryPositions)
        .WillOnce(Throw(server_exception));

    position_params.client_positions_fallback =
        ClientPositionsFallback::kFallbackOnTotalFailure;

    // should be one position and it should be from  yagr
    auto result = ExecuteRequest();
    ASSERT_EQ(1, FlattenContractorPositions(result).size());
    EXPECT_FALSE(IsDriverTrackstoryPosition(result));
  });
}
TEST_F(ClientPositionsFallbackFixture, TotalFailureFallbackOn40x) {
  RunInCoro([this]() {
    /// If driver-trackstory throws 40x, client positions still should not be
    /// used and exception should be forwarded. Even though we have fallback
    /// enabled.
    using ResponseException =
        clients::driver_trackstory::query_positions::post::Response400;
    ResponseException server_exception{clients::driver_trackstory::PostError{}};

    client_positions.push_back(CreateYagrPosition(YagrSignalSource::kVerified));

    EXPECT_CALL(*driver_trackstory_mock, QueryPositions)
        .WillOnce(Throw(server_exception));

    position_params.client_positions_fallback =
        ClientPositionsFallback::kFallbackOnTotalFailure;

    EXPECT_THROW(ExecuteRequest(), ResponseException);
  });
}
TEST_F(ClientPositionsFallbackFixture, TotalFailureFallbackOnTimeout) {
  RunInCoro([this]() {
    /// If driver-trackstory throws timeout , client positions shall be used and
    /// exception should be suppressed
    using ResponseException =
        clients::driver_trackstory::query_positions::post::TimeoutException;
    ResponseException server_exception{};

    client_positions.push_back(CreateYagrPosition(YagrSignalSource::kVerified));

    EXPECT_CALL(*driver_trackstory_mock, QueryPositions)
        .WillOnce(Throw(server_exception));

    position_params.client_positions_fallback =
        ClientPositionsFallback::kFallbackOnTotalFailure;

    // should be one position and it should be from  yagr
    auto result = ExecuteRequest();
    ASSERT_EQ(1, FlattenContractorPositions(result).size());
    EXPECT_FALSE(IsDriverTrackstoryPosition(result));
  });
}
TEST_F(ClientPositionsFallbackFixture,
       RedirectToInternalNoFallbackOnFailureSuccess) {
  RunInCoro([this]() {
    query_positions->SetPercentOfUsageInternalTrackstory(100);

    std::vector<std::string> desired_sources{
        "AndroidGps",    "AndroidNetwork", "AndroidFused", "AndroidPassive",
        "YandexLbsWifi", "YandexLbsGsm",   "YandexLbsIp",  "YandexMapkit",
        "YandexNavi",    "Realtime",       "Camera",       "Adjusted",
        "Verified",
    };

    auto internal_response = CreateInternalTrackstoryResponse<
        clients::internal_trackstory::pipeline_bulk_positions::post::Response>(
        desired_sources);

    client_positions.push_back(CreateYagrPosition(YagrSignalSource::kVerified));

    EXPECT_CALL(*internal_trackstory_mock, PipelineBulkPositions)
        .WillOnce(Return(internal_response));

    position_params.client_positions_fallback =
        ClientPositionsFallback::kNoFallback;
    auto result = ExecuteRequest();

    EXPECT_TRUE(IsInternalTrackstoryPosition(result, desired_sources));
  });
}
TEST_F(ClientPositionsFallbackFixture,
       RedirectToInternalNoFallbackOnFailureSuccessNotAll) {
  RunInCoro([this]() {
    query_positions->SetPercentOfUsageInternalTrackstory(100);

    std::vector<std::string> desired_sources{
        "Verified",
        "Adjusted",
    };

    auto internal_response = CreateInternalTrackstoryResponse<
        clients::internal_trackstory::pipeline_bulk_positions::post::Response>(
        desired_sources);

    client_positions.push_back(CreateYagrPosition(YagrSignalSource::kVerified));

    EXPECT_CALL(*internal_trackstory_mock, PipelineBulkPositions)
        .WillOnce(DoAll(
            [&desired_sources](
                const clients::internal_trackstory::pipeline_bulk_positions::
                    post::Request& request,
                const clients::internal_trackstory::CommandControl&) {
              ASSERT_EQ(desired_sources, request.body.sources);
            },
            Return(internal_response)));

    position_params.client_positions_fallback =
        ClientPositionsFallback::kNoFallback;

    position_params.sources = desired_sources;

    auto result = ExecuteRequest();

    EXPECT_TRUE(IsInternalTrackstoryPosition(result, desired_sources));
  });
}
TEST_F(ClientPositionsFallbackFixture,
       RedirectToInternalNoFallbackOnFailureEmptyDriverResponse) {
  RunInCoro([this]() {
    query_positions->SetPercentOfUsageInternalTrackstory(100);

    std::vector<std::string> desired_sources{"Verified"};

    auto internal_response = CreateInternalTrackstoryResponse<
        clients::internal_trackstory::pipeline_bulk_positions::post::Response>(
        {});

    client_positions.push_back(CreateYagrPosition(YagrSignalSource::kVerified));

    position_params.client_positions_fallback =
        ClientPositionsFallback::kNoFallback;

    EXPECT_CALL(*internal_trackstory_mock, PipelineBulkPositions)
        .WillOnce(Return(internal_response));

    auto result = ExecuteRequest();

    ASSERT_TRUE(query_positions->IsServerResponseEmpty(result));
  });
}
TEST_F(ClientPositionsFallbackFixture,
       RedirectToInternalNoFallbackOnFailureException) {
  RunInCoro([this]() {
    using ResponseException =
        clients::internal_trackstory::pipeline_bulk_positions::post::Exception;
    ResponseException server_exception{};
    query_positions->SetPercentOfUsageInternalTrackstory(100);

    client_positions.push_back(CreateYagrPosition(YagrSignalSource::kVerified));

    position_params.client_positions_fallback =
        ClientPositionsFallback::kNoFallback;

    EXPECT_CALL(*internal_trackstory_mock, PipelineBulkPositions)
        .WillOnce(Throw(server_exception));

    EXPECT_THROW(ExecuteRequest(), ResponseException);
  });
}
TEST_F(ClientPositionsFallbackFixture,
       RedirectToInternalNoFallbackOnFailureTimeout) {
  RunInCoro([this]() {
    using ResponseException = clients::internal_trackstory::
        pipeline_bulk_positions::post::TimeoutException;
    ResponseException server_exception{};
    query_positions->SetPercentOfUsageInternalTrackstory(100);

    client_positions.push_back(CreateYagrPosition(YagrSignalSource::kVerified));

    position_params.client_positions_fallback =
        ClientPositionsFallback::kNoFallback;

    EXPECT_CALL(*internal_trackstory_mock, PipelineBulkPositions)
        .WillOnce(Throw(server_exception));

    EXPECT_THROW(ExecuteRequest(), ResponseException);
  });
}
TEST_F(ClientPositionsFallbackFixture,
       RedirectToInternalTotalFailureFallbackSuccess) {
  RunInCoro([this]() {
    query_positions->SetPercentOfUsageInternalTrackstory(100);

    std::vector<std::string> desired_sources{
        "AndroidGps",    "AndroidNetwork", "AndroidFused", "AndroidPassive",
        "YandexLbsWifi", "YandexLbsGsm",   "YandexLbsIp",  "YandexMapkit",
        "YandexNavi",    "Realtime",       "Camera",       "Adjusted",
        "Verified",
    };

    auto internal_response = CreateInternalTrackstoryResponse<
        clients::internal_trackstory::pipeline_bulk_positions::post::Response>(
        desired_sources);

    client_positions.push_back(CreateYagrPosition(YagrSignalSource::kVerified));

    EXPECT_CALL(*internal_trackstory_mock, PipelineBulkPositions)
        .WillOnce(Return(internal_response));

    position_params.client_positions_fallback =
        ClientPositionsFallback::kFallbackOnTotalFailure;
    auto result = ExecuteRequest();

    EXPECT_TRUE(IsInternalTrackstoryPosition(result, desired_sources));
  });
}
TEST_F(ClientPositionsFallbackFixture,
       RedirectToInternalTotalFailureFallbackSuccessNotAll) {
  RunInCoro([this]() {
    query_positions->SetPercentOfUsageInternalTrackstory(100);

    std::vector<std::string> desired_sources{
        "Verified",
        "Adjusted",
    };

    auto internal_response = CreateInternalTrackstoryResponse<
        clients::internal_trackstory::pipeline_bulk_positions::post::Response>(
        desired_sources);

    client_positions.push_back(CreateYagrPosition(YagrSignalSource::kVerified));

    EXPECT_CALL(*internal_trackstory_mock, PipelineBulkPositions)
        .WillOnce(DoAll(
            [&desired_sources](
                const clients::internal_trackstory::pipeline_bulk_positions::
                    post::Request& request,
                const clients::internal_trackstory::CommandControl&) {
              ASSERT_EQ(desired_sources, request.body.sources);
            },
            Return(internal_response)));

    position_params.client_positions_fallback =
        ClientPositionsFallback::kFallbackOnTotalFailure;

    position_params.sources = desired_sources;

    auto result = ExecuteRequest();

    EXPECT_TRUE(IsInternalTrackstoryPosition(result, desired_sources));
  });
}
TEST_F(ClientPositionsFallbackFixture,
       RedirectToInternalTotalFailureFallbackEmptyDriverResponse) {
  RunInCoro([this]() {
    query_positions->SetPercentOfUsageInternalTrackstory(100);

    std::vector<std::string> desired_sources{"Verified"};

    auto internal_response = CreateInternalTrackstoryResponse<
        clients::internal_trackstory::pipeline_bulk_positions::post::Response>(
        {});

    client_positions.push_back(CreateYagrPosition(YagrSignalSource::kVerified));

    position_params.client_positions_fallback =
        ClientPositionsFallback::kFallbackOnTotalFailure;

    EXPECT_CALL(*internal_trackstory_mock, PipelineBulkPositions)
        .WillOnce(Return(internal_response));

    auto result = ExecuteRequest();

    ASSERT_EQ(1, FlattenContractorPositions(result).size());
    EXPECT_FALSE(IsInternalTrackstoryPosition(result, desired_sources));
    EXPECT_FALSE(IsDriverTrackstoryPosition(result));
  });
}
TEST_F(ClientPositionsFallbackFixture,
       RedirectToInternalTotalFailureFallbackException) {
  RunInCoro([this]() {
    using ResponseException =
        clients::internal_trackstory::pipeline_bulk_positions::post::Exception;
    ResponseException server_exception{};
    query_positions->SetPercentOfUsageInternalTrackstory(100);

    std::vector<std::string> desired_sources{"Verified"};

    client_positions.push_back(CreateYagrPosition(YagrSignalSource::kVerified));

    position_params.client_positions_fallback =
        ClientPositionsFallback::kFallbackOnTotalFailure;

    EXPECT_CALL(*internal_trackstory_mock, PipelineBulkPositions)
        .WillOnce(Throw(server_exception));

    auto result = ExecuteRequest();

    ASSERT_EQ(1, FlattenContractorPositions(result).size());
    EXPECT_FALSE(IsInternalTrackstoryPosition(result, desired_sources));
    EXPECT_FALSE(IsDriverTrackstoryPosition(result));
  });
}
TEST_F(ClientPositionsFallbackFixture,
       RedirectToInternalTotalFailureFallbackTimeout) {
  RunInCoro([this]() {
    using ResponseException = clients::internal_trackstory::
        pipeline_bulk_positions::post::TimeoutException;
    ResponseException server_exception{};
    query_positions->SetPercentOfUsageInternalTrackstory(100);

    std::vector<std::string> desired_sources{"Verified"};

    client_positions.push_back(CreateYagrPosition(YagrSignalSource::kVerified));

    position_params.client_positions_fallback =
        ClientPositionsFallback::kFallbackOnTotalFailure;

    EXPECT_CALL(*internal_trackstory_mock, PipelineBulkPositions)
        .WillOnce(Throw(server_exception));

    auto result = ExecuteRequest();

    ASSERT_EQ(1, FlattenContractorPositions(result).size());
    EXPECT_FALSE(IsInternalTrackstoryPosition(result, desired_sources));
    EXPECT_FALSE(IsDriverTrackstoryPosition(result));
  });
}

#define CreateNoFallbackOnSuccessTest(Handler, HandlerResponse, Params)    \
  TEST_F(ClientPositionsFallbackFixture, Handler##NoFallbackOnSuccess) {   \
    RunInCoro([this]() {                                                   \
      auto internal_response =                                             \
          CreateInternalTrackstoryResponse<HandlerResponse>({"Verified"}); \
                                                                           \
      client_positions.push_back(                                          \
          CreateYagrPosition(YagrSignalSource::kVerified));                \
                                                                           \
      EXPECT_CALL(*internal_trackstory_mock, Handler)                      \
          .WillOnce(Return(internal_response));                            \
                                                                           \
      (Params).client_positions_fallback =                                 \
          ClientPositionsFallback::kNoFallback;                            \
                                                                           \
      auto result = query_positions->Handler(contractor_id, (Params),      \
                                             CreateClientPositions());     \
                                                                           \
      ASSERT_EQ(1, FlattenContractorPositions(result).size());             \
      auto it = result.extra.find("Verified");                             \
      ASSERT_TRUE(it != result.extra.end());                               \
      EXPECT_TRUE(IsInternalTrackstoryPosition(it->second[0]));            \
    });                                                                    \
  }

CreateNoFallbackOnSuccessTest(
    PipelineShorttrack,
    clients::internal_trackstory::pipeline_shorttrack::post::Response,
    shorttrack_params);

CreateNoFallbackOnSuccessTest(
    PipelinePosition,
    clients::internal_trackstory::pipeline_position::post::Response,
    position_params);

CreateNoFallbackOnSuccessTest(
    PipelineTrack, clients::internal_trackstory::pipeline_track::post::Response,
    track_params);

#define CreateNoFallbackOnFailureTest(Handler, HandlerResponse, Params)  \
  TEST_F(ClientPositionsFallbackFixture, Handler##NoFallbackOnFailure) { \
    RunInCoro([this]() {                                                 \
      auto internal_response =                                           \
          CreateInternalTrackstoryResponse<HandlerResponse>({});         \
                                                                         \
      client_positions.push_back(                                        \
          CreateYagrPosition(YagrSignalSource::kVerified));              \
                                                                         \
      EXPECT_CALL(*internal_trackstory_mock, Handler)                    \
          .WillOnce(Return(internal_response));                          \
                                                                         \
      (Params).client_positions_fallback =                               \
          ClientPositionsFallback::kNoFallback;                          \
                                                                         \
      auto result = query_positions->Handler(contractor_id, (Params),    \
                                             CreateClientPositions());   \
                                                                         \
      ASSERT_TRUE(result.extra.empty());                                 \
    });                                                                  \
  }

CreateNoFallbackOnFailureTest(
    PipelineShorttrack,
    clients::internal_trackstory::pipeline_shorttrack::post::Response,
    shorttrack_params);

CreateNoFallbackOnFailureTest(
    PipelinePosition,
    clients::internal_trackstory::pipeline_position::post::Response,
    position_params);

CreateNoFallbackOnFailureTest(
    PipelineTrack, clients::internal_trackstory::pipeline_track::post::Response,
    track_params);

#define CreateNoFallbackOnExceptionTest(Handler, HandlerResponse, Params)  \
  TEST_F(ClientPositionsFallbackFixture, Handler##NoFallbackOnException) { \
    RunInCoro([this]() {                                                   \
      using ResponseException = HandlerResponse;                           \
      ResponseException server_exception{};                                \
                                                                           \
      client_positions.push_back(                                          \
          CreateYagrPosition(YagrSignalSource::kVerified));                \
                                                                           \
      (Params).client_positions_fallback =                                 \
          ClientPositionsFallback::kNoFallback;                            \
                                                                           \
      EXPECT_CALL(*internal_trackstory_mock, Handler)                      \
          .WillOnce(Throw(server_exception));                              \
                                                                           \
      EXPECT_THROW(query_positions->Handler(contractor_id, (Params),       \
                                            CreateClientPositions()),      \
                   ResponseException);                                     \
    });                                                                    \
  }

CreateNoFallbackOnExceptionTest(
    PipelineShorttrack,
    clients::internal_trackstory::pipeline_shorttrack::post::Exception,
    shorttrack_params);

CreateNoFallbackOnExceptionTest(
    PipelinePosition,
    clients::internal_trackstory::pipeline_position::post::Exception,
    position_params);

CreateNoFallbackOnExceptionTest(
    PipelineTrack,
    clients::internal_trackstory::pipeline_track::post::Exception,
    track_params);

#define CreateNoFallbackOnTimeoutTest(Handler, HandlerResponse, Params)  \
  TEST_F(ClientPositionsFallbackFixture, Handler##NoFallbackOnTimeout) { \
    RunInCoro([this]() {                                                 \
      using ResponseException = HandlerResponse;                         \
      ResponseException server_exception{};                              \
                                                                         \
      client_positions.push_back(                                        \
          CreateYagrPosition(YagrSignalSource::kVerified));              \
                                                                         \
      (Params).client_positions_fallback =                               \
          ClientPositionsFallback::kNoFallback;                          \
                                                                         \
      EXPECT_CALL(*internal_trackstory_mock, Handler)                    \
          .WillOnce(Throw(server_exception));                            \
                                                                         \
      EXPECT_THROW(query_positions->Handler(contractor_id, (Params),     \
                                            CreateClientPositions()),    \
                   ResponseException);                                   \
    });                                                                  \
  }

CreateNoFallbackOnTimeoutTest(
    PipelineShorttrack,
    clients::internal_trackstory::pipeline_shorttrack::post::TimeoutException,
    shorttrack_params);

CreateNoFallbackOnTimeoutTest(
    PipelinePosition,
    clients::internal_trackstory::pipeline_position::post::TimeoutException,
    position_params);

CreateNoFallbackOnTimeoutTest(
    PipelineTrack,
    clients::internal_trackstory::pipeline_track::post::TimeoutException,
    track_params);

#define CreateTotalFailureFallbackOnSuccessTest(Handler, HandlerResponse,  \
                                                Params)                    \
  TEST_F(ClientPositionsFallbackFixture,                                   \
         Handler##TotalFailureFallbackOnSuccess) {                         \
    RunInCoro([this]() {                                                   \
      auto internal_response =                                             \
          CreateInternalTrackstoryResponse<HandlerResponse>({"Verified"}); \
                                                                           \
      client_positions.push_back(                                          \
          CreateYagrPosition(YagrSignalSource::kVerified));                \
                                                                           \
      EXPECT_CALL(*internal_trackstory_mock, Handler)                      \
          .WillOnce(Return(internal_response));                            \
                                                                           \
      (Params).client_positions_fallback =                                 \
          ClientPositionsFallback::kFallbackOnTotalFailure;                \
                                                                           \
      auto result = query_positions->Handler(contractor_id, (Params),      \
                                             CreateClientPositions());     \
                                                                           \
      ASSERT_EQ(1, FlattenContractorPositions(result).size());             \
      auto it = result.extra.find("Verified");                             \
      ASSERT_TRUE(it != result.extra.end());                               \
      EXPECT_TRUE(IsInternalTrackstoryPosition(it->second[0]));            \
    });                                                                    \
  }

CreateTotalFailureFallbackOnSuccessTest(
    PipelineShorttrack,
    clients::internal_trackstory::pipeline_shorttrack::post::Response,
    shorttrack_params);

CreateTotalFailureFallbackOnSuccessTest(
    PipelinePosition,
    clients::internal_trackstory::pipeline_position::post::Response,
    position_params);

CreateTotalFailureFallbackOnSuccessTest(
    PipelineTrack, clients::internal_trackstory::pipeline_track::post::Response,
    track_params);

#define CreateTotalFailureFallbackOnFailureTest(Handler, HandlerResponse, \
                                                Params)                   \
  TEST_F(ClientPositionsFallbackFixture,                                  \
         Handler##TotalFailureFallbackOnFailure) {                        \
    RunInCoro([this]() {                                                  \
      auto internal_response =                                            \
          CreateInternalTrackstoryResponse<HandlerResponse>({});          \
                                                                          \
      client_positions.push_back(                                         \
          CreateYagrPosition(YagrSignalSource::kVerified));               \
                                                                          \
      EXPECT_CALL(*internal_trackstory_mock, Handler)                     \
          .WillOnce(Return(internal_response));                           \
                                                                          \
      (Params).client_positions_fallback =                                \
          ClientPositionsFallback::kFallbackOnTotalFailure;               \
                                                                          \
      auto result = query_positions->Handler(contractor_id, (Params),     \
                                             CreateClientPositions());    \
                                                                          \
      ASSERT_EQ(1, FlattenContractorPositions(result).size());            \
      auto it = result.extra.find("Verified");                            \
      ASSERT_TRUE(it != result.extra.end());                              \
      EXPECT_FALSE(IsInternalTrackstoryPosition(it->second[0]));          \
    });                                                                   \
  }

CreateTotalFailureFallbackOnFailureTest(
    PipelineShorttrack,
    clients::internal_trackstory::pipeline_shorttrack::post::Response,
    shorttrack_params);

CreateTotalFailureFallbackOnFailureTest(
    PipelinePosition,
    clients::internal_trackstory::pipeline_position::post::Response,
    position_params);

CreateTotalFailureFallbackOnFailureTest(
    PipelineTrack, clients::internal_trackstory::pipeline_track::post::Response,
    track_params);

#define CreateTotalFailureFallbackOnExceptionTest(Handler, HandlerResponse, \
                                                  Params)                   \
  TEST_F(ClientPositionsFallbackFixture,                                    \
         Handler##TotalFailureFallbackOnException) {                        \
    RunInCoro([this]() {                                                    \
      using ResponseException = HandlerResponse;                            \
      ResponseException server_exception{};                                 \
                                                                            \
      client_positions.push_back(                                           \
          CreateYagrPosition(YagrSignalSource::kVerified));                 \
                                                                            \
      (Params).client_positions_fallback =                                  \
          ClientPositionsFallback::kFallbackOnTotalFailure;                 \
                                                                            \
      EXPECT_CALL(*internal_trackstory_mock, Handler)                       \
          .WillOnce(Throw(server_exception));                               \
                                                                            \
      auto result = query_positions->Handler(contractor_id, (Params),       \
                                             CreateClientPositions());      \
                                                                            \
      ASSERT_EQ(1, FlattenContractorPositions(result).size());              \
      auto it = result.extra.find("Verified");                              \
      ASSERT_TRUE(it != result.extra.end());                                \
      EXPECT_FALSE(IsInternalTrackstoryPosition(it->second[0]));            \
    });                                                                     \
  }

CreateTotalFailureFallbackOnExceptionTest(
    PipelineShorttrack,
    clients::internal_trackstory::pipeline_shorttrack::post::Exception,
    shorttrack_params);

CreateTotalFailureFallbackOnExceptionTest(
    PipelinePosition,
    clients::internal_trackstory::pipeline_position::post::Exception,
    position_params);

CreateTotalFailureFallbackOnExceptionTest(
    PipelineTrack,
    clients::internal_trackstory::pipeline_track::post::Exception,
    track_params);

#define CreateTotalFailureFallbackOnTimeoutTest(Handler, HandlerResponse, \
                                                Params)                   \
  TEST_F(ClientPositionsFallbackFixture,                                  \
         Handler##TotalFailureFallbackOnTimeout) {                        \
    RunInCoro([this]() {                                                  \
      using ResponseException = HandlerResponse;                          \
      ResponseException server_exception{};                               \
                                                                          \
      client_positions.push_back(                                         \
          CreateYagrPosition(YagrSignalSource::kVerified));               \
                                                                          \
      (Params).client_positions_fallback =                                \
          ClientPositionsFallback::kFallbackOnTotalFailure;               \
                                                                          \
      EXPECT_CALL(*internal_trackstory_mock, Handler)                     \
          .WillOnce(Throw(server_exception));                             \
                                                                          \
      auto result = query_positions->Handler(contractor_id, (Params),     \
                                             CreateClientPositions());    \
                                                                          \
      ASSERT_EQ(1, FlattenContractorPositions(result).size());            \
      auto it = result.extra.find("Verified");                            \
      ASSERT_TRUE(it != result.extra.end());                              \
      EXPECT_FALSE(IsInternalTrackstoryPosition(it->second[0]));          \
    });                                                                   \
  }

CreateTotalFailureFallbackOnTimeoutTest(
    PipelineShorttrack,
    clients::internal_trackstory::pipeline_shorttrack::post::TimeoutException,
    shorttrack_params);

CreateTotalFailureFallbackOnTimeoutTest(
    PipelinePosition,
    clients::internal_trackstory::pipeline_position::post::TimeoutException,
    position_params);

CreateTotalFailureFallbackOnTimeoutTest(
    PipelineTrack,
    clients::internal_trackstory::pipeline_track::post::TimeoutException,
    track_params);

#define CreateResponse400Test(Handler, HandlerResponse, Params)       \
  TEST_F(ClientPositionsFallbackFixture, Handler##Response400) {      \
    RunInCoro([this]() {                                              \
      using ResponseException = HandlerResponse;                      \
      ResponseException server_exception{};                           \
                                                                      \
      client_positions.push_back(                                     \
          CreateYagrPosition(YagrSignalSource::kVerified));           \
                                                                      \
      (Params).client_positions_fallback =                            \
          ClientPositionsFallback::kFallbackOnTotalFailure;           \
                                                                      \
      EXPECT_CALL(*internal_trackstory_mock, Handler)                 \
          .WillOnce(Throw(server_exception));                         \
                                                                      \
      EXPECT_THROW(query_positions->Handler(contractor_id, (Params),  \
                                            CreateClientPositions()), \
                   ResponseException);                                \
    });                                                               \
  }

CreateResponse400Test(
    PipelineShorttrack,
    clients::internal_trackstory::pipeline_shorttrack::post::Response400,
    shorttrack_params);

CreateResponse400Test(
    PipelinePosition,
    clients::internal_trackstory::pipeline_position::post::Response400,
    position_params);

}  // namespace query_positions
