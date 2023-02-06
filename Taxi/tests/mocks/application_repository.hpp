#pragma once

#include "internal/client_application/repository.hpp"

#include <functional>

namespace sweet_home::mocks {

using GetMenuForApplicationHandler =
    std::function<client_application::SDKMenu(const core::SDKClient&)>;

class ApplicationRepositoryMock
    : public client_application::ApplicationRepository {
 private:
  GetMenuForApplicationHandler handler_;

 public:
  ApplicationRepositoryMock(const GetMenuForApplicationHandler& handler)
      : handler_(handler){};

  client_application::SDKMenu GetMenuForApplication(
      const core::SDKClient& sdk_client) const override {
    return handler_(sdk_client);
  }
};

}  // namespace sweet_home::mocks
