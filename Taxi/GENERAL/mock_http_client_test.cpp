#include <utest/routing/mock_http_client.hpp>

namespace clients::routing {
namespace utest {

std::shared_ptr<clients::Http> CreateHttpTvmClient() {
  auto http_client = ::utest::CreateHttpClient();
  return std::make_shared<::tvm2::utest::MockClientContext>(*http_client);
}

}  // namespace utest
}  // namespace clients::routing
