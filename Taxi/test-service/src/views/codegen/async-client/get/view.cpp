#include "view.hpp"

#include <clients/codegen/response_future.hpp>
#include <clients/test-service/client.hpp>

namespace handlers::codegen_async_client::get {

namespace {

const auto kRequests = 20;
}

Response View::Handle(Request&& /*request*/, Dependencies&& dependencies) {
  using Future = ::clients::codegen::ResponseFuture<
      clients::test_service::codegen_async_client::get::Response>;

  std::vector<Future> futures;
  auto& client = dependencies.test_service_client;

  futures.reserve(kRequests);
  for (int i = 0; i < kRequests; i++) {
    futures.push_back(client.AsyncCodegenAsyncClient());
  }

  for (auto&& future : futures) {
    future.Get();
  }

  return Response200{};
}

}  // namespace handlers::codegen_async_client::get
