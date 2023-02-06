#include "view.hpp"

#include <clients/test-client/client.hpp>

namespace handlers::logging_x_taxi_query_log_mode_check::get {

Response View::Handle(Request&& /*request*/, Dependencies&& dependencies) {
  namespace client_ns =
      clients::test_client::logging_x_taxi_query_log_mode::get;
  auto& client = dependencies.test_client_client;

  client.LoggingXTaxiQueryLogMode({"secret"});

  return Response200();
}

}  // namespace handlers::logging_x_taxi_query_log_mode_check::get
