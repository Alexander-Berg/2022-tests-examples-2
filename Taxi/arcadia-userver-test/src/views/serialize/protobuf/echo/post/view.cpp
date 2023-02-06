#include "view.hpp"

// test that proto-grpc compiles for tier0
#include <arcadia_userver_test/proto/grpc_sample_shared_client.usrv.pb.hpp>
#include <arcadia_userver_test/proto/grpc_sample_shared_service.usrv.pb.hpp>
#include <grpc_sample_client.usrv.pb.hpp>
#include <grpc_sample_service.usrv.pb.hpp>

#include <clients/bigb/client.hpp>

namespace handlers::serialize_protobuf_echo::post {

Response View::Handle(Request&& request, Dependencies&& dependencies) {
  Response200 response;

  clients::bigb::bigb::get::Request bigb_request{
      std::to_string(request.body.first()),  // puid
      "test",
      "protobuf",
  };

  const auto& bigb_response = dependencies.bigb_client.Bigb(bigb_request);
  response.body.set_sum(bigb_response.body.items(0).keyword_id() +
                        request.body.second());

  return response;
}

}  // namespace handlers::serialize_protobuf_echo::post
