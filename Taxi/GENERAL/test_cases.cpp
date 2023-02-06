#include "test_cases.hpp"

#include <hejmdal/sql_queries.hpp>
#include <utils/except.hpp>

namespace hejmdal::views::postgres {

TestCases::TestCases(const storages::postgres::ClusterPtr& cluster)
    : cluster_(cluster) {}

TestCaseCreateResult TestCases::Create(models::postgres::TestCase&& test_case,
                                       const CommandControl& command_control) {
  try {
    return cluster_
        ->Execute(storages::postgres::ClusterHostType::kMaster, command_control,
                  sql::kInsertTestCase, test_case.description,
                  test_case.test_data_id, test_case.schema_id,
                  test_case.out_point_id, test_case.start_time,
                  test_case.end_time, test_case.check_type,
                  test_case.check_params, test_case.is_enabled)
        .AsSingleRow<TestCaseCreateResult>(storages::postgres::kFieldTag);
  } catch (const std::exception& ex) {
    throw except::Error(ex, "Failed to insert test_case");
  }
}

std::vector<models::postgres::TestCase> TestCases::GetForSchema(
    const std::string& schema_id, const CommandControl& command_control) {
  try {
    return cluster_
        ->Execute(storages::postgres::ClusterHostType::kSlave, command_control,
                  sql::kSelectTestCasesBySchemaId, schema_id)
        .AsContainer<std::vector<models::postgres::TestCase>>(
            storages::postgres::kRowTag);
  } catch (const std::exception& ex) {
    throw except::Error(ex, "Failed to select test_cases for schema {}",
                        schema_id);
  }
}

models::postgres::TestCase TestCases::Get(
    const std::int32_t& id, const CommandControl& command_control) {
  try {
    return cluster_
        ->Execute(storages::postgres::ClusterHostType::kSlave, command_control,
                  sql::kSelectTestCase, id)
        .AsSingleRow<models::postgres::TestCase>(storages::postgres::kRowTag);
  } catch (const storages::postgres::NonSingleRowResultSet& ex) {
    throw except::NotFound(ex, "Failed to get test_case {}: Not found", id);
  } catch (const std::exception& ex) {
    throw except::Error(ex, "Failed to select test_case {}", id);
  }
}

std::vector<models::postgres::TestCase> TestCases::Get(
    const std::vector<int>& ids, const CommandControl& command_control) {
  try {
    return cluster_
        ->Execute(storages::postgres::ClusterHostType::kSlave, command_control,
                  sql::kSelectTestCasesById, ids)
        .AsContainer<std::vector<models::postgres::TestCase>>(
            storages::postgres::kRowTag);
  } catch (const std::exception& ex) {
    throw except::Error(ex, "Failed to select test_cases by ids");
  }
}

void TestCases::Update(const std::int32_t& id,
                       models::postgres::TestCase&& test_case,
                       const CommandControl& command_control) {
  try {
    cluster_->Execute(
        storages::postgres::ClusterHostType::kMaster, command_control,
        sql::kUpdateTestCase, id, test_case.description, test_case.test_data_id,
        test_case.schema_id, test_case.out_point_id, test_case.start_time,
        test_case.end_time, test_case.check_type, test_case.check_params,
        test_case.is_enabled);
  } catch (const storages::postgres::NonSingleRowResultSet& ex) {
    throw except::NotFound(ex, "Failed to update test_case {}: Not found", id);
  } catch (const std::exception& ex) {
    throw except::Error(ex, "Failed to update test_case {}", id);
  }
}

void TestCases::Delete(const std::int32_t& id,
                       const CommandControl& command_control) {
  std::size_t rows_affected = 0;
  try {
    rows_affected = cluster_
                        ->Execute(storages::postgres::ClusterHostType::kMaster,
                                  command_control, sql::kDeleteTestCase, id)
                        .RowsAffected();
  } catch (const std::exception& ex) {
    throw except::Error(ex, "Failed to delete test_case {}", id);
  }
  if (rows_affected == 0) {
    throw except::NotFound("Failed to delete test_case {}: Not found", id);
  }
}

void TestCases::Activate(const std::int32_t& id, bool do_activate,
                         const CommandControl& command_control) {
  try {
    cluster_->Execute(storages::postgres::ClusterHostType::kMaster,
                      command_control, sql::kActivateTestCase, id, do_activate);
  } catch (const storages::postgres::NonSingleRowResultSet& ex) {
    throw except::NotFound(ex, "Failed to activate test_case {}: Not found",
                           id);
  } catch (const std::exception& ex) {
    throw except::Error(ex, "Failed to activate test_case {}", id);
  }
}

std::vector<models::postgres::TestCaseInfo> TestCases::List(
    std::optional<std::string> schema_id,
    const CommandControl& command_control) {
  try {
    if (schema_id.has_value()) {
      return cluster_
          ->Execute(storages::postgres::ClusterHostType::kSlave,
                    command_control, sql::kSelectTestCasesInfoForSchema,
                    schema_id)
          .AsContainer<std::vector<models::postgres::TestCaseInfo>>(
              storages::postgres::kRowTag);
    } else {
      return cluster_
          ->Execute(storages::postgres::ClusterHostType::kSlave,
                    command_control, sql::kSelectTestCasesInfo)
          .AsContainer<std::vector<models::postgres::TestCaseInfo>>(
              storages::postgres::kRowTag);
    }
  } catch (const std::exception& ex) {
    throw except::Error(ex, "Failed to get test_case infos");
  }
}

}  // namespace hejmdal::views::postgres
