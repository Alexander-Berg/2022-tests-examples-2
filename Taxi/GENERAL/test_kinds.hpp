#pragma once

#include <string>
#include <vector>

#include <taxi_config/taxi_config.hpp>
#include <userver/storages/postgres/cluster.hpp>

namespace utils::validation {

bool CheckTestsInConfig(const std::vector<std::string>& test_kinds,
                        const taxi_config::TaxiConfig& config);

bool CheckTestsInLabEntity(const std::vector<std::string>& test_kinds,
                           const std::string& lab_entity_id,
                           storages::postgres::Transaction& trx);

bool CheckTestsInLabEntityShifts(const std::vector<std::string>& test_kinds,
                                 const std::string& lab_entity_id,
                                 storages::postgres::Transaction& trx);

}  // namespace utils::validation
