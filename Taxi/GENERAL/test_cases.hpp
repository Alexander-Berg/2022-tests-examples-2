#pragma once

#include <models/postgres/test_case.hpp>
#include <userver/dynamic_config/snapshot.hpp>
#include <userver/storages/postgres/cluster.hpp>

namespace hejmdal::views::postgres {

using CommandControl = storages::postgres::CommandControl;
using TestCaseCreateResult = std::int32_t;

class TestCases {
 public:
  TestCases(const storages::postgres::ClusterPtr& cluster);

  TestCaseCreateResult Create(models::postgres::TestCase&& test_case,
                              const CommandControl& command_control);

  models::postgres::TestCase Get(const std::int32_t& id,
                                 const CommandControl& command_control);

  std::vector<models::postgres::TestCase> Get(
      const std::vector<std::int32_t>& ids,
      const CommandControl& command_control);

  std::vector<models::postgres::TestCase> GetForSchema(
      const std::string& schema_id, const CommandControl& command_control);

  void Update(const std::int32_t& id, models::postgres::TestCase&& test_case,
              const CommandControl& command_control);

  void Delete(const std::int32_t& id, const CommandControl& command_control);

  void Activate(const std::int32_t& id, bool do_activate,
                const CommandControl& command_control);

  std::vector<models::postgres::TestCaseInfo> List(
      std::optional<std::string> schema_id,
      const CommandControl& command_control);

 private:
  storages::postgres::ClusterPtr cluster_;
};

}  // namespace hejmdal::views::postgres
