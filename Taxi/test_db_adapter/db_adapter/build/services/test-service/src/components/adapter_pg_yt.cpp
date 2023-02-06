#include <userver/components/component.hpp>
#include <userver/utils/datetime.hpp>

#include <components/adapter_pg_yt.hpp>

#include <test_service/sql_queries.hpp>

#include <db-adapter/db-adapter.hpp>

namespace db_adapter {

using PKeyKeyFooKeyBar = components::adapter_pg_yt::PKeyKeyFooKeyBar;

template <>
struct DataTrait<handlers::ComplicatedRow, PKeyKeyFooKeyBar> {
  static PKeyKeyFooKeyBar GetPrimaryKey(const handlers::ComplicatedRow& doc) {
    return std::make_tuple(doc.key_foo, doc.key_bar);
  }
  static bool NeedDummyColdCheck(
      [[maybe_unused]] const handlers::ComplicatedRow& doc,
      [[maybe_unused]] const dynamic_config::Source taxi_config) {
    return true;
  }
};

}  // namespace db_adapter

namespace components::adapter_pg_yt {
namespace {
const yt_replica_reader::models::Aliases kAliasesOneByPrimaryKey = {
    {"main_table.old_value", "value"}};

}  // namespace

AdapterMaster::AdapterMaster(const components::ComponentConfig& config,
                             const components::ComponentContext& context)
    : LoggableComponentBase(config, context),
      pg_database_(
          context.FindComponent<components::Postgres>("postgresql-random")
              .GetDatabase()),
      yt_reader_(
          context
              .FindComponent<yt_replica_reader::components::YtReplicaReader>()
              .GetYtReader()),
      taxi_config_(
          context.FindComponent<::components::DynamicConfig>().GetSource())
{
  {
    auto pg_layer = db_adapter::pg::PgWrapper(
        pg_database_->GetCluster(),
        userver_db_adapter_sample::sql::kSampleRetrieveOne);
    auto yt_layer = db_adapter::yt::YtWrapper(
        yt_reader_, "pg_yt_composite_primary_key", {"key_foo", "key_bar"},
        kAliasesOneByPrimaryKey);
    retrieve_one_by_primary_key_ = ::db_adapter::RetrieveOneAdapter<
        handlers::ComplicatedRow, PKeyKeyFooKeyBar, ::db_adapter::pg::PgWrapper,
        ::db_adapter::yt::YtWrapper>::Create({pg_layer, yt_layer},
                                             taxi_config_);
  }
}

std::optional<handlers::ComplicatedRow> AdapterMaster::RetrieveOneByPrimaryKey(
    std::string key_foo, std::int64_t key_bar, const Options& options) const {
  return retrieve_one_by_primary_key_->RetrieveOne(
      {std::move(key_foo), std::move(key_bar)}, options);
}

}  // namespace components::adapter_pg_yt
