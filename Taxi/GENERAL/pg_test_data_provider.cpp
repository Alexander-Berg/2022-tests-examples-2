#include "pg_test_data_provider.hpp"

#include <views/postgres/test_data.hpp>

#include <fmt/format.h>

#include <set>

#include <userver/logging/log.hpp>

namespace hejmdal::views::utils {

PgTestDataProvider::PgTestDataProvider(storages::postgres::ClusterPtr cluster,
                                       postgres::CommandControl command_control)
    : cluster_(cluster), command_control_(std::move(command_control)) {}

radio::tester::DataIdToDataMap PgTestDataProvider::CollectTestData(
    std::set<int>&& test_data_ids) {
  LOG_DEBUG() << fmt::format(
      "TestDataProviderImpl: collecting {} test_data objects",
      test_data_ids.size());
  try {
    auto test_data_vec = views::postgres::TestData(cluster_).Get(
        test_data_ids, command_control_);
    DataIdToDataMap result;
    for (auto&& data : test_data_vec) {
      result.emplace(data.id, std::make_shared<formats::json::Value>(
                                  std::move(data.data)));
    }
    return result;
  } catch (std::exception& ex) {
    throw except::Error(ex,
                        "TestDataProviderImpl: could not collect test data");
  }
}

}  // namespace hejmdal::views::utils
