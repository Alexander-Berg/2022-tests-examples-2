#pragma once

#include <handlers/databases/clickhouse/value/get/request.hpp>
#include <handlers/databases/clickhouse/value/get/response.hpp>
#include <handlers/dependencies.hpp>

namespace handlers::databases_clickhouse_value::get {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);
};

}  // namespace handlers::databases_clickhouse_value::get
