#include <userver/utest/utest.hpp>

#include <clients/eats-report-storage/client_gmock.hpp>
#include <components/digest_sender.hpp>

namespace testing {

using ::eats_restapp_communications::components::digest_sender::detail::
    ComponentImpl;
namespace types = ::eats_restapp_communications::types;
namespace reports_client =
    clients::eats_report_storage::internal_place_metrics_v1_digests::post;
using clients::eats_report_storage::DigestStatus;

struct DigestSenderComponentTest : public Test {
  std::shared_ptr<StrictMock<clients::eats_report_storage::ClientGMock>>
      reports_mock = std::make_shared<
          StrictMock<clients::eats_report_storage::ClientGMock>>();

  const ::utils::datetime::Date period_date =
      ::utils::datetime::DateFromRFC3339String("2022-05-01");

  ComponentImpl component;

  DigestSenderComponentTest() : component(*reports_mock) {}

  clients::eats_report_storage::DigestsRequestDigestsA MakeRequestItem(
      int64_t place_id) const {
    return {place_id, period_date};
  }

  clients::eats_report_storage::Digest MakeEmptyDigest(int64_t place_id,
                                                       DigestStatus status) {
    clients::eats_report_storage::Digest digest;
    digest.place_id = place_id;
    digest.period_date = period_date;
    digest.place_name = "place-" + std::to_string(place_id);
    digest.place_address = "address-" + std::to_string(place_id);
    digest.status = status;
    digest.delivery_type = "native";
    return digest;
  }

  static void FillValues(clients::eats_report_storage::Digest& digest) {
    digest.orders_total_cnt = "100";
    digest.orders_success_cnt = "80";
    digest.avg_cheque = "150₽";
    digest.cancels_pcnt = "20%";
    digest.revenue_earned_lcy = "15 000₽";
    digest.revenue_lost_lcy = "128₽";
    digest.fines_lcy = "50₽";
    digest.delay_min = "100";
    digest.rating = "4.5";
    digest.availability_pcnt = "80%";
  }

  static void FillDeltas(clients::eats_report_storage::Digest& digest) {
    digest.orders_total_cnt_delta = "(+10)";
    digest.orders_success_cnt_delta = "(-10)";
    digest.avg_cheque_delta = "(-30₽)";
    digest.cancels_pcnt_delta = "(+20%)";
    digest.revenue_earned_delta_lcy = "(-230₽)";
    digest.revenue_lost_delta_lcy = "(+128₽)";
    digest.fines_delta_lcy = "(+50₽)";
    digest.delay_delta_min = "(-10)";
    digest.rating_delta = "(+0.1)";
    digest.availability_delta_pcnt = "(-20%)";
  }

  ::formats::json::Value MakeEmptyArgs(int64_t place_id) const {
    ::formats::json::ValueBuilder result;
    result["period_date"] = "2022-05-01";
    result["place_name"] = "place-" + std::to_string(place_id);
    result["place_address"] = "address-" + std::to_string(place_id);
    result["delivery_type"] = "native";
    return result.ExtractValue();
  }

  ::formats::json::Value MakeArgsWithValues(int64_t place_id) const {
    ::formats::json::ValueBuilder result(MakeEmptyArgs(place_id));
    result["orders_total_cnt"] = "100";
    result["orders_success_cnt"] = "80";
    result["avg_cheque"] = "150₽";
    result["cancels_pcnt"] = "20%";
    result["revenue_earned_lcy"] = "15 000₽";
    result["revenue_lost_lcy"] = "128₽";
    result["fines_lcy"] = "50₽";
    result["delay_min"] = "100";
    result["rating"] = "4.5";
    result["availability_pcnt"] = "80%";

    result["orders_total_cnt_delta"] = "";
    result["orders_success_cnt_delta"] = "";
    result["avg_cheque_delta"] = "";
    result["cancels_pcnt_delta"] = "";
    result["revenue_earned_delta_lcy"] = "";
    result["revenue_lost_delta_lcy"] = "";
    result["fines_delta_lcy"] = "";
    result["delay_delta_min"] = "";
    result["rating_delta"] = "";
    result["availability_delta_pcnt"] = "";
    return result.ExtractValue();
  }

  ::formats::json::Value MakeFullArgs(int64_t place_id) const {
    ::formats::json::ValueBuilder result(MakeArgsWithValues(place_id));
    result["orders_total_cnt_delta"] = "(+10)";
    result["orders_success_cnt_delta"] = "(-10)";
    result["avg_cheque_delta"] = "(-30₽)";
    result["cancels_pcnt_delta"] = "(+20%)";
    result["revenue_earned_delta_lcy"] = "(-230₽)";
    result["revenue_lost_delta_lcy"] = "(+128₽)";
    result["fines_delta_lcy"] = "(+50₽)";
    result["delay_delta_min"] = "(-10)";
    result["rating_delta"] = "(+0.1)";
    result["availability_delta_pcnt"] = "(-20%)";
    return result.ExtractValue();
  }
};

TEST_F(DigestSenderComponentTest, should_make_empty_digests_on_empty_response) {
  std::vector<types::PlacePeriod> place_periods{{1, period_date},
                                                {2, period_date}};
  {
    reports_client::Request request;
    request.body.digests.push_back(MakeRequestItem(1));
    request.body.digests.push_back(MakeRequestItem(2));
    EXPECT_CALL(*reports_mock, InternalPlaceMetricsV1Digests(request, _))
        .WillOnce(Return(reports_client::Response200()));
  }
  const auto result = component.GetDigests(place_periods);
  ASSERT_TRUE(result.active.empty());
  ASSERT_TRUE(result.inactive.empty());
}

TEST_F(DigestSenderComponentTest,
       should_make_different_status_digests_on_response) {
  std::vector<types::PlacePeriod> place_periods{
      {1, period_date}, {2, period_date}, {3, period_date}};
  {
    reports_client::Request request;
    request.body.digests.push_back(MakeRequestItem(1));
    request.body.digests.push_back(MakeRequestItem(2));
    request.body.digests.push_back(MakeRequestItem(3));
    reports_client::Response200 response;
    response.digests.push_back(MakeEmptyDigest(1, DigestStatus::kActive));
    response.digests.push_back(MakeEmptyDigest(2, DigestStatus::kNoOrders));
    response.digests.push_back(MakeEmptyDigest(3, DigestStatus::kInactive));
    EXPECT_CALL(*reports_mock, InternalPlaceMetricsV1Digests(request, _))
        .WillOnce(Return(response));
  }
  const auto result = component.GetDigests(place_periods);
  ASSERT_EQ(result.active.size(), 1);
  ASSERT_TRUE(result.active.count(1));
  ASSERT_EQ(result.inactive.size(), 1);
  ASSERT_TRUE(result.inactive.count(3));
}

TEST_F(DigestSenderComponentTest, should_ignore_data_for_inactive) {
  std::vector<types::PlacePeriod> place_periods{{1, period_date}};
  {
    reports_client::Request request;
    request.body.digests.push_back(MakeRequestItem(1));
    reports_client::Response200 response;
    auto digest = MakeEmptyDigest(1, DigestStatus::kInactive);
    FillValues(digest);
    FillDeltas(digest);
    response.digests.push_back(digest);
    EXPECT_CALL(*reports_mock, InternalPlaceMetricsV1Digests(request, _))
        .WillOnce(Return(response));
  }
  const auto result = component.GetDigests(place_periods);
  ASSERT_TRUE(result.active.empty());
  ASSERT_EQ(result.inactive.size(), 1);
  ASSERT_EQ(result.inactive.at(1), MakeEmptyArgs(1));
}

TEST_F(DigestSenderComponentTest, should_work_on_empty_data_for_active) {
  std::vector<types::PlacePeriod> place_periods{{1, period_date}};
  {
    reports_client::Request request;
    request.body.digests.push_back(MakeRequestItem(1));
    reports_client::Response200 response;
    auto digest = MakeEmptyDigest(1, DigestStatus::kActive);
    response.digests.push_back(digest);
    EXPECT_CALL(*reports_mock, InternalPlaceMetricsV1Digests(request, _))
        .WillOnce(Return(response));
  }
  const auto result = component.GetDigests(place_periods);
  ASSERT_TRUE(result.inactive.empty());
  ASSERT_EQ(result.active.size(), 1);
  ASSERT_EQ(result.active.at(1), MakeEmptyArgs(1));
}

TEST_F(DigestSenderComponentTest,
       should_ignore_deltas_on_empty_values_for_active) {
  std::vector<types::PlacePeriod> place_periods{{1, period_date}};
  {
    reports_client::Request request;
    request.body.digests.push_back(MakeRequestItem(1));
    reports_client::Response200 response;
    auto digest = MakeEmptyDigest(1, DigestStatus::kActive);
    FillDeltas(digest);
    response.digests.push_back(digest);
    EXPECT_CALL(*reports_mock, InternalPlaceMetricsV1Digests(request, _))
        .WillOnce(Return(response));
  }
  const auto result = component.GetDigests(place_periods);
  ASSERT_TRUE(result.inactive.empty());
  ASSERT_EQ(result.active.size(), 1);
  ASSERT_EQ(result.active.at(1), MakeEmptyArgs(1));
}

TEST_F(DigestSenderComponentTest, should_fill_on_empty_deltas_for_active) {
  std::vector<types::PlacePeriod> place_periods{{1, period_date}};
  {
    reports_client::Request request;
    request.body.digests.push_back(MakeRequestItem(1));
    reports_client::Response200 response;
    auto digest = MakeEmptyDigest(1, DigestStatus::kActive);
    FillValues(digest);
    response.digests.push_back(digest);
    EXPECT_CALL(*reports_mock, InternalPlaceMetricsV1Digests(request, _))
        .WillOnce(Return(response));
  }
  const auto result = component.GetDigests(place_periods);
  ASSERT_TRUE(result.inactive.empty());
  ASSERT_EQ(result.active.size(), 1);
  ASSERT_EQ(result.active.at(1), MakeArgsWithValues(1));
}

TEST_F(DigestSenderComponentTest, should_fill_all_data_for_active) {
  std::vector<types::PlacePeriod> place_periods{{1, period_date}};
  {
    reports_client::Request request;
    request.body.digests.push_back(MakeRequestItem(1));
    reports_client::Response200 response;
    auto digest = MakeEmptyDigest(1, DigestStatus::kActive);
    FillValues(digest);
    FillDeltas(digest);
    response.digests.push_back(digest);
    EXPECT_CALL(*reports_mock, InternalPlaceMetricsV1Digests(request, _))
        .WillOnce(Return(response));
  }
  const auto result = component.GetDigests(place_periods);
  ASSERT_TRUE(result.inactive.empty());
  ASSERT_EQ(result.active.size(), 1);
  ASSERT_EQ(result.active.at(1), MakeFullArgs(1));
}

}  // namespace testing

namespace clients::eats_report_storage {
namespace internal_place_metrics_v1_digests::post {
inline bool operator==(const Request& lhs, const Request& rhs) {
  return lhs.body.digests == rhs.body.digests;
}
}  // namespace internal_place_metrics_v1_digests::post

inline bool operator==(const DigestsRequestDigestsA& lhs,
                       const DigestsRequestDigestsA& rhs) {
  return std::tie(lhs.place_id, lhs.period_date) ==
         std::tie(rhs.place_id, rhs.period_date);
}
}  // namespace clients::eats_report_storage
