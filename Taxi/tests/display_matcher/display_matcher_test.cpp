#include <gmock/gmock.h>

#include "dependencies.hpp"

#include <userver/utils/datetime.hpp>
#include <userver/utils/mock_now.hpp>

namespace {

namespace dm = eats_orders_tracking::display_matcher;

using RequestData = eats_orders_tracking::utils::RequestData;
using TrackedOrderPayload = eats_orders_tracking::utils::TrackedOrderPayload;
using defs::internal::pg_order_dynamic::EstimateStatus;
using defs::internal::pg_waybill::CourierType;
using eats_orders_tracking::models::CourierStaticWithPayload;

using eats_orders_tracking::tests::display_matcher::DependenciesForTest;
using eats_orders_tracking::tests::display_matcher::DependenciesForTestFallback;
using eats_orders_tracking::tests::display_matcher::DependenciesForTestNotNull;

}  // namespace

TEST(DisplayMatcher, EmptyKwargs) {
  const RequestData request_data;
  const TrackedOrderPayload tracked_order_payload;
  const DependenciesForTest dependencies;
  EXPECT_NO_THROW(
      dm::impl::BuildKwargs(request_data, tracked_order_payload, dependencies));
}

TEST(DisplayMatcher, EmptyCancelReasonKwargs) {
  const RequestData request_data;
  const TrackedOrderPayload tracked_order_payload;
  const DependenciesForTest dependencies;
  dm::KwargsBuilder kwargs_builder;
  EXPECT_NO_THROW(kwargs_builder = dm::impl::BuildKwargs(
                      request_data, tracked_order_payload, dependencies));

  const auto& kwargs = kwargs_builder.Build();
  EXPECT_FALSE(kwargs.FindOptional("cancel_reason"));
  EXPECT_FALSE(kwargs.FindOptional("raw_cancel_reason"));
}

TEST(DisplayMatcher, NotEmptyCancelReasonKwargs) {
  const RequestData request_data;
  TrackedOrderPayload tracked_order_payload;
  tracked_order_payload.order.payload.raw_cancel_reason.emplace(
      "payment_failed");
  tracked_order_payload.order.payload.cancel_reason.emplace(
      defs::internal::pg_order::CancelReason::kPaymentFailed);
  const DependenciesForTest dependencies;
  dm::KwargsBuilder kwargs_builder;
  EXPECT_NO_THROW(kwargs_builder = dm::impl::BuildKwargs(
                      request_data, tracked_order_payload, dependencies));

  const auto& kwargs = kwargs_builder.Build();
  EXPECT_TRUE(kwargs.FindOptional("cancel_reason"));
  EXPECT_TRUE(kwargs.FindOptional("raw_cancel_reason"));

  EXPECT_TRUE(std::holds_alternative<std::string>(
      *kwargs.FindOptional("cancel_reason")));
  EXPECT_TRUE(std::holds_alternative<std::string>(
      *kwargs.FindOptional("raw_cancel_reason")));

  EXPECT_EQ(std::get<std::string>(*kwargs.FindOptional("cancel_reason")),
            "payment_failed");
  EXPECT_EQ(std::get<std::string>(*kwargs.FindOptional("raw_cancel_reason")),
            "payment_failed");
}

TEST(DisplayMatcher, Default) {
  const RequestData request_data;
  const TrackedOrderPayload tracked_order_payload;
  const DependenciesForTestNotNull dependencies;
  const auto display_template = dm::MatchDisplayTemplate(
      request_data, tracked_order_payload, dependencies);
  ASSERT_TRUE(display_template.display_template_code.find(
                  dm::impl::kSelectedCaseSuffixDefault) != std::string::npos);
}

TEST(DisplayMatcher, Rover) {
  const RequestData request_data;
  const DependenciesForTestNotNull dependencies;

  TrackedOrderPayload tracked_order_payload;
  tracked_order_payload.order_courier_assignment.emplace();
  tracked_order_payload.order_courier_assignment->waybill_info.courier_type =
      CourierType::kRover;

  const auto display_template = dm::MatchDisplayTemplate(
      request_data, tracked_order_payload, dependencies);
  ASSERT_TRUE(display_template.display_template_code.find(
                  dm::impl::kSelectedCaseSuffixRover) != std::string::npos);
}

TEST(DisplayMatcher, HardOfHearing) {
  const RequestData request_data;
  const DependenciesForTestNotNull dependencies;

  TrackedOrderPayload tracked_order_payload;
  tracked_order_payload.order_courier_assignment.emplace();
  tracked_order_payload.order_courier_assignment->waybill_info.courier_type =
      CourierType::kPedestrian;
  tracked_order_payload.order_courier_assignment->performer_info
      .is_hard_of_hearing = true;

  const auto display_template = dm::MatchDisplayTemplate(
      request_data, tracked_order_payload, dependencies);
  ASSERT_TRUE(display_template.display_template_code.find(
                  dm::impl::kSelectedCaseSuffixHardOfHearing) !=
              std::string::npos);
}

TEST(DisplayMatcher, EmptyDeliverySlotKwargs) {
  const RequestData request_data;
  const TrackedOrderPayload tracked_order_payload;
  const DependenciesForTest dependencies;
  dm::KwargsBuilder kwargs_builder;
  EXPECT_NO_THROW(kwargs_builder = dm::impl::BuildKwargs(
                      request_data, tracked_order_payload, dependencies));

  const auto& kwargs = kwargs_builder.Build();
  EXPECT_FALSE(kwargs.FindOptional("delivery_slot_from"));
  EXPECT_FALSE(kwargs.FindOptional("delivery_slot_to"));

  EXPECT_TRUE(kwargs.FindOptional("is_slot_delivery"));
  EXPECT_EQ(std::get<bool>(*kwargs.FindOptional("is_slot_delivery")), false);
}

TEST(DisplayMatcher, NotEmptyDeliverySlotKwargs) {
  constexpr const char* kTimezone = "Europe/Moscow";
  const auto kFrom = ::utils::datetime::Stringtime(
      "2021-02-12 11:17:00", kTimezone, "%Y-%m-%d %H:%M:%S");
  const auto kTo = ::utils::datetime::Stringtime(
      "2021-02-12 12:17:00", kTimezone, "%Y-%m-%d %H:%M:%S");

  const RequestData request_data;
  TrackedOrderPayload tracked_order_payload;

  tracked_order_payload.order.payload.delivery_slot.emplace();
  tracked_order_payload.order.payload.delivery_slot->from = kFrom;
  tracked_order_payload.order.payload.delivery_slot->to = kTo;

  const DependenciesForTest dependencies;
  dm::KwargsBuilder kwargs_builder;
  EXPECT_NO_THROW(kwargs_builder = dm::impl::BuildKwargs(
                      request_data, tracked_order_payload, dependencies));

  const auto& kwargs = kwargs_builder.Build();
  EXPECT_TRUE(kwargs.FindOptional("is_slot_delivery"));
  EXPECT_TRUE(kwargs.FindOptional("delivery_slot_from"));
  EXPECT_TRUE(kwargs.FindOptional("delivery_slot_to"));

  EXPECT_TRUE(
      std::holds_alternative<bool>(*kwargs.FindOptional("is_slot_delivery")));
  EXPECT_TRUE(std::holds_alternative<std::chrono::system_clock::time_point>(
      *kwargs.FindOptional("delivery_slot_from")));
  EXPECT_TRUE(std::holds_alternative<std::chrono::system_clock::time_point>(
      *kwargs.FindOptional("delivery_slot_to")));

  EXPECT_EQ(std::get<bool>(*kwargs.FindOptional("is_slot_delivery")), true);
  EXPECT_EQ(std::get<std::chrono::system_clock::time_point>(
                *kwargs.FindOptional("delivery_slot_from")),
            kFrom);
  EXPECT_EQ(std::get<std::chrono::system_clock::time_point>(
                *kwargs.FindOptional("delivery_slot_to")),
            kTo);
}

TEST(DisplayMatcher, MinutesToPromiseAsap) {
  auto now = ::utils::datetime::Stringtime("2020-01-01T00:10:00.00Z", "UTC");
  ::utils::datetime::MockNowSet(now);

  const RequestData request_data;
  TrackedOrderPayload tracked_order_payload;
  tracked_order_payload.order.payload.is_asap = true;
  tracked_order_payload.order.payload.promise =
      ::utils::datetime::Now() + std::chrono::minutes(5);
  const DependenciesForTest dependencies;
  dm::KwargsBuilder kwargs_builder;
  EXPECT_NO_THROW(kwargs_builder = dm::impl::BuildKwargs(
                      request_data, tracked_order_payload, dependencies));

  const auto& kwargs = kwargs_builder.Build();
  EXPECT_TRUE(kwargs.FindOptional("minutes_to_promise"));

  EXPECT_TRUE(std::holds_alternative<std::int64_t>(
      *kwargs.FindOptional("minutes_to_promise")));

  EXPECT_EQ(std::get<std::int64_t>(*kwargs.FindOptional("minutes_to_promise")),
            5);
}

TEST(DisplayMatcher, MinutesToPromiseNotAsap) {
  auto now = ::utils::datetime::Stringtime("2020-01-01T00:10:00.00Z", "UTC");
  ::utils::datetime::MockNowSet(now);

  const RequestData request_data;
  TrackedOrderPayload tracked_order_payload;
  tracked_order_payload.order.payload.is_asap = false;
  tracked_order_payload.order.payload.promise =
      ::utils::datetime::Now() + std::chrono::minutes(5);
  tracked_order_payload.order.payload.pre_order_date.emplace(
      ::utils::datetime::Now() + std::chrono::minutes(6));
  const DependenciesForTest dependencies;
  dm::KwargsBuilder kwargs_builder;
  EXPECT_NO_THROW(kwargs_builder = dm::impl::BuildKwargs(
                      request_data, tracked_order_payload, dependencies));

  const auto& kwargs = kwargs_builder.Build();
  EXPECT_TRUE(kwargs.FindOptional("minutes_to_promise"));

  EXPECT_TRUE(std::holds_alternative<std::int64_t>(
      *kwargs.FindOptional("minutes_to_promise")));

  EXPECT_EQ(std::get<std::int64_t>(*kwargs.FindOptional("minutes_to_promise")),
            6);
}

TEST(DisplayMatcher, MinutesToPromiseBelowZero) {
  auto now = ::utils::datetime::Stringtime("2020-01-01T00:10:00.00Z", "UTC");
  ::utils::datetime::MockNowSet(now);

  const RequestData request_data;
  TrackedOrderPayload tracked_order_payload;
  tracked_order_payload.order.payload.is_asap = false;
  tracked_order_payload.order.payload.promise =
      ::utils::datetime::Now() - std::chrono::minutes(5);
  tracked_order_payload.order.payload.pre_order_date.emplace(
      ::utils::datetime::Now() - std::chrono::minutes(6));
  const DependenciesForTest dependencies;
  dm::KwargsBuilder kwargs_builder;
  EXPECT_NO_THROW(kwargs_builder = dm::impl::BuildKwargs(
                      request_data, tracked_order_payload, dependencies));

  const auto& kwargs = kwargs_builder.Build();
  EXPECT_TRUE(kwargs.FindOptional("minutes_to_promise"));

  EXPECT_TRUE(std::holds_alternative<std::int64_t>(
      *kwargs.FindOptional("minutes_to_promise")));

  EXPECT_EQ(std::get<std::int64_t>(*kwargs.FindOptional("minutes_to_promise")),
            -6);
}

TEST(DisplayMatcher, PlannedLateMinutes) {
  auto now = ::utils::datetime::Stringtime("2020-01-01T00:10:00.00Z", "UTC");
  ::utils::datetime::MockNowSet(now);

  const RequestData request_data;
  TrackedOrderPayload tracked_order_payload;
  tracked_order_payload.order.payload.is_asap = true;
  tracked_order_payload.order.payload.promise =
      ::utils::datetime::Now() + std::chrono::minutes(5);
  tracked_order_payload.order_courier_assignment.emplace();
  tracked_order_payload.order_dynamic_data.estimates.courier_arriving_to_client
      .expected_at = ::utils::datetime::Now() + std::chrono::minutes(7);
  const DependenciesForTest dependencies;
  dm::KwargsBuilder kwargs_builder;
  EXPECT_NO_THROW(kwargs_builder = dm::impl::BuildKwargs(
                      request_data, tracked_order_payload, dependencies));

  const auto& kwargs = kwargs_builder.Build();
  EXPECT_TRUE(kwargs.FindOptional("planned_late_minutes"));

  EXPECT_TRUE(std::holds_alternative<std::int64_t>(
      *kwargs.FindOptional("planned_late_minutes")));

  EXPECT_EQ(
      std::get<std::int64_t>(*kwargs.FindOptional("planned_late_minutes")), 2);
}

TEST(DisplayMatcher, PlannedLateMinutesBelowZero) {
  auto now = ::utils::datetime::Stringtime("2020-01-01T00:10:00.00Z", "UTC");
  ::utils::datetime::MockNowSet(now);

  const RequestData request_data;
  TrackedOrderPayload tracked_order_payload;
  tracked_order_payload.order.payload.is_asap = true;
  tracked_order_payload.order.payload.promise =
      ::utils::datetime::Now() + std::chrono::minutes(5);
  tracked_order_payload.order_courier_assignment.emplace();
  tracked_order_payload.order_dynamic_data.estimates.courier_arriving_to_client
      .expected_at = ::utils::datetime::Now() + std::chrono::minutes(3);
  const DependenciesForTest dependencies;
  dm::KwargsBuilder kwargs_builder;
  EXPECT_NO_THROW(kwargs_builder = dm::impl::BuildKwargs(
                      request_data, tracked_order_payload, dependencies));

  const auto& kwargs = kwargs_builder.Build();
  EXPECT_TRUE(kwargs.FindOptional("planned_late_minutes"));

  EXPECT_TRUE(std::holds_alternative<std::int64_t>(
      *kwargs.FindOptional("planned_late_minutes")));

  EXPECT_EQ(
      std::get<std::int64_t>(*kwargs.FindOptional("planned_late_minutes")), -2);
}

TEST(DisplayMatcher, MinutesAfterReadyForDeliveryNotFinished) {
  auto now = ::utils::datetime::Stringtime("2020-01-01T00:10:00.00Z", "UTC");
  ::utils::datetime::MockNowSet(now);

  const RequestData request_data;
  TrackedOrderPayload tracked_order_payload;
  tracked_order_payload.order.payload.status_history.moved_to_delivery_at
      .emplace(::utils::datetime::Stringtime("2020-01-01T00:00:00.00Z", "UTC"));
  const DependenciesForTest dependencies;
  dm::KwargsBuilder kwargs_builder;
  EXPECT_NO_THROW(kwargs_builder = dm::impl::BuildKwargs(
                      request_data, tracked_order_payload, dependencies));

  const auto& kwargs = kwargs_builder.Build();

  EXPECT_EQ(std::get<std::int64_t>(
                *kwargs.FindOptional("minutes_after_moving_to_delivery")),
            10);
}

TEST(DisplayMatcher, MinutesAfterReadyForDeliveryFinished) {
  auto now = ::utils::datetime::Stringtime("2020-01-01T00:10:00.00Z", "UTC");
  ::utils::datetime::MockNowSet(now);

  const RequestData request_data;
  TrackedOrderPayload tracked_order_payload;
  tracked_order_payload.order.payload.status_history.moved_to_delivery_at
      .emplace(::utils::datetime::Stringtime("2020-01-01T00:00:00.00Z", "UTC"));
  tracked_order_payload.order.payload.status_history.finished_at.emplace(
      ::utils::datetime::Stringtime("2020-01-01T00:05:00.00Z", "UTC"));
  const DependenciesForTest dependencies;
  dm::KwargsBuilder kwargs_builder;
  EXPECT_NO_THROW(kwargs_builder = dm::impl::BuildKwargs(
                      request_data, tracked_order_payload, dependencies));

  const auto& kwargs = kwargs_builder.Build();

  EXPECT_EQ(std::get<std::int64_t>(
                *kwargs.FindOptional("minutes_after_moving_to_delivery")),
            5);
}

TEST(DisplayMatcher, CommonKwargs) {
  const RequestData request_data;
  TrackedOrderPayload tracked_order_payload;
  tracked_order_payload.order.payload.location.longitude = 1;
  tracked_order_payload.order.payload.location.latitude = 2;
  tracked_order_payload.place.payload.location.longitude = 3;
  tracked_order_payload.place.payload.location.latitude = 4;
  tracked_order_payload.order_courier_assignment.emplace();
  tracked_order_payload.order_dynamic_data.estimates.courier_arriving_to_place
      .emplace();
  tracked_order_payload.order_dynamic_data.estimates.courier_arriving_to_place
      ->status = EstimateStatus::kFinished;
  const DependenciesForTest dependencies;
  dm::KwargsBuilder kwargs_builder;
  EXPECT_NO_THROW(kwargs_builder = dm::impl::BuildKwargs(
                      request_data, tracked_order_payload, dependencies));

  const auto& kwargs = kwargs_builder.Build();

  EXPECT_EQ(std::get<::utils::geometry::Point>(
                *kwargs.FindOptional("client_location"))
                .lon,
            1);
  EXPECT_EQ(std::get<::utils::geometry::Point>(
                *kwargs.FindOptional("client_location"))
                .lat,
            2);
  EXPECT_EQ(
      std::get<::utils::geometry::Point>(*kwargs.FindOptional("place_location"))
          .lon,
      3);
  EXPECT_EQ(
      std::get<::utils::geometry::Point>(*kwargs.FindOptional("place_location"))
          .lat,
      4);

  EXPECT_TRUE(kwargs.FindOptional("courier_arrived_to_place"));
  EXPECT_EQ(std::get<bool>(*kwargs.FindOptional("courier_arrived_to_place")),
            true);
}

TEST(DisplayMatcher, WaybillChainKwargs) {
  const RequestData request_data;
  TrackedOrderPayload tracked_order_payload;
  tracked_order_payload.order_courier_assignment.emplace();
  tracked_order_payload.order_courier_assignment
      ->chained_previous_waybill_points.emplace();
  tracked_order_payload.order_courier_assignment
      ->chained_previous_waybill_points->resize(1);
  tracked_order_payload.order_courier_assignment
      ->chained_previous_waybill_points.value()[0]
      .visit_status = defs::internal::pg_waybill::PointVisitStatus::kPending;
  const DependenciesForTest dependencies;
  dm::KwargsBuilder kwargs_builder;
  EXPECT_NO_THROW(kwargs_builder = dm::impl::BuildKwargs(
                      request_data, tracked_order_payload, dependencies));

  const auto& kwargs = kwargs_builder.Build();

  EXPECT_TRUE(kwargs.FindOptional("is_chained_waybill"));
  EXPECT_EQ(std::get<bool>(*kwargs.FindOptional("is_chained_waybill")), true);

  EXPECT_TRUE(kwargs.FindOptional("is_previous_chained_waybill_finished"));
  EXPECT_EQ(std::get<bool>(
                *kwargs.FindOptional("is_previous_chained_waybill_finished")),
            false);

  EXPECT_TRUE(std::holds_alternative<std::int64_t>(
      *kwargs.FindOptional("chained_waybill_points_in_progress_count")));
  EXPECT_EQ(std::get<std::int64_t>(*kwargs.FindOptional(
                "chained_waybill_points_in_progress_count")),
            1);
}

TEST(DisplayMatcher, WaybillBatchKwargs) {
  const RequestData request_data;
  TrackedOrderPayload tracked_order_payload;
  tracked_order_payload.order_courier_assignment.emplace();
  tracked_order_payload.order_courier_assignment->waybill_info.waybill_points
      .resize(6);
  tracked_order_payload.order_courier_assignment->waybill_info.waybill_points[0]
      .visit_order = 1;
  tracked_order_payload.order_courier_assignment->waybill_info.waybill_points[1]
      .visit_order = 2;
  tracked_order_payload.order_courier_assignment->waybill_info.waybill_points[2]
      .visit_order = 3;
  tracked_order_payload.order_courier_assignment->waybill_info.waybill_points[3]
      .visit_order = 4;
  tracked_order_payload.order_courier_assignment->waybill_info.waybill_points[4]
      .visit_order = 5;
  tracked_order_payload.order_courier_assignment->waybill_info.waybill_points[5]
      .visit_order = 6;
  tracked_order_payload.order_courier_assignment->waybill_info.waybill_points[0]
      .type = defs::internal::pg_waybill::PointType::kSource;
  tracked_order_payload.order_courier_assignment->waybill_info.waybill_points[1]
      .type = defs::internal::pg_waybill::PointType::kSource;
  tracked_order_payload.order_courier_assignment->waybill_info.waybill_points[2]
      .type = defs::internal::pg_waybill::PointType::kSource;
  tracked_order_payload.order_courier_assignment->waybill_info.waybill_points[0]
      .visit_status = defs::internal::pg_waybill::PointVisitStatus::kVisited;
  tracked_order_payload.order_courier_assignment->waybill_info.waybill_points[1]
      .visit_status = defs::internal::pg_waybill::PointVisitStatus::kVisited;
  tracked_order_payload.order_courier_assignment->waybill_info.waybill_points[2]
      .visit_status = defs::internal::pg_waybill::PointVisitStatus::kVisited;
  tracked_order_payload.order_courier_assignment->waybill_info.waybill_points[3]
      .type = defs::internal::pg_waybill::PointType::kDestination;
  tracked_order_payload.order_courier_assignment->waybill_info.waybill_points[4]
      .type = defs::internal::pg_waybill::PointType::kDestination;
  tracked_order_payload.order_courier_assignment->waybill_info.waybill_points[5]
      .type = defs::internal::pg_waybill::PointType::kDestination;
  tracked_order_payload.order_courier_assignment->waybill_info.waybill_points[3]
      .visit_status = defs::internal::pg_waybill::PointVisitStatus::kPending;
  tracked_order_payload.order_courier_assignment->waybill_info.waybill_points[4]
      .visit_status = defs::internal::pg_waybill::PointVisitStatus::kPending;
  tracked_order_payload.order_courier_assignment->waybill_info.waybill_points[5]
      .visit_status = defs::internal::pg_waybill::PointVisitStatus::kPending;
  tracked_order_payload.order.order_nr = "11111-111111";
  tracked_order_payload.order_courier_assignment->waybill_info.waybill_points[1]
      .external_order_id = tracked_order_payload.order.order_nr;
  tracked_order_payload.order_courier_assignment->waybill_info.waybill_points[5]
      .external_order_id = tracked_order_payload.order.order_nr;

  const DependenciesForTest dependencies;
  dm::KwargsBuilder kwargs_builder;
  EXPECT_NO_THROW(kwargs_builder = dm::impl::BuildKwargs(
                      request_data, tracked_order_payload, dependencies));

  const auto& kwargs = kwargs_builder.Build();

  EXPECT_TRUE(kwargs.FindOptional("is_batched_waybill"));
  EXPECT_EQ(std::get<bool>(*kwargs.FindOptional("is_batched_waybill")), true);

  EXPECT_TRUE(kwargs.FindOptional("all_orders_in_batch_taken"));
  EXPECT_EQ(std::get<bool>(*kwargs.FindOptional("all_orders_in_batch_taken")),
            true);

  EXPECT_TRUE(std::holds_alternative<std::int64_t>(*kwargs.FindOptional(
      "destination_points_in_progress_before_eater_destination_count")));
  EXPECT_EQ(
      std::get<std::int64_t>(*kwargs.FindOptional(
          "destination_points_in_progress_before_eater_destination_count")),
      2);

  EXPECT_TRUE(std::holds_alternative<std::int64_t>(
      *kwargs.FindOptional("source_points_in_progress_count")));
  EXPECT_EQ(std::get<std::int64_t>(
                *kwargs.FindOptional("source_points_in_progress_count")),
            0);

  EXPECT_TRUE(std::holds_alternative<std::string>(
      *kwargs.FindOptional("destination_point_status")));
  EXPECT_EQ(
      std::get<std::string>(*kwargs.FindOptional("destination_point_status")),
      "pending");

  EXPECT_TRUE(std::holds_alternative<std::string>(
      *kwargs.FindOptional("source_point_status")));
  EXPECT_EQ(std::get<std::string>(*kwargs.FindOptional("source_point_status")),
            "visited");
}
