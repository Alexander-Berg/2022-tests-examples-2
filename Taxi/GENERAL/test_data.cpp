#include "test_data.hpp"

#include <hejmdal/sql_queries.hpp>
#include <utils/except.hpp>

#include <set>

namespace hejmdal::views::postgres {

struct TestDataAndCases {
  std::uint32_t test_data_id;
  std::vector<std::uint32_t> test_case_ids;

  TestDataAndCases(const storages::postgres::Row&& row)
      : test_data_id(row["test_data_id"].As<std::int32_t>()) {
    for (auto test_case_id :
         row["test_cases"].As<std::vector<std::int32_t>>()) {
      test_case_ids.push_back(std::move(test_case_id));
    }
  }
};

TestData::TestData(const storages::postgres::ClusterPtr& cluster)
    : cluster_(cluster) {}

models::TestDataCreateResult TestData::Create(
    models::TestData&& test_data, const CommandControl& command_control) {
  auto id = cluster_
                ->Execute(storages::postgres::ClusterHostType::kMaster,
                          command_control, sql::kInsertTestData,
                          test_data.description, test_data.schema_id,
                          test_data.start_time, test_data.precedent_time,
                          test_data.end_time, test_data.data, test_data.meta)
                .AsSingleRow<int>();
  return models::TestDataCreateResult{id};
}

models::TestData TestData::Get(const std::int32_t& id,
                               const CommandControl& command_control) {
  try {
    return cluster_
        ->Execute(storages::postgres::ClusterHostType::kSlave, command_control,
                  sql::kSelectTestData, id)
        .AsSingleRow<models::TestData>(storages::postgres::kRowTag);
  } catch (const storages::postgres::NonSingleRowResultSet&) {
    throw except::NotFound("Failed to get test_data {}: Not found", id);
  } catch (const std::exception& ex) {
    throw except::Error(ex, "Failed to get test_data {}", id);
  }
}

std::vector<models::TestData> TestData::Get(
    const std::set<std::int32_t>& ids, const CommandControl& command_control) {
  try {
    return cluster_
        ->Execute(storages::postgres::ClusterHostType::kSlave, command_control,
                  sql::kSelectTestDataById,
                  std::vector<std::int32_t>(ids.begin(), ids.end()))
        .AsContainer<std::vector<models::TestData>>(
            storages::postgres::kRowTag);
  } catch (const std::exception& ex) {
    throw except::Error(ex, "Failed to select test_data");
  }
}

void TestData::Update(const std::int32_t& id, models::TestData&& test_data,
                      const CommandControl& command_control) {
  try {
    cluster_->Execute(storages::postgres::ClusterHostType::kMaster,
                      command_control, sql::kUpdateTestData, id,
                      test_data.description, test_data.schema_id,
                      test_data.start_time, test_data.precedent_time,
                      test_data.end_time, test_data.data, test_data.meta);
  } catch (const storages::postgres::NonSingleRowResultSet& ex) {
    throw except::NotFound(ex, "Failed to update test_data {}: Not found", id);
  } catch (const std::exception& ex) {
    throw except::Error(ex, "Failed to update test_data {}", id);
  }
}

void TestData::Delete(const std::int32_t& id,
                      const CommandControl& command_control) {
  std::size_t rows_affected;
  try {
    rows_affected = cluster_
                        ->Execute(storages::postgres::ClusterHostType::kMaster,
                                  command_control, sql::kDeleteTestData, id)
                        .RowsAffected();
  } catch (const std::exception& ex) {
    throw except::Error(ex, "Failed to delete test_data {}", id);
  }
  if (rows_affected == 0) {
    throw except::NotFound("Failed to delete test_data {}: Not found", id);
  }
}

std::vector<models::TestDataInfo> TestData::List(
    std::optional<std::string> schema_id,
    const CommandControl& command_control) {
  try {
    if (schema_id.has_value()) {
      return cluster_
          ->Execute(storages::postgres::ClusterHostType::kSlave,
                    command_control, sql::kSelectTestDataInfoForSchema,
                    schema_id.value())
          .AsContainer<std::vector<models::TestDataInfo>>(
              storages::postgres::kRowTag);
    } else {
      return cluster_
          ->Execute(storages::postgres::ClusterHostType::kSlave,
                    command_control, sql::kSelectTestDataInfo)
          .AsContainer<std::vector<models::TestDataInfo>>(
              storages::postgres::kRowTag);
    }
  } catch (const std::exception& ex) {
    throw except::Error(ex, "Failed to get test_data infos");
  }
}

TestDataToCasesMap TestData::GetTestDataToCases(
    const CommandControl& command_control) {
  try {
    auto pg_result =
        cluster_->Execute(storages::postgres::ClusterHostType::kSlave,
                          command_control, sql::kSelectTestDataToTestCasesMap);

    TestDataToCasesMap result;
    for (auto&& pg_row : pg_result) {
      TestDataAndCases info(std::move(pg_row));
      result.insert(
          {std::move(info.test_data_id), std::move(info.test_case_ids)});
    }
    return result;
  } catch (const std::exception& ex) {
    throw except::Error(ex, "Failed to get test_data to test_cases map");
  }
}

}  // namespace hejmdal::views::postgres
