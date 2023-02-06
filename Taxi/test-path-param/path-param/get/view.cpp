#include "view.hpp"

#include <clients/userver-sample/client.hpp>

namespace handlers::autogen_test_path_param_path_param::get {

Response View::Handle(Request&& request, Dependencies&& dependencies) {
  namespace client_ns =
      clients::userver_sample::autogen_test_path_param_path_param::get;

  auto& client = dependencies.userver_sample_client;
  auto response = client.AutogenTestPathParamPathParam(
      client_ns::Request{request.path_param});

  return Response200{response.path_param};
}

}  // namespace handlers::autogen_test_path_param_path_param::get
