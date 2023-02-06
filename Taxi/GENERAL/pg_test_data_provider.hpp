#pragma once

#include <radio/tester/circuit_tester.hpp>
#include <views/postgres/detail/control.hpp>

#include <set>

namespace hejmdal::views::utils {

using DataIdToDataMap = radio::tester::DataIdToDataMap;

class PgTestDataProvider final : public radio::tester::TestDataProvider {
 public:
  PgTestDataProvider(storages::postgres::ClusterPtr cluster,
                     postgres::CommandControl command_control);

  DataIdToDataMap CollectTestData(std::set<int>&& test_data_ids) override;

 private:
  storages::postgres::ClusterPtr cluster_;
  postgres::CommandControl command_control_;
};

}  // namespace hejmdal::views::utils
