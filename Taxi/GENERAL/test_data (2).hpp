#pragma once

#include <unordered_map>

#include <models/test_data.hpp>

#include <set>

#include <userver/dynamic_config/snapshot.hpp>
#include <userver/storages/postgres/cluster.hpp>

namespace hejmdal::views::postgres {

using CommandControl = storages::postgres::CommandControl;
using TestDataToCasesMap =
    std::unordered_map<std::uint32_t, std::vector<std::uint32_t>>;

class TestData {
 public:
  TestData(const storages::postgres::ClusterPtr& cluster);

  models::TestDataCreateResult Create(models::TestData&& test_data,
                                      const CommandControl& command_control);

  models::TestData Get(const std::int32_t& id,
                       const CommandControl& command_control);

  std::vector<models::TestData> Get(const std::set<std::int32_t>& ids,
                                    const CommandControl& command_control);

  void Update(const std::int32_t& id, models::TestData&& test_data,
              const CommandControl& command_control);

  void Delete(const std::int32_t& id, const CommandControl& command_control);

  std::vector<models::TestDataInfo> List(std::optional<std::string> schema_id,
                                         const CommandControl& command_control);

  TestDataToCasesMap GetTestDataToCases(const CommandControl& command_control);

 private:
  storages::postgres::ClusterPtr cluster_;
};

}  // namespace hejmdal::views::postgres
