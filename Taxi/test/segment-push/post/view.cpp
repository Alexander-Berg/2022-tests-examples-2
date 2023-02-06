#include "view.hpp"

#include <userver/formats/parse/to.hpp>
#include <userver/storages/postgres/cluster.hpp>

#include <clients/cargo-dispatch/definitions.hpp>

#include <defs/internal/proposition.hpp>
#include <experiments3/models/cache_manager.hpp>
#include <experiments3/united_dispatch_segment_shard_selector.hpp>
#include <models/grocery/independent.hpp>
#include <models/united_dispatch/segment.hpp>
#include <models/united_dispatch/segment_executor.hpp>
#include <sql/mappings/segment.hpp>
#include <sql/mappings/segment_executor.hpp>
#include <sql/mappings/segment_with_building_version.hpp>
#include <united_dispatch/sql_queries.hpp>
#include <utils/constants.hpp>

namespace handlers::test_segment_push::post {

namespace {

using SegmentId = std::string;

struct NewSegment {
  united_dispatch::models::pg::InsertingSegment data;
  uint8_t shard;
  united_dispatch::models::SegmentDoc segment_doc;
};

::experiments3::united_dispatch_segment_shard_selector::Value
GetExpSegmentShardSelector(
    const ::experiments3::kwargs_builders::UnitedDispatchSegmentDoc& kwargs,
    const ::experiments3::models::CacheManagerPtr& experiments3) {
  const auto exp_value =
      experiments3->GetValue<experiments3::UnitedDispatchSegmentShardSelector>(
          kwargs);
  if (!exp_value) {
    LOG_INFO() << "Config3.0 united_dispatch_segment_shard_selector "
                  "not found";
    return {0};  // default shard
  }

  return *exp_value;
}

uint8_t SelectSegmentShard(
    const ::experiments3::kwargs_builders::UnitedDispatchSegmentDoc& kwargs,
    const handlers::Dependencies& dependencies) {
  auto exp_shard =
      GetExpSegmentShardSelector(kwargs, dependencies.experiments3).shard;

  return exp_shard;
}

united_dispatch::models::SegmentDoc GetSegmentProjection(
    const clients::cargo_dispatch::SegmentInfo& dispatch_segment) {
  auto raw_full = clients::cargo_dispatch::Serialize(
      dispatch_segment, formats::serialize::To<formats::json::Value>());

  return defs::internal::segment::Parse(
      std::move(raw_full),
      formats::parse::To<defs::internal::segment::ExternalSegmentFull>());
}

auto GetSegmentStatus(
    const clients::cargo_dispatch::SegmentInfo& dispatch_segment) {
  united_dispatch::models::SegmentStatus status =
      united_dispatch::models::SegmentStatus::kExecuting;
  if (dispatch_segment.dispatch.resolved ||
      dispatch_segment.segment.resolution.has_value()) {
    status = united_dispatch::models::SegmentStatus::kResolved;
  } else if (dispatch_segment.dispatch.chosen_waybill.has_value() &&
             dispatch_segment.dispatch.chosen_waybill.value().router_id !=
                 united_dispatch::constants::kRouterId) {
    status = united_dispatch::models::SegmentStatus::kAnotherRouterChosen;
  }
  return status;
}

NewSegment ConvertDispatchSegment(
    const clients::cargo_dispatch::SegmentInfo& dispatch_segment,
    const ::handlers::Dependencies& dependencies) {
  NewSegment segment;
  segment.segment_doc = GetSegmentProjection(dispatch_segment);

  const auto segment_kwargs = united_dispatch::models::BuildSegmentDocKwargs(
      segment.segment_doc, dependencies);
  segment.shard = SelectSegmentShard(segment_kwargs, dependencies);

  // convert segment
  segment.data.id = dispatch_segment.segment.id;
  segment.data.waybill_building_version =
      dispatch_segment.dispatch.waybill_building_version;
  segment.data.raw_segment_info = defs::internal::segment::Serialize(
      segment.segment_doc, formats::serialize::To<formats::json::Value>());
  segment.data.status = ToString(GetSegmentStatus(dispatch_segment));

  return segment;
}

std::optional<NewSegment> FetchSegment(
    const clients::cargo_dispatch::SegmentInfo& segment_info,
    const ::handlers::Dependencies& dependencies) {
  if (!segment_info.dispatch.waybill_building_awaited) {
    LOG_INFO() << "Do not need to fetch segment yet "
               << segment_info.segment.id;
    return std::nullopt;
  }

  return ConvertDispatchSegment(segment_info, dependencies);
}

void StoreSegment(const NewSegment& segment,
                  const std::vector<united_dispatch::models::SegmentExecutor>&
                      segment_executors,
                  const storages::postgres::DatabasePtr& pg_ud) {
  std::vector<united_dispatch::models::pg::InsertingSegmentExecutor>
      inserting_segment_executors;
  inserting_segment_executors.reserve(segment_executors.size());
  for (const auto& segment_executor : segment_executors) {
    inserting_segment_executors.push_back(
        united_dispatch::models::pg::Serialize(segment_executor));
  }

  pg_ud->GetClusterForShard(segment.shard)
      ->Execute(storages::postgres::ClusterHostType::kMaster,
                united_dispatch::sql::kInsertSegment, segment.data,
                inserting_segment_executors);
}

}  // namespace

Response View::Handle(Request&& request, Dependencies&& dependencies) {
  const auto segment =
      Parse(request.body.extra,
            formats::parse::To<clients::cargo_dispatch::SegmentInfo>{});

  if (const auto new_segment = FetchSegment(segment, dependencies);
      new_segment.has_value()) {
    const auto segment_executors = united_dispatch::models::GetExecutors(
        new_segment->segment_doc, new_segment->shard, dependencies);

    StoreSegment(new_segment.value(), segment_executors,
                 dependencies.pg_united_dispatch);
  }

  return Response200{};
}

}  // namespace handlers::test_segment_push::post
