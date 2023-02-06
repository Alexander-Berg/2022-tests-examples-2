#include <views/internal/v1/available-tests/post/view.hpp>

#include <geobase/utils/city.hpp>

#include <taxi_config/taxi_config.hpp>
#include <userver/dynamic_config/snapshot.hpp>
#include <userver/logging/log.hpp>

#include <persey_labs/sql_queries.hpp>
#include <userver/storages/postgres/cluster.hpp>

#include "utils/common.hpp"
#include "utils/tests.hpp"

namespace handlers::internal_v1_available_tests::post {

Response View::Handle(Request&& request, Dependencies&& dependencies) {
  Response200 response;
  geometry::Position pos(request.body.position);

  auto taxi_config = dependencies.config.Get<taxi_config::TaxiConfig>();

  int locality_id;
  try {
    auto zone_locality_id =
        persey_labs::utils::common::GetLocalilityIdFromGeobase(
            pos, dependencies.extra.geobase);
    if (!zone_locality_id) {
      LOG_INFO() << "Failed to resolve locality_id by zone";
      return response;
    }
    locality_id = *zone_locality_id;
  } catch (const std::exception& ex) {
    LOG_INFO() << "Failed to get localities by zone: " << ex.what();
    return response;
  }

  response.locality.id = locality_id;
  const auto region = dependencies.extra.geobase->GetRegionById(locality_id);
  response.locality.name = region.GetName();

  auto cluster = dependencies.pg_persey_labs->GetCluster();

  const auto test_kinds_db =
      cluster
          ->Execute(storages::postgres::ClusterHostType::kSlave,
                    persey_labs::sql::kGetAvailableTests, locality_id)
          .AsContainer<std::unordered_set<std::string>>();

  for (const auto& tk_db : test_kinds_db) {
    auto tariff = persey_labs::utils::GetTestById(tk_db, dependencies);
    if (!tariff) {
      continue;
    }
    response.tests.emplace_back(std::move(tariff.value()));
  }
  return response;
}

}  // namespace handlers::internal_v1_available_tests::post
