#pragma once

#include <tvm2/authorizer.hpp>

#include <userver/server/handlers/auth/auth_checker_base.hpp>
#include <userver/server/http/http_request.hpp>

namespace tvm2 {

class AuthCheckerServiceTesting final
    : public server::handlers::auth::AuthCheckerBase {
 public:
  using AuthCheckResult = server::handlers::auth::AuthCheckResult;

  explicit AuthCheckerServiceTesting(AuthorizerPtr authorizer);

  [[nodiscard]] AuthCheckResult CheckAuth(
      const server::http::HttpRequest& request,
      server::request::RequestContext& request_context) const override;

  [[nodiscard]] bool SupportsUserAuth() const noexcept override {
    return false;
  }

 private:
  const AuthorizerPtr authorizer_;
};

}  // namespace tvm2
