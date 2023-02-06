#include <algorithm>
#include <functional>
#include <iterator>
#include <unordered_map>
#include <vector>

#include <gtest/gtest.h>

#include <userver/components/component_context.hpp>
#include <userver/tracing/span.hpp>
#include <userver/utest/utest.hpp>
#include <userver/utils/mock_now.hpp>
#include <userver/yaml_config/yaml_config.hpp>

#include <infraver-classes/classes_serialization.hpp>
#include <yt-logger/messages/delivery_log/message.hpp>

#include <dispatch/input/environment.hpp>
#include <dispatch/proposition-applier.hpp>
#include <dispatch/proposition-builders/delivery/gamble_settings.hpp>
#include <dispatch/proposition-builders/delivery/metrics/filter.hpp>
#include <dispatch/proposition-builders/delivery/route.hpp>
#include <dispatch/proposition-builders/delivery/route_filter.hpp>
#include <dispatch/proposition-builders/delivery/route_filter_validators.hpp>
#include <experiments3/united_dispatch_clients_to_sla_groups_mapping.hpp>
#include <experiments3/united_dispatch_generators_settings.hpp>
#include <experiments3/united_dispatch_sla_groups_settings.hpp>
#include <models/united_dispatch/segment.hpp>
#include <utils/constants.hpp>
#include <utils/logging.hpp>
#include <utils/test_helpers.hpp>
#include <utils/waybill_create.hpp>
#include <workers/utils/base.hpp>

using namespace united_dispatch::waybill::delivery;
using namespace united_dispatch::models;
using namespace united_dispatch::test_helpers;

using defs::internal::delivery::BatchRejectReason;

class DummyLogger : public united_dispatch::logging::LoggerInterface {
 public:
  virtual ~DummyLogger(){};

  void LogMessage(const united_dispatch::logging::Message& /*msg*/,
                  const std::string& /*stage_id*/,
                  const std::string& /*content_type*/) const override {}

  void LogRoute(const united_dispatch::waybill::delivery::Route& /*route*/,
                const std::string& /*stage_id*/,
                const std::string& /*content_type*/,
                const formats::json::Value& /*info*/ =
                    united_dispatch::logging::kEmptyJsonValue,
                const std::optional<std::string>& /*candidate_id*/ =
                    std::nullopt) const override {}

  void LogSegment(const std::string& /*segment_id*/,
                  const std::string& /*stage_id*/,
                  const std::string& /*content_type*/,
                  const formats::json::Value& /*info*/ =
                      united_dispatch::logging::kEmptyJsonValue,
                  const united_dispatch::waybill::delivery::Route* const
                  /*route*/
                  = nullptr,
                  const std::optional<std::string>& /*candidate_id*/ =
                      std::nullopt) const override {}

  void LogProposition(
      const united_dispatch::waybill::delivery::solver::
          Proposition& /*proposition*/,
      const std::string& /*stage_id*/, const std::string& /*content_type*/,
      const formats::json::Value& /*info*/ =
          united_dispatch::logging::kEmptyJsonValue) const override {}
};

std::shared_ptr<united_dispatch::logging::LoggerWrapper> GetLoggerWrapper() {
  auto logger = std::make_shared<DummyLogger>();
  return std::make_shared<united_dispatch::logging::LoggerWrapper>(
      logger, "test_stage", "test_content");
}

const double BATCH_DISTANCE = 5.0;
const double SEGMENT_DISTANCE = 150.0;

Route GetBatchRoute(
    std::optional<std::vector<handlers::SegmentPointTimeInterval>> intervals =
        std::nullopt,
    std::optional<std::chrono::system_clock::time_point> due = std::nullopt,
    WaybillProposalPtr previous_waybill = nullptr) {
  /*
    Three segments:
      A1 -> B1 and A2 -> B2 and A3 -> B3

    Town:
      -------------|
      |            |
      |  A1--A2--A3-
      |  |   |   |
      |--B1--B2--B3

    Distance:
        A1 A2 A3 B1 B2 B3
      A1    1     50
      A2       1     50
      A3          1     50
      B1             1
      B2                1

      Without Batch: A1 -> B1 + A2 -> B2 + A3 -> B3                       = 150
      With    Batch: A1 -> A2 + A2 -> A3 + A3 -> B1 + B1 -> B2 + B2 -> B3 = 5
  */

  const int segments_num = 3;

  std::vector<std::shared_ptr<Segment>> segments;
  for (int segment_num = 1; segment_num <= segments_num; ++segment_num) {
    GenerateSegmentKwargs segment_kwargs;
    segment_kwargs.segment_id = "segment-" + std::to_string(segment_num);
    segment_kwargs.intervals = intervals;
    segment_kwargs.due = due;
    segments.push_back(GenerateSegment(segment_kwargs));
  }

  std::vector<Waypoint> batch_path;
  const std::vector<std::pair<int, int>> batch_path_info = {
      {0, 0}, {1, 0}, {2, 0}, {0, 1}, {1, 1}, {2, 1}, {0, 2}, {1, 2}, {2, 2},
  };
  int visited_order = 0;
  for (const auto& [segment_num, point_num] : batch_path_info) {
    segments[segment_num]->points[point_num].visit_order = ++visited_order;
    batch_path.emplace_back(segments[segment_num]->points[point_num],
                            segments[segment_num]);
  }

  Route route(std::to_string(segments_num) + "-segment", batch_path, true,
              nullptr, nullptr, previous_waybill);

  std::unordered_map<
      handlers::libraries::united_dispatch_definitions::RouterType,
      EdgesRouterData>
      routers_data;

  std::vector<std::tuple<std::pair<int, int>, std::pair<int, int>, int>>
      routers_info = {
          {{0, 0}, {0, 1}, 50}, {{1, 0}, {1, 1}, 50}, {{2, 0}, {2, 1}, 50},
          {{0, 0}, {1, 0}, 1},  {{1, 0}, {2, 0}, 1},  {{2, 0}, {0, 1}, 1},
          {{0, 1}, {1, 1}, 1},  {{1, 1}, {2, 1}, 1},
      };
  for (const auto& [from, to, distance] : routers_info) {
    auto& car_data = routers_data
        [handlers::libraries::united_dispatch_definitions::RouterType::kCar]
        [{segments[from.first]->points[from.second].id,
          segments[to.first]->points[to.second].id}];
    car_data.distance = distance;
    car_data.time = std::chrono::seconds{distance};

    auto& pedestrian_data =
        routers_data[handlers::libraries::united_dispatch_definitions::
                         RouterType::kPedestrian]
                    [{segments[from.first]->points[from.second].id,
                      segments[to.first]->points[to.second].id}];
    pedestrian_data.distance = distance;
    pedestrian_data.time = std::chrono::seconds{distance};
  }
  route.ComputeRoutersData(routers_data);
  return route;
}

UTEST(RouteFilterTest, ConstDistanceAssertation) {
  ASSERT_EQ(BATCH_DISTANCE, 5.0);
  ASSERT_EQ(SEGMENT_DISTANCE, 150.0);
}

UTEST(RouteFilterTest, ValidateBatchSize) {
  std::unordered_map<std::string, int> max_batch_size;
  max_batch_size[dynamic_config::kValueDictDefaultName] = 1;

  experiments3::united_dispatch_delivery_generators_settings::Common
      common_settings{};
  common_settings.max_batch_size =
      ::dynamic_config::ValueDict<int>(max_batch_size);

  route_filter::ValidatorSettings settings{{}, common_settings, {}, {}, {}};

  auto logger = std::make_shared<DummyLogger>();
  auto logger_wrapper =
      std::make_shared<united_dispatch::logging::LoggerWrapper>(
          logger, "test_stage", "test_content");

  route_filter::AllowedBatchSizeValidator validator(false, settings);

  GenerateSegmentKwargs segment_kwargs;
  segment_kwargs.segment_id = "segment-1";
  auto segment_1 = GenerateSegment(segment_kwargs);
  auto path = GetPath(segment_1);
  {
    Route route("single-segment", path, true);
    auto reject = validator.Validate(route);
    ASSERT_EQ(route.GetPath().GetNumSegments(), 1);
    ASSERT_FALSE(reject.reason.has_value());
  }

  {
    segment_kwargs.segment_id = "segment-2";
    auto segment_2 = GenerateSegment(segment_kwargs);
    for (const auto& point : GetPath(segment_2)) {
      path.push_back(point);
    }

    Route route("single-segment", path, true);
    ASSERT_EQ(route.GetPath().GetNumSegments(), 2);
    auto reject = validator.Validate(route);
    ASSERT_TRUE(reject.reason.has_value());
  }
}

UTEST(RouteFilterTest, ValidateBatchVisitOrder) {
  route_filter::ValidatorSettings settings{{}, {}, {}, {}, {}};

  route_filter::BatchVisitOrderValidator validator(false, settings);

  {
    auto segment = GenerateSegment();
    auto path = GetPath(segment);
    Route route("single-segment", path, true);
    auto reject = validator.Validate(route);
    ASSERT_FALSE(reject.reason.has_value());
  }

  {
    GenerateSegmentKwargs segment_kwargs;
    segment_kwargs.is_valid = false;
    auto segment = GenerateSegment(segment_kwargs);
    auto path = GetPath(segment);
    ::Route route("single-segment", path, true);

    auto reject = validator.Validate(route);
    ASSERT_FALSE(reject.reason.has_value());
  }

  {
    GenerateSegmentKwargs segment_kwargs;
    segment_kwargs.segment_id = "segment-1";
    auto segment1 = GenerateSegment(segment_kwargs);
    segment_kwargs.segment_id = "segment-2";
    auto segment2 = GenerateSegment(segment_kwargs);
    auto path = GetPath({segment1, segment2});
    Route route("batch", path, true);
    auto reject = validator.Validate(route);
    ASSERT_FALSE(reject.reason.has_value());
  }

  {
    GenerateSegmentKwargs segment_kwargs;
    segment_kwargs.segment_id = "segment-1";
    segment_kwargs.is_valid = false;
    auto segment1 = GenerateSegment(segment_kwargs);
    segment_kwargs.segment_id = "segment-2";
    segment_kwargs.is_valid = true;
    auto segment2 = GenerateSegment(segment_kwargs);
    auto path = GetPath({segment1, segment2});
    ::Route route("batch", path, true);

    auto reject = validator.Validate(route);
    ASSERT_TRUE(reject.reason.has_value());
  }
}

UTEST(RouteFilterTest, ValidateSamePointsOrder) {
  route_filter::ValidatorSettings settings{{}, {}, {}, {}, {}};

  route_filter::SamePointsOrderValidator validator(false, settings);

  auto segment1 =
      GenerateSegment({true, "segment-1", "", "", {}, {}, true, false});
  auto segment2 =
      GenerateSegment({true, "segment-2", "", "", {}, {}, true, false});
  for (size_t i = 0; i < segment1->points.size(); ++i) {
    const auto& coords = segment1->points[i].coordinates;
    segment2->points[i].coordinates = {coords.lat * 100, coords.lon * 100};
  }

  auto valid_route = GetRouteFromSegments({segment1, segment2});
  auto invalid_route = GetRouteWithSegments("test", {"segment-1", "segment-2"});

  {
    auto reject = validator.Validate(valid_route);
    ASSERT_FALSE(reject.reason.has_value());
  }

  {
    auto reject = validator.Validate(invalid_route);
    ASSERT_TRUE(reject.reason.has_value());
  }
}

UTEST(RouteFilterTest, ValidateSegmentDuration) {
  GambleSettings gamble_settings{};
  experiments3::united_dispatch_delivery_generators_settings::Common
      common_settings{};

  united_dispatch::waybill::delivery::SlaGroupsSettings
      clients_groups_settings{};

  clients_groups_settings = dynamic_config::ValueDict<
      experiments3::united_dispatch_sla_groups_settings::SlaGroupProperties>{
      {dynamic_config::kValueDictDefaultName, {}}};

  united_dispatch::waybill::delivery::ClientsToSlaGroupsMapping
      clients_to_groups_mapping{};

  clients_to_groups_mapping = dynamic_config::ValueDict<std::string>{
      {dynamic_config::kValueDictDefaultName,
       dynamic_config::kValueDictDefaultName}};

  route_filter::ValidatorSettings settings{gamble_settings,
                                           common_settings,
                                           clients_groups_settings,
                                           clients_to_groups_mapping,
                                           {}};

  route_filter::SegmentDurationValidator validator(false, settings);

  auto route = GetBatchRoute();

  {
    common_settings.max_segment_duration_increase =
        dynamic_config::ValueDict<double>{
            {dynamic_config::kValueDictDefaultName, 2}};
    auto reject = validator.Validate(route);
    ASSERT_FALSE(reject.reason.has_value());
  }

  {
    common_settings.max_segment_duration_increase =
        dynamic_config::ValueDict<double>{
            {dynamic_config::kValueDictDefaultName,
             BATCH_DISTANCE / SEGMENT_DISTANCE - 0.01}};

    auto reject = validator.Validate(route);
    ASSERT_TRUE(reject.reason.has_value());
  }

  {
    gamble_settings.make_duration_validation_optional = true;

    common_settings.max_segment_duration_increase =
        dynamic_config::ValueDict<double>{
            {dynamic_config::kValueDictDefaultName,
             BATCH_DISTANCE / SEGMENT_DISTANCE - 0.01}};

    clients_groups_settings = dynamic_config::ValueDict<
        experiments3::united_dispatch_sla_groups_settings::SlaGroupProperties>{
        {dynamic_config::kValueDictDefaultName, {1}}};

    auto reject = validator.Validate(route);
    ASSERT_FALSE(reject.reason.has_value());
  }
}

UTEST(RouteFilterTest, ValidateBatchGoodness) {
  experiments3::united_dispatch_delivery_generators_settings::Common
      common_settings{};

  route_filter::ValidatorSettings settings{{}, common_settings, {}, {}, {}};

  route_filter::BatchGoodnessValidator validator(false, settings);

  auto route = GetBatchRoute();

  common_settings.distance_of_arrival = dynamic_config::ValueDict<double>{
      {dynamic_config::kValueDictDefaultName, 0}};

  // Сто лет не видел такого...
  {
    // Неприятное усложнение юниттестов свидетельствует о том, что, наверное,
    // стоит переписать фильтры, вынести их из RouteValidator и просто запускать
    // в отдельной функции поочередно (а, может, я не прав)
    common_settings.batch_size2_goodness_ratio_threshold =
        dynamic_config::ValueDict<double>{
            {dynamic_config::kValueDictDefaultName,
             SEGMENT_DISTANCE / BATCH_DISTANCE}};
    common_settings.batch_size2_goodness_diff_threshold =
        dynamic_config::ValueDict<int>{{dynamic_config::kValueDictDefaultName,
                                        SEGMENT_DISTANCE - BATCH_DISTANCE}};
    auto reject = validator.Validate(route);
    ASSERT_FALSE(reject.reason.has_value());
  }

  {
    common_settings.batch_size2_goodness_ratio_threshold =
        dynamic_config::ValueDict<double>{
            {dynamic_config::kValueDictDefaultName,
             SEGMENT_DISTANCE / BATCH_DISTANCE + 0.1}};
    common_settings.batch_size2_goodness_diff_threshold =
        dynamic_config::ValueDict<int>{{dynamic_config::kValueDictDefaultName,
                                        SEGMENT_DISTANCE - BATCH_DISTANCE}};
    auto reject = validator.Validate(route);
    ASSERT_TRUE(reject.reason.has_value());
  }

  {
    common_settings.batch_size2_goodness_ratio_threshold =
        dynamic_config::ValueDict<double>{
            {dynamic_config::kValueDictDefaultName,
             SEGMENT_DISTANCE / BATCH_DISTANCE}};
    common_settings.batch_size2_goodness_diff_threshold =
        dynamic_config::ValueDict<int>{{dynamic_config::kValueDictDefaultName,
                                        SEGMENT_DISTANCE - BATCH_DISTANCE + 1}};
    auto reject = validator.Validate(route);
    ASSERT_TRUE(reject.reason.has_value());
  }
}

UTEST(RouteFilterTest, ValidateSla) {
  experiments3::UnitedDispatchClientsToSlaGroupsMapping::Value sla_mapping{
      {dynamic_config::kValueDictDefaultName,
       dynamic_config::kValueDictDefaultName}};

  {
    experiments3::UnitedDispatchSlaGroupsSettings::Value sla_settings{
        {dynamic_config::kValueDictDefaultName, {-(50 - 1)}}};

    route_filter::ValidatorSettings settings{
        {}, {}, sla_settings, sla_mapping, {}};

    route_filter::SlaValidator validator(false, settings);

    auto route = GetBatchRoute();
    auto reject = validator.Validate(route);
    ASSERT_TRUE(reject.reason.has_value());
  }

  {
    experiments3::UnitedDispatchSlaGroupsSettings::Value sla_settings{
        {dynamic_config::kValueDictDefaultName, {-(50 - 3 - 1 - 1)}}};

    route_filter::ValidatorSettings settings{
        {}, {}, sla_settings, sla_mapping, {}};

    route_filter::SlaValidator validator(false, settings);

    auto route = GetBatchRoute();
    auto reject = validator.Validate(route);
    ASSERT_FALSE(reject.reason.has_value());
  }

  {
    experiments3::UnitedDispatchSlaGroupsSettings::Value sla_settings{
        {dynamic_config::kValueDictDefaultName, {-(50 - 3 - 1)}}};

    GeneratorsCommonSettings common_settings;
    common_settings.forbidden_second_in_batch_sla = {
        {dynamic_config::kValueDictDefaultName, -100}};

    auto waybill_ptr = std::make_shared<WaybillProposal>();
    auto route = GetBatchRoute(std::nullopt, std::nullopt, waybill_ptr);
    auto& segments = route.GetPath().GetAllSegments();

    waybill_ptr->segments = {segments[0], segments[1]};
    size_t p_idx = 0;
    for (auto& point : route.GetPath().GetPoints()) {
      if (point.segment->id != segments[0]->id &&
          point.segment->id != segments[1]->id) {
        continue;
      }

      defs::internal::waybill::WaybillPathItem item;
      item.point_id = point.point.get().id;
      item.resolution =
          p_idx++ < 3 ? std::make_optional(
                            defs::internal::waybill::PointResolution::kVisited)
                      : std::nullopt;
      item.segment_id = point.segment->id;
      waybill_ptr->path.push_back(item);
    }
    ASSERT_EQ(waybill_ptr->path.size(), 6);

    route_filter::ValidatorSettings settings{
        {}, common_settings, sla_settings, sla_mapping, {}};

    route_filter::SlaValidator validator(false, settings);

    auto reject = validator.Validate(route);
    ASSERT_FALSE(reject.reason.has_value());
  }

  {
    experiments3::UnitedDispatchSlaGroupsSettings::Value sla_settings{
        {dynamic_config::kValueDictDefaultName, {-(100)}}};

    GeneratorsCommonSettings common_settings;
    common_settings.forbidden_second_in_batch_sla = {
        {dynamic_config::kValueDictDefaultName, -100}};

    auto waybill_ptr = std::make_shared<WaybillProposal>();
    auto route = GetBatchRoute(std::nullopt, std::nullopt, waybill_ptr);
    auto& segments = route.GetPath().GetAllSegments();

    waybill_ptr->segments = {segments[0], segments[1]};
    size_t p_idx = 0;
    for (auto& point : route.GetPath().GetPoints()) {
      const_cast<handlers::SegmentPoint&>(
          const_cast<Waypoint&>(point).point.get())
          .type = handlers::SegmentPointType::kReturn;

      if (point.segment->id != segments[0]->id &&
          point.segment->id != segments[1]->id) {
        continue;
      }

      defs::internal::waybill::WaybillPathItem item;
      item.point_id = point.point.get().id;
      item.resolution =
          p_idx++ < 3 ? std::make_optional(
                            defs::internal::waybill::PointResolution::kVisited)
                      : std::nullopt;
      item.segment_id = point.segment->id;
      waybill_ptr->path.push_back(item);
    }
    ASSERT_EQ(waybill_ptr->path.size(), 6);

    route_filter::ValidatorSettings settings{
        {}, common_settings, sla_settings, sla_mapping, {}};

    route_filter::SlaValidator validator(false, settings);

    auto reject = validator.Validate(route);
    ASSERT_FALSE(reject.reason.has_value());
  }

  {
    experiments3::UnitedDispatchSlaGroupsSettings::Value sla_settings{
        {dynamic_config::kValueDictDefaultName, {-(50 - 3 - 1)}}};

    GeneratorsCommonSettings common_settings;
    common_settings.forbidden_second_in_batch_sla = {
        {dynamic_config::kValueDictDefaultName, -100}};

    auto waybill_ptr = std::make_shared<WaybillProposal>();
    auto route = GetBatchRoute(std::nullopt, std::nullopt, waybill_ptr);
    auto& segments = route.GetPath().GetAllSegments();

    waybill_ptr->segments = {segments[0], segments[2]};
    size_t p_idx = 0;
    for (auto& point : route.GetPath().GetPoints()) {
      if (point.segment->id != segments[0]->id &&
          point.segment->id != segments[2]->id) {
        continue;
      }

      defs::internal::waybill::WaybillPathItem item;
      item.point_id = point.point.get().id;
      item.resolution =
          p_idx++ < 1 ? std::make_optional(
                            defs::internal::waybill::PointResolution::kVisited)
                      : std::nullopt;
      item.segment_id = point.segment->id;
      waybill_ptr->path.push_back(item);
    }

    route_filter::ValidatorSettings settings{
        {}, common_settings, sla_settings, sla_mapping, {}};

    route_filter::SlaValidator validator(false, settings);

    auto reject = validator.Validate(route);
    ASSERT_TRUE(reject.reason.has_value());
  }

  {
    experiments3::UnitedDispatchSlaGroupsSettings::Value sla_settings{
        {dynamic_config::kValueDictDefaultName, {-(50 - 3 - 1 - 1)}}};

    GeneratorsCommonSettings common_settings;
    common_settings.forbidden_second_in_batch_sla = {
        {dynamic_config::kValueDictDefaultName, -100}};

    route_filter::ValidatorSettings settings{
        {}, common_settings, sla_settings, sla_mapping, {}};

    route_filter::SlaValidator validator(false, settings);

    auto route = GetBatchRoute();
    auto segment = route.GetPath().GetAllSegments()[0].get();
    const_cast<Segment*>(segment)
        ->context_info.is_forbidden_to_be_second_in_batch = true;

    auto reject = validator.Validate(route);
    ASSERT_TRUE(reject.reason.has_value());
  }
}

UTEST(RouteFilterTest, ValidateBuffer) {
  GambleSettings gamble_settings{};
  gamble_settings.batch_restrictions.max_number_of_destination_points = 1;
  gamble_settings.batch_restrictions.required_taxi_classes = {"courier"};

  using experiments3::united_dispatch_delivery_generators_settings::
      BufferSettings;
  BufferSettings buffer_settings;
  const int P2P_AFTER_CREATED = 120;
  const int P2P_BEFORE_DUE = 60;
  buffer_settings.p2p_after_created = P2P_AFTER_CREATED;
  buffer_settings.p2p_before_due = P2P_BEFORE_DUE;

  std::unordered_map<std::string, BufferSettings> buffer_settings_init;
  buffer_settings_init[dynamic_config::kValueDictDefaultName] = buffer_settings;
  experiments3::united_dispatch_delivery_generators_settings::Common
      common_settings;
  common_settings.buffer_settings =
      ::dynamic_config::ValueDict<BufferSettings>(buffer_settings_init);

  route_filter::ValidatorSettings settings{
      gamble_settings, common_settings, {}, {}, {}};

  route_filter::BufferValidator validator(true, settings, nullptr);

  auto CREATED_TS = utils::datetime::Now();
  {
    // check that segments inside of buffer window are filtered
    GenerateSegmentKwargs segment_kwargs;
    segment_kwargs.created_ts = CREATED_TS;
    auto now = CREATED_TS + std::chrono::seconds(10);
    utils::datetime::MockNowSet(now);
    auto segment_can_batch = GenerateSegment(segment_kwargs);
    auto route_can_batch = GetRouteFromSegment(segment_can_batch);
    auto reject_can_batch = validator.Validate(route_can_batch);
    ASSERT_TRUE(reject_can_batch.reason.has_value());
  }

  {
    // check that segments outside of buffer window are not filtered
    GenerateSegmentKwargs segment_kwargs;
    segment_kwargs.created_ts = CREATED_TS;
    auto now = CREATED_TS + std::chrono::seconds(130);
    utils::datetime::MockNowSet(now);
    auto segment_can_batch = GenerateSegment(segment_kwargs);
    auto route_can_batch = GetRouteFromSegment(segment_can_batch);
    auto reject_can_batch = validator.Validate(route_can_batch);
    ASSERT_FALSE(reject_can_batch.reason.has_value());
  }

  {
    // check that segments which cannot be batched are not filtered
    GenerateSegmentKwargs segment_kwargs;
    segment_kwargs.created_ts = CREATED_TS;
    auto now = CREATED_TS + std::chrono::seconds(10);
    utils::datetime::MockNowSet(now);
    segment_kwargs.allow_batch = false;
    auto segment_cannot_batch = GenerateSegment(segment_kwargs);
    auto route_cannot_batch = GetRouteFromSegment(segment_cannot_batch);
    auto reject_cannot_batch = validator.Validate(route_cannot_batch);
    ASSERT_FALSE(reject_cannot_batch.reason.has_value());
  }

  // check cases when due - y > created + x (see notation in
  // https://st.yandex-team.ru/CARGODEV-11607#6290a775ec82601fc575d0e4)
  {
    // now < created + x
    GenerateSegmentKwargs segment_kwargs;
    segment_kwargs.created_ts = CREATED_TS;
    segment_kwargs.due = CREATED_TS + std::chrono::seconds(P2P_AFTER_CREATED +
                                                           P2P_BEFORE_DUE + 30);
    auto now = CREATED_TS - std::chrono::seconds(60);
    utils::datetime::MockNowSet(now);
    auto route = GetRouteFromSegment(GenerateSegment(segment_kwargs));
    auto reject = validator.Validate(route);
    ASSERT_TRUE(reject.reason.has_value());
  }
  {
    // due - y > created + x, created + x < now < due - y
    GenerateSegmentKwargs segment_kwargs;
    segment_kwargs.created_ts = CREATED_TS;
    segment_kwargs.due = CREATED_TS + std::chrono::seconds(P2P_AFTER_CREATED +
                                                           P2P_BEFORE_DUE + 30);
    auto now = CREATED_TS + std::chrono::seconds(15);
    utils::datetime::MockNowSet(now);
    auto route = GetRouteFromSegment(GenerateSegment(segment_kwargs));
    auto reject = validator.Validate(route);
    ASSERT_TRUE(reject.reason.has_value());
  }
  {
    // due - y > created + x, now > due - y
    GenerateSegmentKwargs segment_kwargs;
    segment_kwargs.created_ts = CREATED_TS;
    segment_kwargs.due = CREATED_TS + std::chrono::seconds(P2P_AFTER_CREATED +
                                                           P2P_BEFORE_DUE + 30);
    auto now = segment_kwargs.due.value() + std::chrono::seconds(15);
    utils::datetime::MockNowSet(now);
    auto route = GetRouteFromSegment(GenerateSegment(segment_kwargs));
    auto reject = validator.Validate(route);
    ASSERT_FALSE(reject.reason.has_value());
  }

  // check cases when due - y < created + x
  {
    // now < due - y
    GenerateSegmentKwargs segment_kwargs;
    segment_kwargs.created_ts = CREATED_TS;
    segment_kwargs.due = CREATED_TS + std::chrono::seconds(P2P_AFTER_CREATED +
                                                           P2P_BEFORE_DUE - 30);
    auto now =
        segment_kwargs.due.value() - std::chrono::seconds(P2P_BEFORE_DUE + 10);
    utils::datetime::MockNowSet(now);
    auto route = GetRouteFromSegment(GenerateSegment(segment_kwargs));
    auto reject = validator.Validate(route);
    ASSERT_TRUE(reject.reason.has_value());
  }
  {
    // due - y < now < created + x
    GenerateSegmentKwargs segment_kwargs;
    segment_kwargs.created_ts = CREATED_TS;
    segment_kwargs.due = CREATED_TS + std::chrono::seconds(P2P_AFTER_CREATED +
                                                           P2P_BEFORE_DUE - 30);
    auto now =
        segment_kwargs.due.value() - std::chrono::seconds(P2P_BEFORE_DUE - 15);
    utils::datetime::MockNowSet(now);
    auto route = GetRouteFromSegment(GenerateSegment(segment_kwargs));
    auto reject = validator.Validate(route);
    ASSERT_TRUE(reject.reason.has_value());
  }
  {
    // now > created + x
    GenerateSegmentKwargs segment_kwargs;
    segment_kwargs.created_ts = CREATED_TS;
    segment_kwargs.due = CREATED_TS + std::chrono::seconds(P2P_AFTER_CREATED +
                                                           P2P_BEFORE_DUE - 30);
    auto now = CREATED_TS + std::chrono::seconds(P2P_AFTER_CREATED + 10);
    utils::datetime::MockNowSet(now);
    auto route = GetRouteFromSegment(GenerateSegment(segment_kwargs));
    auto reject = validator.Validate(route);
    ASSERT_FALSE(reject.reason.has_value());
  }
}

UTEST(RouteFilterTest, ScoreRoutes) {
  auto route = GetBatchRoute();
  std::unordered_map<std::string, double> scores =
      route_filter::ScoreRoutes({route});
  ASSERT_EQ(scores[route.GetRouteId()], BATCH_DISTANCE / SEGMENT_DISTANCE);
}

UTEST(RouteFilterTest, ChooseBestRoutes) {
  const auto& batches_limit_reached =
      ToString(BatchRejectReason::kBatchesLimitReached);
  const auto& batches_per_segment_limit_reached =
      ToString(BatchRejectReason::kBatchesPerSegmentLimitReached);

  auto route_1 = GetRouteWithSegments("test", {"segment-1"});
  auto route_2 = GetRouteWithSegments("test", {"segment-2"});
  auto route_3 = GetRouteWithSegments("test", {"segment-3"});
  auto route_4 = GetRouteWithSegments("test", {"segment-4"});

  auto route_1_2 = GetRouteWithSegments("test", {"segment-1", "segment-2"});
  auto route_1_2_3 =
      GetRouteWithSegments("test", {"segment-1", "segment-2", "segment-3"});

  auto logger = std::make_shared<DummyLogger>();
  united_dispatch::logging::LoggerWrapper logger_wrapper(logger, "test_stage",
                                                         "test_content");

  {
    const size_t max_batches_per_segment = 1;
    const size_t max_mean_batches_per_segment = 5;

    std::vector<std::reference_wrapper<const Route>> routes{
        route_1, route_2, route_3, route_4, route_1_2, route_1_2_3};
    std::unordered_map<std::string, double> scores{
        {route_1.GetRouteId(), 2},   {route_2.GetRouteId(), 2},
        {route_3.GetRouteId(), 2},   {route_4.GetRouteId(), 2},

        {route_1_2.GetRouteId(), 1}, {route_1_2_3.GetRouteId(), 1},
    };

    united_dispatch::waybill::delivery::metrics::RouteFilterStats stats;
    route_filter::ChooseBestRoutes(
        routes, scores, stats, max_batches_per_segment,
        max_mean_batches_per_segment, logger_wrapper, false);

    ASSERT_EQ(routes.front().get().GetPath().GetNumSegments(), 1);
    ASSERT_EQ(routes.size(), 4);
    ASSERT_EQ(stats.rejections[batches_limit_reached], 0);
    ASSERT_EQ(stats.rejections[batches_per_segment_limit_reached], 2);
  }

  {
    const size_t max_batches_per_segment = 2;
    const size_t max_mean_batches_per_segment = 5;

    std::vector<std::reference_wrapper<const Route>> routes{
        route_1, route_2, route_3, route_4, route_1_2, route_1_2_3};
    std::unordered_map<std::string, double> scores{
        {route_1.GetRouteId(), 2},   {route_2.GetRouteId(), 2},
        {route_3.GetRouteId(), 2},   {route_4.GetRouteId(), 2},

        {route_1_2.GetRouteId(), 4}, {route_1_2_3.GetRouteId(), 3},
    };

    united_dispatch::waybill::delivery::metrics::RouteFilterStats stats;
    route_filter::ChooseBestRoutes(
        routes, scores, stats, max_batches_per_segment,
        max_mean_batches_per_segment, logger_wrapper, false);

    ASSERT_EQ(routes.front().get().GetPath().GetNumSegments(), 1);
    ASSERT_EQ(routes.back().get().GetRouteId(), route_1_2.GetRouteId());
    ASSERT_EQ(routes.size(), 5);
    ASSERT_EQ(stats.rejections[batches_limit_reached], 0);
    ASSERT_EQ(stats.rejections[batches_per_segment_limit_reached], 1);
  }

  {
    const size_t max_batches_per_segment = 3;
    const size_t max_mean_batches_per_segment = 5;

    std::vector<std::reference_wrapper<const Route>> routes{
        route_1, route_2, route_3, route_4, route_1_2, route_1_2_3};
    std::unordered_map<std::string, double> scores{
        {route_1.GetRouteId(), 2},   {route_2.GetRouteId(), 2},
        {route_3.GetRouteId(), 2},   {route_4.GetRouteId(), 2},

        {route_1_2.GetRouteId(), 3}, {route_1_2_3.GetRouteId(), 4},
    };

    united_dispatch::waybill::delivery::metrics::RouteFilterStats stats;
    route_filter::ChooseBestRoutes(
        routes, scores, stats, max_batches_per_segment,
        max_mean_batches_per_segment, logger_wrapper, false);

    ASSERT_EQ(routes.size(), 6);
    ASSERT_EQ(stats.rejections[batches_limit_reached], 0);
    ASSERT_EQ(stats.rejections[batches_per_segment_limit_reached], 0);
  }

  {
    const size_t max_batches_per_segment = 3;
    const size_t max_mean_batches_per_segment = 1;

    std::vector<std::reference_wrapper<const Route>> routes{
        route_1, route_2, route_3, route_4, route_1_2, route_1_2_3};
    std::unordered_map<std::string, double> scores{
        {route_1.GetRouteId(), 2},   {route_2.GetRouteId(), 2},
        {route_3.GetRouteId(), 2},   {route_4.GetRouteId(), 2},

        {route_1_2.GetRouteId(), 3}, {route_1_2_3.GetRouteId(), 4},
    };

    united_dispatch::waybill::delivery::metrics::RouteFilterStats stats;
    route_filter::ChooseBestRoutes(
        routes, scores, stats, max_batches_per_segment,
        max_mean_batches_per_segment, logger_wrapper, false);

    ASSERT_EQ(routes.front().get().GetPath().GetNumSegments(), 1);
    ASSERT_EQ(routes.size(), 4);
    ASSERT_EQ(stats.rejections[batches_limit_reached], 2);
    ASSERT_EQ(stats.rejections[batches_per_segment_limit_reached], 0);
  }

  {
    const size_t max_batches_per_segment = 3;
    const size_t max_mean_batches_per_segment = 2;

    std::vector<std::reference_wrapper<const Route>> routes{
        route_1, route_2,   route_3,   route_3,
        route_3, route_1_2, route_1_2, route_1_2_3};
    std::unordered_map<std::string, double> scores{
        {route_1.GetRouteId(), 2},   {route_2.GetRouteId(), 2},
        {route_3.GetRouteId(), 2},   {route_4.GetRouteId(), 2},

        {route_1_2.GetRouteId(), 3}, {route_1_2_3.GetRouteId(), 4},
    };

    united_dispatch::waybill::delivery::metrics::RouteFilterStats stats;
    route_filter::ChooseBestRoutes(
        routes, scores, stats, max_batches_per_segment,
        max_mean_batches_per_segment, logger_wrapper, false);

    ASSERT_EQ(routes.front().get().GetPath().GetNumSegments(), 1);
    ASSERT_EQ(routes.size(), 6);
    ASSERT_EQ(stats.rejections[batches_limit_reached], 1);
    ASSERT_EQ(stats.rejections[batches_per_segment_limit_reached], 1);
  }
}

UTEST(RouteFilterTest, ValidateSameClientsInBatch) {
  auto s1 = GenerateSegment({true, "segment-1", "corp_1", "zone_1"});
  auto s2 = GenerateSegment({true, "segment-2", "corp_1", "zone_1"});
  auto s3 = GenerateSegment({true, "segment-3", "corp_2", "zone_1"});
  auto s4 = GenerateSegment({true, "segment-4", "corp_1", "zone_2"});
  auto s5 = GenerateSegment({true, "segment-5", "corp_2", "zone_2"});

  handlers::SegmentPoint sp1;
  sp1.segment_id = "segment-1";
  handlers::SegmentPoint sp2;
  sp2.segment_id = "segment-2";
  handlers::SegmentPoint sp3;
  sp3.segment_id = "segment-3";
  handlers::SegmentPoint sp4;
  sp4.segment_id = "segment-4";
  handlers::SegmentPoint sp5;
  sp5.segment_id = "segment-5";

  united_dispatch::waybill::delivery::Waypoint wp1(sp1, s1);
  united_dispatch::waybill::delivery::Waypoint wp2(sp2, s2);
  united_dispatch::waybill::delivery::Waypoint wp3(sp3, s3);
  united_dispatch::waybill::delivery::Waypoint wp4(sp4, s4);
  united_dispatch::waybill::delivery::Waypoint wp5(sp5, s5);

  std::unordered_map<std::string, bool> add_same_corp_validation_init;
  add_same_corp_validation_init[dynamic_config::kValueDictDefaultName] = true;
  experiments3::united_dispatch_delivery_generators_settings::Common
      common_settings;
  common_settings.add_same_corp_validation =
      ::dynamic_config::ValueDict<bool>(add_same_corp_validation_init);

  route_filter::ValidatorSettings settings{{}, common_settings, {}, {}, {}};

  route_filter::SameClientsInBatchValidator validator(false, settings);

  {
    auto reject = validator.Validate({"test_generator", {wp1, wp2}, true});
    ASSERT_FALSE(reject.reason.has_value());
  }

  {
    auto reject = validator.Validate({"test_generator", {wp1, wp2, wp3}, true});
    ASSERT_TRUE(reject.reason.has_value());
  }

  {
    auto reject = validator.Validate({"test_generator", {wp1, wp2, wp4}, true});
    ASSERT_TRUE(reject.reason.has_value());
  }

  {
    auto reject = validator.Validate({"test_generator", {wp1, wp2, wp5}, true});
    ASSERT_TRUE(reject.reason.has_value());
  }
}

UTEST(RouteFilterTest, ValidateBatchLateness) {
  experiments3::united_dispatch_delivery_generators_settings::Common
      common_settings{};
  common_settings.min_performer_eta = dynamic_config::ValueDict<int>{
      {dynamic_config::kValueDictDefaultName, 10}};
  common_settings.max_performer_eta = dynamic_config::ValueDict<int>{
      {dynamic_config::kValueDictDefaultName, 5}};
  common_settings.pickup_time = dynamic_config::ValueDict<int>{
      {dynamic_config::kValueDictDefaultName, 5}};
  common_settings.dropoff_time = dynamic_config::ValueDict<int>{
      {dynamic_config::kValueDictDefaultName, 5}};
  common_settings.strict_from_interval_diff = dynamic_config::ValueDict<int>{
      {dynamic_config::kValueDictDefaultName, 0}};
  common_settings.strict_to_interval_diff = dynamic_config::ValueDict<int>{
      {dynamic_config::kValueDictDefaultName, 0}};

  route_filter::ValidatorSettings settings{{}, common_settings, {}, {}, {}};

  route_filter::BatchLatenessValidator validator(false, settings);

  const auto now = utils::datetime::Now();
  utils::datetime::MockNowSet(now);

  {
    std::vector<handlers::SegmentPointTimeInterval> intervals = {
        {handlers::SegmentPointTimeIntervalType::kStrictMatch,
         now + std::chrono::seconds{0}, now + std::chrono::seconds{20}}};
    auto route = GetBatchRoute(intervals);

    auto reject = validator.Validate(route);
    ASSERT_TRUE(reject.reason.has_value());
  }

  {
    std::vector<handlers::SegmentPointTimeInterval> intervals = {
        {handlers::SegmentPointTimeIntervalType::kStrictMatch,
         now + std::chrono::seconds{0}, now + std::chrono::seconds{20}}};

    auto waybill_ptr = std::make_shared<WaybillProposal>();
    auto route = GetBatchRoute(intervals, std::nullopt, waybill_ptr);
    size_t p_idx = 0;
    for (auto& point : route.GetPath().GetPoints()) {
      defs::internal::waybill::WaybillPathItem item;
      item.point_id = point.point.get().id;
      item.resolution =
          p_idx++ < 5 ? std::make_optional(
                            defs::internal::waybill::PointResolution::kVisited)
                      : std::nullopt;
      item.segment_id = point.segment->id;
      waybill_ptr->path.push_back(item);
    }

    auto reject = validator.Validate(route);

    ASSERT_FALSE(reject.reason.has_value());
  }

  {
    std::vector<handlers::SegmentPointTimeInterval> intervals = {
        {handlers::SegmentPointTimeIntervalType::kStrictMatch,
         now + std::chrono::seconds{10}, now + std::chrono::seconds{40}}};
    auto route = GetBatchRoute(intervals);

    auto reject = validator.Validate(route);
    ASSERT_FALSE(reject.reason.has_value());
  }
}

UTEST(RouteFilterTest, ValidateBatchEarliness) {
  experiments3::united_dispatch_delivery_generators_settings::Common
      common_settings{};
  common_settings.min_performer_eta = dynamic_config::ValueDict<int>{
      {dynamic_config::kValueDictDefaultName, 5}};
  common_settings.max_performer_eta = dynamic_config::ValueDict<int>{
      {dynamic_config::kValueDictDefaultName, 5}};
  common_settings.pickup_time = dynamic_config::ValueDict<int>{
      {dynamic_config::kValueDictDefaultName, 10}};
  common_settings.dropoff_time = dynamic_config::ValueDict<int>{
      {dynamic_config::kValueDictDefaultName, 10}};
  common_settings.strict_from_interval_diff = dynamic_config::ValueDict<int>{
      {dynamic_config::kValueDictDefaultName, 0}};
  common_settings.strict_to_interval_diff = dynamic_config::ValueDict<int>{
      {dynamic_config::kValueDictDefaultName, 0}};

  route_filter::ValidatorSettings settings{{}, common_settings, {}, {}, {}};

  route_filter::BatchEarlinessValidator validator(false, settings);

  const auto now = utils::datetime::Now();
  utils::datetime::MockNowSet(now);

  {
    std::vector<handlers::SegmentPointTimeInterval> intervals = {
        {handlers::SegmentPointTimeIntervalType::kStrictMatch,
         now + std::chrono::seconds{45}, now + std::chrono::seconds{200}}};
    auto route = GetBatchRoute(intervals);
    auto reject = validator.Validate(route);

    ASSERT_TRUE(reject.reason.has_value());
  }

  {
    std::vector<handlers::SegmentPointTimeInterval> intervals = {
        {handlers::SegmentPointTimeIntervalType::kStrictMatch,
         now + std::chrono::seconds{45}, now + std::chrono::seconds{200}}};

    auto waybill_ptr = std::make_shared<WaybillProposal>();
    auto route = GetBatchRoute(intervals, std::nullopt, waybill_ptr);
    size_t p_idx = 0;
    for (auto& point : route.GetPath().GetPoints()) {
      defs::internal::waybill::WaybillPathItem item;
      item.point_id = point.point.get().id;
      item.resolution =
          p_idx++ < 3 ? std::make_optional(
                            defs::internal::waybill::PointResolution::kVisited)
                      : std::nullopt;
      item.segment_id = point.segment->id;
      waybill_ptr->path.push_back(item);
    }

    auto reject = validator.Validate(route);

    ASSERT_TRUE(reject.reason.has_value());
  }

  {
    std::vector<handlers::SegmentPointTimeInterval> intervals = {
        {handlers::SegmentPointTimeIntervalType::kStrictMatch,
         now + std::chrono::seconds{5}, now + std::chrono::seconds{10}}};
    auto route = GetBatchRoute(intervals);
    auto reject = validator.Validate(route);

    ASSERT_FALSE(reject.reason.has_value());
  }
}

UTEST(RouteFilterTest, IntervalsValidatorWithDue) {
  experiments3::united_dispatch_delivery_generators_settings::Common
      common_settings{};
  common_settings.min_performer_eta = dynamic_config::ValueDict<int>{
      {dynamic_config::kValueDictDefaultName, 5}};
  common_settings.max_performer_eta = dynamic_config::ValueDict<int>{
      {dynamic_config::kValueDictDefaultName, 5}};
  common_settings.pickup_time = dynamic_config::ValueDict<int>{
      {dynamic_config::kValueDictDefaultName, 5}};
  common_settings.dropoff_time = dynamic_config::ValueDict<int>{
      {dynamic_config::kValueDictDefaultName, 5}};
  common_settings.strict_from_interval_diff = dynamic_config::ValueDict<int>{
      {dynamic_config::kValueDictDefaultName, 0}};
  common_settings.strict_to_interval_diff = dynamic_config::ValueDict<int>{
      {dynamic_config::kValueDictDefaultName, 0}};

  route_filter::ValidatorSettings settings{{}, common_settings, {}, {}, {}};
  route_filter::BatchEarlinessValidator validator(false, settings);

  const auto now = utils::datetime::Now();
  utils::datetime::MockNowSet(now);

  {
    std::vector<handlers::SegmentPointTimeInterval> intervals = {
        {handlers::SegmentPointTimeIntervalType::kStrictMatch, now,
         now + std::chrono::seconds{200}}};
    auto route = GetBatchRoute(intervals, now + std::chrono::seconds{100});
    auto reject = validator.Validate(route);

    ASSERT_TRUE(reject.reason.has_value());
  }

  {
    auto route = GetBatchRoute(std::nullopt, now + std::chrono::seconds{100});
    auto reject = validator.Validate(route);

    ASSERT_TRUE(reject.reason.has_value());
  }
}

UTEST(RouteFilterTest, MaxSegmentDurationInBatch) {
  experiments3::united_dispatch_delivery_generators_settings::Common
      common_settings{};
  common_settings.min_performer_eta = dynamic_config::ValueDict<int>{
      {dynamic_config::kValueDictDefaultName, 5}};
  common_settings.max_performer_eta = dynamic_config::ValueDict<int>{
      {dynamic_config::kValueDictDefaultName, 5}};
  common_settings.pickup_time = dynamic_config::ValueDict<int>{
      {dynamic_config::kValueDictDefaultName, 5}};
  common_settings.dropoff_time = dynamic_config::ValueDict<int>{
      {dynamic_config::kValueDictDefaultName, 5}};
  common_settings.strict_from_interval_diff = dynamic_config::ValueDict<int>{
      {dynamic_config::kValueDictDefaultName, 0}};
  common_settings.strict_to_interval_diff = dynamic_config::ValueDict<int>{
      {dynamic_config::kValueDictDefaultName, 0}};

  GambleSettings gamble_settings{};
  gamble_settings.enable_max_segment_ctd_in_batch_checker = true;

  experiments3::UnitedDispatchClientsToSlaGroupsMapping::Value sla_mapping{
      {dynamic_config::kValueDictDefaultName,
       dynamic_config::kValueDictDefaultName}};

  const auto now = utils::datetime::Now();
  utils::datetime::MockNowSet(now);

  {
    experiments3::united_dispatch_sla_groups_settings::SlaGroupProperties
        sla_group_propserties;
    sla_group_propserties.max_segment_duration_absolute_increase = 5000;
    sla_group_propserties.max_segment_ctd_in_batch = 10000;
    experiments3::UnitedDispatchSlaGroupsSettings::Value sla_settings{
        {dynamic_config::kValueDictDefaultName, sla_group_propserties}};

    route_filter::ValidatorSettings settings{
        gamble_settings, common_settings, sla_settings, sla_mapping, {}};

    route_filter::BatchLatenessValidator validator(false, settings);
    auto route = GetBatchRoute(std::nullopt, now);
    auto reject = validator.Validate(route);

    ASSERT_FALSE(reject.reason.has_value());
  }

  {
    experiments3::united_dispatch_sla_groups_settings::SlaGroupProperties
        sla_group_propserties;
    sla_group_propserties.max_segment_duration_absolute_increase = 5000;
    sla_group_propserties.max_segment_ctd_in_batch = 0;
    experiments3::UnitedDispatchSlaGroupsSettings::Value sla_settings{
        {dynamic_config::kValueDictDefaultName, sla_group_propserties}};

    route_filter::ValidatorSettings settings{
        gamble_settings, common_settings, sla_settings, sla_mapping, {}};

    route_filter::BatchLatenessValidator validator(false, settings);
    auto route = GetBatchRoute(std::nullopt, now);
    auto reject = validator.Validate(route);

    ASSERT_TRUE(reject.reason.has_value());
  }
}

UTEST(RouteFilterTest, IntervalsValidatorsInfo) {
  experiments3::united_dispatch_delivery_generators_settings::Common
      common_settings{};
  common_settings.min_performer_eta = dynamic_config::ValueDict<int>{
      {dynamic_config::kValueDictDefaultName, 5}};
  common_settings.max_performer_eta = dynamic_config::ValueDict<int>{
      {dynamic_config::kValueDictDefaultName, 5}};
  common_settings.pickup_time = dynamic_config::ValueDict<int>{
      {dynamic_config::kValueDictDefaultName, 5}};
  common_settings.dropoff_time = dynamic_config::ValueDict<int>{
      {dynamic_config::kValueDictDefaultName, 5}};
  common_settings.strict_from_interval_diff = dynamic_config::ValueDict<int>{
      {dynamic_config::kValueDictDefaultName, 0}};
  common_settings.strict_to_interval_diff = dynamic_config::ValueDict<int>{
      {dynamic_config::kValueDictDefaultName, 0}};

  route_filter::ValidatorSettings settings{{}, common_settings, {}, {}, {}};
  route_filter::BatchEarlinessValidator validator(false, settings);

  const auto now = utils::datetime::Now();
  utils::datetime::MockNowSet(now);

  std::vector<handlers::SegmentPointTimeInterval> intervals = {
      {handlers::SegmentPointTimeIntervalType::kStrictMatch,
       now + std::chrono::seconds{10}, now + std::chrono::seconds{20}}};
  auto route = GetBatchRoute(intervals);
  auto reject = validator.Validate(route);

  ASSERT_TRUE(reject.reason.has_value());

  const auto reasons = reject.info["reasons"];
  ASSERT_EQ(reasons.GetSize(), 2);
  ASSERT_EQ(reasons[0]["segment_id"].As<std::string>(), "segment-1");
  ASSERT_EQ(reasons[0]["point_number"].As<int>(), 0);
  ASSERT_EQ(reasons[0]["point_type"].As<std::string>(), "pickup");

  formats::json::ValueBuilder date_builder;
  date_builder["date"] = now + std::chrono::seconds{10};
  ASSERT_EQ(reasons[0]["threshold"].As<std::string>(),
            date_builder.ExtractValue()["date"].As<std::string>());
}

UTEST(RouteFilterTest, CargoPipelineFeature) {
  experiments3::united_dispatch_delivery_generators_settings::Common
      common_settings{};

  route_filter::ValidatorSettings settings{{}, common_settings, {}, {}, {}};
  route_filter::CargoPipelineFeatureValidator validator(false, settings);

  // features
  auto use_cargo_pipeline_feature =
      united_dispatch::constants::kCargoFinanceUseCargoPipelineFeature;

  // generate segments
  std::vector<std::shared_ptr<Segment>> segments;
  auto ordinary_segment = GenerateSegment({true, "ordinary-segment"});
  auto ordinary_segment_2 = GenerateSegment({true, "ordinary-segment-2"});
  segments.push_back(ordinary_segment);
  segments.push_back(ordinary_segment_2);

  auto webcorp_segment_kwargs = GenerateSegmentKwargs{};
  webcorp_segment_kwargs.segment_id = "webcorp-segment";
  webcorp_segment_kwargs.claim_origin = "webcorp";
  auto webcorp_segment = GenerateSegment(webcorp_segment_kwargs);
  webcorp_segment_kwargs.segment_id = "webcorp-segment-2";
  auto webcorp_segment_2 = GenerateSegment(webcorp_segment_kwargs);
  segments.push_back(webcorp_segment);
  segments.push_back(webcorp_segment_2);

  auto ordinary_with_cargo_pipeline_segment_kwargs = GenerateSegmentKwargs{};
  ordinary_with_cargo_pipeline_segment_kwargs.segment_id =
      "ordinary-with-cargo-pipeline-segment";
  ordinary_with_cargo_pipeline_segment_kwargs.claim_features_set = {
      use_cargo_pipeline_feature};
  auto ordinary_with_cargo_pipeline_segment =
      GenerateSegment(ordinary_with_cargo_pipeline_segment_kwargs);
  ordinary_with_cargo_pipeline_segment_kwargs.segment_id =
      "ordinary-with-cargo-pipeline-segment-2";
  auto ordinary_with_cargo_pipeline_segment_2 =
      GenerateSegment(ordinary_with_cargo_pipeline_segment_kwargs);
  segments.push_back(ordinary_with_cargo_pipeline_segment);
  segments.push_back(ordinary_with_cargo_pipeline_segment_2);

  auto webcorp_with_cargo_pipeline_segment_kwargs = GenerateSegmentKwargs{};
  webcorp_with_cargo_pipeline_segment_kwargs.segment_id =
      "webcorp-with-cargo-pipeline-segment";
  webcorp_with_cargo_pipeline_segment_kwargs.claim_origin = "webcorp";
  webcorp_with_cargo_pipeline_segment_kwargs.claim_features_set = {
      use_cargo_pipeline_feature};
  auto webcorp_with_cargo_pipeline_segment =
      GenerateSegment(webcorp_with_cargo_pipeline_segment_kwargs);
  webcorp_with_cargo_pipeline_segment_kwargs.segment_id =
      "webcorp-with-cargo-pipeline-segment-2";
  auto webcorp_with_cargo_pipeline_segment_2 =
      GenerateSegment(webcorp_with_cargo_pipeline_segment_kwargs);
  segments.push_back(webcorp_with_cargo_pipeline_segment);
  segments.push_back(webcorp_with_cargo_pipeline_segment_2);

  // check batches
  for (const auto& segment : segments) {
    auto p2p_route = GetRouteFromSegment(segment);
    ASSERT_FALSE(validator.Validate(p2p_route).reason.has_value());
  }

  auto ordinary_route_no_feature =
      GetRouteFromSegments({ordinary_segment, ordinary_segment_2});
  ASSERT_FALSE(
      validator.Validate(ordinary_route_no_feature).reason.has_value());
  auto ordinary_route_same_features =
      GetRouteFromSegments({ordinary_with_cargo_pipeline_segment,
                            ordinary_with_cargo_pipeline_segment_2});
  ASSERT_FALSE(
      validator.Validate(ordinary_route_same_features).reason.has_value());
  auto ordinary_route_different_features = GetRouteFromSegments(
      {ordinary_segment, ordinary_with_cargo_pipeline_segment});
  ASSERT_TRUE(
      validator.Validate(ordinary_route_different_features).reason.has_value());

  auto webcorp_route_no_feature =
      GetRouteFromSegments({webcorp_segment, webcorp_segment_2});
  ASSERT_FALSE(validator.Validate(webcorp_route_no_feature).reason.has_value());
  auto webcorp_route_same_features =
      GetRouteFromSegments({webcorp_with_cargo_pipeline_segment,
                            webcorp_with_cargo_pipeline_segment_2});
  ASSERT_FALSE(
      validator.Validate(webcorp_route_same_features).reason.has_value());
  auto webcorp_route_different_features = GetRouteFromSegments(
      {webcorp_segment, webcorp_with_cargo_pipeline_segment});
  ASSERT_TRUE(
      validator.Validate(webcorp_route_different_features).reason.has_value());
}

UTEST(RouteFilterTest, ValidateBatchEarlinessWithIntervaDiff) {
  experiments3::united_dispatch_delivery_generators_settings::Common
      common_settings{};
  common_settings.min_performer_eta = dynamic_config::ValueDict<int>{
      {dynamic_config::kValueDictDefaultName, 5}};
  common_settings.max_performer_eta = dynamic_config::ValueDict<int>{
      {dynamic_config::kValueDictDefaultName, 5}};
  common_settings.pickup_time = dynamic_config::ValueDict<int>{
      {dynamic_config::kValueDictDefaultName, 5}};
  common_settings.dropoff_time = dynamic_config::ValueDict<int>{
      {dynamic_config::kValueDictDefaultName, 5}};
  common_settings.strict_from_interval_diff = dynamic_config::ValueDict<int>{
      {dynamic_config::kValueDictDefaultName, 100}};
  common_settings.strict_to_interval_diff = dynamic_config::ValueDict<int>{
      {dynamic_config::kValueDictDefaultName, 0}};

  route_filter::ValidatorSettings settings{{}, common_settings, {}, {}, {}};
  route_filter::BatchEarlinessValidator validator(false, settings);

  const auto now = utils::datetime::Now();
  utils::datetime::MockNowSet(now);

  std::vector<handlers::SegmentPointTimeInterval> intervals = {
      {handlers::SegmentPointTimeIntervalType::kStrictMatch,
       now + std::chrono::seconds{100}, now + std::chrono::seconds{10}}};
  auto route = GetBatchRoute(intervals);
  auto reject = validator.Validate(route);

  ASSERT_FALSE(reject.reason.has_value());
}
