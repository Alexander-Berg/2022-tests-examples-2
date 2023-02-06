#include "test_kinds.hpp"

#include <userver/logging/log.hpp>

#include <persey_labs/sql_queries.hpp>

namespace utils::validation {

bool CheckTestsInConfig(const std::vector<std::string>& test_kinds,
                        const taxi_config::TaxiConfig& config) {
  const auto& tests_cfg = config.persey_labs_tests.extra;

  for (const auto& test_kind : test_kinds) {
    if (tests_cfg.find(test_kind) == tests_cfg.end()) {
      LOG_ERROR() << "Test kind = " << test_kind << " not in config";
      return false;
    }
  }

  return true;
}

bool CheckTestsInLabEntity(const std::vector<std::string>& test_kinds,
                           const std::string& lab_entity_id,
                           storages::postgres::Transaction& trx) {
  auto entity_tests =
      trx.Execute(persey_labs::sql::kGetLabEntityTests, lab_entity_id)
          .AsContainer<std::unordered_set<std::string>>();
  if (entity_tests.empty()) {
    LOG_ERROR() << "Lab entity = " << lab_entity_id
                << " without test kinds in db";
    return false;
  }

  for (const auto& test_kind : test_kinds) {
    if (entity_tests.find(test_kind) == entity_tests.end()) {
      LOG_ERROR() << "Test kind = " << test_kind
                  << " not in entity id=" << lab_entity_id;
      return false;
    }
  }

  return true;
}

bool CheckTestsInLabEntityShifts(const std::vector<std::string>& test_kinds,
                                 const std::string& lab_entity_id,
                                 storages::postgres::Transaction& trx) {
  auto entity_shifts_tests =
      trx.Execute(persey_labs::sql::kGetAdminLabEntityShiftsTests,
                  lab_entity_id)
          .AsContainer<std::vector<std::string>>();
  if (entity_shifts_tests.empty()) {
    return true;
  }

  for (const auto& shift_test : entity_shifts_tests) {
    if (std::find(test_kinds.begin(), test_kinds.end(), shift_test) ==
        test_kinds.end()) {
      LOG_ERROR() << "Shift selected test = " << shift_test
                  << " not in new test kinds entity id=" << lab_entity_id;
      return false;
    }
  }

  return true;
}

}  // namespace utils::validation
