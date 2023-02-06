#pragma once

#include <memory>

#include <userver/components/component_config.hpp>
#include <userver/components/component_context.hpp>

#include <handlers/composite-primary-key/post/response.hpp>

#include <userver/dynamic_config/fwd.hpp>
#include <userver/dynamic_config/storage/component.hpp>
#include <userver/storages/postgres/component.hpp>
#include <yt-replica-reader/components/yt_replica_reader.hpp>

#include <db-adapter/db-adapter-abstract.hpp>
#include <db-adapter/pg-adapter.hpp>
#include <db-adapter/yt-adapter.hpp>

namespace components::adapter_pg_yt {

using Options = db_adapter::options::Options<db_adapter::pg::options::Options,
                                             db_adapter::yt::options::Options>;

using PKeyKeyFooKeyBar = std::tuple<std::string, std::int64_t>;

class AdapterMaster final: public components::LoggableComponentBase {
 public:
  static constexpr const char* kName = "db-adapter-pg-yt";

  AdapterMaster(const components::ComponentConfig& config,
                const components::ComponentContext& context);
  ~AdapterMaster() {}

  template <typename... Option>
  Options MakeOptions(Option&&... options) const {
    return db_adapter::options::MakeOptions<db_adapter::pg::options::Options,
                                            db_adapter::yt::options::Options>(
        std::forward<Option>(options)...);
  }

  std::optional<handlers::ComplicatedRow> RetrieveOneByPrimaryKey(
      std::string key_foo, std::int64_t key_bar,
      const Options& options = {}) const;

 private:
  ::storages::postgres::DatabasePtr pg_database_;
  const yt_replica_reader::YtReader& yt_reader_;
  const dynamic_config::Source taxi_config_;

  std::unique_ptr<::db_adapter::RetrieveOneAdapterAbstract<
      handlers::ComplicatedRow, PKeyKeyFooKeyBar, ::db_adapter::pg::PgWrapper,
      ::db_adapter::yt::YtWrapper>>
      retrieve_one_by_primary_key_;
};

}  // namespace components::adapter_pg_yt
