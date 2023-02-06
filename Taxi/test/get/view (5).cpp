#include "view.hpp"

#include <userver/utils/assert.hpp>

#include <clients/userver-sample/client.hpp>

namespace handlers::autogen_mockserver_test::get {

Response View::Handle(Request&& /*request*/, Dependencies&& dependencies) {
  namespace clients_empty_get = clients::userver_sample::autogen_empty::get;
  Response200 response;

  response.status = "ok";
  try {
    dependencies.userver_sample_client.AutogenEmptyGet();

    // Unfortunatley there is no other way to tell exception type but message
  } catch (const clients_empty_get::TimeoutException& exc) {
    response.status = "timeout_error";
    response.message = exc.what();
  } catch (const clients_empty_get::Exception& exc) {
    response.status = "error";
    response.message = exc.what();
  }

  return response;
}

}  // namespace handlers::autogen_mockserver_test::get
