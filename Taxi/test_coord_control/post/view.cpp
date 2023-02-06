#include "view.hpp"

#include <driver-id/dbid_uuid.hpp>

#include <fmt/format.h>

#include <userver/logging/log.hpp>
#include <userver/storages/redis/client.hpp>

#include <common/communications/drop_bad_track.hpp>
#include <redis/location_settings.hpp>
#include <redis/names/coord_control.hpp>
#include <utils/redis.hpp>

namespace {

void SetTestLocationSettings(
    handlers::TestLocationSettings&& test_location_settings,
    const handlers::Dependencies& dependencies) {
  using namespace coord_control::redis::names;

  const auto& taxi_cfg = dependencies.config.Get<taxi_config::TaxiConfig>();

  if (test_location_settings.location_settings) {
    coord_control::models::StrategyInfo strategy_info{
        test_location_settings.driver_id,
        *test_location_settings.location_settings,
        {},
        test_location_settings.location_settings_etag};
    strategy_info.taximeter_agent_info =
        test_location_settings.taximeter_agent_info;

    coord_control::redis::StoreLocationSettingsBulk(
        {{std::move(strategy_info)}},
        taxi_cfg.coord_control_saving_strategies_chunk_size,
        dependencies.redis_coord_control, taxi_cfg.coord_control_redis_settings,
        dependencies.extra.metrix_writer,
        taxi_cfg.coord_control_storage_settings_v2.max_performer_age);
  }
}
}  // namespace

namespace handlers::test_coord_control::post {

Response View::Handle(Request&& request, Dependencies&& dependencies) {
  using namespace coord_control::communications;
  Response200 response;

  auto test_request_body = request.body;
  if (test_request_body.test_location_settings) {
    SetTestLocationSettings(
        std::move(*test_request_body.test_location_settings), dependencies);

    if (test_request_body.test_location_settings->drop_bad_track) {
      auto& driver_id = test_request_body.test_location_settings->driver_id;
      LOG_INFO() << fmt::format(
          "sending driver notification from coord-control to {}", driver_id);
      driver_id::DriverDbidUndscrUuid dbid_uuid{std::move(driver_id)};
      SendDropBadTrackPush(dbid_uuid.GetDbid().ToString(),
                           dbid_uuid.GetUuid().ToString(), std::nullopt,
                           dependencies.client_notify_client);
    }
  }

  return response;
}

}  // namespace handlers::test_coord_control::post
