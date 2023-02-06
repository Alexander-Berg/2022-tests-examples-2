#include <tvm2/auth_checker_service_testing.hpp>

namespace tvm2 {

AuthCheckerServiceTesting::AuthCheckerServiceTesting(AuthorizerPtr authorizer)
    : authorizer_(std::move(authorizer)) {}

AuthCheckerServiceTesting::AuthCheckResult AuthCheckerServiceTesting::CheckAuth(
    const server::http::HttpRequest& request,
    server::request::RequestContext& request_context) const {
  using namespace server::handlers::auth;

  return authorizer_->CheckServiceTicket(request, request_context,
                                         Authorizer::kIgnoreMissingAuthToken);
}

}  // namespace tvm2
