#include "view.hpp"

#include <userver/storages/clickhouse/cluster.hpp>
#include <userver/storages/clickhouse/io/columns/string_column.hpp>
#include <userver/storages/clickhouse/io/io_fwd.hpp>
#include <userver/storages/clickhouse/query.hpp>

namespace {

struct Data final {
  std::vector<std::string> ids;
  std::vector<std::string> values;
};

}  // namespace

namespace storages::clickhouse::io {

template <>
struct CppToClickhouse<Data> {
  using mapped_type = std::tuple<columns::StringColumn, columns::StringColumn>;
};

}  // namespace storages::clickhouse::io

namespace handlers::databases_clickhouse_value::get {

Response View::Handle(Request&& request, Dependencies&& dependencies) {
  const auto& cluster = dependencies.ch_arcadia_test;

  const storages::clickhouse::Query q{
      "SELECT id, value FROM test_values WHERE id = {}"};
  const auto data = cluster->Execute(q, request.key).As<Data>();
  if (data.values.size() != 1) {
    throw std::runtime_error{"Unexpected data size"};
  }

  handlers::OkayValueResponse res{data.values.front()};
  return Response200{std::move(res)};
}

}  // namespace handlers::databases_clickhouse_value::get
