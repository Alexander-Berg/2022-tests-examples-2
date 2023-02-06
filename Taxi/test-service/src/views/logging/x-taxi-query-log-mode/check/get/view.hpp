#pragma once

#include <handlers/dependencies.hpp>
#include <handlers/logging/x-taxi-query-log-mode/check/get/request.hpp>
#include <handlers/logging/x-taxi-query-log-mode/check/get/response.hpp>

namespace handlers::logging_x_taxi_query_log_mode_check::get {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);
};

}  // namespace handlers::logging_x_taxi_query_log_mode_check::get
